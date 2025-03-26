'''
This script will pull the latest changes from the specified Git repository and branch,
flash the SCuM chip, and run the validation tests.

Script will run at a specified time each day.

'''
from datetime import datetime
import subprocess
import time

from Config import *
from Analog import validate_analog_signals
from scumProgram import scum_program
import os
import sys

def get_commit_hash():
    """
    Get the latest commit hash from the Git repository.

    Returns:
        str: The latest commit hash.
    """
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, cwd=GIT_DIRECTORY)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Failed to get commit hash: {e}")
        return None
    
def get_file_commit_hash(file_path):
    """
    Get the commit hash of a specific file from the Git repository.

    Args:
        file_path (str): The relative path to the file within the Git repository.

    Returns:
        str: The commit hash of the file, or None if an error occurs or the result is empty.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-n", "1", "--pretty=format:%H", "--", file_path],
            check=True,
            capture_output=True,
            text=True,
            cwd=GIT_DIRECTORY
        )
        commit_hash = result.stdout.strip()
        if not commit_hash:
            print(f"Error: Commit hash for file '{file_path}' is empty.")
            return None
        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Failed to get commit hash for file '{file_path}': {e}")
        return None
    
def pull_latest_changes():
    """
    Pull the latest changes from the Git repository.

    Returns:
        bool: True if the pull was successful, False otherwise.
    """
    try:
        result = subprocess.run(["git", "pull"], check=True, capture_output=True, text=True, cwd=GIT_DIRECTORY)
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull from Git repository: {e}")
        return False
    
     # Check for any errors in the output,
    if result.stderr:
        print(f"Git pull failed with error: {result.stderr}")
        return False
    
    return True

# List of tests to be performed on each binary
# NOTE: Program upload and Power Consumption must be the first and last tests respectively
tests = [
    { 'name': 'Program upload',         'function': scum_program,            },
    { 'name': 'Analog validation',      'function': validate_analog_signals, },
    { 'name': 'Power Consumption',      'function': None,                    },
]

# Sanity check
if tests[0]['name'] != "Program upload": 
    print("Error: The first test must be 'Program upload'. Exiting...")
    sys.exit(1)

if __name__ == "__main__":

    last_commit_hash = None  # Variable to store the last commit hash checked
    test_results = {}  # List to store test results

    # Check if the GitTestingRepos directory exists
    if not os.path.exists(GIT_DIRECTORY):
        print(f"Error: The directory '{GIT_DIRECTORY}' does not exist. Please run the setup script to initialize the environment, and ensure the Git repository is cloned to GitTestingRepos.")
        sys.exit(1)

    # Create test results structure
    for binary in GIT_BINARY_PATHS:
        binary_name = os.path.basename(binary['path']) 
        test_results[binary_name] = {'tests': {}} 

        for test in tests:
            test_results[binary_name]['tests'][test['name']] = {'results': []}

    '''
    test_results format:
    {
        'binary_name': {
            'tests': {
                'test_name':  {'results': []},
                'test_name2': {'results': []},
            }
        },
        # Add more binaries as needed
    }

    results list is formatted as:
    [
        { 'sub-test': 'pin 1', 'pass': False, value: [] },
        { 'sub-test': 'pin 2', 'pass': False, value: [] },
        # Add more values as needed

    ]

    value list is formatted as:
    [
        {'name': 'value_name1', 'value': 0},
        {'name': 'value_name2', 'value': 1},
        # Add more values as needed
    ]
    '''

    while 1:

        changes_found = False

        # Check if the current time matches the specified time to run
        now = datetime.now()
        if RUN_IN_DEV_MODE or now.strftime("%H:%M") == TIME_TO_RUN:

            # Cycle through the binary paths to check for new changes
            for binary in GIT_BINARY_PATHS:
                # switch to the correct branch
                subprocess.run(["git", "checkout", binary['branch']], cwd=GIT_DIRECTORY) #TODO: check for errors

                # Verify if the binary file exists
                if not os.path.exists(binary['path']):
                    print(f"Error: The binary file '{binary['path']}' does not exist.")
                    continue

                # Get the binary name
                binary_name = os.path.basename(binary['path']) 

                print("Checking for new changes...")

                # Pull the latest changes from the Git repository
                if pull_latest_changes():
                    # Get the latest commit hash of binary file
                    current_commit_hash = get_file_commit_hash(binary['path'])

                    # If there are changes, run the validation tests
                    if current_commit_hash and current_commit_hash != binary['lastHash']:

                        changes_found = True

                        # Store the last commit hash for future comparisons
                        print(f"Changes detected: {current_commit_hash}")
                        binary['lastHash'] = current_commit_hash

                        # Cycle through all the tests
                        # Skip the last tests since it is handled differently
                        for test in tests[0:len(tests)-1]:

                            # Create handle to test results structure
                            results_handle = test_results[binary_name][test['name']]['results']

                            # Handle program upload differently
                            if test['name'] == 'Program upload':
                                # Flash the SCuM chip with the new binary
                                print(f"Flashing the SCuM chip with {binary['path']}...")

                                try:
                                    results_handle = test['function'](binary['path'])
                                except Exception as e:
                                    print(f"Error flashing SCuM chip for {binary['path']}:\n {e}")
                                    results_handle = {
                                            'test': 'Program upload',
                                            'pass': False,
                                            'value': []
                                        }
                                    break
                            else:
                                
                                print(f"Running test: {test['name']}...")

                                results_handle = test['function']()
                    else:
                        print("No new commits detected.")

            if changes_found:
                pass
                # TODO: Generate report

        # Sleep for a while before checking again
        time.sleep(60) 