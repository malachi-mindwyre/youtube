from typing import Dict, List, Optional, Any, Set
import os
from datetime import datetime
import pandas as pd
from googleapiclient.discovery import build
import re
from dotenv import load_dotenv

class ChannelAnalysisConfig:
    """Configuration class for channel analysis settings."""
    def __init__(self) -> None:
        load_dotenv()
        self.api_key: str = os.getenv("API_KEY", "")
        self.batch_size: int = 50  # API limit for channel details

    def validate(self) -> None:
        """Validate configuration values."""
        assert self.api_key, "API_KEY environment variable is not set"
        assert self.batch_size > 0, "Batch size must be positive"

class ChannelAnalyzer:
    """Class for analyzing YouTube channels."""
    def __init__(self, config: ChannelAnalysisConfig) -> None:
        self.config = config
        self.config.validate()
        self.youtube = build("youtube", "v3", developerKey=self.config.api_key)
        self.social_patterns: Dict[str, str] = {
            'instagram': r'(?:instagram\.com|instagr\.am)/([^/\s]+)',
            'twitter': r'(?:twitter\.com|x\.com)/([^/\s]+)',
            'facebook': r'facebook\.com/([^/\s]+)',
            'tiktok': r'tiktok\.com/@([^/\s]+)',
            'linkedin': r'linkedin\.com/(?:in|company)/([^/\s]+)',
            'website': r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?'
        }

    def extract_email_from_text(self, text: Optional[str]) -> Optional[str]:
        """Extract email addresses from text using regex."""
        if not text:
            return None
            
        assert isinstance(text, str), "Text must be a string"
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return ', '.join(emails) if emails else None

    def extract_social_links(self, text: Optional[str]) -> Dict[str, str]:
        """Extract social media and other links from text."""
        if not text:
            return {}
            
        assert isinstance(text, str), "Text must be a string"
        links: Dict[str, str] = {}
        
        for platform, pattern in self.social_patterns.items():
            matches = re.findall(pattern, text, re.I)
            if matches:
                links[platform] = ', '.join(matches)
        
        return links

    def get_channel_details(self, channel_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed information about YouTube channels."""
        assert channel_ids, "Channel IDs list cannot be empty"
        assert all(isinstance(id, str) for id in channel_ids), "All channel IDs must be strings"
        
        channel_data: List[Dict[str, Any]] = []
        
        for i in range(0, len(channel_ids), self.config.batch_size):
            batch_ids = channel_ids[i:i + self.config.batch_size]
            
            try:
                channels_response = self.youtube.channels().list(
                    part="snippet,statistics,brandingSettings",
                    id=",".join(batch_ids)
                ).execute()

                for channel in channels_response.get("items", []):
                    channel_info = self._process_channel(channel)
                    channel_data.append(channel_info)
                    
            except Exception as e:
                raise RuntimeError(f"Failed to process channel batch: {str(e)}")
        
        return channel_data

    def _process_channel(self, channel: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual channel data."""
        assert isinstance(channel, dict), "Channel data must be a dictionary"
        
        channel_id = channel["id"]
        snippet = channel["snippet"]
        statistics = channel["statistics"]
        branding = channel.get("brandingSettings", {})
        
        try:
            about_response = self.youtube.channels().list(
                part="brandingSettings",
                id=channel_id
            ).execute()
            
            channel_about = about_response.get("items", [{}])[0].get("brandingSettings", {}).get("channel", {})
            
            description = snippet.get("description", "")
            email = self.extract_email_from_text(description)
            social_links = self.extract_social_links(description)
            
            custom_url = None
            if 'customUrl' in snippet:
                custom_url = f"@{snippet['customUrl']}"

            channel_info = {
                "channel_id": channel_id,
                "channel_title": snippet.get("title"),
                "custom_url": custom_url,
                "creation_date": snippet.get("publishedAt"),
                "subscribers": statistics.get("subscriberCount"),
                "total_views": statistics.get("viewCount"),
                "total_videos": statistics.get("videoCount"),
                "country": snippet.get("country"),
                "email": email,
                "description": description,
                "keywords": channel_about.get("keywords"),
                "channel_url": f"https://www.youtube.com/channel/{channel_id}"
            }
            
            channel_info.update(social_links)
            return channel_info
            
        except Exception as e:
            raise RuntimeError(f"Failed to process channel {channel_id}: {str(e)}")

    def process_channels(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """Process channels from input DataFrame and return detailed channel information."""
        assert isinstance(input_df, pd.DataFrame), "Input must be a pandas DataFrame"
        assert 'channel_id' in input_df.columns, "Input DataFrame must contain 'channel_id' column"
        
        channel_ids = input_df['channel_id'].unique().tolist()
        channel_data = self.get_channel_details(channel_ids)
        
        df_channels = pd.DataFrame(channel_data)
        
        numeric_cols = ['subscribers', 'total_views', 'total_videos']
        for col in numeric_cols:
            df_channels[col] = pd.to_numeric(df_channels[col], errors='coerce')
        
        return df_channels

def main(input_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Main function to process channel data."""
    if input_df is None or 'channel_id' not in input_df.columns:
        raise ValueError("Input DataFrame required with 'channel_id' column")
    
    config = ChannelAnalysisConfig()
    analyzer = ChannelAnalyzer(config)
    
    try:
        df_channels = analyzer.process_channels(input_df)
        
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print("\nChannel Analysis Results:")
        print(f"\nTotal channels analyzed: {len(df_channels)}")
        print("\nFirst few channels:")
        print(df_channels.head())
        
        print("\nChannel Statistics:")
        print(df_channels[['subscribers', 'total_views', 'total_videos']].describe())
        
        email_count = df_channels['email'].notna().sum()
        print(f"\nChannels with email addresses: {email_count} ({(email_count/len(df_channels))*100:.1f}%)")
        
        return df_channels
        
    except Exception as e:
        raise RuntimeError(f"Failed to execute channel analysis: {str(e)}")

if __name__ == "__main__":
    test_df = pd.DataFrame({'channel_id': ['UC_x5XG1OV2P6uZZ5FSM9Ttw']})  # Google Developers channel
    df_channels = main(test_df)