"""Unit tests for google_storage.py module."""

import pytest
from unittest.mock import patch
from executables.google_storage import GoogleStorageConfig, GoogleStorage
from tests.test_utils import get_mock_storage_client
from typing import Any

@pytest.fixture
def config() -> GoogleStorageConfig:
    """Create a test configuration."""
    config = GoogleStorageConfig()
    config.bucket_name = "test-bucket"
    config.destination_blob_name = "test/blob.txt"
    return config

@pytest.fixture
def storage() -> GoogleStorage:
    """Create a test GoogleStorage instance with mocked client."""
    with patch('executables.google_storage.storage.Client') as mock_client:
        mock_client.return_value = get_mock_storage_client()
        return GoogleStorage()

def test_config_validation(config: GoogleStorageConfig) -> None:
    """Test configuration validation."""
    # Test valid configuration
    config.validate()
    
    # Test missing bucket name
    config.bucket_name = None
    with pytest.raises(AssertionError):
        config.validate()
    
    # Test missing destination blob name
    config.bucket_name = "test-bucket"
    config.destination_blob_name = None
    with pytest.raises(AssertionError):
        config.validate()

def test_upload_to_bucket(storage: GoogleStorage, config: GoogleStorageConfig) -> None:
    """Test file upload functionality."""
    # Test valid input
    source_file = "test.txt"
    storage.upload_to_bucket(source_file, config)
    
    # Test invalid source file type
    with pytest.raises(AssertionError):
        storage.upload_to_bucket(123, config)
    
    # Test empty source file path
    with pytest.raises(AssertionError):
        storage.upload_to_bucket("", config)
    
    # Test invalid config
    with pytest.raises(AssertionError):
        storage.upload_to_bucket(source_file, None)

@patch('executables.google_storage.storage.Client')
def test_upload_to_gcp_bucket(mock_client: Any) -> None:
    """Test utility function for uploading to GCP bucket."""
    mock_client.return_value = get_mock_storage_client()
    
    from executables.google_storage import upload_to_gcp_bucket
    
    # Test valid input
    upload_to_gcp_bucket(
        "test.txt",
        "test-bucket",
        "test/blob.txt"
    )
    
    # Test invalid source file
    with pytest.raises(AssertionError):
        upload_to_gcp_bucket(123, "test-bucket", "test/blob.txt")
    
    # Test invalid bucket name
    with pytest.raises(AssertionError):
        upload_to_gcp_bucket("test.txt", None, "test/blob.txt")
    
    # Test invalid destination blob name
    with pytest.raises(AssertionError):
        upload_to_gcp_bucket("test.txt", "test-bucket", None) 