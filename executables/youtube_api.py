from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import pandas as pd
from googleapiclient.discovery import build
from dateutil import parser
import pytz
from dotenv import load_dotenv
import yaml
import re

def has_email(text: str) -> bool:
    """Check if text contains an email address.
    
    Args:
        text: Text to check for email addresses
        
    Returns:
        bool: True if email found, False otherwise
    """
    if not text:
        return False
    # Simple email regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.search(email_pattern, text))

class YouTubeAPIConfig:
    """Configuration class for YouTube API settings."""
    def __init__(self) -> None:
        load_dotenv()
        self.api_key: str = os.getenv("API_KEY", "")
        
        # Load configuration from YAML file
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            
        # Search settings
        self.search_keyword: str = config['search']['keyword']
        self.max_results: int = config['search']['max_results']
        
        # Filter settings
        self.min_views: int = config['filters']['min_views']
        self.min_views_per_hour: float = config['filters']['min_views_per_hour']
        self.min_comments_per_hour: float = config['filters']['min_comments_per_hour']
        self.min_likes_per_hour: float = config['filters']['min_likes_per_hour']
        self.max_hours_since_published: float = config['filters']['max_hours_since_published']
        
        # Output settings
        self.save_csv: bool = config['output']['save_csv']
        self.save_excel: bool = config['output']['save_excel']
        self.save_json: bool = config['output']['save_json']
        self.output_directory: str = config['output']['output_directory']
        
        # Analysis settings
        self.include_channel_stats: bool = config['analysis']['include_channel_stats']
        self.include_video_stats: bool = config['analysis']['include_video_stats']
        self.include_engagement_metrics: bool = config['analysis']['include_engagement_metrics']
        self.include_sentiment_analysis: bool = config['analysis']['include_sentiment_analysis']

    def validate(self) -> None:
        """Validate configuration values."""
        assert self.api_key, "API_KEY environment variable is not set"
        assert isinstance(self.search_keyword, str), "Search keyword must be a string"
        assert self.max_results > 0, "Max results must be positive"
        assert self.min_views >= 0, "Minimum views must be non-negative"
        assert self.min_views_per_hour >= 0, "Minimum views per hour must be non-negative"
        assert self.min_comments_per_hour >= 0, "Minimum comments per hour must be non-negative"
        assert self.min_likes_per_hour >= 0, "Minimum likes per hour must be non-negative"
        assert self.max_hours_since_published > 0, "Maximum hours since published must be positive"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

class YouTubeAPI:
    """Class for interacting with YouTube Data API."""
    def __init__(self, config: YouTubeAPIConfig) -> None:
        self.config = config
        self.config.validate()
        self.youtube = build("youtube", "v3", developerKey=self.config.api_key)

    def search_videos_by_keyword(self, keyword: str, max_results: int) -> List[Dict[str, Any]]:
        """Search YouTube videos by keyword and return raw API response."""
        assert isinstance(keyword, str), "Keyword must be a string"
        assert max_results > 0, "Max results must be positive"
        
        try:
            search_response = self.youtube.search().list(
                q=keyword,
                part="snippet",
                type="video",
                maxResults=max_results,
                order="viewCount"
            ).execute()
            return search_response.get("items", [])
        except Exception as e:
            raise RuntimeError(f"Failed to search videos: {str(e)}")

    def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed statistics for videos using their IDs."""
        assert video_ids, "Video IDs list cannot be empty"
        assert all(isinstance(id, str) for id in video_ids), "All video IDs must be strings"
        
        try:
            videos_response = self.youtube.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids)
            ).execute()
            return videos_response.get("items", [])
        except Exception as e:
            raise RuntimeError(f"Failed to get video details: {str(e)}")

    def calculate_hourly_metrics(self, published_at: str, stats: Dict[str, str]) -> Dict[str, float]:
        """Calculate engagement metrics per hour since video publication."""
        assert isinstance(published_at, str), "Published at must be a string"
        assert isinstance(stats, dict), "Stats must be a dictionary"
        
        publish_time = parser.parse(published_at)
        current_time = datetime.now(pytz.UTC)
        hours_since_published = max(1, (current_time - publish_time).total_seconds() / 3600)
        
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        
        return {
            "views_per_hour": views / hours_since_published,
            "likes_per_hour": likes / hours_since_published,
            "comments_per_hour": comments / hours_since_published,
            "hours_since_published": hours_since_published
        }

    def meets_criteria(self, metrics: Dict[str, float], stats: Dict[str, str]) -> bool:
        """Check if video meets minimum engagement criteria."""
        assert isinstance(metrics, dict), "Metrics must be a dictionary"
        assert isinstance(stats, dict), "Stats must be a dictionary"
        
        views = int(stats.get("viewCount", 0))
        return (
            views >= self.config.min_views and
            metrics["views_per_hour"] >= self.config.min_views_per_hour and
            metrics["comments_per_hour"] >= self.config.min_comments_per_hour and
            metrics["likes_per_hour"] >= self.config.min_likes_per_hour and
            metrics["hours_since_published"] <= self.config.max_hours_since_published
        )

    def process_data(self, search_items: List[Dict[str, Any]], video_details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine search results and video details into structured data with hourly metrics."""
        assert len(search_items) == len(video_details), "Search items and video details must have same length"
        
        processed_data = []
        
        for item, details in zip(search_items, video_details):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            video_snippet = details["snippet"]
            stats = details["statistics"]
            
            hourly_metrics = self.calculate_hourly_metrics(snippet["publishedAt"], stats)
            
            if not self.meets_criteria(hourly_metrics, stats):
                continue
                
            processed_data.append({
                "video_id": video_id,
                "title": snippet["title"],
                "published_at": snippet["publishedAt"],
                "channel_id": snippet["channelId"],
                "channel_title": snippet["channelTitle"],
                "views": stats.get("viewCount", 0),
                "likes": stats.get("likeCount", 0),
                "comments": stats.get("commentCount", 0),
                "views_per_hour": round(hourly_metrics["views_per_hour"], 2),
                "likes_per_hour": round(hourly_metrics["likes_per_hour"], 2),
                "comments_per_hour": round(hourly_metrics["comments_per_hour"], 2),
                "hours_since_published": round(hourly_metrics["hours_since_published"], 2),
                "url": f"https://youtube.com/watch?v={video_id}"
            })
        
        return processed_data

def main() -> pd.DataFrame:
    """Main function to execute the YouTube video analysis."""
    config = YouTubeAPIConfig()
    youtube_api = YouTubeAPI(config)
    
    try:
        # Step 1: Search videos by keyword
        search_items = youtube_api.search_videos_by_keyword(
            config.search_keyword, 
            config.max_results
        )
        video_ids = [item["id"]["videoId"] for item in search_items]
        
        # Step 2: Get detailed video stats
        video_details = youtube_api.get_video_details(video_ids)
        
        # Step 3: Process data and create DataFrame
        processed_data = youtube_api.process_data(search_items, video_details)
        
        # Create pandas DataFrame
        df = pd.DataFrame(processed_data)
        
        # Configure pandas display options
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print("\nDataFrame Info:")
        print(df.info())
        
        print("\nFirst few rows of the DataFrame:")
        print(df.head())
        
        print("\nBasic statistics for numeric columns:")
        print(df.describe())
        
        return df
        
    except Exception as e:
        raise RuntimeError(f"Failed to execute YouTube analysis: {str(e)}")

if __name__ == "__main__":
    df = main()