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
from scumProgram import scumProgram

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
    


if __name__ == "__main__":

    last_commit_hash = None  # Variable to store the last commit hash checked

    while 1:

        # Check if the current time matches the specified time to run
        now = datetime.now()
        if RUN_IN_DEV_MODE or now.strftime("%H:%M") == TIME_TO_RUN:
            print("Checking for new commits...")

            # Pull the latest changes from the Git repository
            if pull_latest_changes():
                # Get the latest commit hash
                current_commit_hash = get_commit_hash()

                # If we have a new commit, run the validation tests
                if current_commit_hash and current_commit_hash != last_commit_hash:
                    print(f"New commit detected: {current_commit_hash}")
                    last_commit_hash = current_commit_hash

                    # Run the validation tests
                    print("Running validation tests...")

                    # Flash the SCuM chip
                    scumProgram()

                    # Run the validation test
                    validate_analog_signals()
                
                else:
                    print("No new commits detected.")


        # Sleep for a while before checking again
        time.sleep(60)