import base64
import matplotlib.pyplot as plt
import random
from datetime import datetime, timezone
from io import BytesIO


def generate_html_report(test_results, filename="test_results_report.html"):
    """
    Generate a self-contained HTML report from test results and save it to a file.
    Automatically graphs list-type values and embeds them as images.

    Args:
        test_results (dict): Dictionary of test results (see format spec).
        filename (str): Output HTML file path.

    Returns:
        None
    """

    def get_unit_pass_status(tests):
        """
        Determine if an entire unit test has passed.

        A unit is only considered passed if every test has non-empty results
        AND all its sub-tests passed.
        """
        for test_data in tests.values():
            results = test_data.get("results", [])
            if not results or not all(sub.get("pass", False) for sub in results):
                return False
        return True

    def encode_plot_image(data, title):
        """
        Create a line plot from a list of values and return it as base64 string.

        Args:
            data (list): The y-values for the graph
            title (str): The name of the value (used for labeling)

        Returns:
            str: A base64-encoded PNG image string for embedding in HTML
        """
        fig, ax = plt.subplots()
        ax.plot(data, marker='o')
        ax.set_title(title)
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    def get_css_styles():
        """Return the CSS block used in the HTML."""
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
    # Begin HTML construction
    # ----------------------------
    html = [
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

    # Add report generation date in UTC
    now = datetime.now(timezone.utc).strftime("%B %d, %Y — %H:%M UTC")
    html.append(f"<p><em>Generated on: {now}</em></p>")


    # ----------------------------
    # Loop through each unit test
    # ----------------------------
    for unit_name, unit_data in test_results.items():
        tests = unit_data.get("tests", {})
        unit_pass = get_unit_pass_status(tests)
        unit_status = "✅ PASSED" if unit_pass else "❌ FAILED"
        unit_class = "passed" if unit_pass else "failed"

        html.append(f"<div class='unit-test'><h2>{unit_name} - <span class='{unit_class}'>{unit_status}</span></h2>")

        # ------------------------
        # Loop through each test
        # ------------------------
        for test_name, test_data in tests.items():
            results = test_data.get("results", [])
            if not results:
                html.append(f"<div class='test'><h3>{test_name} - <span class='failed'>FAILED</span></h3>")
                html.append("<p>No sub-tests provided.</p></div>")
                continue

            test_pass = all(sub.get("pass", False) for sub in results)
            test_status = "PASSED" if test_pass else "FAILED"
            test_class = "passed" if test_pass else "failed"
            html.append(f"<div class='test'><h3>{test_name} - <span class='{test_class}'>{test_status}</span></h3>")

            # ---------------------
            # Loop through sub-tests
            # ---------------------
            for sub in results:
                sub_name = sub.get("sub-test", "Unnamed Sub-Test")
                sub_pass = sub.get("pass", False)
                sub_status = "PASSED" if sub_pass else "FAILED"
                sub_class = "passed" if sub_pass else "failed"
                html.append(f"<div class='sub-test'><strong>{sub_name}</strong>: <span class='{sub_class}'>{sub_status}</span></div>")

                # -----------------
                # List/Graph values
                # -----------------
                values = sub.get("values", [])
                if values:
                    html.append("<ul class='values'>")
                    for val in values:
                        val_name = val.get("name", "Unnamed Value")
                        val_data = val.get("value", "")
                        if isinstance(val_data, list):
                            encoded_img = encode_plot_image(val_data, val_name)
                            html.append(f"<li>{val_name}:<br><img src='data:image/png;base64,{encoded_img}' alt='Graph for {val_name}'></li>")
                        else:
                            html.append(f"<li>{val_name}: {val_data}</li>")
                    html.append("</ul>")

            html.append("</div>")  # Close test
        html.append("</div>")  # Close unit-test

    # ----------------------------
    # Close and write HTML file
    # ----------------------------
    html.append("</body></html>")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

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
                    ]
                },
            }
        }
    }
    html_report = generate_html_report(sample_results)

    print("HTML report generated and saved to 'test_results_report.html'.")  # No sub-tests, considered as failed.
