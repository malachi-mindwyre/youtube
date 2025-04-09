"""Unit tests for youtube_api.py module."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pytz
from unittest.mock import patch
import pandas as pd
from executables.youtube_api import YouTubeAPIConfig, YouTubeAPI
from tests.test_utils import (
    get_mock_youtube_service,
    get_mock_video_response,
    get_mock_video_details
)

@pytest.fixture
def config() -> YouTubeAPIConfig:
    """Create a test configuration."""
    config = YouTubeAPIConfig()
    config.api_key = "test_api_key"
    return config

@pytest.fixture
def youtube_api(config: YouTubeAPIConfig) -> YouTubeAPI:
    """Create a test YouTubeAPI instance with mocked service."""
    with patch('executables.youtube_api.build') as mock_build:
        mock_build.return_value = get_mock_youtube_service()
        return YouTubeAPI(config)

def test_config_validation(config: YouTubeAPIConfig) -> None:
    """Test configuration validation."""
    # Test valid configuration
    config.validate()
    
    # Test invalid API key
    config.api_key = ""
    with pytest.raises(AssertionError):
        config.validate()
    
    # Test invalid max_results
    config.api_key = "test_api_key"
    config.max_results = 0
    with pytest.raises(AssertionError):
        config.validate()

def test_search_videos_by_keyword(youtube_api: YouTubeAPI) -> None:
    """Test video search functionality."""
    # Test valid input
    result = youtube_api.search_videos_by_keyword("test", 5)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"]["videoId"] == "test_video_1"
    
    # Test invalid keyword
    with pytest.raises(AssertionError):
        youtube_api.search_videos_by_keyword(123, 5)
    
    # Test invalid max_results
    with pytest.raises(AssertionError):
        youtube_api.search_videos_by_keyword("test", 0)

def test_get_video_details(youtube_api: YouTubeAPI) -> None:
    """Test video details retrieval."""
    # Test valid input
    video_ids = ["test_video_1", "test_video_2"]
    result = youtube_api.get_video_details(video_ids)
    assert isinstance(result, list)
    assert len(result) == 2
    assert "statistics" in result[0]
    
    # Test empty list
    with pytest.raises(AssertionError):
        youtube_api.get_video_details([])
    
    # Test invalid video IDs
    with pytest.raises(AssertionError):
        youtube_api.get_video_details([123, "test_id2"])

def test_calculate_hourly_metrics(youtube_api: YouTubeAPI) -> None:
    """Test hourly metrics calculation."""
    # Test valid input
    published_at = (datetime.now(pytz.UTC) - timedelta(hours=2)).isoformat()
    stats = {
        "viewCount": "1000",
        "likeCount": "100",
        "commentCount": "10"
    }
    result = youtube_api.calculate_hourly_metrics(published_at, stats)
    
    assert isinstance(result, dict)
    assert "views_per_hour" in result
    assert "likes_per_hour" in result
    assert "comments_per_hour" in result
    assert "hours_since_published" in result
    
    # Test invalid published_at
    with pytest.raises(AssertionError):
        youtube_api.calculate_hourly_metrics(123, stats)
    
    # Test invalid stats
    with pytest.raises(AssertionError):
        youtube_api.calculate_hourly_metrics(published_at, "invalid")

def test_meets_criteria(youtube_api: YouTubeAPI) -> None:
    """Test criteria checking functionality."""
    # Test valid input
    metrics = {
        "views_per_hour": 10.0,
        "likes_per_hour": 2.0,
        "comments_per_hour": 0.5
    }
    stats = {
        "viewCount": "2000",
        "likeCount": "200",
        "commentCount": "20"
    }
    result = youtube_api.meets_criteria(metrics, stats)
    assert isinstance(result, bool)
    
    # Test invalid metrics
    with pytest.raises(AssertionError):
        youtube_api.meets_criteria("invalid", stats)
    
    # Test invalid stats
    with pytest.raises(AssertionError):
        youtube_api.meets_criteria(metrics, "invalid")

def test_process_data(youtube_api: YouTubeAPI) -> None:
    """Test data processing functionality."""
    # Test valid input
    search_items = get_mock_video_response()["items"]
    video_details = get_mock_video_details()["items"]
    result = youtube_api.process_data(search_items, video_details)
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Test mismatched lengths
    with pytest.raises(AssertionError):
        youtube_api.process_data(search_items, [])

@patch('executables.youtube_api.build')
def test_main(mock_build: Any) -> None:
    """Test main function execution."""
    mock_build.return_value = get_mock_youtube_service()
    
    from executables.youtube_api import main
    result = main()
    
    assert isinstance(result, pd.DataFrame)
    assert 'video_id' in result.columns
    assert 'title' in result.columns
    assert 'views_per_hour' in result.columns 