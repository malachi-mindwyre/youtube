"""Combined YouTube analysis script."""

from typing import Tuple, List, Dict, Any
import pandas as pd
import os
from datetime import datetime
from executables.youtube_api import YouTubeAPI, YouTubeAPIConfig

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
    """Process channel details into a DataFrame."""
    processed_data = []
    
    for channel in channel_details:
        snippet = channel["snippet"]
        stats = channel["statistics"]
        
        processed_data.append({
            "channel_id": channel["id"],
            "channel_title": snippet["title"],
            "custom_url": snippet.get("customUrl", ""),
            "creation_date": snippet["publishedAt"],
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "total_videos": int(stats.get("videoCount", 0)),
            "country": snippet.get("country", ""),
            "email": snippet.get("email", ""),
            "description": snippet.get("description", ""),
            "keywords": snippet.get("keywords", ""),
            "channel_url": f"https://www.youtube.com/channel/{channel['id']}",
            "website": snippet.get("customUrl", "")
        })
    
    return pd.DataFrame(processed_data)

def save_to_csv(df: pd.DataFrame, filename: str) -> None:
    """Save DataFrame to CSV file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")

def main() -> pd.DataFrame:
    """Main function to execute combined YouTube video and channel analysis."""
    try:
        # Initialize YouTube API
        config = YouTubeAPIConfig()
        youtube_api = YouTubeAPI(config)
        
        # Step 1: Get videos and their channel information
        search_items = youtube_api.search_videos_by_keyword(
            config.search_keyword,
            config.max_results
        )
        video_ids = [item["id"]["videoId"] for item in search_items]
        video_details = youtube_api.get_video_details(video_ids)
        videos_df = pd.DataFrame(youtube_api.process_data(search_items, video_details))
        
        # Print unique channels found
        unique_channels = videos_df['channel_id'].unique()
        print(f"\nFound {len(unique_channels)} unique channels")
        
        # Step 2: Get detailed channel information
        channel_details = get_channel_details(youtube_api, list(unique_channels))
        channels_df = process_channel_data(channel_details)
        
        # Save data to CSV files
        save_to_csv(videos_df, "youtube_videos")
        save_to_csv(channels_df, "youtube_channels")
        
        return videos_df
        
    except Exception as e:
        raise RuntimeError(f"Failed to execute combined analysis: {str(e)}")

if __name__ == "__main__":
    try:
        df = main()
        
        # Display sample data
        print("\nVideo Data Sample:")
        print(df[['channel_title', 'title', 'views_per_hour']].head())
        
    except Exception as e:
        print(f"Error: {str(e)}")