import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import datetime, timezone

def generate_html_report(test_results, filename="test_results_report.html"):
    """
    Generate a self-contained HTML report from test results and save it to a file.
    
    For each sub-test:
      1. Process the list of value objects in order.
      2. If a value qualifies as graphable data (a list of numbers, a list-of-[x,y] pairs, or an image path),
         then generate its graph.
      3. For list-of-[x,y] pairs, pair the data with the next available axis label object.
      4. Display all graphable values (with graphs) first, then the remaining values as plain text.
    
    Args:
        test_results (dict): Dictionary containing test results.
        filename (str): Output HTML file path.
    
    Returns:
        None
    """
    
    # ============================
    # Helper Functions
    # ============================
    
    def is_image_path(file_path):
        """
        Return True if the provided file_path string appears to be an image path.
        """
        if not isinstance(file_path, str):
            return False
        file_path_lower = file_path.lower()
        return file_path_lower.endswith('.png') or file_path_lower.endswith('.jpg') or \
               file_path_lower.endswith('.jpeg') or file_path_lower.endswith('.gif')
    
    def is_graph_data(data_value):
        """
        Return True if data_value qualifies as graphable:
          - A non-empty list of numbers.
          - A non-empty list of [x, y] pairs (each pair is a list with 2 numbers).
        """
        if isinstance(data_value, list) and data_value:
            # Check for a list of numbers.
            if all(isinstance(item, (int, float)) for item in data_value):
                return True
            # Check for a list of [x,y] pairs.
            if all(isinstance(pair, list) and len(pair) == 2 and 
                   all(isinstance(num, (int, float)) for num in pair) for pair in data_value):
                return True
        return False
    
    def encode_plot_image(plot_data, plot_title, x_axis_label, y_axis_label):
        """
        Create a plot from the provided plot_data and return a base64-encoded PNG image.
        
        If plot_data is a list-of-[x,y] pairs, extract x and y values.
        Otherwise, treat plot_data as a simple list of numbers.
        """
        fig, axis = plt.subplots()
        if isinstance(plot_data, list) and plot_data and isinstance(plot_data[0], list) and len(plot_data[0]) == 2:
            x_values = [pair[0] for pair in plot_data]
            y_values = [pair[1] for pair in plot_data]
            axis.plot(x_values, y_values, marker='o')
        else:
            axis.plot(plot_data, marker='o')
        axis.set_title(plot_title)
        axis.set_xlabel(x_axis_label)
        axis.set_ylabel(y_axis_label)
        plt.tight_layout()
    
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')
    
    def generate_graph_html(data_value, title="Graph", x_axis_label=None, y_axis_label=None):
        """
        Determine whether data_value should be graphed and return an HTML snippet.
        
        Cases:
          1. If data_value is graphable numeric data:
             - For a list-of-[x,y] pairs, use provided axis labels if available, else default to "no label given".
             - For a simple list of numbers, use default labels "Index" and "Value".
          2. If data_value is a string that looks like an image path, verify that the file exists and embed the image.
          3. Otherwise, return the text representation of data_value.
        """
        # Case 1: Graphable numeric data.
        if is_graph_data(data_value):
            if isinstance(data_value[0], list) and len(data_value[0]) == 2:
                if x_axis_label is None or y_axis_label is None:
                    x_axis_label = x_axis_label or "no label given"
                    y_axis_label = y_axis_label or "no label given"
                    print(f"Warning: No axis labels provided for '{title}'. Using default labels.")
            else:
                x_axis_label = "Index"
                y_axis_label = "Value"
            encoded_image = encode_plot_image(data_value, title, x_axis_label, y_axis_label)
            return f"<br><img src='data:image/png;base64,{encoded_image}' alt='Graph for {title}'>"
        
        # Case 2: Image file path.
        elif isinstance(data_value, str) and is_image_path(data_value):
            if os.path.exists(data_value):
                try:
                    with open(data_value, "rb") as image_file:
                        encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    return f"<br><img src='data:image/png;base64,{encoded}' alt='Embedded Image for {title}'>"
                except Exception as error:
                    print(f"Error reading image at {data_value}: {error}")
                    return f"<br><span class='failed'>Error reading image for {title}.</span>"
            else:
                print(f"Image path not valid: {data_value}")
                return f"<br><span class='failed'>Image path not valid: {data_value}</span>"
        
        # Case 3: Not graphable data; display as text.
        else:
            return f"<br>{data_value}"
    
    def process_sub_test_values(value_objects):
        """
        Process the list of value_objects from a sub-test.
        
        Returns two lists:
          - graph_htmls: HTML snippets for each graphable value.
          - other_htmls: HTML snippets for non-graphable values.
        
        Flow:
          - Iterate through value_objects in order.
          - For a value object with graphable list-of-[x,y] data, look ahead to pair it with the next axis label object.
          - Process simple graphable data or image paths immediately.
          - Non-graphable values are collected as plain text.
        """
        graph_htmls = []
        other_htmls = []
        used_indices = set()  # Indices of value objects that have been paired as axis labels.
        index = 0
        while index < len(value_objects):
            # Skip already paired axis label objects.
            if index in used_indices:
                index += 1
                continue

            value_object = value_objects[index]
            value_name = value_object.get("name", "Value")
            data_value = value_object.get("value", "")
            
            # If this object is an axis label not paired, add it as text.
            if value_name == "axis_label" and isinstance(data_value, dict):
                other_htmls.append(f"<li>{value_name}: {data_value}</li>")
                index += 1
                continue
            
            # If data_value qualifies as graphable (or is an image path).
            if is_graph_data(data_value) or (isinstance(data_value, str) and is_image_path(data_value)):
                # For list-of-[x,y] pairs, look ahead for the next axis label object.
                if isinstance(data_value, list) and data_value and isinstance(data_value[0], list) and len(data_value[0]) == 2:
                    paired_axis_labels = None
                    lookahead_index = index + 1
                    while lookahead_index < len(value_objects):
                        candidate = value_objects[lookahead_index]
                        if candidate.get("name") == "axis_label" and isinstance(candidate.get("value"), dict):
                            paired_axis_labels = candidate.get("value")
                            used_indices.add(lookahead_index)
                            break
                        lookahead_index += 1
                    if paired_axis_labels:
                        x_axis_label = paired_axis_labels.get("x-label", "no label given")
                        y_axis_label = paired_axis_labels.get("y-label", "no label given")
                    else:
                        x_axis_label = "no label given"
                        y_axis_label = "no label given"
                        print(f"Warning: No axis labels provided for '{value_name}'. Using default labels.")
                    graph_html = generate_graph_html(data_value, title=value_name,
                                                     x_axis_label=x_axis_label, y_axis_label=y_axis_label)
                    graph_htmls.append(f"<li>{value_name}:{graph_html}</li>")
                else:
                    # For simple lists of numbers or image paths.
                    graph_html = generate_graph_html(data_value, title=value_name)
                    graph_htmls.append(f"<li>{value_name}:{graph_html}</li>")
            else:
                # Not graphable; add as plain text.
                other_htmls.append(f"<li>{value_name}: {data_value}</li>")
            index += 1

        return graph_htmls, other_htmls
    
    def get_css_styles():
        """
        Return a string of CSS styles used to format the HTML report.
        """
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
    
    def get_unit_pass_status(tests):
        """
        Return True if every test in the unit has non-empty results and all its sub-tests pass.
        """
        for test_data in tests.values():
            results = test_data.get("results", [])
            if not results or not all(sub_test.get("pass", False) for sub_test in results):
                return False
        return True

    # ============================
    # Build the HTML Report
    # ============================
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
    
    # Insert the current UTC timestamp.
    current_timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y — %H:%M UTC")
    html_parts.append(f"<p><em>Generated on: {current_timestamp}</em></p>")
    
    # Loop through each unit test.
    for unit_name, unit_data in test_results.items():
        tests = unit_data.get("tests", {})
        unit_pass = get_unit_pass_status(tests)
        unit_status = "✅ PASSED" if unit_pass else "❌ FAILED"
        unit_class = "passed" if unit_pass else "failed"
        html_parts.append(f"<div class='unit-test'><h2>{unit_name} - <span class='{unit_class}'>{unit_status}</span></h2>")
    
        # Loop through each test within the unit.
        for test_name, test_data in tests.items():
            sub_tests = test_data.get("results", [])
            if not sub_tests:
                html_parts.append(f"<div class='test'><h3>{test_name} - <span class='failed'>FAILED</span></h3>")
                html_parts.append("<p>No sub-tests provided.</p></div>")
                continue
    
            test_pass = all(sub_test.get("pass", False) for sub_test in sub_tests)
            test_status = "PASSED" if test_pass else "FAILED"
            test_class = "passed" if test_pass else "failed"
            html_parts.append(f"<div class='test'><h3>{test_name} - <span class='{test_class}'>{test_status}</span></h3>")
    
            # Process each sub-test.
            for sub_test in sub_tests:
                sub_test_name = sub_test.get("sub-test", "Unnamed Sub-Test")
                sub_test_pass = sub_test.get("pass", False)
                sub_test_status = "PASSED" if sub_test_pass else "FAILED"
                sub_test_class = "passed" if sub_test_pass else "failed"
                html_parts.append(f"<div class='sub-test'><strong>{sub_test_name}</strong>: <span class='{sub_test_class}'>{sub_test_status}</span></div>")
    
                # Process the values for the current sub-test.
                value_objects = sub_test.get("values", [])
                graph_html_snippets, other_html_snippets = process_sub_test_values(value_objects)
    
                if graph_html_snippets:
                    html_parts.append("<ul class='values'>")
                    html_parts.extend(graph_html_snippets)
                    html_parts.append("</ul>")
                if other_html_snippets:
                    html_parts.append("<ul class='values'>")
                    html_parts.extend(other_html_snippets)
                    html_parts.append("</ul>")
    
            html_parts.append("</div>")  # End test block.
        html_parts.append("</div>")  # End unit test block.
    html_parts.append("</body>")
    html_parts.append("</html>")
    
    # Write the complete HTML to the output file.
    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(html_parts))
    print(f"✅ HTML report saved to '{filename}'")





if __name__ == "__main__":
    import random
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
                                # CASE: two [x,y] pair plots with axis labels
                        {'sub-test': 'Frequency Calibration - Channel Iota', 'pass': True, 'values': [{'name': 'Frequency', 'value': [[x, random.uniform(0.0, 100.0)] for x in range(100, 10100, 100)]}, {'name': 'axis_label', 'value': {'x-label': 'Time (s)', 'y-label': 'Frequency (Hz)'}}, {'name': 'Not Frequency', 'value': [[x, random.uniform(0.0, 100.0)] for x in range(0, 101)]}, {'name': 'axis_label', 'value': {'x-label': 'Not Time (s)', 'y-label': 'Not Frequency (Hz)'}}]},
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
