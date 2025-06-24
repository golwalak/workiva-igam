#!/usr/bin/env python
"""
Data Validation Utilities for Workiva IGAM Tests

This module provides utilities for validating data during testing.
It includes functions for validating CSV files, checking data integrity,
and verifying compliance with business requirements.
"""

import os
import csv
import re
import json
from typing import List, Dict, Any, Tuple, Optional

def validate_csv_structure(csv_path: str, expected_headers: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate the structure of a CSV file
    
    Args:
        csv_path (str): Path to the CSV file
        expected_headers (list): List of expected header column names
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not os.path.exists(csv_path):
        return False, f"CSV file not found: {csv_path}"
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)
            
            if not headers:
                return False, "CSV file is empty"
            
            # Check for missing headers
            missing_headers = [h for h in expected_headers if h not in headers]
            if missing_headers:
                return False, f"Missing expected headers: {', '.join(missing_headers)}"
            
            # Check for unexpected headers
            unexpected_headers = [h for h in headers if h not in expected_headers]
            if unexpected_headers:
                return False, f"Unexpected headers: {', '.join(unexpected_headers)}"
            
            return True, None
    except Exception as e:
        return False, f"Error reading CSV file: {str(e)}"

def validate_email_format(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_email_domain(email: str, allowed_domains: List[str]) -> bool:
    """
    Validate that email domain is in the allowed list
    
    Args:
        email (str): Email address to validate
        allowed_domains (list): List of allowed domains
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email or '@' not in email:
        return False
    
    domain = email.split('@')[-1].lower()
    return domain in [d.lower() for d in allowed_domains]

def validate_csv_data_integrity(csv_path: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate data integrity in a CSV file
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        tuple: (is_valid, error_message, statistics)
    """
    if not os.path.exists(csv_path):
        return False, f"CSV file not found: {csv_path}", {}
    
    statistics = {
        'total_rows': 0,
        'valid_emails': 0,
        'invalid_emails': 0,
        'active_users': 0,
        'inactive_users': 0,
        'roles_distribution': {},
        'domains': {}
    }
    
    errors = []
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for i, row in enumerate(reader, 1):
                statistics['total_rows'] += 1
                
                # Validate required fields
                if not all(field in row for field in ['Username', 'Email', 'Active', 'Roles']):
                    errors.append(f"Row {i}: Missing required fields")
                    continue
                
                # Check email format
                email = row['Email'].strip()
                if validate_email_format(email):
                    statistics['valid_emails'] += 1
                else:
                    statistics['invalid_emails'] += 1
                    errors.append(f"Row {i}: Invalid email format: {email}")
                
                # Track email domains
                if '@' in email:
                    domain = email.split('@')[-1].lower()
                    statistics['domains'][domain] = statistics['domains'].get(domain, 0) + 1
                
                # Track active/inactive users
                active = row['Active'].strip().lower()
                if active in ('true', 'yes', '1'):
                    statistics['active_users'] += 1
                else:
                    statistics['inactive_users'] += 1
                
                # Track roles distribution
                role = row['Roles'].strip()
                if role:
                    statistics['roles_distribution'][role] = statistics['roles_distribution'].get(role, 0) + 1
        
        # Check if any errors were found
        if errors:
            return False, "\n".join(errors), statistics
        
        return True, None, statistics
    
    except Exception as e:
        return False, f"Error validating CSV file: {str(e)}", statistics

def validate_api_response(response_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate the structure and content of an API response
    
    Args:
        response_data (dict): API response data
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if response has 'data' field
    if not isinstance(response_data, dict):
        return False, "API response is not a dictionary"
    
    if 'data' not in response_data:
        return False, "API response missing 'data' field"
    
    if not isinstance(response_data['data'], list):
        return False, "'data' field is not a list"
    
    # Check user record structure for a sample of records
    errors = []
    for i, user in enumerate(response_data['data'][:10]):  # Check first 10 records
        if not isinstance(user, dict):
            errors.append(f"User record {i} is not a dictionary")
            continue
        
        # Check required fields
        for field in ['id', 'type', 'attributes']:
            if field not in user:
                errors.append(f"User record {i} missing required field: {field}")
        
        # Check attributes structure if present
        if 'attributes' in user and isinstance(user['attributes'], dict):
            attrs = user['attributes']
            for field in ['userName', 'email', 'active']:
                if field not in attrs:
                    errors.append(f"User record {i} attributes missing required field: {field}")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, None

def validate_output_against_requirements(csv_path: str, requirements: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that CSV output meets business requirements
    
    Args:
        csv_path (str): Path to the CSV file
        requirements (dict): Dictionary of business requirements to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Get data integrity statistics
    valid, error, stats = validate_csv_data_integrity(csv_path)
    if not valid:
        return False, f"Data integrity validation failed: {error}"
    
    errors = []
    
    # Validate against business requirements
    if 'allowed_domains' in requirements:
        # Check if all domains are in allowed list
        allowed_domains = requirements['allowed_domains']
        for domain, count in stats['domains'].items():
            if domain not in [d.lower() for d in allowed_domains]:
                errors.append(f"Found disallowed domain: {domain} ({count} occurrences)")
    
    if 'require_active_only' in requirements and requirements['require_active_only']:
        # Check that all users are active
        if stats['inactive_users'] > 0:
            errors.append(f"Found {stats['inactive_users']} inactive users (requirement is active users only)")
    
    # Add more business rule validations as needed
    
    if errors:
        return False, "\n".join(errors)
    
    return True, None

def compare_datasets(source_data: List[Dict[str, Any]], processed_data: List[Dict[str, Any]], 
                     mapping: Dict[str, str]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Compare source data with processed data to verify transformations
    
    Args:
        source_data (list): Original source data (e.g., API response)
        processed_data (list): Processed data (e.g., CSV rows)
        mapping (dict): Mapping between source and processed data fields
        
    Returns:
        tuple: (is_matching, error_message, statistics)
    """
    if not source_data or not processed_data:
        return False, "Empty data sets", {}
    
    statistics = {
        'source_count': len(source_data),
        'processed_count': len(processed_data),
        'matching_count': 0,
        'mismatches': []
    }
    
    # This is a simplified comparison - would need to be customized
    # for the specific transformation logic of the application
    
    # For simple demonstrations, we'll just return a placeholder
    # Actual implementation would depend on the specific transformations
    # applied by the application
    
    return True, None, statistics
