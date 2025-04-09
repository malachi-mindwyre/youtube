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
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import the analysis script
from executables.combined_youtube_analysis_script import main, load_config

def run_analysis():
    """Run the YouTube analysis and display results."""
    print("🚀 Starting YouTube Analysis...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Run the analysis
        videos_df, channels_df = main()
        
        # Display summary
        print("\n✅ Analysis Complete!")
        print(f"\n📊 Found {len(videos_df)} videos meeting your criteria")
        
        # Show top 5 videos by views per hour
        print("\n📈 Top 5 Videos by Views per Hour:")
        top_videos = videos_df.nlargest(5, 'views_per_hour')[['title', 'views_per_hour', 'likes_per_hour', 'comments_per_hour']]
        print("\n", top_videos.to_string())
        
        # Show basic statistics
        print("\n📊 Summary Statistics:")
        stats = videos_df[['views_per_hour', 'likes_per_hour', 'comments_per_hour']].describe()
        print("\n", stats.to_string())
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    run_analysis()