import os
import time
import logging
from typing import List, Dict, Tuple, Optional
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import pytz
from dataclasses import dataclass
import yaml
from dotenv import load_dotenv
from dateutil import parser
import traceback
import json
import sqlite3

from executables.utils import has_email, extract_email, calculate_hours_since_published, should_update_channel
from executables.data_processing import merge_dataframes
from executables.email_generation import generate_email_content
from executables.transcript_processing import get_video_transcript, extract_key_moments
from executables.config import YouTubeAPIConfig, Config
from executables.dev_affiliate import AffiliateDatabase

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Load environment variables
load_dotenv()

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

class YouTubeAPI:
    """YouTube API wrapper for video and channel analysis."""
    
    def __init__(self, config: Config):
        """Initialize YouTube API client with configuration."""
        self.config = config
        self.service = self._get_service()
        self.logger = logging.getLogger(__name__)
        self.db = AffiliateDatabase()
        
    def _get_service(self):
        """Get YouTube API service using API key."""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment variables")
        
        return build('youtube', 'v3', developerKey=api_key)
        
    def search_videos(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search for videos matching query."""
        try:
            request = self.service.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                order="viewCount"  # Sort by view count
            )
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            logging.error(f"Error searching videos: {e}")
            return []
            
    def get_video_details(self, video_id: str) -> Dict:
        """Get detailed video statistics."""
        try:
            request = self.service.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            return response.get('items', [{}])[0]
        except HttpError as e:
            logging.error(f"Error getting video details: {e}")
            return {}
            
    def get_channel_details(self, channel_id: str) -> Dict:
        """Get detailed channel statistics."""
        try:
            request = self.service.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()
            return response.get('items', [{}])[0]
        except HttpError as e:
            logging.error(f"Error getting channel details: {e}")
            return {}
            
    def get_video_transcript(self, video_id: str) -> Optional[str]:
        """Get video transcript if available using YouTube Transcript API."""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            if transcript_list:
                # Combine all transcript pieces into one string
                full_transcript = ' '.join(item['text'] for item in transcript_list)
                return full_transcript
        except Exception as e:
            logging.error(f"Error getting video transcript: {e}")
        return None
            
    def process_video_data(self, video_data: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Process raw video data into structured DataFrames."""
        videos = []
        channels = []
        transcripts = []
        emails = []
        
        for video in video_data:
            video_id = video['id']['videoId']
            video_details = self.get_video_details(video_id)
            
            if not video_details:
                continue
                
            # Extract video metrics
            video_stats = video_details.get('statistics', {})
            views = int(video_stats.get('viewCount', 0))
            likes = int(video_stats.get('likeCount', 0))
            comments = int(video_stats.get('commentCount', 0))
            
            # Calculate engagement rate
            engagement_rate = (likes + comments) / views if views > 0 else 0
            
            # Get channel details
            channel_id = video_details['snippet']['channelId']
            channel_details = self.get_channel_details(channel_id)
            
            if not channel_details:
                continue
                
            # Extract channel metrics
            channel_stats = channel_details.get('statistics', {})
            subscribers = int(channel_stats.get('subscriberCount', 0))
            total_videos = int(channel_stats.get('videoCount', 0))
            total_views = int(channel_stats.get('viewCount', 0))
            
            # Get video transcript
            transcript = self.get_video_transcript(video_id)
            
            # Check for email in transcript
            has_email_in_transcript = has_email(transcript) if transcript else False
            email = extract_email(transcript) if transcript else None
            
            # Store video data
            videos.append({
                'video_id': video_id,
                'title': video_details['snippet']['title'],
                'channel_id': channel_id,
                'published_at': video_details['snippet']['publishedAt'],
                'views': views,
                'likes': likes,
                'comments': comments,
                'engagement_rate': engagement_rate,
                'has_transcript': bool(transcript),
                'has_email': has_email_in_transcript
            })
            
            # Store channel data
            channels.append({
                'channel_id': channel_id,
                'channel_title': channel_details['snippet']['title'],
                'subscribers': subscribers,
                'total_videos': total_videos,
                'total_views': total_views,
                'email': email
            })
            
            # Store transcript data
            if transcript:
                transcripts.append({
                    'video_id': video_id,
                    'transcript': transcript
                })
                
            # Store email data if found
            if email:
                emails.append({
                    'channel_id': channel_id,
                    'channel_title': channel_details['snippet']['title'],
                    'email': email,
                    'source': 'transcript'
                })
                
        # Convert to DataFrames
        videos_df = pd.DataFrame(videos)
        channels_df = pd.DataFrame(channels)
        transcripts_df = pd.DataFrame(transcripts)
        emails_df = pd.DataFrame(emails)
        
        return videos_df, channels_df, transcripts_df, emails_df
        
    def save_results(self, channels: List[Dict], videos: List[Dict], email_content: List[Dict]) -> None:
        """Save results to CSV and/or Excel files."""
        # Create output directory if it doesn't exist
        os.makedirs(self.config.output_directory, exist_ok=True)
        
        # Define file paths
        channels_file = os.path.join(self.config.output_directory, 'youtube_channels.csv')
        videos_file = os.path.join(self.config.output_directory, 'youtube_videos.csv')
        email_file = os.path.join(self.config.output_directory, 'youtube_email_content.csv')
        excel_file = os.path.join(self.config.output_directory, 'youtube_analysis.xlsx')
        
        # Convert to DataFrames
        channels_df = pd.DataFrame(channels)
        videos_df = pd.DataFrame(videos)
        email_df = pd.DataFrame(email_content)
        
        # Save CSV files if enabled
        if self.config.save_csv:
            channels_df.to_csv(channels_file, index=False)
            videos_df.to_csv(videos_file, index=False)
            email_df.to_csv(email_file, index=False)
            
        # Save Excel file if enabled
        if self.config.save_excel:
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                channels_df.to_excel(writer, sheet_name='Channels', index=False)
                videos_df.to_excel(writer, sheet_name='Videos', index=False)
                email_df.to_excel(writer, sheet_name='Email Content', index=False)
                
        # Save JSON file if enabled
        if self.config.save_json:
            json_file = os.path.join(self.config.output_directory, 'youtube_analysis.json')
            with open(json_file, 'w') as f:
                json.dump({
                    'channels': channels,
                    'videos': videos,
                    'email_content': email_content
                }, f, indent=2)

    def save_to_db(self, videos_df: pd.DataFrame, channels_df: pd.DataFrame, 
                    transcripts_df: pd.DataFrame, emails_df: pd.DataFrame) -> None:
        conn = self.db.connect()
        
        try:
            # Handle youtube_videos: Check video_id, replace if exists, append if not
            if not videos_df.empty:
                cursor = conn.cursor()
                for _, row in videos_df.iterrows():
                    cursor.execute('''
                        INSERT OR REPLACE INTO youtube_videos (
                            video_id, title, description, channel_id, published_at, 
                            views, likes, comments, engagement_rate, has_transcript, has_email
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('video_id'), 
                        row.get('title'), 
                        row.get('description'),
                        row.get('channel_id'), 
                        row.get('published_at'), 
                        row.get('views'),
                        row.get('likes'), 
                        row.get('comments'), 
                        row.get('engagement_rate'),
                        row.get('has_transcript'), 
                        row.get('has_email')
                    ))
                self.logger.info(f"Processed {len(videos_df)} videos (upserted)")
            
            # Handle youtube_channels: Check channel_id, replace if exists, append if not
            if not channels_df.empty:
                cursor = conn.cursor()
                for _, row in channels_df.iterrows():
                    cursor.execute('''
                        INSERT OR REPLACE INTO youtube_channels (
                            channel_id, channel_title, subscribers, total_videos, total_views, email
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('channel_id'), 
                        row.get('channel_title'), 
                        row.get('subscribers'),
                        row.get('total_videos'), 
                        row.get('total_views'), 
                        row.get('email')
                    ))
                self.logger.info(f"Processed {len(channels_df)} channels (upserted)")
            
            # Handle youtube_transcripts: Check video_id, replace if exists, append if not
            if transcripts_df is not None and not transcripts_df.empty:
                cursor = conn.cursor()
                for _, row in transcripts_df.iterrows():
                    cursor.execute('''
                        INSERT OR REPLACE INTO youtube_transcripts (
                            video_id, transcript_text
                        ) VALUES (?, ?)
                    ''', (
                        row.get('video_id'), 
                        row.get('transcript')
                    ))
                self.logger.info(f"Processed {len(transcripts_df)} transcripts (upserted)")
            
            # Handle youtube_email_content: Check channel_id, skip if exists, append if not
            if emails_df is not None and not emails_df.empty:
                cursor = conn.cursor()
                new_emails_count = 0
                
                for _, row in emails_df.iterrows():
                    # Check if channel_id already exists
                    cursor.execute('SELECT id FROM youtube_email_content WHERE channel_id = ?', (row.get('channel_id'),))
                    existing = cursor.fetchone()
                    
                    if not existing:
                        # Only insert if channel_id doesn't exist
                        cursor.execute('''
                            INSERT INTO youtube_email_content (
                                channel_id, channel_title, email, email_subject, email_body
                            ) VALUES (?, ?, ?, ?, ?)
                        ''', (
                            row.get('channel_id'), 
                            row.get('channel_title'), 
                            row.get('email'),
                            row.get('email_subject'), 
                            row.get('email_body')
                        ))
                        new_emails_count += 1
                
                self.logger.info(f"Added {new_emails_count} new email records (skipped {len(emails_df) - new_emails_count} existing)")
                
                # Handle affiliates: Check email, create only if not exists
                for _, row in emails_df.iterrows():
                    if pd.notna(row.get('email')):
                        # Check if this email already exists in affiliates
                        cursor.execute('SELECT id FROM affiliates WHERE email = ?', (row.get('email'),))
                        
                        # If not found, insert new affiliate
                        if not cursor.fetchone():
                            referral_id = self.db.generate_referral_id(row.get('channel_title'))
                            affiliate_link = self.db.generate_affiliate_link(referral_id)
                            
                            cursor.execute('''
                                INSERT INTO affiliates (
                                    name, email, referral_id, affiliate_link
                                ) VALUES (?, ?, ?, ?)
                            ''', (
                                row.get('channel_title'),
                                row.get('email'),
                                referral_id,
                                affiliate_link
                            ))
                            self.logger.info(f"Created new affiliate for channel: {row.get('channel_title')} with link: {affiliate_link}")
            
            conn.commit()
            self.logger.info("Successfully saved all YouTube data to database")
            
        except Exception as e:
            self.logger.error(f"Error saving to database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def analyze(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Run complete YouTube analysis."""
        # Search for videos
        video_data = self.search_videos(self.config.search_query, self.config.max_results)
        if not video_data:
            raise ValueError("No videos found matching criteria")
            
        # Process video data and extract key details
        videos_df, channels_df, transcripts_df, emails_df = self.process_video_data(video_data)
        
        # Save results to files
        if videos_df.shape[0] > 0 or channels_df.shape[0] > 0 or emails_df.shape[0] > 0:
            self.save_results(
                channels=channels_df.to_dict('records'),
                videos=videos_df.to_dict('records'),
                email_content=emails_df.to_dict('records')
            )
            
            # Save to database
            self.save_to_db(videos_df, channels_df, transcripts_df, emails_df)
            
        return videos_df, channels_df, emails_df

def main() -> pd.DataFrame:
    """Main function to execute the YouTube video analysis."""
    config = YouTubeAPIConfig(
        api_key="YOUR_API_KEY",
        search_query="Your Search Query",
        max_results=50,
        save_csv=True,
        save_excel=True,
        save_json=True
    )
    youtube_api = YouTubeAPI(config)
    
    try:
        # Step 1: Search videos by keyword
        search_items = youtube_api.search_videos(
            config.search_query, 
            config.max_results
        )
        video_ids = [item["id"]["videoId"] for item in search_items]
        
        # Step 2: Get detailed video stats
        video_details = youtube_api.get_video_details(video_ids)
        
        # Step 3: Process data and create DataFrame
        processed_data, transcripts_data = youtube_api.process_video_data(search_items)
        
        # Create pandas DataFrame
        videos_df = pd.DataFrame(processed_data)
        transcripts_df = pd.DataFrame(transcripts_data)
        
        # Configure pandas display options
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print("\nDataFrame Info:")
        print(videos_df.info())
        print(transcripts_df.info())
        
        print("\nFirst few rows of the DataFrame:")
        print(videos_df.head())
        print(transcripts_df.head())
        
        print("\nBasic statistics for numeric columns:")
        print(videos_df.describe())
        print(transcripts_df.describe())
        
        return videos_df, transcripts_df
        
    except Exception as e:
        raise RuntimeError(f"Failed to execute YouTube analysis: {str(e)}")

if __name__ == "__main__":
    videos_df, transcripts_df = main()