# Import both scripts
from youtube_api import main as get_videos  # your first script
from channel_analysis import main as get_channels  # your second script

def main():
    # Step 1: Get videos and their channel information
    videos_df = get_videos()
    
    # Print unique channels found
    unique_channels = videos_df['channel_id'].unique()
    print(f"\nFound {len(unique_channels)} unique channels")
    
    # Step 2: Get detailed channel information
    channels_df = get_channels(videos_df)
    
    return videos_df, channels_df

if __name__ == "__main__":
    videos_df, channels_df = main()
    
    # Now you have both DataFrames available for analysis
    print("\nVideo Data Sample:")
    print(videos_df[['channel_title', 'title', 'views_per_hour']].head())
    
    print("\nChannel Data Sample:")
    print(channels_df[['channel_title', 'subscribers', 'email']].head())