"""Data processing functions for YouTube API analysis."""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pytz
import logging
from executables.utils import has_email, extract_email, calculate_hours_since_published

def merge_dataframes(existing_df: pd.DataFrame, new_df: pd.DataFrame, key: str, 
                    update_all: bool = False) -> pd.DataFrame:
    """Merge existing and new data, intelligently handling updates.
    
    Args:
        existing_df: Existing DataFrame
        new_df: New DataFrame
        key: Primary key for merging ('video_id' or 'channel_id')
        update_all: Whether to update all records or check for significant changes
        
    Returns:
        pd.DataFrame: Merged DataFrame
    """
    # Add last_updated field to new data if not present
    if 'last_updated' not in new_df.columns:
        new_df['last_updated'] = datetime.now(pytz.UTC).isoformat()
        
    if existing_df.empty:
        return new_df
        
    # For videos and transcripts, always update with new data
    if update_all or key == 'video_id':
        return pd.concat([existing_df, new_df]).drop_duplicates(subset=[key], keep='last')
        
    # For channels, check each record for significant changes
    merged_data = []
    existing_channels = existing_df.set_index(key).to_dict('index')
    new_channels = new_df.set_index(key).to_dict('index')
    
    # Process all channels
    all_channels = set(existing_channels.keys()) | set(new_channels.keys())
    for channel_id in all_channels:
        if channel_id in existing_channels and channel_id in new_channels:
            existing = pd.Series(existing_channels[channel_id])
            new = pd.Series(new_channels[channel_id])
            if should_update_channel(existing, new):
                merged_data.append(new_channels[channel_id])
            else:
                merged_data.append(existing_channels[channel_id])
        elif channel_id in new_channels:
            merged_data.append(new_channels[channel_id])
        else:
            merged_data.append(existing_channels[channel_id])
            
    return pd.DataFrame(merged_data)

def should_update_channel(existing: pd.Series, new: pd.Series, threshold: float = 0.1) -> bool:
    """Determine if channel data should be updated based on significant changes.
    
    Args:
        existing: Existing channel data
        new: New channel data
        threshold: Minimum relative change to consider significant (default 10%)
        
    Returns:
        bool: True if update needed, False otherwise
    """
    # Always update if email changed from empty to non-empty
    if not existing['email'] and new['email']:
        return True
        
    # Check for significant changes in numeric values
    for field in ['subscribers', 'total_views', 'total_videos']:
        if existing[field] == 0:
            if new[field] > 0:
                return True
        else:
            relative_change = abs(new[field] - existing[field]) / existing[field]
            if relative_change > threshold:
                return True
                
    # Check for changes in text fields
    for field in ['channel_title', 'custom_url', 'country']:
        if existing[field] != new[field]:
            return True
            
    return False

def process_video_data(video_data: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Process raw video data into structured DataFrames."""
    # Initialize empty lists for each data type
    videos = []
    channels = []
    transcripts = []
    emails = []
    
    for video in video_data:
        # Process video data
        video_info = {
            'video_id': video['id']['videoId'],
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'published_at': video['snippet']['publishedAt'],
            'channel_id': video['snippet']['channelId'],
            'channel_title': video['snippet']['channelTitle'],
            'hours_since_published': calculate_hours_since_published(video['snippet']['publishedAt'])
        }
        videos.append(video_info)
        
        # Process channel data
        channel_info = {
            'channel_id': video['snippet']['channelId'],
            'channel_title': video['snippet']['channelTitle'],
            'subscribers': video['statistics']['subscriberCount'],
            'total_videos': video['statistics']['videoCount'],
            'total_views': video['statistics']['viewCount']
        }
        channels.append(channel_info)
        
        # Process transcript data
        if 'transcript' in video:
            transcript_info = {
                'video_id': video['id']['videoId'],
                'transcript': video['transcript'],
                'word_count': len(video['transcript'].split())
            }
            transcripts.append(transcript_info)
        
        # Process email data
        if has_email(video['snippet']['description']):
            email_info = {
                'channel_id': video['snippet']['channelId'],
                'email': extract_email(video['snippet']['description'])
            }
            emails.append(email_info)
    
    # Convert lists to DataFrames
    videos_df = pd.DataFrame(videos)
    channels_df = pd.DataFrame(channels)
    transcripts_df = pd.DataFrame(transcripts)
    emails_df = pd.DataFrame(emails)
    
    return videos_df, channels_df, transcripts_df, emails_df 