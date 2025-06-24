"""
Workiva Role Visualization

This script creates visualizations from the Workiva_Account_Aggregation.csv file
to show roles assigned per user.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from collections import Counter

# Set style for plots
plt.style.use('ggplot')
sns.set_palette("viridis")

def load_data(file_path):
    """Load CSV data from the given file path"""
    print(f"Loading data from {file_path}")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows of data")
    print(f"Found {df['Username'].nunique()} unique users")
    return df

def plot_role_distribution(df):
    """Create a bar chart of role distribution"""
    print("Creating role distribution plot...")
    
    # Count occurrences of each role
    role_counts = Counter(df['Roles'])
    
    # Sort roles by count in descending order
    sorted_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)
    roles = [r[0] for r in sorted_roles]
    counts = [r[1] for r in sorted_roles]
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    bars = plt.bar(roles, counts)
    
    # Add count labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.title('Distribution of Roles in Workiva', fontsize=16)
    plt.xlabel('Role', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'role_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Role distribution plot saved to {output_path}")
    
    return output_path

def plot_users_with_most_roles(df, top_n=20):
    """Create a bar chart of users with the most roles"""
    print(f"Creating plot for top {top_n} users with most roles...")
    
    # Count the number of roles per user
    user_role_counts = df.groupby('Username').size().sort_values(ascending=False)
    
    # Take the top N users
    top_users = user_role_counts[:top_n]
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    bars = plt.bar(top_users.index, top_users.values)
    
    # Add count labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.title(f'Top {top_n} Users with Most Assigned Roles', fontsize=16)
    plt.xlabel('Username', fontsize=12)
    plt.ylabel('Number of Roles', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'top_users_by_roles.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Top users plot saved to {output_path}")
    
    return output_path

def plot_role_heatmap(df, top_n_users=30, top_n_roles=15):
    """Create a heatmap showing which users have which roles"""
    print(f"Creating role assignment heatmap for top {top_n_users} users and top {top_n_roles} roles...")
    
    # Get users with most roles
    user_role_counts = df.groupby('Username').size().sort_values(ascending=False)
    top_users = user_role_counts[:top_n_users].index.tolist()
    
    # Get most common roles
    role_counts = Counter(df['Roles'])
    top_roles = [role for role, _ in role_counts.most_common(top_n_roles)]
    
    # Filter the dataframe to include only top users and roles
    df_filtered = df[df['Username'].isin(top_users) & df['Roles'].isin(top_roles)]
    
    # Create a pivot table (1 for role assigned, 0 for not assigned)
    pivot_df = pd.crosstab(df_filtered['Username'], df_filtered['Roles'])
    
    # Create the heatmap
    plt.figure(figsize=(14, 10))
    sns.heatmap(pivot_df, cmap='viridis', cbar_kws={'label': 'Role Assigned'}, linewidths=0.5)
    
    plt.title(f'Role Assignments for Top {top_n_users} Users', fontsize=16)
    plt.ylabel('Username', fontsize=12)
    plt.xlabel('Role', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'role_assignment_heatmap.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Role assignment heatmap saved to {output_path}")
    
    return output_path

def plot_role_pie_chart(df):
    """Create a pie chart of the most common roles"""
    print("Creating role distribution pie chart...")
    
    # Count occurrences of each role
    role_counts = Counter(df['Roles'])
    
    # Get the top 10 roles and combine the rest as "Other"
    top_roles = role_counts.most_common(10)
    top_role_names = [r[0] for r in top_roles]
    top_role_counts = [r[1] for r in top_roles]
    
    # Calculate "Other" category
    other_count = sum(cnt for role, cnt in role_counts.items() if role not in top_role_names)
    
    # Add "Other" if significant
    if other_count > 0:
        top_role_names.append('Other')
        top_role_counts.append(other_count)
    
    # Create the plot
    plt.figure(figsize=(10, 10))
    plt.pie(top_role_counts, labels=top_role_names, autopct='%1.1f%%', 
            shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    plt.title('Distribution of Top 10 Roles', fontsize=16)
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'role_distribution_pie.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Role distribution pie chart saved to {output_path}")
    
    return output_path

def create_html_report(file_paths):
    """Create an HTML report with all visualizations"""
    print("Creating HTML report...")
    
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
        .visualization {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        .visualization img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }
        .description {
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <h1>Workiva Role Assignment Visualization</h1>
    <div class="timestamp">Generated on: """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + """</div>
    
    <div class="visualization">
        <h2>Distribution of Roles</h2>
        <div class="description">
            <p>This bar chart shows the distribution of different roles assigned in the Workiva system.</p>
            <p>The height of each bar represents the number of users assigned to that role.</p>
        </div>
        <img src="role_distribution.png" alt="Distribution of Roles">
    </div>
    
    <div class="visualization">
        <h2>Top Users by Number of Assigned Roles</h2>
        <div class="description">
            <p>This bar chart displays the users with the highest number of assigned roles.</p>
            <p>Users with more roles typically have broader access rights within the system.</p>
        </div>
        <img src="top_users_by_roles.png" alt="Top Users by Roles">
    </div>
    
    <div class="visualization">
        <h2>Role Assignment Heatmap</h2>
        <div class="description">
            <p>This heatmap visualizes which roles are assigned to which users.</p>
            <p>Each colored cell indicates that a specific role (column) is assigned to a specific user (row).</p>
        </div>
        <img src="role_assignment_heatmap.png" alt="Role Assignment Heatmap">
    </div>
    
    <div class="visualization">
        <h2>Distribution of Top 10 Roles (Pie Chart)</h2>
        <div class="description">
            <p>This pie chart shows the relative distribution of the top 10 most common roles.</p>
            <p>Each slice represents the percentage of the total role assignments that belong to that role.</p>
        </div>
        <img src="role_distribution_pie.png" alt="Role Distribution Pie Chart">
    </div>
    
</body>
</html>
"""
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workiva_role_visualization.html')
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report saved to {output_path}")
    return output_path

def main():
    """Main function to run the visualization"""
    print("Starting Workiva role visualization...")
    
    # Load data
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Workiva_Account_Aggregation.csv')
    df = load_data(file_path)
    
    # Create visualizations
    paths = []
    paths.append(plot_role_distribution(df))
    paths.append(plot_users_with_most_roles(df))
    paths.append(plot_role_heatmap(df))
    paths.append(plot_role_pie_chart(df))
    
    # Create HTML report
    html_path = create_html_report(paths)
    
    print(f"Visualization complete! Open {html_path} to view the report.")
    
    return html_path

if __name__ == "__main__":
    main()
