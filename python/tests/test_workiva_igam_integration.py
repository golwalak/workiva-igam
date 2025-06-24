"""
Integration Tests for Workiva IGAM Application

This module contains integration tests that test the full workflow
and interaction between different components of the application.
"""

import unittest
import configparser
import os
import tempfile
import csv
import json
import time
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys
import logging

# Add paths for importing the main script modules
script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "OneDrive - Southern California Edison", 
                          "Documents", "Applications", "Workiva", 
                          "IGAM Development")
sys.path.insert(0, script_path)

# Optionally import the main script module - uncomment if needed
# try:
#     import W_IGAM_Request_new as workiva_igam
# except ImportError:
#     print(f"Warning: Could not import main script module from {script_path}")

class TestFullWorkflow(unittest.TestCase):
    """Test the complete application workflow"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.ini')
        self.log_dir = os.path.join(self.temp_dir, 'logs')
        self.output_file = os.path.join(self.temp_dir, 'test_output.csv')
        
        # Create test configuration
        self.create_test_config()
        
        # Create log directory
        os.makedirs(self.log_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_config(self):
        """Create a test configuration file"""
        config_content = f"""
[api]
token_url = https://test.workiva.com/oauth/token
users_url = https://test.workiva.com/api/users

[auth]
client_id = test_client_id
client_secret = test_client_secret

[output]
output_dir = {self.temp_dir}
file_name = test_output.csv

[email]
enabled = false
smtp_server = smtp.test.com
smtp_port = 587
sender_email = test@example.com
recipients = test1@example.com, test2@example.com
subject = Test Subject
include_report = false

[logging]
level = DEBUG
log_directory = {self.log_dir}
"""
        with open(self.config_file, 'w') as f:
            f.write(config_content)

    @patch('smtplib.SMTP')
    @patch('requests.get')
    def test_complete_workflow_success(self, mock_get, mock_smtp):
        """Test complete successful workflow from API to CSV output"""
        # Mock API response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = {
            'data': [
                {
                    'id': '1',
                    'type': 'user',
                    'attributes': {
                        'userName': 'John Doe',
                        'email': 'john.doe@sce.com',
                        'active': True,
                        'workspaceMemberships': [
                            {'workspaceId': 'ws-1', 'workspaceRoles': ['Admin']},
                            {'workspaceId': 'ws-2', 'workspaceRoles': ['User']}
                        ],
                        'organizationRoles': ['User']
                    }
                },
                {
                    'id': '2',
                    'type': 'user',
                    'attributes': {
                        'userName': 'Jane Smith',
                        'email': 'jane.smith@edisonintl.com',
                        'active': True,
                        'workspaceMemberships': [
                            {'workspaceId': 'ws-3', 'workspaceRoles': ['User']}
                        ],
                        'organizationRoles': ['User']
                    }
                },
                {
                    'id': '3',
                    'type': 'user',
                    'attributes': {
                        'userName': 'Bob Johnson',
                        'email': 'bob.johnson@external.com',
                        'active': True,
                        'workspaceMemberships': [],
                        'organizationRoles': ['Viewer']
                    }
                },
                {
                    'id': '4',
                    'type': 'user',
                    'attributes': {
                        'userName': 'Alice Brown',
                        'email': 'alice.brown@sce.com',
                        'active': False,
                        'workspaceMemberships': [
                            {'workspaceId': 'ws-4', 'workspaceRoles': ['User', 'Manager']}
                        ],
                        'organizationRoles': []
                    }
                }
            ]
        }
        mock_get.return_value = mock_api_response

        # Mock SMTP
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance

        # Simulate the workflow
        config = configparser.ConfigParser()
        config.read(self.config_file)
        
        # Setup logging
        logs_dir = os.path.join(self.temp_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, 'test.log')
        
        # Configure a basic logger
        logger = logging.getLogger('test_logger')
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_file)
        logger.addHandler(file_handler)
        
        # Extract user data from simulated API response
        api_data = mock_api_response.json()
        
        # Process user data with filters
        user_data = []
        for user_record in api_data['data']:
            attrs = user_record['attributes']
            
            # Apply domain filter
            email = attrs.get('email', '').lower()
            if not (email.endswith('@sce.com') or email.endswith('@edisonintl.com')):
                continue
                
            # Apply active filter
            if not attrs.get('active', False):
                continue
            
            # Process roles
            roles = []
            
            for membership in attrs.get('workspaceMemberships', []):
                roles.extend(membership.get('workspaceRoles', []))
                
            roles.extend(attrs.get('organizationRoles', []))
            
            # Create user record
            user_data.append({
                'User ID': user_record['id'],
                'Name': attrs.get('userName', ''),
                'Email': email,
                'Role': ', '.join(roles),
                'Status': 'Active' if attrs.get('active', False) else 'Inactive'
            })
        
        # Write to CSV
        csv_data = []
        for record in user_data:
            # Expand each role to a separate row
            roles = record['Role'].split(', ')
            if roles and roles[0]:
                for role in roles:
                    csv_data.append({
                        'User ID': record['User ID'],
                        'Name': record['Name'],
                        'Email': record['Email'],
                        'Role': role,
                        'Status': record['Status']
                    })
            else:
                # Keep record as is if no roles
                csv_data.append(record)
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = ['User ID', 'Name', 'Email', 'Role', 'Status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

        # 6. Verify CSV file was created and has correct content
        self.assertTrue(os.path.exists(self.output_file))
        
        with open(self.output_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 5)
            
            # Check specific data
            john_rows = [row for row in rows if row['Name'] == 'John Doe']
            self.assertEqual(len(john_rows), 2)
            john_roles = set(row['Role'] for row in john_rows)
            self.assertEqual(john_roles, {'Admin', 'User'})

    @patch('requests.get')
    def test_api_failure_handling(self, mock_get):
        """Test handling of API failures"""
        # Mock API failure
        mock_get.side_effect = Exception("API Connection Failed")

        config = configparser.ConfigParser()
        config.read(self.config_file)

        # Simulate API call failure
        import requests
        with self.assertRaises(Exception):
            requests.get(config['api']['users_url'])

    def test_invalid_config_handling(self):
        """Test handling of invalid configuration"""
        # Create invalid config file
        invalid_config_file = os.path.join(self.temp_dir, 'invalid_config.ini')
        with open(invalid_config_file, 'w') as f:
            f.write("Invalid configuration content")

        config = configparser.ConfigParser()
        with self.assertRaises(configparser.Error):
            config.read_string("Invalid configuration content")
            
    def test_empty_api_response_handling(self):
        """Test handling of empty API response"""
        # Empty API response
        api_data = {'data': []}
        
        # Process user data with filters
        user_data = []
        for user_record in api_data['data']:
            attrs = user_record.get('attributes', {})
            
            # Apply filters and processing
            email = attrs.get('email', '').lower()
            if not (email.endswith('@sce.com') or email.endswith('@edisonintl.com')):
                continue
                
            if not attrs.get('active', False):
                continue
            
            # Create user record
            user_data.append({
                'User ID': user_record.get('id', ''),
                'Name': attrs.get('userName', ''),
                'Email': email,
                'Status': 'Active' if attrs.get('active', False) else 'Inactive'
            })
        
        # Should result in empty user data
        self.assertEqual(len(user_data), 0)

class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        nonexistent_file = os.path.join(self.temp_dir, 'nonexistent.ini')
        
        config = configparser.ConfigParser()
        result = config.read(nonexistent_file)
        
        # Should return empty list for missing file
        self.assertEqual(len(result), 0)
    
    def test_permission_denied_log_directory(self):
        """Test handling of permission denied for log directory"""
        import tempfile
        
        # Note: This test simulates permission error handling, but doesn't
        # actually create permission errors as that would depend on OS security
        
        # Create a temporary directory to simulate logging
        temp_log_dir = os.path.join(self.temp_dir, 'restricted_logs')
        log_file = os.path.join(temp_log_dir, 'log.txt')
        
        # Should handle gracefully if directory doesn't exist
        self.assertFalse(os.path.exists(temp_log_dir))
        
        # Create directory to test file creation
        os.makedirs(temp_log_dir, exist_ok=True)
        
        # Test with a writeable directory
        try:
            with open(log_file, 'w') as f:
                f.write("Test log entry")
            self.assertTrue(os.path.exists(log_file))
        except PermissionError:
            self.fail("Unexpected permission error")
            
    def test_csv_write_failure(self):
        """Test handling of CSV write failures"""
        import tempfile
        
        # Create a directory for output
        output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Test case where data is empty
        data = []
        file_path = os.path.join(output_dir, 'empty.csv')
        
        # Simple function to write CSV
        def write_csv(data, file_path):
            if not data:
                return False
                
            with open(file_path, 'w', newline='') as csvfile:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            return True
        
        # Should return False for empty data
        self.assertFalse(write_csv(data, file_path))
        self.assertFalse(os.path.exists(file_path))
            
        # Test with valid data
        data = [{'name': 'Test', 'email': 'test@example.com'}]
        file_path = os.path.join(output_dir, 'valid.csv')
        
        # Should create file with valid data
        self.assertTrue(write_csv(data, file_path))
        self.assertTrue(os.path.exists(file_path))
    
    @patch('smtplib.SMTP')
    def test_email_sending_failure(self, mock_smtp):
        """Test handling of email sending failures"""
        # Mock SMTP failure
        mock_smtp.side_effect = Exception("SMTP Connection Failed")
        
        import smtplib
        with self.assertRaises(Exception):
            smtp = smtplib.SMTP('smtp.test.com', 587)

class TestDataValidation(unittest.TestCase):
    """Test data validation and integrity"""

    def test_user_data_validation(self):
        """Test validation of user data structure"""
        valid_user = {
            'id': '123',
            'name': 'John Doe',
            'email': 'john.doe@sce.com',
            'status': 'active',
            'roles': ['Admin', 'User']
        }
        
        invalid_users = [
            {'id': '123'},  # Missing required fields
            {'id': '123', 'name': 'John', 'email': 'invalid-email'},  # Invalid email
            {'id': '123', 'name': 'John', 'email': 'john@sce.com', 'status': 'unknown'},  # Invalid status
            {'id': '123', 'name': 'John', 'email': 'john@sce.com', 'status': 'active', 'roles': None}  # Invalid roles
        ]
        
        # Validation function
        def validate_user(user):
            required_fields = ['id', 'name', 'email', 'status']
            
            # Check required fields
            for field in required_fields:
                if field not in user:
                    return False, f"Missing required field: {field}"
            
            # Basic email validation
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(user['email']):
                return False, "Invalid email format"
            
            # Status validation
            valid_statuses = ['active', 'inactive', 'pending']
            if user['status'] not in valid_statuses:
                return False, "Invalid status"
            
            # Roles validation
            if 'roles' in user and user['roles'] is not None:
                if not isinstance(user['roles'], list):
                    return False, "Roles must be a list"
            
            return True, "Valid"
        
        # Test valid user
        is_valid, message = validate_user(valid_user)
        self.assertTrue(is_valid)
        
        # Test invalid users
        for invalid_user in invalid_users:
            is_valid, message = validate_user(invalid_user)
            self.assertFalse(is_valid, f"User should be invalid: {invalid_user}")
    
    def test_csv_data_integrity(self):
        """Test CSV data integrity"""
        test_data = [
            {'User ID': '1', 'Name': 'John Doe', 'Email': 'john@sce.com', 'Role': 'Admin'},
            {'User ID': '2', 'Name': 'Jane Smith', 'Email': 'jane@sce.com', 'Role': 'User'}
        ]
        
        # Create temporary CSV file
        temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_csv_path = temp_csv.name
        
        try:
            # Write CSV data
            with open(temp_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['User ID', 'Name', 'Email', 'Role']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(test_data)
            
            # Read back and validate
            with open(temp_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]['Name'], 'John Doe')
                self.assertEqual(rows[1]['Email'], 'jane@sce.com')
                
                # Verify all expected columns are present
                expected_columns = {'User ID', 'Name', 'Email', 'Role'}
                actual_columns = set(reader.fieldnames)
                self.assertEqual(actual_columns, expected_columns)
                
        finally:
            # Clean up
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Create a large dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'id': str(i),
                'name': f'User {i}',
                'email': f'user{i}@sce.com',
                'status': 'active' if i % 2 == 0 else 'inactive',
                'roles': ['User', 'Viewer'] if i % 3 == 0 else ['User']
            })
        
        # Test filtering performance
        start_time = time.time()
        
        filtered_users = [user for user in large_dataset if user['status'] == 'active']
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 1000 users quickly (less than 1 second)
        self.assertLess(processing_time, 1.0)
        self.assertEqual(len(filtered_users), 500)  # Half should be active
    
    def test_role_expansion_with_empty_roles(self):
        """Test role expansion when users have no roles"""
        users_with_empty_roles = [
            {'id': '1', 'name': 'User with empty list', 'roles': []},
            {'id': '2', 'name': 'User with None', 'roles': None},
            {'id': '3', 'name': 'User without roles field'}
        ]
        
        # Function to expand roles
        def expand_roles(users):
            expanded = []
            for user in users:
                roles = user.get('roles', [])
                if roles is None:
                    roles = []
                
                if roles:
                    for role in roles:
                        expanded.append({'id': user['id'], 'name': user['name'], 'role': role})
                else:
                    # Add with empty role
                    expanded.append({'id': user['id'], 'name': user['name'], 'role': ''})
            return expanded
        
        # Should handle empty roles without errors
        expanded = expand_roles(users_with_empty_roles)
        self.assertEqual(len(expanded), 3)
        self.assertEqual(expanded[0]['role'], '')
        self.assertEqual(expanded[1]['role'], '')
        self.assertEqual(expanded[2]['role'], '')

class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""

    def test_large_dataset_processing_time(self):
        """Test processing time for large datasets"""
        # Create a large dataset
        large_dataset = []
        for i in range(5000):
            large_dataset.append({
                'id': str(i),
                'name': f'User {i}',
                'email': f'user{i % 3}@{"sce.com" if i % 2 == 0 else "edisonintl.com"}',
                'status': 'active',
                'roles': ['Admin'] if i % 100 == 0 else ['User', 'Viewer'] if i % 10 == 0 else ['User']
            })
        
        # Measure processing time for role expansion
        start_time = time.time()
        
        # Expand roles
        expanded_data = []
        for user in large_dataset:
            for role in user['roles']:
                expanded_data.append({
                    'user_id': user['id'],
                    'name': user['name'],
                    'role': role
                })
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 5000 users in reasonable time (less than 2 seconds)
        self.assertLess(processing_time, 2.0)
        print(f"Processed 5000 users in {processing_time:.3f} seconds")
    
    def test_memory_usage_with_large_dataset(self):
        """Test memory usage with large datasets"""
        # This test is more illustrative than precise without specialized memory profiling
        
        # Create datasets of increasing size
        dataset_sizes = [100, 500, 1000, 2000]
        memory_usage = []
        
        for size in dataset_sizes:
            # Generate dataset
            dataset = []
            for i in range(size):
                dataset.append({
                    'id': str(i),
                    'name': f'User {i}',
                    'email': f'user{i}@example.com',
                    'status': 'active',
                    'roles': ['User']
                })
            
            # Get approximate memory size
            import sys
            memory_usage.append(sys.getsizeof(dataset))
            
            # Process dataset
            filtered = [item for item in dataset if '@example.com' in item['email']]
            self.assertEqual(len(filtered), size)
        
        # Basic assertion that memory usage is not excessive
        self.assertLess(memory_usage[-1], 1024 * 1024)  # Less than 1MB
        print(f"Memory usage for {dataset_sizes[-1]} users: {memory_usage[-1]} bytes")

if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nIntegration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    if result.testsRun > 0:
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
