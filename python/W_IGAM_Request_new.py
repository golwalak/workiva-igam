"""
Workiva Identity, Governance, and Access Management (IGAM) Reporting Tool

This script connects to the Workiva API, retrieves user account information,
processes the data according to business requirements, and generates a 
standardized CSV report for analysis and compliance purposes.

The script uses OAuth 2.0 client credentials flow for authentication and
retrieves user data from the Workiva organization endpoint. It then filters
and transforms the data according to SCE's requirements before generating
a CSV report.

Configuration is stored in an external config.ini file for improved security
and maintainability.

Author: SCE IAM Team
Version: 1.1
Last Updated: 2023-05-21

Usage:
    python W_IGAM_Request_new.py

Output:
    Workiva_Account_Aggregation.csv - A CSV file containing user account data

Configuration:
    config.ini - Contains API endpoints and authentication credentials
"""

import requests
import json
import urllib3
import csv
import os
import configparser
import stat
import smtplib
import socket
import logging
import sys
import traceback
import importlib.util
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
 
# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_config():
    """
    Load configuration from config.ini file
    
    This function reads API endpoints and authentication credentials from
    the config.ini file in the same directory as the script. It implements
    error handling for missing or malformed configuration files.
    
    Returns:
        dict: A dictionary containing configuration values if successful, None otherwise
    """
    print("Loading configuration...")
    
    # Calculate config file path and log it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    print(f"Config path: {config_path}")
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found at {config_path}")
        print("Please create a config.ini file with [api] and [auth] sections")
        return None
    
    try:
        # Get file modification time for debugging
        config_mtime = datetime.fromtimestamp(os.path.getmtime(config_path))
        config_size = os.path.getsize(config_path)
        print(f"Config file size: {config_size} bytes, last modified: {config_mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Use configparser to read the configuration
        config = configparser.ConfigParser()
        config.read(config_path)
        print(f"Config sections found: {', '.join(config.sections())}")
          
        # Verify all required sections and keys exist
        required_sections = ['api', 'auth', 'output']
        required_keys = {
            'api': ['token_url', 'users_url'],
            'auth': ['client_id', 'client_secret'],
            'output': ['output_dir', 'file_name']
        }
        
        # Optional email section and keys (won't cause errors if missing)
        optional_sections = ['email']
        optional_keys = {
            'email': ['enabled', 'smtp_server', 'smtp_port', 'sender_email', 
                      'recipients', 'subject', 'include_report']
        }
        
        print("Validating required configuration sections and keys...")
        
        # Check for required sections
        missing_sections = []
        for section in required_sections:
            if section not in config.sections():
                print(f"Error: Missing required section [{section}] in config file")
                missing_sections.append(section)
        
        if missing_sections:
            print(f"Missing required sections: {', '.join(missing_sections)}")
            return None
        
        # Check for required keys in each section
        missing_keys = {}
        empty_keys = {}
        
        for section, keys in required_keys.items():
            for key in keys:
                if not config.has_option(section, key):
                    print(f"Error: Missing required key '{key}' in section [{section}]")
                    if section not in missing_keys:
                        missing_keys[section] = []
                    missing_keys[section].append(key)
                elif not config.get(section, key).strip():
                    print(f"Error: Empty value for key '{key}' in section [{section}]")
                    if section not in empty_keys:
                        empty_keys[section] = []
                    empty_keys[section].append(key)
        
        if missing_keys:
            print("Missing keys by section:")
            for section, keys in missing_keys.items():
                print(f"  - [{section}]: {', '.join(keys)}")
            return None
            
        if empty_keys:
            print("Empty keys by section:")
            for section, keys in empty_keys.items():
                print(f"  - [{section}]: {', '.join(keys)}")
            return None
        
        print("Required configuration validation passed")
        
        # Set restricted permissions on config file (owner read/write only)
        # This only works on Linux/Unix/Mac systems, will be ignored on Windows
        try:
            print("Setting restricted permissions on config file...")
            os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600 - Owner read/write only
            print("File permissions set successfully")
        except Exception as perm_error:
            print(f"Note: Could not restrict config file permissions: {perm_error}")
            print(f"Operating system: {os.name}, Platform: {sys.platform}")
        
        print("Building configuration dictionary...")
        
        # Initialize configuration dictionary with required values
        config_dict = {
            'token_url': config.get('api', 'token_url').strip('"\''),
            'users_url': config.get('api', 'users_url').strip('"\''),
            'client_id': config.get('auth', 'client_id').strip('"\''),
            'client_secret': config.get('auth', 'client_secret').strip('"\''),
            'output_dir': config.get('output', 'output_dir').strip('"\''),
            'file_name': config.get('output', 'file_name').strip('"\'')
        }
        
        # Create output directory if it doesn't exist
        if not os.path.exists(config_dict['output_dir']):
            print(f"Output directory doesn't exist. Creating: {config_dict['output_dir']}")
            try:
                os.makedirs(config_dict['output_dir'])
                print("Output directory created successfully")
            except Exception as dir_error:
                print(f"Warning: Could not create output directory: {dir_error}")
        else:
            print(f"Output directory exists: {config_dict['output_dir']}")
            
            # Check if output directory is writable
            if os.access(config_dict['output_dir'], os.W_OK):
                print("Output directory is writable")
            else:
                print("Warning: Output directory may not be writable")
        
        # Add email configuration if present
        print("Processing email configuration...")
        if 'email' in config.sections():
            print(f"Email configuration found with keys: {', '.join(config.options('email'))}")
            
            # Log email settings
            email_enabled = config.get('email', 'enabled', fallback='false').lower() == 'true'
            print(f"Email notifications enabled: {email_enabled}")
            
            if email_enabled:
                smtp_server = config.get('email', 'smtp_server', fallback='')
                smtp_port = config.get('email', 'smtp_port', fallback='25')
                recipients = config.get('email', 'recipients', fallback='')
                
                if not smtp_server:
                    print("Warning: Email enabled but SMTP server not specified")
                
                if not recipients:
                    print("Warning: Email enabled but no recipients specified")
                else:
                    recipient_count = len([r for r in recipients.split(',') if r.strip()])
                    print(f"Email recipients count: {recipient_count}")
            
            config_dict['email'] = {
                'enabled': email_enabled,
                'smtp_server': config.get('email', 'smtp_server', fallback=''),
                'smtp_port': config.get('email', 'smtp_port', fallback='25'),
                'sender_email': config.get('email', 'sender_email', fallback=''),
                'recipients': config.get('email', 'recipients', fallback=''),
                'subject': config.get('email', 'subject', fallback='Workiva IGAM Report'),
                'include_report': config.get('email', 'include_report', fallback='false').lower() == 'true'
            }
        else:
            print("Email configuration section not found, email notifications will be disabled")
            config_dict['email'] = {'enabled': False}
        
        print("Configuration loaded successfully")
        return config_dict
    
    except configparser.Error as e:
        print(f"Error parsing configuration file: {e}")
        # More detailed error information
        if hasattr(e, 'message'):
            print(f"Parser message: {e.message}")
        if hasattr(e, 'section'):
            print(f"Section with error: {e.section}")
        if hasattr(e, 'source'):
            print(f"Source file: {e.source}")
        if hasattr(e, 'lineno'):
            print(f"Line number: {e.lineno}")
        return None
    
    except Exception as e:
        print(f"Unexpected error reading configuration: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        return None

def setup_logging(output_dir):
    """
    Set up logging to both console and file
    
    Args:
        output_dir (str): Directory where the log file will be saved
        
    Returns:
        logger: Configured logger object
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(output_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
      # Configure logging with timestamp in filename
    log_filename = os.path.join(logs_dir, f'workiva_igam_{datetime.now().strftime("%Y%m%d")}.log')
      # Create logger
    logger = logging.getLogger('workiva_igam')
    # Clear any existing handlers (to prevent duplicate logs if the logger already exists)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)  # Changed from INFO to DEBUG to capture all debug messages
    
    # Create file handler with mode='w' to overwrite the log file on each run
    file_handler = logging.FileHandler(log_filename, mode='w')
    file_handler.setLevel(logging.DEBUG)  # Changed from INFO to DEBUG
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Keep INFO level for console to avoid too much output
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
      # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.debug("========== Log file reset for new execution ==========")
    logger.debug("Logging initialized at DEBUG level")
    
    return logger

# Load configuration
config = load_config()
if not config:
    print("Failed to load configuration. Exiting.")
    exit(1)

# API endpoints and credentials from config
token_url = config['token_url']
users_url = config['users_url']
client_id = config['client_id']
client_secret = config['client_secret']
 
def get_access_token():
    """
    Obtain an OAuth access token from the Workiva API
    
    This function makes a POST request to the token endpoint using the client credentials
    authentication flow. It returns the access token that will be used for subsequent API calls.
    
    Returns:
        str: Access token if successful, None otherwise
    """
    try:
        # Request for OAuth token
        logger.info("Requesting OAuth token...")
        # logger.debug(f"Authentication endpoint: {token_url}")
        # logger.debug(f"Using client ID: {client_id[:5]}{'*' * 10} (partially masked)")
        
        request_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        # logger.debug("Preparing authentication request with grant_type=client_credentials")
        
        token_response = requests.post(
            token_url,
            data=request_data,
            verify=False  # Note: In production, SSL verification should ideally be enabled
        )
        
        # logger.debug(f"Authentication response status code: {token_response.status_code}")
        
        # Check response status
        token_response.raise_for_status()
        # logger.debug("Authentication response status check passed")
        
        # Extract and return the access token
        token_data = token_response.json()
        # logger.debug(f"Authentication response keys: {', '.join(token_data.keys())}")
        
        if 'access_token' not in token_data:
            logger.error("Error: Access token not found in the response")
            # logger.debug(f"Response data: {token_data}")
            return None
            
        # Mask token for security in logs
        token_preview = f"{token_data['access_token'][:5]}{'*' * 15}"
        # logger.debug(f"Access token obtained: {token_preview}")
        
        # Check if we have expiration information
        if 'expires_in' in token_data:
            # logger.debug(f"Token expires in {token_data['expires_in']} seconds")
            pass
        logger.info("OAuth token obtained successfully")
        return token_data['access_token']
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error getting access token: {e}")
        # logger.debug(f"HTTP Error details: Status code {token_response.status_code}")
        logger.error(f"Response: {token_response.text if 'token_response' in locals() else 'No response'}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error getting access token: {e}")
        # logger.debug(f"Connection Error details: {str(e)}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error getting access token: {e}")
        # logger.debug(f"Timeout Error details: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting access token: {e}")
        # logger.debug(f"Request Error details: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting access token: {e}")
        # logger.debug(f"Exception type: {type(e).__name__}, Details: {str(e)}")
        return None
 
def make_api_request():
    """
    Make a request to the Workiva API to retrieve user data
    
    This function obtains an OAuth access token and then uses it to make a GET request
    to the users endpoint. It retrieves and returns user account information from Workiva.
    
    API Response Format:
    {
        "data": [
            {
                "id": "user-uuid",
                "type": "user",
                "attributes": {
                    "userName": "username",
                    "email": "user@example.com",
                    "active": true,
                    "workspaceMemberships": [
                        {
                            "workspaceId": "workspace-id",
                            "workspaceRoles": ["Admin", "User"]
                        }
                    ],
                    "organizationRoles": ["Org Admin", "User"]
                }
            }
        ]
    }
    
    Error Handling:
    - HTTP errors (4xx, 5xx responses)
    - Connection errors (network issues)
    - Timeout errors
    - JSON parsing errors
    - Unexpected exceptions
    
    Returns:
        dict: JSON response containing user data if successful, None otherwise
    """
    try:
        # First get the access token
        # logger.debug("Calling get_access_token() to obtain authorization token")
        access_token = get_access_token()
        if not access_token:
            # logger.debug("Failed to obtain access token, aborting API request")
            return None
 
        # Mask token for security in logs
        token_preview = f"{access_token[:5]}{'*' * 15}" if access_token else "None"
        # logger.debug(f"Using access token: {token_preview}")
        
        # Prepare request headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        # logger.debug(f"Request headers prepared: {', '.join(headers.keys())}")
        # logger.debug(f"API endpoint: {users_url}")
        
        # Make the GET request with OAuth token
        logger.info(f"Requesting user data from {users_url}")
        
        start_time = datetime.now()
        # logger.debug(f"API request started at: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        
        response = requests.get(
            users_url,
            headers=headers,
            verify=False  # Note: In production, SSL verification should ideally be enabled
        )
        
        end_time = datetime.now()
        request_time = (end_time - start_time).total_seconds()
        # logger.debug(f"API request completed in {request_time:.2f} seconds")
        # logger.debug(f"Response status code: {response.status_code}")
       
        # Check if the request was successful
        response.raise_for_status()
        # logger.debug("Response status check passed")
       
        # Parse the response
        # logger.debug("Parsing JSON response")
        data = response.json()
        
        # Debug response size and structure
        response_size = len(response.content)
        # logger.debug(f"Response size: {response_size} bytes")
        # logger.debug(f"Response top-level keys: {', '.join(data.keys()) if isinstance(data, dict) else 'Not a dictionary'}")
        
        # Validate response structure
        if 'data' not in data:
            logger.warning("Warning: Unexpected API response format - 'data' field not found")
            # logger.debug(f"Available keys in response: {', '.join(data.keys())}")
        else:
            user_count = len(data['data'])
            logger.info(f"Successfully retrieved data for {user_count} users")
            # logger.debug(f"First user ID: {data['data'][0]['id'] if user_count > 0 else 'No users'}")
            
            # Log sample of user attributes if available
            # if user_count > 0 and 'attributes' in data['data'][0]:
            #     sample_user = data['data'][0]['attributes']
            #     logger.debug(f"Sample user attributes: {', '.join(sample_user.keys())}")
        
        return data
       
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error making API request: {e}")
        if 'response' in locals():
            # logger.debug(f"HTTP Error details: Status code {response.status_code}")
            # logger.debug(f"Response headers: {response.headers}")
            logger.error(f"Response: {response.text}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error making API request: {e}")
        # logger.debug(f"Connection Error details: {str(e)}")
        # logger.debug(f"API endpoint: {users_url}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error making API request: {e}")
        # logger.debug(f"Timeout Error details: {str(e)}")
        # logger.debug(f"API endpoint: {users_url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making API request: {e}")
        # logger.debug(f"Request Error details: {str(e)}")
        # logger.debug(f"API endpoint: {users_url}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing API response: {e}")
        # logger.debug(f"JSON decode error at position: {e.pos}")
        # if 'response' in locals():
        #     logger.debug(f"Response content type: {response.headers.get('Content-Type', 'unknown')}")
        #     logger.debug(f"First 100 characters of response: {response.text[:100]}...")
        return None
    except Exception as e:
        logger.error(f"Unexpected error making API request: {e}")
        # logger.debug(f"Exception type: {type(e).__name__}, Details: {str(e)}")
        return None
 
def extract_user_data(api_data):
    """
    Extract and transform user data from the API response
    
    This function processes the API response to extract relevant user information.
    It applies business filters (filtering by email domain) and transformations
    (lowercase conversion) according to requirements.
      Filtering Logic:
    1. Excludes users without valid attributes
    2. Includes only users with email domains: @sce.com or @edisonintl.com
    3. Includes only active users (Active = True)
    4. Processes workspace memberships and organization roles
    5. Converts usernames and emails to lowercase for consistency
    
    To add additional email domains:
    - Modify the email domain check in the filter condition
    - Example: if not (email.endswith('@sce.com') or email.endswith('@edisonintl.com') 
               or email.endswith('@newdomain.com')):
    
    Args:
        api_data (dict): The JSON response from the Workiva API
        
    Returns:
        list: A list of dictionaries containing processed user records
    """
    user_data = []
    
    # logger.debug("Starting user data extraction")
    
    # Validate input data structure
    if not api_data:
        logger.error("API data is None or empty")
        return user_data
        
    if 'data' not in api_data:
        logger.error("No 'data' field found in API response")
        # logger.debug(f"Available keys in response: {', '.join(api_data.keys()) if isinstance(api_data, dict) else 'Not a dictionary'}")
        return user_data
    
    total_records = len(api_data['data'])
    logger.info(f"Processing {total_records} user records...")
    # logger.debug(f"Data extraction started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
      # Statistics for debugging
    filtered_count = 0
    filtered_domain_count = 0
    filtered_inactive_count = 0
    missing_attributes_count = 0
    valid_count = 0
    domain_counts = {}
    roles_distribution = {}
    
    for i, user in enumerate(api_data['data']):
        # Periodically log progress for large datasets
        if i > 0 and i % 100 == 0:
            # logger.debug(f"Processed {i}/{total_records} records...")
            pass
        
        user_id = user.get('id', 'unknown-id')
        
        # Skip records without attributes
        if 'attributes' not in user:
            logger.warning(f"Warning: User record missing 'attributes' field: {user}")
            missing_attributes_count += 1
            continue
            
        attributes = user['attributes']
        # logger.debug(f"Processing user ID: {user_id}, Username: {attributes.get('userName', 'unknown')}")
        
        # Process workspace memberships
        workspace_memberships = ""
        if attributes.get('workspaceMemberships'):
            workspaces = []
            workspace_count = len(attributes['workspaceMemberships'])
            # logger.debug(f"User has {workspace_count} workspace memberships")
            
            for workspace in attributes['workspaceMemberships']:
                # Only include the roles without workspace names or parentheses
                workspace_id = workspace.get('workspaceId', 'unknown-workspace')
                roles = workspace.get('workspaceRoles', ['No role'])
                
                # logger.debug(f"Workspace ID: {workspace_id}, Roles: {roles}")
                
                workspace_info = ', '.join(roles)
                workspaces.append(workspace_info)
                
                # Track role distribution for debugging
                for role in roles:
                    if role in roles_distribution:
                        roles_distribution[role] += 1
                    else:
                        roles_distribution[role] = 1
                
            workspace_memberships = " | ".join(workspaces)
            # logger.debug(f"Combined workspace memberships: {workspace_memberships}")
        else:
            # logger.debug("User has no workspace memberships")
            pass
        
        # Get licenses as a string (not used in final output but processed for completeness)
        licenses = ", ".join(attributes.get('licenses', []))
        # if licenses:
        #     logger.debug(f"User licenses: {licenses}")
        
        # Get organization roles as a string
        org_roles = ", ".join(attributes.get('organizationRoles', []))
        # if org_roles:
        #     logger.debug(f"Organization roles: {org_roles}")
            
        # Track organization role distribution too
        for role in attributes.get('organizationRoles', []):
            role_key = f"Org:{role}"
            if role_key in roles_distribution:
                roles_distribution[role_key] += 1
            else:
                roles_distribution[role_key] = 1
        
        # Append organization roles to workspace memberships if org_roles is not empty
        if org_roles:
            if workspace_memberships:
                workspace_memberships += ", " + org_roles
                # logger.debug(f"Combined roles (workspace + org): {workspace_memberships}")
            else:
                workspace_memberships = org_roles
                # logger.debug(f"Using org roles only: {workspace_memberships}")
                
        # Get email and convert to lowercase
        email = attributes.get('email', '').lower()
        
        # Track email domain distribution
        if email:
            domain = email.split('@')[-1] if '@' in email else 'no-domain'
            if domain in domain_counts:
                domain_counts[domain] += 1
            else:
                domain_counts[domain] = 1        # Filter: Only include users with @sce.com or @edisonintl.com email domains
        # NOTE: To add additional email domains, update the condition below
        # Example: if not (email.endswith('@sce.com') or email.endswith('@edisonintl.com') or email.endswith('@newdomain.com')):
        if not (email.endswith('@sce.com') or email.endswith('@edisonintl.com')):
            # logger.debug(f"Filtering out user with non-matching email domain: {email}")
            filtered_domain_count += 1
            continue
        
        # Filter: Only include active users (Active = True)
        user_active = attributes.get('active', False)
        if not user_active:
            # logger.debug(f"Filtering out inactive user: {email}")
            filtered_inactive_count += 1
            continue
        
        # Create user record with only the required columns
        user_record = {
            'Username': attributes.get('userName', '').lower(),  # Convert username to lowercase
            'Email': email,  # Already converted to lowercase
            'Active': str(attributes.get('active', False)),
            'Roles': workspace_memberships
        }
        
        # logger.debug(f"Created record: Username={user_record['Username']}, Email={user_record['Email']}, "
        #             f"Active={user_record['Active']}, Roles count={len(workspace_memberships.split(',')) if workspace_memberships else 0}")
        
        user_data.append(user_record)
        valid_count += 1
    
    # Log detailed statistics
    # logger.debug("--- Data Extraction Statistics ---")
    # logger.debug(f"Total records in API response: {total_records}")
    # logger.debug(f"Records missing attributes: {missing_attributes_count}")
    # logger.debug(f"Records filtered out by domain: {filtered_count}")
    # logger.debug(f"Valid records processed: {valid_count}")
    
    # logger.debug("Email domain distribution:")
    # for domain, count in domain_counts.items():
    #     logger.debug(f"  - {domain}: {count} users")
    
    # logger.debug("Top roles distribution:")
    # # Sort roles by count and log top 10
    # top_roles = sorted(roles_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    # for role, count in top_roles:
    #     logger.debug(f"  - {role}: {count} occurrences")
      # Calculate total filtered count
    total_filtered_count = filtered_domain_count + filtered_inactive_count
    
    logger.info(f"Processed {len(user_data)} records after filtering ({total_filtered_count} records filtered out: {filtered_domain_count} by domain, {filtered_inactive_count} inactive users)")
    # logger.debug(f"Data extraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    
    return user_data

def save_to_csv(data, filename):
    """
    Save processed user data to a CSV file
    
    This function transforms the data to expand roles into separate rows,
    sorts the data by username, and writes it to a CSV file.
    
    The output directory is loaded from the config.ini file.
    
    CSV Format:
    - Username: The user's login name (lowercase)
    - Email: The user's email address (lowercase) 
    - Active: Whether the user account is active (True/False)
    - Roles: The user's assigned role(s)
    
    Args:
        data (list): List of dictionaries containing user records
        filename (str): Name of the CSV file to create
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # logger.debug("Starting CSV file creation")
        start_time = datetime.now()
        
        # Get output directory from configuration
        output_dir = config['output_dir']
        # logger.debug(f"Output directory from config: {output_dir}")
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            # logger.debug(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir)
        
        file_path = os.path.join(output_dir, filename)
        # logger.debug(f"Full CSV file path: {file_path}")
        
        # If data is empty, return early
        if not data:
            logger.warning(f"No data to write to {file_path}")
            return False
        
        # Get the fieldnames from the first record
        fieldnames = data[0].keys()
        # logger.debug(f"CSV fieldnames: {', '.join(fieldnames)}")
        
        logger.info("Transforming data: expanding roles into separate rows...")
        
        # Debug statistics
        role_count_before = sum(1 for record in data if record['Roles'])
        multi_role_users = sum(1 for record in data if record['Roles'] and (',' in record['Roles'] or '|' in record['Roles']))
        
        # logger.debug(f"Input data: {len(data)} records")
        # logger.debug(f"Users with roles: {role_count_before}")
        # logger.debug(f"Users with multiple roles: {multi_role_users}")
        
        # Create expanded data with repeated rows for each role
        expanded_data = []
        role_counts = {}
        
        # Track expansion statistics
        users_expanded = 0
        total_roles_expanded = 0
        unique_roles = set()
        
        for user_record in data:
            # Get the roles
            username = user_record['Username']
            roles = user_record['Roles']
            
            # logger.debug(f"Processing user: {username}, Roles content: {roles[:50]}{'...' if len(roles) > 50 else ''}")
            
            if roles:
                # First split by pipe to separate different roles
                pipe_split = roles.split('|')
                # logger.debug(f"Pipe split resulted in {len(pipe_split)} parts")
                
                all_memberships = []
                
                # Then process each part
                for part in pipe_split:
                    # Split by comma to get individual roles
                    comma_split = [role.strip() for role in part.split(',')]
                    # logger.debug(f"Comma split resulted in {len(comma_split)} roles")
                    all_memberships.extend(comma_split)
                
                if len(all_memberships) > 1:
                    users_expanded += 1
                
                # Create a row for each role
                for membership in all_memberships:
                    if membership.strip():  # Ensure not empty
                        # Add to role statistics
                        unique_roles.add(membership.strip())
                        total_roles_expanded += 1
                        
                        if membership.strip() in role_counts:
                            role_counts[membership.strip()] += 1
                        else:
                            role_counts[membership.strip()] = 1
                        
                        # Create a copy of the user record
                        new_record = user_record.copy()
                        # Replace the roles with just this one
                        new_record['Roles'] = membership.strip()
                        expanded_data.append(new_record)
                        
                        # logger.debug(f"Created expanded record: {username} with role '{membership.strip()}'")
            else:
                # logger.debug(f"No roles for user {username}, adding record as-is")
                # If no roles, just add the original record
                expanded_data.append(user_record.copy())
        
        # Log role distribution for debugging
        # logger.debug("--- Role Distribution in Final Data ---")
        # top_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        # for role, count in top_roles:
        #     logger.debug(f"  - {role}: {count} occurrences")
        
        # Log expansion statistics
        # logger.debug(f"Data transformation statistics:")
        # logger.debug(f"  - Users expanded: {users_expanded}")
        # logger.debug(f"  - Total unique roles: {len(unique_roles)}")
        # logger.debug(f"  - Total role assignments: {total_roles_expanded}")
        
        # Calculate expansion ratio
        expansion_ratio = len(expanded_data) / len(data) if data else 0
        # logger.debug(f"Expansion ratio: {expansion_ratio:.2f}x (increased from {len(data)} to {len(expanded_data)} records)")
        
        logger.info(f"Data transformation complete: {len(expanded_data)} rows after expansion")
        
        # Sort the expanded data by Username in ascending order
        # logger.debug("Sorting expanded data by Username")
        expanded_data.sort(key=lambda x: x['Username'])
        
        # Write to CSV
        logger.info(f"Writing data to {file_path}...")
        write_start_time = datetime.now()
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(expanded_data)
        
        write_time = (datetime.now() - write_start_time).total_seconds()
        # logger.debug(f"CSV writing time: {write_time:.2f} seconds")
        
        # Get file size for debugging
        file_size = os.path.getsize(file_path)
        # logger.debug(f"CSV file size: {file_size} bytes ({file_size/1024:.2f} KB)")
        
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Data successfully saved to {file_path}")
        # logger.debug(f"Total save_to_csv execution time: {total_time:.2f} seconds")
        
        return True
    
    except PermissionError as e:
        logger.error(f"Permission error writing to CSV: {e}")
        logger.error("Please ensure you have write access to the output directory")
        # logger.debug(f"Output directory permissions: {os.access(output_dir, os.W_OK)}")
        return False
    except IOError as e:
        logger.error(f"I/O error writing to CSV: {e}")
        # logger.debug(f"I/O error details: {str(e)}")
        # logger.debug(f"File path: {file_path if 'file_path' in locals() else 'Unknown'}")
        return False
    except Exception as e:
        logger.error(f"Error saving data to CSV: {e}")
        # logger.debug(f"Exception type: {type(e).__name__}, Details: {str(e)}")
        # import traceback
        # logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

def send_email(csv_file_path, execution_time=None, success=True):
    """
    Send an email notification with the execution results
    
    This function sends an email notification indicating the status of the script execution.
    Optionally, it can attach the generated CSV file to the email.
    
    Args:
        csv_file_path (str): Path to the CSV file to attach (if configured)
        execution_time (float): Total execution time in seconds (if available)
        success (bool): Whether the script executed successfully
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    global config
    
    # logger.debug(f"Starting email notification process")
    # logger.debug(f"Parameters: csv_file_path={csv_file_path}, execution_time={execution_time}, success={success}")
    
    # Check if email notifications are enabled
    if not config.get('email', {}).get('enabled', False):
        logger.info("Email notifications are disabled in config.")
        return False
        
    start_time = datetime.now()
    # logger.debug(f"Email process started at: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    
    try:
        # Get email configuration
        email_config = config['email']
        smtp_server = email_config['smtp_server']
        # logger.debug(f"SMTP server: {smtp_server}")
        
        # Check for empty or missing required values
        recipients = email_config.get('recipients', '').strip()
        if not recipients or not smtp_server:
            logger.warning("Email notification skipped: Missing smtp_server or recipients in config.")
            return False
            
        # Parse recipients
        recipients_list = [r.strip() for r in recipients.split(',') if r.strip()]
        if not recipients_list:
            logger.warning("Email notification skipped: No valid recipients specified.")
            return False
        
        # logger.debug(f"Recipients: {', '.join(recipients_list)}")
        
        smtp_port = int(email_config.get('smtp_port', '25'))
        # logger.debug(f"SMTP port: {smtp_port}")
        
        sender_email = email_config.get('sender_email', 'workiva.igam.noreply@sce.com')
        # logger.debug(f"Sender email: {sender_email}")
        
        # Handle include_report as either boolean or string
        include_report = email_config.get('include_report', False)
        if isinstance(include_report, str):
            include_report = include_report.lower() == 'true'
        
        # logger.debug(f"Include report attachment: {include_report}")
        
        # Format email subject with current date
        subject = email_config.get('subject', 'Workiva IGAM Report - {date}')
        subject = subject.format(date=datetime.now().strftime('%Y-%m-%d'))
        # logger.debug(f"Email subject: {subject}")
        
        # Check report file if we're supposed to include it
        if include_report and csv_file_path:
            if os.path.exists(csv_file_path):
                file_size = os.path.getsize(csv_file_path)
                # logger.debug(f"Attachment file exists: {csv_file_path} (Size: {file_size/1024:.2f} KB)")
                pass
            else:
                logger.warning(f"Attachment file not found: {csv_file_path}")
        
        # Create message container
        # logger.debug("Creating email message")
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(recipients_list)
        message['Subject'] = subject
        
        # Create email body
        hostname = socket.gethostname()
        # logger.debug(f"Hostname for email: {hostname}")
        
        body = f"""
        <html>
        <body>
        <h2>Workiva IGAM Report Execution Summary</h2>
        <p>This is an automated notification from the Workiva IGAM Report tool.</p>
        
        <h3>Execution Details:</h3>
        <ul>
            <li><strong>Status:</strong> {"Successful" if success else "Failed"}</li>
            <li><strong>Date/Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            <li><strong>Server:</strong> {hostname}</li>
            {"<li><strong>Execution Time:</strong> {:.2f} seconds</li>".format(execution_time) if execution_time else ""}
        </ul>
        
        <p>
            {"The user data has been successfully processed and saved." if success else "The script encountered an error during execution. Please check the logs."}
        </p>
        {"<p>The report is attached to this email.</p>" if success and include_report and csv_file_path and os.path.exists(csv_file_path) else ""}
        
        <p>This is an automated message. Please do not reply.</p>
        <p>SCE IGAM Recon file generation process</p>
        </body>
        </html>
        """
        
        # Attach HTML body
        # logger.debug("Attaching HTML body to email")
        message.attach(MIMEText(body, 'html'))
        
        # Attach the CSV file if configured and file exists
        if success and include_report and csv_file_path and os.path.exists(csv_file_path):
            logger.info(f"Attaching report file: {os.path.basename(csv_file_path)}")
            attachment_start = datetime.now()
            
            with open(csv_file_path, 'rb') as file:
                file_content = file.read()
                # logger.debug(f"Read {len(file_content)} bytes from file")
                
                attachment = MIMEApplication(file_content, _subtype="csv")
                attachment.add_header('Content-Disposition', 'attachment', 
                                     filename=os.path.basename(csv_file_path))
                message.attach(attachment)
            
            attachment_time = (datetime.now() - attachment_start).total_seconds()
            # logger.debug(f"File attachment completed in {attachment_time:.2f} seconds")
            # logger.info(f"Added attachment: {os.path.basename(csv_file_path)}")
          # Attach the log file
        logs_dir = os.path.join(config['output_dir'], 'logs')
        log_filename = f'workiva_igam_{datetime.now().strftime("%Y%m%d")}.log'
        log_file_path = os.path.join(logs_dir, log_filename)
        
        if os.path.exists(log_file_path):
            logger.info(f"Attaching log file: {log_filename}")
            # log_attachment_start = datetime.now()
            
            try:
                with open(log_file_path, 'rb') as log_file:
                    log_content = log_file.read()
                    # logger.debug(f"Read {len(log_content)} bytes from log file")
                    
                    log_attachment = MIMEApplication(log_content, _subtype="log")
                    log_attachment.add_header('Content-Disposition', 'attachment', 
                                         filename=log_filename)
                    message.attach(log_attachment)
                
                # log_attachment_time = (datetime.now() - log_attachment_start).total_seconds()
                # logger.debug(f"Log file attachment completed in {log_attachment_time:.2f} seconds")
                # logger.info(f"Added log attachment: {log_filename}")
            except Exception as log_error:
                logger.warning(f"Could not attach log file: {str(log_error)}")
        else:
            logger.warning(f"Log file not found at {log_file_path}")
        
        # Generate and attach the visualization HTML
        try:
            # Check if the simple_visualize_roles.py module exists
            viz_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simple_visualize_roles.py')
            if os.path.exists(viz_script_path):
                logger.info("Generating role visualization report...")
                
                # Import the simple_visualize_roles module dynamically
                spec = importlib.util.spec_from_file_location("simple_visualize_roles", viz_script_path)
                viz_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(viz_module)
                
                # Generate the visualization HTML using the CSV file path
                html_viz_path = viz_module.generate_visualization(csv_file_path)
                
                if os.path.exists(html_viz_path):
                    logger.info(f"Attaching visualization report: {os.path.basename(html_viz_path)}")
                    
                    with open(html_viz_path, 'rb') as html_file:
                        html_content = html_file.read()
                        
                        html_attachment = MIMEApplication(html_content, _subtype="html")
                        html_attachment.add_header('Content-Disposition', 'attachment', 
                                             filename=os.path.basename(html_viz_path))
                        message.attach(html_attachment)
                        
                    body = body.replace("</ul>", "</ul>\n<p>A visualization of user roles is also attached to this email.</p>")
                    message.replace_header("Subject", f"{subject} with Role Visualization")
                    
                    # Replace the HTML body to include the mention of visualization
                    message.get_payload()[0].set_payload(body)
                else:
                    logger.warning(f"Visualization file not found at {html_viz_path}")
            else:
                logger.info("Visualization script not found, skipping role visualization")
        except Exception as viz_error:
            logger.warning(f"Could not attach visualization report: {str(viz_error)}")
            logger.debug(f"Visualization error details: {traceback.format_exc()}")
          # Connect to SMTP server and send email
        logger.info(f"Sending email notification to {', '.join(recipients_list)}...")
        
        # Define multiple SMTP configurations to try
        smtp_configs = [
            # Primary configuration from config
            {'server': smtp_server, 'port': smtp_port, 'use_tls': True},
            {'server': smtp_server, 'port': smtp_port, 'use_tls': False},
            
            # Alternative SCE SMTP servers
            {'server': 'mail.sce.com', 'port': 25, 'use_tls': False},
            {'server': 'relay.sce.com', 'port': 25, 'use_tls': False},
            {'server': 'smtp.sce.com', 'port': 587, 'use_tls': True},
            {'server': 'smtp.sce.com', 'port': 2525, 'use_tls': False},
            
            # Office 365 fallbacks (if SCE uses Office 365)
            {'server': 'smtp.office365.com', 'port': 587, 'use_tls': True},
            {'server': 'outlook.office365.com', 'port': 587, 'use_tls': True},
        ]
        
        last_error = None
        
        for i, config in enumerate(smtp_configs):
            try:
                logger.info(f"Attempt {i+1}: Trying {config['server']}:{config['port']} (TLS: {config['use_tls']})")
                
                with smtplib.SMTP(config['server'], config['port'], timeout=30) as server:
                    if config['use_tls']:
                        try:
                            server.starttls()
                            logger.info("TLS connection established")
                        except Exception as tls_error:
                            logger.warning(f"TLS failed: {str(tls_error)}, continuing without TLS")
                    
                    # Check for authentication if provided in config
                    smtp_username = email_config.get('smtp_username', '').strip()
                    smtp_password = email_config.get('smtp_password', '').strip()
                    
                    if smtp_username and smtp_password:
                        logger.info("Authenticating with SMTP server")
                        server.login(smtp_username, smtp_password)
                    
                    server.send_message(message)
                    logger.info(f"Email sent successfully via {config['server']}:{config['port']}")
                    
                    total_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Email notification sent successfully in {total_time:.2f} seconds")
                    return True
                    
            except socket.gaierror as dns_error:
                last_error = f"DNS resolution failed for {config['server']}: {str(dns_error)}"
                logger.warning(last_error)
                continue
            except ConnectionRefusedError as conn_error:
                last_error = f"Connection refused to {config['server']}:{config['port']}: {str(conn_error)}"
                logger.warning(last_error)
                continue
            except smtplib.SMTPAuthenticationError as auth_error:
                last_error = f"SMTP authentication failed for {config['server']}: {str(auth_error)}"
                logger.warning(last_error)
                continue
            except smtplib.SMTPException as smtp_error:
                last_error = f"SMTP error with {config['server']}:{config['port']}: {str(smtp_error)}"
                logger.warning(last_error)
                continue
            except Exception as general_error:
                last_error = f"Unexpected error with {config['server']}:{config['port']}: {str(general_error)}"
                logger.warning(last_error)
                continue
        
        # If all attempts failed
        logger.error("All SMTP server attempts failed")
        if last_error:
            logger.error(f"Last error: {last_error}")
        
        raise Exception(f"Failed to send email after trying {len(smtp_configs)} configurations. Last error: {last_error}")
        
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")
        # logger.debug(f"Exception type: {type(e).__name__}, Details: {str(e)}")
        # import traceback
        # logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    """
    Main execution flow
    
    This is the entry point for the script. It performs the following steps:
    1. Set up logging
    2. Display script header and start time
    3. Retrieve user data from the Workiva API
    4. Process and filter the data
    5. Generate and save the CSV report
    6. Send email notification
    7. Display completion status and execution time
    
    Maintenance Notes:
    - To modify the output filename, change the 'file_name' value in config.ini
    - For email domain changes, modify the filter in extract_user_data() function
    - Email notification settings can be configured in the config.ini file
    - Logs are saved to the 'logs' subdirectory in the output directory
    - Error handling is implemented at each stage to provide detailed logs
    """
    # Set up logging first
    try:
        logger = setup_logging(config['output_dir'])
    except Exception as log_error:
        print(f"Warning: Could not set up logging: {log_error}")
        print("Continuing with console output only...")
        logger = logging.getLogger('workiva_igam')
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)
    
    logger.info("=" * 80)
    logger.info("Workiva IGAM Reporting Tool")
    logger.info("Version 1.2 - SCE IAM Team")
    logger.info("=" * 80)
    
    # Log system information for troubleshooting
    import platform
    import sys
    
    # logger.debug("--- System Information ---")
    # logger.debug(f"Python Version: {sys.version}")
    # logger.debug(f"Platform: {platform.platform()}")
    # logger.debug(f"Machine: {platform.machine()}")
    # logger.debug(f"Processor: {platform.processor()}")
    
    # Log script configuration
    # logger.debug("--- Script Configuration ---")
    # logger.debug(f"Working Directory: {os.getcwd()}")
    # logger.debug(f"Output Directory: {config['output_dir']}")
    # logger.debug(f"Output Filename: {config.get('file_name', 'Workiva_Account_Aggregation.csv')}")
    # logger.debug(f"API Endpoints: token_url={token_url}, users_url={users_url}")
    # logger.debug(f"Email Notifications Enabled: {config.get('email', {}).get('enabled', False)}")
    
    # Get memory usage if psutil is available
    try:
        # Commented out to avoid psutil dependency issues
        # import psutil
        # process = psutil.Process(os.getpid())
        # logger.debug(f"Initial Memory Usage: {process.memory_info().rss / (1024 * 1024):.2f} MB")
        pass
    except ImportError:
        # logger.debug("Memory usage tracking not available (psutil not installed)")
        pass
    
    # Get the current timestamp for logging
    start_time = datetime.now()
    logger.info(f"Script started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track execution times for different stages
    api_request_time = None
    extract_data_time = None
    save_csv_time = None
    email_time = None
    
    try:
        # logger.debug("Starting main execution flow")
        
        # Execute API request
        logger.info("Retrieving data from Workiva API...")
        api_request_start = datetime.now()
        api_data = make_api_request()
        api_request_time = (datetime.now() - api_request_start).total_seconds()
        # logger.debug(f"API request completed in {api_request_time:.2f} seconds")
        
        if api_data:
            # logger.debug(f"API data retrieved successfully, proceeding with data extraction")
            
            # Extract and process the data
            logger.info("Extracting and processing user data...")
            extract_start = datetime.now()
            user_data = extract_user_data(api_data)
            extract_data_time = (datetime.now() - extract_start).total_seconds()
            # logger.debug(f"Data extraction completed in {extract_data_time:.2f} seconds")
            # logger.debug(f"Extracted {len(user_data)} user records")
            
            # Log memory usage after data extraction if psutil is available
            try:
                # Commented out to avoid psutil dependency issues
                # import psutil
                # process = psutil.Process(os.getpid())
                # logger.debug(f"Memory Usage after data extraction: {process.memory_info().rss / (1024 * 1024):.2f} MB")
                pass
            except ImportError:
                pass
            
            # Save the processed data to CSV
            logger.info("Saving data to CSV...")
            save_start = datetime.now()
            csv_filename = config.get('file_name', 'Workiva_Account_Aggregation.csv')
            success = save_to_csv(user_data, csv_filename)
            save_csv_time = (datetime.now() - save_start).total_seconds()
            # logger.debug(f"CSV saving completed in {save_csv_time:.2f} seconds")
            
            # Script completion status
            end_time = datetime.now()
            execution_time = end_time - start_time
            execution_seconds = execution_time.total_seconds()
            
            # Send email notification based on success
            if success:
                logger.info("Sending email notification...")
                email_start = datetime.now()
                file_path = os.path.join(config['output_dir'], csv_filename)
                send_email(file_path, execution_seconds, success=True)
                email_time = (datetime.now() - email_start).total_seconds()
                # logger.debug(f"Email notification completed in {email_time:.2f} seconds")
            else:
                logger.error("Sending failure notification...")
                email_start = datetime.now()
                send_email(None, execution_seconds, success=False)
                email_time = (datetime.now() - email_start).total_seconds()
                # logger.debug(f"Failure email notification completed in {email_time:.2f} seconds")
            
            # Log execution time breakdown
            # logger.debug("--- Execution Time Breakdown ---")
            # logger.debug(f"API Request:     {api_request_time:.2f} seconds ({(api_request_time/execution_seconds*100):.1f}%)")
            # logger.debug(f"Data Extraction: {extract_data_time:.2f} seconds ({(extract_data_time/execution_seconds*100):.1f}%)")
            # logger.debug(f"CSV Generation:  {save_csv_time:.2f} seconds ({(save_csv_time/execution_seconds*100):.1f}%)")
            # logger.debug(f"Email Sending:   {email_time:.2f} seconds ({(email_time/execution_seconds*100):.1f}%)")
            # logger.debug(f"Other Time:      {(execution_seconds - api_request_time - extract_data_time - save_csv_time - (email_time or 0)):.2f} seconds")
            
            # Final Memory usage
            try:
                # Commented out to avoid psutil dependency issues
                # import psutil
                # process = psutil.Process(os.getpid())
                # logger.debug(f"Final Memory Usage: {process.memory_info().rss / (1024 * 1024):.2f} MB")
                pass
            except ImportError:
                pass
            
            logger.info("=" * 80)
            if success:
                logger.info(f"Script completed successfully in {execution_seconds:.2f} seconds")
                logger.info(f"Output file: {csv_filename}")
                # logger.debug(f"Output file full path: {os.path.join(config['output_dir'], csv_filename)}")
            else:
                logger.error(f"Script completed with errors in {execution_seconds:.2f} seconds")
            logger.info("=" * 80)
        else:
            logger.error("ERROR: Failed to retrieve data from Workiva API. Script cannot continue.")
            logger.error("Please check your configuration and network connectivity.")
            # logger.debug("API request returned None or empty data")
            
            # Send email notification for API request failure
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            email_start = datetime.now()
            send_email(None, execution_time, success=False)
            email_time = (datetime.now() - email_start).total_seconds()
            # logger.debug(f"Failure email notification completed in {email_time:.2f} seconds")
            
    except Exception as e:
        # Catch any unhandled exceptions
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        # logger.debug(f"Exception type: {type(e).__name__}, Details: {str(e)}")
        logger.critical(f"Script failed after {execution_time:.2f} seconds")
        
        # import traceback
        # logger.debug(f"Detailed traceback:\n{traceback.format_exc()}")
        
        # Attempt to send email notification for the critical error
        try:
            # logger.debug("Attempting to send failure email notification")
            email_start = datetime.now()
            send_email(None, execution_time, success=False)
            email_time = (datetime.now() - email_start).total_seconds()
            # logger.debug(f"Failure email notification completed in {email_time:.2f} seconds")
        except Exception as email_error:
            logger.error("Could not send email notification due to an error")
            # logger.debug(f"Email error: {str(email_error)}")
            
        logger.info("=" * 80)
    
    # logger.debug("Script execution complete")
