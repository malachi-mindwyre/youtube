"""Shared test fixtures and utilities."""

import pytest
import os
from typing import Generator
from datetime import datetime, timedelta
import pytz

@pytest.fixture(scope="session")
def test_data_dir() -> str:
    """Create and return path to test data directory."""
    test_dir = os.path.join(os.path.dirname(__file__), "test_data")
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

@pytest.fixture(scope="session")
def mock_api_key() -> str:
    """Return a mock API key for testing."""
    return "test_api_key_1234567890"

@pytest.fixture(scope="session")
def mock_channel_id() -> str:
    """Return a mock YouTube channel ID for testing."""
    return "UC_test_channel_id_1234567890"

@pytest.fixture(scope="session")
def mock_video_id() -> str:
    """Return a mock YouTube video ID for testing."""
    return "test_video_id_1234567890"

@pytest.fixture(scope="session")
def mock_timestamp() -> str:
    """Return a mock ISO format timestamp for testing."""
    return (datetime.now(pytz.UTC) - timedelta(hours=2)).isoformat()

@pytest.fixture(scope="session")
def mock_video_stats() -> dict:
    """Return mock video statistics for testing."""
    return {
        "viewCount": "1000",
        "likeCount": "100",
        "commentCount": "10"
    }

@pytest.fixture(scope="session")
def mock_channel_stats() -> dict:
    """Return mock channel statistics for testing."""
    return {
        "subscriberCount": "10000",
        "viewCount": "100000",
        "videoCount": "100"
    }

@pytest.fixture(scope="session")
def mock_bucket_name() -> str:
    """Return a mock GCP bucket name for testing."""
    return "test-bucket-1234567890"

@pytest.fixture(scope="session")
def mock_blob_name() -> str:
    """Return a mock GCP blob name for testing."""
    return "test/data/blob.txt"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Set up test environment before tests and clean up after."""
    # Set up test environment variables
    os.environ["API_KEY"] = "test_api_key_1234567890"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "test_credentials.json"
    
    yield
    
    # Clean up test environment
    if "API_KEY" in os.environ:
        del os.environ["API_KEY"]
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"] 