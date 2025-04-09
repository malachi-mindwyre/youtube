"""Unit tests for combined_youtube_analysis_script.py module."""

import pytest
import pandas as pd
from typing import Any
from unittest.mock import patch
from executables.combined_youtube_analysis_script import main
from tests.test_utils import get_mock_youtube_service

@patch('executables.youtube_api.build')
@patch('executables.channel_analysis.build')
def test_main(mock_channel_build: Any, mock_video_build: Any) -> None:
    """Test main function execution."""
    # Set up mocks
    mock_service = get_mock_youtube_service()
    mock_video_build.return_value = mock_service
    mock_channel_build.return_value = mock_service
    
    # Test successful execution
    videos_df, channels_df = main()
    
    # Verify return types
    assert isinstance(videos_df, pd.DataFrame)
    assert isinstance(channels_df, pd.DataFrame)
    
    # Verify required columns
    assert 'channel_id' in videos_df.columns
    assert 'channel_id' in channels_df.columns
    
    # Verify data consistency
    assert len(videos_df) > 0
    assert len(channels_df) > 0
    
    # Verify data types
    assert pd.api.types.is_numeric_dtype(videos_df['views_per_hour'])
    assert pd.api.types.is_numeric_dtype(channels_df['subscribers'])
    
    # Test error handling
    # Note: This would require mocking the API calls
    # and is typically done in integration tests 