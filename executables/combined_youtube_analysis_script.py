from typing import Tuple
import pandas as pd
from youtube_api import main as get_videos
from channel_analysis import main as get_channels

def main() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Main function to execute combined YouTube video and channel analysis."""
    try:
        # Step 1: Get videos and their channel information
        videos_df = get_videos()
        assert isinstance(videos_df, pd.DataFrame), "Video analysis must return a DataFrame"
        assert 'channel_id' in videos_df.columns, "Video DataFrame must contain 'channel_id' column"
        
        # Print unique channels found
        unique_channels = videos_df['channel_id'].unique()
        print(f"\nFound {len(unique_channels)} unique channels")
        
        # Step 2: Get detailed channel information
        channels_df = get_channels(videos_df)
        assert isinstance(channels_df, pd.DataFrame), "Channel analysis must return a DataFrame"
        
        return videos_df, channels_df
        
    except Exception as e:
        raise RuntimeError(f"Failed to execute combined analysis: {str(e)}")

if __name__ == "__main__":
    try:
        videos_df, channels_df = main()
        
        # Display sample data
        print("\nVideo Data Sample:")
        print(videos_df[['channel_title', 'title', 'views_per_hour']].head())
        
        print("\nChannel Data Sample:")
        print(channels_df[['channel_title', 'subscribers', 'email']].head())
        
    except Exception as e:
        print(f"Error: {str(e)}")