"""Unit tests for channel_analysis.py module."""

import pytest
import pandas as pd
from typing import Dict, List, Any
from unittest.mock import patch
from executables.channel_analysis import ChannelAnalysisConfig, ChannelAnalyzer
from tests.test_utils import get_mock_youtube_service, get_mock_channel_response

@pytest.fixture
def config() -> ChannelAnalysisConfig:
    """Create a test configuration."""
    config = ChannelAnalysisConfig()
    config.api_key = "test_api_key"
    return config

@pytest.fixture
def analyzer(config: ChannelAnalysisConfig) -> ChannelAnalyzer:
    """Create a test ChannelAnalyzer instance with mocked service."""
    with patch('executables.channel_analysis.build') as mock_build:
        mock_build.return_value = get_mock_youtube_service()
        return ChannelAnalyzer(config)

def test_config_validation(config: ChannelAnalysisConfig) -> None:
    """Test configuration validation."""
    # Test valid configuration
    config.validate()
    
    # Test invalid API key
    config.api_key = ""
    with pytest.raises(AssertionError):
        config.validate()
    
    # Test invalid batch size
    config.api_key = "test_api_key"
    config.batch_size = 0
    with pytest.raises(AssertionError):
        config.validate()

def test_extract_email_from_text(analyzer: ChannelAnalyzer) -> None:
    """Test email extraction functionality."""
    # Test valid input with email
    text = "Contact us at test@example.com"
    result = analyzer.extract_email_from_text(text)
    assert result == "test@example.com"
    
    # Test valid input without email
    result = analyzer.extract_email_from_text("No email here")
    assert result is None
    
    # Test None input
    result = analyzer.extract_email_from_text(None)
    assert result is None
    
    # Test invalid input
    with pytest.raises(AssertionError):
        analyzer.extract_email_from_text(123)

def test_extract_social_links(analyzer: ChannelAnalyzer) -> None:
    """Test social media link extraction."""
    # Test valid input with links
    text = "Follow us on instagram.com/test and twitter.com/test"
    result = analyzer.extract_social_links(text)
    assert isinstance(result, dict)
    assert "instagram" in result
    assert "twitter" in result
    
    # Test valid input without links
    result = analyzer.extract_social_links("No links here")
    assert isinstance(result, dict)
    assert not result
    
    # Test None input
    result = analyzer.extract_social_links(None)
    assert isinstance(result, dict)
    assert not result
    
    # Test invalid input
    with pytest.raises(AssertionError):
        analyzer.extract_social_links(123)

def test_get_channel_details(analyzer: ChannelAnalyzer) -> None:
    """Test channel details retrieval."""
    # Test valid input
    channel_ids = ["test_channel_1"]
    result = analyzer.get_channel_details(channel_ids)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["channel_id"] == "test_channel_1"
    
    # Test empty list
    with pytest.raises(AssertionError):
        analyzer.get_channel_details([])
    
    # Test invalid channel IDs
    with pytest.raises(AssertionError):
        analyzer.get_channel_details([123, "test_id2"])

def test_process_channels(analyzer: ChannelAnalyzer) -> None:
    """Test channel processing functionality."""
    # Test valid input
    input_df = pd.DataFrame({
        'channel_id': ['test_channel_1']
    })
    result = analyzer.process_channels(input_df)
    assert isinstance(result, pd.DataFrame)
    assert 'channel_id' in result.columns
    assert 'subscribers' in result.columns
    assert len(result) == 1
    
    # Test invalid input type
    with pytest.raises(AssertionError):
        analyzer.process_channels("invalid")
    
    # Test missing channel_id column
    with pytest.raises(AssertionError):
        analyzer.process_channels(pd.DataFrame({'other_column': [1, 2]}))

@patch('executables.channel_analysis.build')
def test_main(mock_build: Any) -> None:
    """Test main function execution."""
    mock_build.return_value = get_mock_youtube_service()
    
    from executables.channel_analysis import main
    
    # Test with valid input
    input_df = pd.DataFrame({
        'channel_id': ['test_channel_1']
    })
    result = main(input_df)
    assert isinstance(result, pd.DataFrame)
    assert 'channel_id' in result.columns
    assert 'subscribers' in result.columns
    assert len(result) == 1
    
    # Test with invalid input
    with pytest.raises(ValueError):
        main(None)
    
    # Test with missing channel_id
    with pytest.raises(ValueError):
        main(pd.DataFrame({'other_column': [1]})) 