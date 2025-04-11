#!/usr/bin/env python3
"""Script to run YouTube video and channel analysis."""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
from datetime import datetime
import yaml
from dotenv import load_dotenv
from youtube_api import YouTubeAPI, YouTubeAPIConfig
import traceback

# Add parent directory to Python path to allow importing youtube_api
sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Run the YouTube channel analysis."""
    start_time = datetime.now()
    print(f"Starting analysis at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize configuration
        config = YouTubeAPIConfig()
        config.validate()
        
        # Initialize API
        api = YouTubeAPI(config)
        
        # Print search query
        print(f"\nUsing search query: {config.search_query}")
        
        # Run analysis
        videos_df, channels_df, transcripts_df, emails_df = api.analyze_channels()
        
        # Save results if we have data
        if len(channels_df) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if config.save_csv:
                channels_df.to_csv(f"{config.output_directory}/youtube_channels.csv", index=False)
                videos_df.to_csv(f"{config.output_directory}/youtube_videos.csv", index=False)
                if len(emails_df) > 0:
                    emails_df.to_csv(f"{config.output_directory}/youtube_email_content.csv", index=False)
            
            if config.save_excel:
                with pd.ExcelWriter(f"{config.output_directory}/youtube_analysis_{timestamp}.xlsx") as writer:
                    channels_df.to_excel(writer, sheet_name="Channels", index=False)
                    videos_df.to_excel(writer, sheet_name="Videos", index=False)
                    if len(emails_df) > 0:
                        emails_df.to_excel(writer, sheet_name="Emails", index=False)
            
            if config.save_json:
                channels_df.to_json(f"{config.output_directory}/youtube_channels_{timestamp}.json", orient="records")
                videos_df.to_json(f"{config.output_directory}/youtube_videos_{timestamp}.json", orient="records")
                if len(emails_df) > 0:
                    emails_df.to_json(f"{config.output_directory}/youtube_emails_{timestamp}.json", orient="records")
            
            print(f"\nResults saved to {config.output_directory}/")
        
        # Print analysis summary
        print("\nAnalysis Summary:")
        print(f"Total videos found: {len(videos_df)}")
        print(f"Total channels found: {len(channels_df)}")
        print(f"Total emails generated: {len(emails_df)}")
        
    except Exception as e:
        print(f"Error analyzing channels: {str(e)}")
        traceback.print_exc()
    
    end_time = datetime.now()
    print(f"\nAnalysis completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 