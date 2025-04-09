from typing import Optional
from google.cloud import storage

class GoogleStorageConfig:
    """Configuration class for Google Cloud Storage settings."""
    def __init__(self) -> None:
        self.bucket_name: Optional[str] = None
        self.destination_blob_name: Optional[str] = None

    def validate(self) -> None:
        """Validate configuration values."""
        assert self.bucket_name, "Bucket name must be set"
        assert self.destination_blob_name, "Destination blob name must be set"

class GoogleStorage:
    """Class for interacting with Google Cloud Storage."""
    def __init__(self) -> None:
        self.storage_client = storage.Client()

    def upload_to_bucket(self, source_file: str, config: GoogleStorageConfig) -> None:
        """Upload a file to Google Cloud Storage bucket."""
        assert isinstance(source_file, str), "Source file path must be a string"
        assert source_file, "Source file path cannot be empty"
        
        config.validate()
        
        try:
            bucket = self.storage_client.bucket(config.bucket_name)
            blob = bucket.blob(config.destination_blob_name)
            blob.upload_from_filename(source_file)
            print(f"Uploaded {source_file} to GCP bucket {config.bucket_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to GCP bucket: {str(e)}")

def upload_to_gcp_bucket(source_file: str, bucket_name: str, destination_blob_name: str) -> None:
    """Utility function to upload a file to Google Cloud Storage bucket."""
    config = GoogleStorageConfig()
    config.bucket_name = bucket_name
    config.destination_blob_name = destination_blob_name
    
    storage = GoogleStorage()
    storage.upload_to_bucket(source_file, config)