"""Combined YouTube analysis script."""

from typing import Tuple, List, Dict, Any
import pandas as pd
import os
import yaml
import re
from datetime import datetime
from executables.youtube_api import YouTubeAPI, YouTubeAPIConfig

def load_config() -> dict:
    """Load configuration from config.yaml file.
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}")

def get_channel_details(youtube_api: YouTubeAPI, channel_ids: List[str]) -> List[Dict[str, Any]]:
    """Get detailed information for a list of channels."""
    try:
        channels_response = youtube_api.youtube.channels().list(
            part="snippet,statistics",
            id=",".join(channel_ids)
        ).execute()
        return channels_response.get("items", [])
    except Exception as e:
        raise RuntimeError(f"Failed to get channel details: {str(e)}")

def process_channel_data(channel_details: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process channel details into a DataFrame and extract emails."""
    processed_data = []
    channels_with_email = set()
    
    for channel in channel_details:
        snippet = channel["snippet"]
        stats = channel["statistics"]
        description = snippet.get("description", "")
        
        # Extract email from description
        email = ""
        if has_email(description):
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)
            if email_match:
                email = email_match.group(0)
                channels_with_email.add(channel["id"])
        
        processed_data.append({
            "channel_id": channel["id"],
            "channel_title": snippet["title"],
            "custom_url": snippet.get("customUrl", ""),
            "creation_date": snippet["publishedAt"],
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "total_videos": int(stats.get("videoCount", 0)),
            "country": snippet.get("country", ""),
            "email": email,
            "channel_url": f"https://www.youtube.com/channel/{channel['id']}"
        })
    
    df = pd.DataFrame(processed_data)
    return df, channels_with_email

def save_data(df: pd.DataFrame, prefix: str, config: dict) -> str:
    """Save DataFrame to file based on configuration."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = config.get('output', {}).get('output_directory', 'results')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if config.get('output', {}).get('save_excel', False):
        filename = f"{prefix}_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False)
    else:
        filename = f"{prefix}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
    
    return filepath

def has_email(text: str) -> bool:
    """Check if text contains an email address."""
    if not text:
        return False
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.search(email_pattern, text))

def main() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Main function to execute combined YouTube video and channel analysis."""
    try:
        # Load configuration
        yaml_config = load_config()
        
        # Initialize YouTube API
        api_config = YouTubeAPIConfig()
        youtube_api = YouTubeAPI(api_config)
        
        # Step 1: Get videos and their channel information
        search_items = youtube_api.search_videos_by_keyword(
            api_config.search_keyword,
            api_config.max_results
        )
        video_ids = [item["id"]["videoId"] for item in search_items]
        video_details = youtube_api.get_video_details(video_ids)
        videos_df = pd.DataFrame(youtube_api.process_data(search_items, video_details))
        
        # Print unique channels found
        unique_channels = videos_df['channel_id'].unique()
        print(f"\nFound {len(unique_channels)} unique channels")
        
        # Step 2: Get detailed channel information and process
        channel_details = get_channel_details(youtube_api, list(unique_channels))
        channels_df, channels_with_email = process_channel_data(channel_details)
        
        # Step 3: Filter based on email requirement
        if yaml_config.get('filters', {}).get('require_email_found', True):
            # Filter channels to only those with emails
            channels_df = channels_df[channels_df['email'] != ""]
            # Filter videos to only those from channels with emails
            videos_df = videos_df[videos_df['channel_id'].isin(channels_with_email)]
            
            print(f"\nAfter email filtering: {len(channels_df)} channels with emails found")
            print(f"Videos from these channels: {len(videos_df)}")
        
        # Save results based on configuration
        if yaml_config.get('output', {}).get('save_csv', False) or yaml_config.get('output', {}).get('save_excel', False):
            videos_file = save_data(videos_df, "youtube_videos", yaml_config)
            channels_file = save_data(channels_df, "youtube_channels", yaml_config)
            print(f"Results saved to:\n- {videos_file}\n- {channels_file}")
        
        return videos_df, channels_df
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        videos_df, channels_df = main()
        
        # Display sample data
        print("\nChannels with Emails:")
        print(channels_df[['channel_title', 'email']].head())
        
    except Exception as e:
        print(f"Error: {str(e)}")