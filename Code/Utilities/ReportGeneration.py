import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime, timezone
import random

def generate_html_report(test_results, filename="test_results_report.html"):
    """
    Generate a self-contained HTML report from test results and save it to a file.
    
    This report supports:
      - Plotting a list-of-numbers (line graph with default labels).
      - Plotting a list-of-[x,y] pairs.
          * If custom axis labels are provided (with a value object named "axis_label"), those are used.
          * Otherwise, "no label given" is used for both axes, and a warning is logged.
      - Embedding an image if a value is a valid path to an image file.
          * If the path is invalid, it logs a warning and displays that the path was not valid.
      - Only one graph is supported per sub-test.
    
    Args:
        test_results (dict): The dictionary containing the test results.
        filename (str): The output HTML file path.
    
    Returns:
        None
    """

    # ----------------------------
    # Helper: Check if a string looks like an image path.
    # ----------------------------
    def is_image_path(s):
        if not isinstance(s, str):
            return False
        lower = s.lower()
        return lower.endswith('.png') or lower.endswith('.jpg') or lower.endswith('.jpeg') or lower.endswith('.gif')

    # ----------------------------
    # Helper: Create a plot and return a base64-encoded image.
    # If 'data' is a list-of-[x,y] pairs, plot x and y separately.
    # Otherwise, treat it as a list-of-numbers.
    # ----------------------------
    def encode_plot_image(data, title, x_label="Index", y_label="Value"):
        fig, ax = plt.subplots()
        # Check if data is a list-of-pairs (each element is a list with 2 items)
        if isinstance(data, list) and data and isinstance(data[0], list) and len(data[0]) == 2:
            xs = [pair[0] for pair in data]
            ys = [pair[1] for pair in data]
            ax.plot(xs, ys, marker='o')
        else:
            ax.plot(data, marker='o')
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    # ----------------------------
    # Helper: Return CSS styles for the HTML report.
    # ----------------------------
    def get_css_styles():
        return """
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 30px;
                background-color: #f7f7f7;
            }
            .unit-test {
                background: #ffffff;
                border: 1px solid #ddd;
                border-left: 8px solid #2c3e50;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 40px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            }
            .test {
                border: 1px solid #ccc;
                padding: 10px;
                margin-top: 15px;
                border-radius: 6px;
                background-color: #fcfcfc;
            }
            .passed { color: green; font-weight: bold; }
            .failed { color: red; font-weight: bold; }
            .sub-test { margin-left: 20px; margin-top: 10px; }
            .values { margin-left: 40px; font-size: 90%; }
            img { margin-left: 40px; max-width: 600px; border: 1px solid #aaa; margin-top: 5px; }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; }
            h3 { margin-bottom: 8px; }
        </style>
        """

    # ----------------------------
    # Helper: Determine if the whole unit test passes.
    # A unit test passes only if every contained test has non-empty results and all sub-tests pass.
    # ----------------------------
    def get_unit_pass_status(tests):
        for test_data in tests.values():
            results = test_data.get("results", [])
            if not results or not all(sub.get("pass", False) for sub in results):
                return False
        return True

    # ----------------------------
    # Begin constructing the HTML report
    # ----------------------------
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Test Results Report</title>",
        get_css_styles(),
        "</head>",
        "<body>",
        "<h1>Test Results Report</h1>"
    ]

    # Insert UTC timestamp
    now = datetime.now(timezone.utc).strftime("%B %d, %Y — %H:%M UTC")
    html_parts.append(f"<p><em>Generated on: {now}</em></p>")

    # ----------------------------
    # Loop through each unit test
    # ----------------------------
    for unit_name, unit_data in test_results.items():
        tests = unit_data.get("tests", {})
        unit_pass = get_unit_pass_status(tests)
        unit_status = "✅ PASSED" if unit_pass else "❌ FAILED"
        unit_class = "passed" if unit_pass else "failed"
        html_parts.append(f"<div class='unit-test'><h2>{unit_name} - <span class='{unit_class}'>{unit_status}</span></h2>")

        # ------------------------
        # Loop through each test in the unit
        # ------------------------
        for test_name, test_data in tests.items():
            results = test_data.get("results", [])
            if not results:
                html_parts.append(f"<div class='test'><h3>{test_name} - <span class='failed'>FAILED</span></h3>")
                html_parts.append("<p>No sub-tests provided.</p></div>")
                continue

            test_pass = all(sub.get("pass", False) for sub in results)
            test_status = "PASSED" if test_pass else "FAILED"
            test_class = "passed" if test_pass else "failed"
            html_parts.append(f"<div class='test'><h3>{test_name} - <span class='{test_class}'>{test_status}</span></h3>")

            # ---------------------
            # Loop through each sub-test in the test
            # ---------------------
            for sub in results:
                sub_name = sub.get("sub-test", "Unnamed Sub-Test")
                sub_pass = sub.get("pass", False)
                sub_status = "PASSED" if sub_pass else "FAILED"
                sub_class = "passed" if sub_pass else "failed"
                html_parts.append(f"<div class='sub-test'><strong>{sub_name}</strong>: <span class='{sub_class}'>{sub_status}</span></div>")

                # -----------------
                # Process sub-test values:
                #   1. Custom Pair Plot: Look for a data object (list-of-[x,y] pairs) and optionally an "axis_label" object.
                #      * If axis labels are missing, use "no label given" and log a warning.
                #   2. Otherwise, if a value is a list, plot it using default labels.
                #   3. If a value is a string and looks like an image path, verify the path.
                #      * If the file exists, embed it.
                #      * Otherwise, log a warning and display that the path is not valid.
                #   4. Else, simply display the value.
                # -----------------
                values = sub.get("values", [])
                processed_indices = set()  # Track values already used in a custom plot
                axis_label_obj = None
                data_obj = None

                # First pass: Identify custom pair plot objects.
                for i, val in enumerate(values):
                    if val.get("name") == "axis_label" and isinstance(val.get("value"), dict):
                        axis_label_obj = val
                        processed_indices.add(i)
                    elif isinstance(val.get("value"), list):
                        v = val.get("value")
                        if v and isinstance(v[0], list) and len(v[0]) == 2:
                            data_obj = val
                            processed_indices.add(i)

                # If a data object is found, generate a plot.
                if data_obj is not None:
                    if axis_label_obj is not None:
                        # Use provided axis labels.
                        x_label = axis_label_obj["value"].get("x-label", "no label given")
                        y_label = axis_label_obj["value"].get("y-label", "no label given")
                    else:
                        # No axis labels provided; use defaults and log it.
                        x_label = "no label given"
                        y_label = "no label given"
                        print(f"Warning: No axis labels provided for data '{data_obj.get('name', 'Data Plot')}'. Using default labels.")
                    encoded_img = encode_plot_image(data_obj["value"], data_obj.get("name", "Data Plot"), x_label, y_label)
                    html_parts.append(
                        f"<ul class='values'><li>{data_obj.get('name', 'Data Plot')}:<br>"
                        f"<img src='data:image/png;base64,{encoded_img}' alt='Graph for {data_obj.get('name', '')}'></li></ul>"
                    )

                # Process remaining values individually.
                if values:
                    html_parts.append("<ul class='values'>")
                    for i, val in enumerate(values):
                        # Skip items already processed in custom plot.
                        if i in processed_indices:
                            continue
                        val_name = val.get("name", "Unnamed Value")
                        val_data = val.get("value", "")
                        # Case: value is a list (line graph).
                        if isinstance(val_data, list):
                            encoded_img = encode_plot_image(val_data, val_name)
                            html_parts.append(f"<li>{val_name}:<br><img src='data:image/png;base64,{encoded_img}' alt='Graph for {val_name}'></li>")
                        # Case: value is a string that looks like an image path.
                        elif isinstance(val_data, str) and is_image_path(val_data):
                            if os.path.exists(val_data):
                                try:
                                    with open(val_data, "rb") as image_file:
                                        encoded = base64.b64encode(image_file.read()).decode('utf-8')
                                    html_parts.append(f"<li>{val_name}:<br><img src='data:image/png;base64,{encoded}' alt='Embedded Image for {val_name}'></li>")
                                except Exception as e:
                                    print(f"Error reading image at {val_data}: {e}")
                                    html_parts.append(f"<li>{val_name}: <span class='failed'>Error reading image.</span></li>")
                            else:
                                print(f"Image path not valid: {val_data}")
                                html_parts.append(f"<li>{val_name}: <span class='failed'>Image path not valid: {val_data}</span></li>")
                        else:
                            # Default: simply display the value.
                            html_parts.append(f"<li>{val_name}: {val_data}</li>")
                    html_parts.append("</ul>")

            html_parts.append("</div>")  # End test
        html_parts.append("</div>")  # End unit-test
    html_parts.append("</body>")
    html_parts.append("</html>")

    # ----------------------------
    # Write the HTML report to file
    # ----------------------------
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    print(f"✅ HTML report saved to '{filename}'")



if __name__ == "__main__":
    # Sample test results 
    sample_results = {
        'Electrical Validation Suite': {
            'tests': {
                'Voltage Integrity Test': {
                    'results': [
                        {'sub-test': 'Voltage Check - Pin Alpha', 'pass': True, 'values': [{'name': 'Voltage', 'value': random.uniform(0.0, 5.0)}, {'name': 'Current', 'value': 1.2}]},
                        {'sub-test': 'Voltage Check - Pin Beta', 'pass': False, 'values': [{'name': 'Voltage', 'value': [random.uniform(0.0, 5.0) for _ in range(100)]}, {'name': 'Current', 'value': 0.1}]},
                    ]
                },
                'Resistance Verification': {
                    'results': [
                        {'sub-test': 'Resistance Test - Node Gamma', 'pass': True, 'values': [{'name': 'Resistance', 'value': 100}]},
                        {'sub-test': 'Resistance Test - Node Delta', 'pass': True, 'values': [{'name': 'Resistance', 'value': [random.uniform(100, 200) for _ in range(100)]}]},
                    ]
                },
            }
        },
        'Power Supply Diagnostics': {
            'tests': {
                'Power Stability Assessment': {
                    'results': [
                        {'sub-test': 'Power Supply Validation - Pin Epsilon', 'pass': True, 'values': [{'name': 'Voltage', 'value': 5.0}]},
                        {'sub-test': 'Current Stability - Pin Zeta', 'pass': True, 'values': [{'name': 'Current', 'value': [random.uniform(1.0, 3.0) for _ in range(100)]}]},
                    ]
                },
                'Voltage Drop Evaluation': {
                    'results': [
                        {'sub-test': 'Voltage Drop Analysis - Pin Eta', 'pass': False, 'values': [{'name': 'Voltage', 'value': [random.uniform(1.0, 2.0) for _ in range(100)]}]},
                    ]
                },
                'Current Evaluation': {
                    'results': [          # CASE: [x, y] pairs for x-y plot with axis labels and a single value
                        {'sub-test': 'Current Over Time', 'pass': True, 'values': [{'name': 'Current', 'value': [[x, random.uniform(0.0, 5.0)] for x in range(100, 10100, 100)]}, {'name': 'axis_label', 'value': {'x-label': 'Time (s)', 'y-label': 'Current (A)'}},  {'name': 'Avg Current (A)', 'value': 42}]},
                    ]
                },
            }
        },   
        'Signal Calibration Tests': {
            'tests': {
                'Frequency Accuracy Check': {
                    'results': [
                        {'sub-test': 'Frequency Calibration - Channel Theta', 'pass': True, 'values': [{'name': 'Frequency', 'value': 50.1}]},
                        {'sub-test': 'Frequency Calibration - Channel Iota', 'pass': False, 'values': [{'name': 'Frequency', 'value': [random.uniform(0.0, 100.0) for _ in range(100)]}]},
                    ]
                },
                'Signal Integrity Test': {
                    'results': [
                        {'sub-test': 'Signal Noise Test - Channel Kappa', 'pass': True, 'values': [{'name': 'Noise Level', 'value': 0.05}]},
                                        # CASE: path to image plot
                        {'sub-test': 'Signal Distortion - Channel Lambda', 'pass': False, 'values': [{'name': 'Signal Distortion', 'value': "C:\\Users\\demet\\Documents\\WEST-Lab-Capstone\\Code\\UserScripts\\img_matplotlib_plotting4.png"}]},
                    ]
                },
                'Test Evaluation': {
                    'results': [         # CASE: [x, y] pairs for x-y plot but no axis labels
                        {'sub-test': 'Signal B Over Time', 'pass': False, 'values': [{'name': 'Signal B', 'value': [[x, random.uniform(0.0, 5.0)] for x in range(100, 10100, 100)]}]},
                                        # CASE: invalid path to image plot
                        {'sub-test': 'Signal C Distortion', 'pass': False, 'values': [{'name': 'Signal C Distortion', 'value': "C:\\Users\\demet\\Documents\\WEST-Lab-Capstone\\Code\\UserScripts\\no_image_here.png"}]},
                    ]
                },
            }
        }
    }
    html_report = generate_html_report(sample_results)

    print("HTML report generated and saved to 'test_results_report.html'.")
