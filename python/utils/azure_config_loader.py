"""
Azure Configuration Loader for Workiva IGAM Reporting Tool

This module handles loading configuration from Azure Key Vault and environment variables
when running in Azure Container Instances with managed identity authentication.
"""

import os
import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import AzureError

def load_azure_config():
    """
    Load configuration from Azure Key Vault using managed identity
    
    Returns:
        dict: A dictionary containing configuration values if successful, None otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Get Key Vault URL from environment variable
        key_vault_url = os.getenv('AZURE_KEY_VAULT_URL')
        if not key_vault_url:
            logger.error("AZURE_KEY_VAULT_URL environment variable not set")
            return None
            
        logger.info(f"Connecting to Key Vault: {key_vault_url}")
        
        # Create credential using managed identity
        credential = DefaultAzureCredential()
        
        # Create Key Vault client
        client = SecretClient(vault_url=key_vault_url, credential=credential)
        
        # Test connection
        try:
            list(client.list_properties_of_secrets(max_page_size=1))
            logger.info("Successfully authenticated with Key Vault")
        except Exception as e:
            logger.error(f"Failed to authenticate with Key Vault: {str(e)}")
            return None
        
        # Load secrets
        secrets = {}
        secret_mappings = {
            'workiva-client-id': 'client_id',
            'workiva-client-secret': 'client_secret',
            'workiva-token-url': 'token_url',
            'workiva-users-url': 'users_url',
            'smtp-server': 'smtp_server',
            'smtp-port': 'smtp_port',
            'email-recipients': 'email_recipients',
            'storage-connection-string': 'storage_connection_string'
        }
        
        for secret_name, config_key in secret_mappings.items():
            try:
                secret = client.get_secret(secret_name)
                secrets[config_key] = secret.value
                logger.debug(f"Successfully retrieved secret: {secret_name}")
            except Exception as e:
                logger.error(f"Failed to retrieve secret {secret_name}: {str(e)}")
                return None
        
        # Build configuration dictionary similar to config.ini structure
        config = {
            'api': {
                'token_url': secrets['token_url'],
                'users_url': secrets['users_url']
            },
            'auth': {
                'client_id': secrets['client_id'],
                'client_secret': secrets['client_secret']
            },
            'output': {
                'output_dir': '/app/reports',
                'file_name': 'Workiva_Account_Aggregation.csv'
            },
            'email': {
                'enabled': 'True',
                'smtp_server': secrets['smtp_server'],
                'smtp_port': secrets['smtp_port'],
                'sender_email': 'workiva-igam@sce.com',
                'recipients': secrets['email_recipients'],
                'subject': 'Workiva IGAM Daily Report - {date}',
                'include_report': 'True'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'file_enabled': 'True',
                'console_enabled': 'True'
            }
        }
        
        # Add Azure-specific configuration
        config['azure'] = {
            'storage_account': os.getenv('AZURE_STORAGE_ACCOUNT', ''),
            'key_vault_url': key_vault_url,
            'environment': os.getenv('ENVIRONMENT', 'production')
        }
        
        logger.info("Azure configuration loaded successfully")
        return config
        
    except AzureError as e:
        logger.error(f"Azure error loading configuration: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {str(e)}")
        return None

def upload_to_azure_storage(file_path, container_name='reports'):
    """
    Upload a file to Azure Storage
    
    Args:
        file_path (str): Path to the file to upload
        container_name (str): Name of the storage container
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        from azure.storage.blob import BlobServiceClient
        
        # Get storage account name from environment
        storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
        if not storage_account:
            logger.error("AZURE_STORAGE_ACCOUNT environment variable not set")
            return False
        
        # Create credential using managed identity
        credential = DefaultAzureCredential()
        
        # Create blob service client
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account}.blob.core.windows.net",
            credential=credential
        )
        
        # Get blob name from file path
        blob_name = os.path.basename(file_path)
        
        # Upload file
        with open(file_path, 'rb') as data:
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"Successfully uploaded {blob_name} to {container_name} container")
        return True
        
    except Exception as e:
        logger.error(f"Failed to upload file to Azure Storage: {str(e)}")
        return False

def setup_azure_logging():
    """
    Set up logging for Azure environment
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/app/logs/workiva_igam_azure.log')
        ]
    )
