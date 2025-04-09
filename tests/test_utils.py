"""Test utilities and mock data."""

from typing import Dict, Any
from datetime import datetime, timedelta
import pytz
from unittest.mock import MagicMock

def get_mock_video_response() -> Dict[str, Any]:
    """Get mock video search response."""
    return {
        "items": [
            {
                "id": {"videoId": "test_video_1"},
                "snippet": {
                    "title": "Test Video 1",
                    "description": "Test Description 1",
                    "publishedAt": (datetime.now(pytz.UTC) - timedelta(hours=2)).isoformat(),
                    "channelId": "test_channel_1",
                    "channelTitle": "Test Channel 1"
                }
            },
            {
                "id": {"videoId": "test_video_2"},
                "snippet": {
                    "title": "Test Video 2",
                    "description": "Test Description 2",
                    "publishedAt": (datetime.now(pytz.UTC) - timedelta(hours=1)).isoformat(),
                    "channelId": "test_channel_2",
                    "channelTitle": "Test Channel 2"
                }
            }
        ]
    }

def get_mock_video_details() -> Dict[str, Any]:
    """Get mock video details response."""
    return {
        "items": [
            {
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100",
                    "commentCount": "10"
                }
            },
            {
                "statistics": {
                    "viewCount": "2000",
                    "likeCount": "200",
                    "commentCount": "20"
                }
            }
        ]
    }

def get_mock_channel_response() -> Dict[str, Any]:
    """Get mock channel response."""
    return {
        "items": [
            {
                "id": "test_channel_1",
                "snippet": {
                    "title": "Test Channel 1",
                    "description": "Contact us at test@example.com\nFollow us on instagram.com/test",
                    "publishedAt": (datetime.now(pytz.UTC) - timedelta(days=30)).isoformat(),
                    "country": "US",
                    "customUrl": "testchannel1"
                },
                "statistics": {
                    "subscriberCount": "10000",
                    "viewCount": "100000",
                    "videoCount": "100"
                },
                "brandingSettings": {
                    "channel": {
                        "keywords": "test, channel, keywords"
                    }
                }
            }
        ]
    }

def get_mock_youtube_service() -> MagicMock:
    """Create a mock YouTube service."""
    mock_service = MagicMock()
    
    # Mock search().list().execute()
    mock_search = MagicMock()
    mock_search.execute.return_value = get_mock_video_response()
    mock_service.search().list.return_value = mock_search
    
    # Mock videos().list().execute()
    mock_videos = MagicMock()
    mock_videos.execute.return_value = get_mock_video_details()
    mock_service.videos().list.return_value = mock_videos
    
    # Mock channels().list().execute()
    mock_channels = MagicMock()
    mock_channels.execute.return_value = get_mock_channel_response()
    mock_service.channels().list.return_value = mock_channels
    
    return mock_service

def get_mock_storage_client() -> MagicMock:
    """Create a mock Google Cloud Storage client."""
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    
    return mock_client 