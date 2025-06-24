# Workiva IGAM Python Scripts

This directory contains Python scripts for the Workiva Identity, Governance, and Access Management (IGAM) reporting and analysis.

## Main Scripts

### W_IGAM_Request_new.py
The primary script for retrieving user account information from the Workiva API and generating CSV reports.

**Features:**
- OAuth 2.0 client credentials authentication
- User data retrieval and filtering
- CSV report generation
- Email notifications
- Comprehensive logging
- Data validation and transformation

**Usage:**
```bash
python W_IGAM_Request_new.py
```

**Requirements:**
- Python 3.7+
- requests
- configparser
- A valid `config.ini` file with API credentials

**Installation:**
```bash
# Install basic requirements
pip install -r requirements.txt

# For Azure deployment, use:
pip install -r requirements-azure.txt
```

## Utils Directory

### visualize_roles.py
Advanced role visualization and reporting tool that generates HTML reports with charts and analytics.

### simple_visualize_roles.py
Simplified version of the role visualization tool for basic reporting needs.

### data_validator.py
Data validation utilities for ensuring data quality and consistency in IGAM reports.

### azure_config_loader.py
Configuration loader for Azure-based deployments and cloud integration.

## Tests Directory

### test_workiva_igam_integration.py
Integration tests for the IGAM reporting system, including API connectivity and data processing tests.

## Configuration

The scripts require a `config.ini` file with the following structure. You can use `config.example.ini` as a starting template:

```bash
# Copy the example configuration
cp config.example.ini config.ini
# Edit config.ini with your actual values
```

```ini
[api]
token_url = https://api.workiva.com/oauth2/token
users_url = https://api.workiva.com/v1/users

[auth]
client_id = your_client_id
client_secret = your_client_secret

[output]
output_dir = ./output
file_name = Workiva_Account_Aggregation.csv

[email]
enabled = true
smtp_server = your_smtp_server
smtp_port = 25
sender_email = your_email@sce.com
recipients = recipient1@sce.com,recipient2@sce.com
subject = Workiva IGAM Report - {date}
include_report = true
```

## Security Notes

- Never commit the actual `config.ini` file with real credentials
- Use environment variables or secure credential storage in production
- Ensure proper file permissions on configuration files
- Review and validate all email recipients before enabling notifications

## Maintenance

- Update API endpoints if Workiva changes their API structure
- Modify email domain filters in `extract_user_data()` function as needed
- Regular testing of authentication and API connectivity
- Monitor log files for errors and performance issues

## Support

For issues or questions, contact the SCE IAM Team.
