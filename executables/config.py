from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import os
import yaml

@dataclass
class YouTubeAPIConfig:
    """Configuration for YouTube API interactions."""
    api_key: str
    search_query: str
    max_results: int
    output_directory: str
    save_csv: bool = True
    save_excel: bool = True
    save_json: bool = False
    min_views: Optional[int] = None
    min_subscribers: Optional[int] = None
    min_videos: Optional[int] = None
    max_hours_since_published: Optional[int] = None
    excluded_channels: List[str] = None
    excluded_keywords: List[str] = None
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'YouTubeAPIConfig':
        """Create config from dictionary.
        
        Args:
            config: Dictionary containing configuration values
            
        Returns:
            YouTubeAPIConfig instance
        """
        api_key = os.getenv('YOUTUBE_API_KEY', '')
        search_query = config.get('search', {}).get('keyword', '')
        max_results = config.get('search', {}).get('max_results', 50)
        output_directory = config.get('output', {}).get('directory', 'results')
        save_csv = config.get('output', {}).get('save_csv', True)
        save_excel = config.get('output', {}).get('save_excel', True)
        save_json = config.get('output', {}).get('save_json', False)
        
        filters = config.get('filters', {})
        min_views = filters.get('min_views')
        min_subscribers = filters.get('min_subscribers')
        min_videos = filters.get('min_videos')
        max_hours_since_published = filters.get('max_hours_since_published')
        excluded_channels = filters.get('excluded_channels', [])
        excluded_keywords = filters.get('excluded_keywords', [])
        
        return cls(
            api_key=api_key,
            search_query=search_query,
            max_results=max_results,
            output_directory=output_directory,
            save_csv=save_csv,
            save_excel=save_excel,
            save_json=save_json,
            min_views=min_views,
            min_subscribers=min_subscribers,
            min_videos=min_videos,
            max_hours_since_published=max_hours_since_published,
            excluded_channels=excluded_channels,
            excluded_keywords=excluded_keywords
        )

@dataclass
class Config:
    """Main configuration class for the application."""
    youtube_api: 'YouTubeAPIConfig'
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """Load configuration from YAML file.
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            Config instance
        """
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        youtube_api_config = YouTubeAPIConfig.from_dict(config_dict)
        return cls(youtube_api=youtube_api_config) 