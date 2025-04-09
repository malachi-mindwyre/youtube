#!/usr/bin/env python3
"""
YouTube Analysis Tool - Simple Runner

This script provides an easy way to run the YouTube analysis tool.
Just run this script to execute the analysis and see the results.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.abspath('..'))

# Import the analysis script
from executables.combined_youtube_analysis_script import main

def run_analysis():
    """Run the YouTube analysis and display results."""
    print("🚀 Starting YouTube Analysis...")
    
    try:
        # Run the analysis
        df = main()
        
        # Display summary
        print("\n✅ Analysis Complete!")
        print(f"\n📊 Found {len(df)} videos meeting your criteria")
        
        # Show top 5 videos by views per hour
        print("\n📈 Top 5 Videos by Views per Hour:")
        top_videos = df.nlargest(5, 'views_per_hour')[['title', 'views_per_hour', 'likes_per_hour', 'comments_per_hour']]
        print("\n", top_videos.to_string())
        
        # Show basic statistics
        print("\n📊 Summary Statistics:")
        stats = df[['views_per_hour', 'likes_per_hour', 'comments_per_hour']].describe()
        print("\n", stats.to_string())
        
        # Check for saved files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        videos_file = f'youtube_videos_{timestamp}.csv'
        channels_file = f'youtube_channels_{timestamp}.csv'
        
        if os.path.exists(videos_file) and os.path.exists(channels_file):
            print(f"\n💾 Results saved to:\n- {videos_file}\n- {channels_file}")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    run_analysis() 