#!/usr/bin/env python3
"""Script to run YouTube video and channel analysis."""

import os
import sys
import yaml
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import pandas as pd
import re

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from executables.youtube_api import YouTubeAPI
from executables.email_generation import generate_email_content

def extract_email(text: str) -> str:
    """Extract the first email address from a string, or return empty string."""
    if not text:
        return ''
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ''

def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        sys.exit(1)

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = load_config()
    output_dir = config.get('output', {}).get('directory', 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Initialize YouTube API
        api = YouTubeAPI(config)
        
        # Get search query from config
        search_query = config.get('search', {}).get('keyword', '')
        max_results = config.get('search', {}).get('max_results', 50)
        
        # Search for videos
        logging.info(f"Searching for videos with query: {search_query}")
        video_data = api.search_videos(search_query, max_results)
        
        if not video_data:
            logging.error("No videos found matching criteria")
            sys.exit(1)
            
        logging.info(f"Found {len(video_data)} videos")
        
        # Collect video, channel, and email details
        videos_list: List[dict] = []
        channels_list: List[dict] = []
        emails_list: List[dict] = []
        channels_with_email = set()  # Track channel IDs that have emails
        
        # First pass: Find channels with emails
        for video in video_data:
            video_id = video['id']['videoId']
            
            # Get video details
            video_details = api.get_video_details(video_id)
            if not video_details:
                continue
                
            snippet = video_details.get('snippet', {})
            channel_id = snippet.get('channelId', '')
            
            # Skip if we already processed this channel
            if channel_id in channels_with_email:
                continue
                
            # Get channel details
            channel_details = api.get_channel_details(channel_id)
            if not channel_details:
                continue
                
            channel_snippet = channel_details.get('snippet', {})
            channel_stats = channel_details.get('statistics', {})
            channel_title = channel_snippet.get('title', '')
            
            # Try to extract email from channel description
            channel_description = channel_snippet.get('description', '')
            channel_email = extract_email(channel_description)
            
            # If not found, try video description
            if not channel_email:
                channel_email = extract_email(snippet.get('description', ''))
                
            # Only process channels with emails
            if channel_email:
                channels_with_email.add(channel_id)
                logging.info(f"Found channel with email: {channel_title} ({channel_email})")
                
                # Add channel to list
                channels_list.append({
                    'channel_id': channel_id,
                    'channel_title': channel_title,
                    'subscribers': channel_stats.get('subscriberCount', ''),
                    'total_videos': channel_stats.get('videoCount', ''),
                    'total_views': channel_stats.get('viewCount', ''),
                    'email': channel_email
                })
                
                # Generate email content
                try:
                    email_content = generate_email_content({
                        'channel_id': channel_id,
                        'channel_title': channel_title,
                        'subscribers': channel_stats.get('subscriberCount', 0),
                        'total_videos': channel_stats.get('videoCount', 0),
                        'total_views': channel_stats.get('viewCount', 0)
                    })
                    
                    # Replace newlines in email body with \n for better CSV export
                    email_body = email_content.get('email_body', '').replace('\n', '\\n')
                    
                    emails_list.append({
                        'channel_id': channel_id,
                        'channel_title': channel_title,
                        'email': channel_email,
                        'email_subject': email_content.get('email_subject', ''),
                        'email_body': email_body
                    })
                except Exception as e:
                    logging.error(f"Error generating email for {channel_title}: {e}")
        
        # Second pass: Add videos from channels with emails
        for video in video_data:
            video_id = video['id']['videoId']
            video_details = api.get_video_details(video_id)
            if not video_details:
                continue
                
            snippet = video_details.get('snippet', {})
            statistics = video_details.get('statistics', {})
            channel_id = snippet.get('channelId', '')
            
            # Only include videos from channels with emails
            if channel_id in channels_with_email:
                videos_list.append({
                    'video_id': video_id,
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'channel_id': channel_id,
                    'views': statistics.get('viewCount', ''),
                    'likes': statistics.get('likeCount', ''),
                    'comments': statistics.get('commentCount', '')
                })
        
        # Save to CSV
        videos_df = pd.DataFrame(videos_list)
        channels_df = pd.DataFrame(channels_list)
        emails_df = pd.DataFrame(emails_list)
        
        videos_csv_path = os.path.join(output_dir, 'youtube_videos.csv')
        channels_csv_path = os.path.join(output_dir, 'youtube_channels.csv')
        emails_csv_path = os.path.join(output_dir, 'youtube_email_content.csv')
        
        # Save with proper handling of newlines and quotes
        videos_df.to_csv(videos_csv_path, index=False, quoting=1)  # QUOTE_ALL
        channels_df.to_csv(channels_csv_path, index=False, quoting=1)
        emails_df.to_csv(emails_csv_path, index=False, quoting=1, escapechar='\\')
        
        # Save to database
        api.save_to_db(videos_df, channels_df, None, emails_df)
        
        logging.info(f"Saved {len(videos_df)} videos to {videos_csv_path}")
        logging.info(f"Saved {len(channels_df)} channels to {channels_csv_path}")
        logging.info(f"Saved {len(emails_df)} emails to {emails_csv_path}")
        logging.info("Analysis completed successfully!")
        
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 