"""
Workiva Role Visualization using built-in libraries.

This script creates a simple HTML visualization from Workiva_Account_Aggregation.csv
that shows roles assigned per user.
"""
import csv
import os
from collections import defaultdict
from datetime import datetime

def load_data(file_path):
    """Load CSV data and process it"""
    print(f"Loading data from {file_path}")
    
    # Dictionary to store users and their roles
    user_roles = defaultdict(set)
    all_roles = set()
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            username = row['Username']
            role = row['Roles']
            user_roles[username].add(role)
            all_roles.add(role)
    
    print(f"Loaded data for {len(user_roles)} unique users with {len(all_roles)} distinct roles")
      # Convert to list of tuples (username, roles) sorted alphabetically by username
    user_role_list = [(username, list(roles)) for username, roles in user_roles.items()]
    user_role_list.sort(key=lambda x: x[0])
    
    return user_role_list, all_roles

def create_html_report(user_role_list, all_roles):
    """Generate an HTML report showing roles per user"""
    print("Creating HTML report...")
    
    all_roles_list = sorted(list(all_roles))
    
    # HTML Header with CSS styling
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workiva Role Assignment Visualization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
        }
        .header {
            background-color: #3498db;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .role-badge {
            display: inline-block;
            padding: 5px 10px;
            margin: 3px;
            background-color: #3498db;
            color: white;
            border-radius: 3px;
            font-size: 0.9em;
        }
        .role-count {
            font-weight: bold;
            color: #e74c3c;
        }
        .filter-container {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #dee2e6;
        }
        #userSearch {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 300px;
            font-size: 16px;
        }
        .summary-section {
            margin: 20px 0;
            padding: 15px;
            background-color: #ebf5fb;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        #topUsersTable {
            width: 100%;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Workiva Role Assignment Visualization</h1>
        <div class="timestamp">Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</div>
    </div>

    <div class="summary-section">
        <h2>Summary</h2>
        <p>Total unique users: <strong>""" + str(len(user_role_list)) + """</strong></p>
        <p>Total distinct roles: <strong>""" + str(len(all_roles)) + """</strong></p>
    </div>
    
    <div class="filter-container">
        <h2>Filter Users</h2>
        <input type="text" id="userSearch" onkeyup="filterTable()" placeholder="Search for username...">
    </div>
      <h2>Users and Their Role Assignments</h2>
    <p>Showing users with their assigned roles, ordered alphabetically by username:</p>
    
    <table id="usersTable">
        <thead>
            <tr>
                <th>Username</th>
                <th>Role Count</th>
                <th>Assigned Roles</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # Add rows for each user
    for username, roles in user_role_list:
        html_content += f"""
            <tr>
                <td>{username}</td>
                <td class="role-count">{len(roles)}</td>
                <td>"""
        
        for role in roles:
            html_content += f'<span class="role-badge">{role}</span> '
        
        html_content += """</td>
            </tr>"""
    
    # HTML Footer with JavaScript for filtering
    html_content += """
        </tbody>
    </table>

    <script>
        function filterTable() {
            // Get the input value
            var input = document.getElementById("userSearch");
            var filter = input.value.toLowerCase();
            var table = document.getElementById("usersTable");
            var rows = table.getElementsByTagName("tr");
            
            // Loop through all rows and hide those that don't match the search
            for (var i = 1; i < rows.length; i++) { // Start at 1 to skip header row
                var username = rows[i].getElementsByTagName("td")[0].textContent.toLowerCase();
                if (username.indexOf(filter) > -1) {
                    rows[i].style.display = "";
                } else {
                    rows[i].style.display = "none";
                }
            }
        }
    </script>
</body>
</html>
"""
    
    # Save the HTML report
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workiva_role_visualization.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report saved to {output_path}")
    return output_path

def generate_visualization(csv_file_path=None):
    """
    Main function to run the visualization, can be called from other scripts
    
    Args:
        csv_file_path (str): Optional path to CSV file, defaults to 'Workiva_Account_Aggregation.csv'
        
    Returns:
        str: Path to the generated HTML visualization file
    """
    print("Starting Workiva role visualization...")
    
    # Load data
    if csv_file_path is None:
        csv_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Workiva_Account_Aggregation.csv')
    
    user_role_list, all_roles = load_data(csv_file_path)
    
    # Create HTML report
    html_path = create_html_report(user_role_list, all_roles)
    
    print(f"Visualization complete! Open {html_path} to view the report.")
    
    return html_path

def main():
    """Main function when run as a standalone script"""
    return generate_visualization()

if __name__ == "__main__":
    main()
