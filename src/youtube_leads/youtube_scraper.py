"""
YouTube data scraping module for the lead generation system.
"""

from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from .config import config

class YouTubeScraper:
    """Class for scraping YouTube data."""
    
    def __init__(self) -> None:
        """Initialize the YouTube scraper with API credentials."""
        self.youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)
        
    def search_videos(self, keywords: str, max_results: int = 50) -> List[Dict]:
        """
        Search for videos based on keywords.
        
        Args:
            keywords: Search keywords
            max_results: Maximum number of results to return
            
        Returns:
            List of video metadata dictionaries
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=keywords,
                type="video",
                maxResults=max_results,
                order="relevance"
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video)
                
            return videos
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            raise
            
    def get_video_details(self, video_id: str) -> Dict:
        """
        Get detailed information about a specific video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video details
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return {}
                
            item = response['items'][0]
            return {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'view_count': item['statistics'].get('viewCount', 0),
                'like_count': item['statistics'].get('likeCount', 0),
                'comment_count': item['statistics'].get('commentCount', 0)
            }
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            raise
            
    def get_channel_details(self, channel_id: str) -> Dict:
        """
        Get detailed information about a YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Dictionary containing channel details
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                return {}
                
            item = response['items'][0]
            return {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'subscriber_count': item['statistics'].get('subscriberCount', 0),
                'video_count': item['statistics'].get('videoCount', 0),
                'view_count': item['statistics'].get('viewCount', 0)
            }
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            raise
            
    def extract_email(self, text: str) -> Optional[str]:
        """
        Extract email address from text using regex.
        
        Args:
            text: Text to search for email addresses
            
        Returns:
            First email address found or None
        """
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
        
    def get_video_transcript(self, video_id: str) -> Optional[str]:
        """
        Get the transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video transcript as text or None if not available
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
            return formatter.format_transcript(transcript_list)
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return None 