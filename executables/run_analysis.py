#!/usr/bin/env python3
"""Script to run YouTube video and channel analysis."""

import os
import sys
import yaml
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from executables.youtube_api import YouTubeAPI

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
        
        # Collect video and channel details
        videos_list: List[dict] = []
        channels_list: List[dict] = []
        
        for video in video_data:
            video_id = video['id']['videoId']
            logging.info(f"Processing video: {video_id}")
            
            # Get video details
            video_details = api.get_video_details(video_id)
            if not video_details:
                continue
            snippet = video_details.get('snippet', {})
            statistics = video_details.get('statistics', {})
            videos_list.append({
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'channel_id': snippet.get('channelId', ''),
                'views': statistics.get('viewCount', ''),
                'likes': statistics.get('likeCount', ''),
                'comments': statistics.get('commentCount', '')
            })
            # Get channel details
            channel_id = snippet.get('channelId', '')
            channel_details = api.get_channel_details(channel_id)
            if channel_details:
                channel_snippet = channel_details.get('snippet', {})
                channel_stats = channel_details.get('statistics', {})
                channels_list.append({
                    'channel_id': channel_id,
                    'channel_title': channel_snippet.get('title', ''),
                    'subscribers': channel_stats.get('subscriberCount', ''),
                    'total_videos': channel_stats.get('videoCount', ''),
                    'total_views': channel_stats.get('viewCount', '')
                })
                logging.info(f"Found channel: {channel_snippet.get('title', '')}")
        # Save to CSV
        videos_df = pd.DataFrame(videos_list)
        channels_df = pd.DataFrame(channels_list)
        videos_csv_path = os.path.join(output_dir, 'youtube_videos.csv')
        channels_csv_path = os.path.join(output_dir, 'youtube_channels.csv')
        videos_df.to_csv(videos_csv_path, index=False)
        channels_df.to_csv(channels_csv_path, index=False)
        logging.info(f"Saved {len(videos_df)} videos to {videos_csv_path}")
        logging.info(f"Saved {len(channels_df)} channels to {channels_csv_path}")
        logging.info("Analysis completed successfully!")
        
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 