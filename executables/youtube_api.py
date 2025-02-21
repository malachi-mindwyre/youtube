import os
from datetime import datetime
import pandas as pd
from googleapiclient.discovery import build
from dateutil import parser
import pytz
from dotenv import load_dotenv

load_dotenv()  


API_KEY = os.getenv("API_KEY") 

# Configuration
API_KEY = "AIzaSyARWIN06r9b64WOSExMea7OoT2Xx6-ce9w"
SEARCH_KEYWORD = "influencer marketing"  # Example keyword
MAX_RESULTS = 50  # Max allowed per API call

# Filtering criteria
MIN_VIEWS = 1000  # Minimum total views
MIN_VIEWS_PER_HOUR = 5  # Minimum views per hour
MIN_COMMENTS_PER_HOUR = 0.1  # Minimum comments per hour
MIN_LIKES_PER_HOUR = 1  # Minimum likes per hour

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

def search_videos_by_keyword(keyword, max_results=50):
    """
    Search YouTube videos by keyword and return raw API response.
    """
    search_response = youtube.search().list(
        q=keyword,
        part="snippet",
        type="video",
        maxResults=max_results,
        order="viewCount"  # Prioritize high-view videos
    ).execute()
    return search_response.get("items", [])

def get_video_details(video_ids):
    """
    Fetch detailed statistics for videos using their IDs.
    """
    videos_response = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    ).execute()
    return videos_response.get("items", [])

def calculate_hourly_metrics(published_at, stats):
    """
    Calculate engagement metrics per hour since video publication.
    """
    publish_time = parser.parse(published_at)
    current_time = datetime.now(pytz.UTC)
    hours_since_published = max(1, (current_time - publish_time).total_seconds() / 3600)
    
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))
    
    return {
        "views_per_hour": views / hours_since_published,
        "likes_per_hour": likes / hours_since_published,
        "comments_per_hour": comments / hours_since_published,
        "hours_since_published": hours_since_published
    }

def meets_criteria(metrics, stats):
    """
    Check if video meets minimum engagement criteria.
    """
    return (
        int(stats.get("viewCount", 0)) >= MIN_VIEWS and
        metrics["views_per_hour"] >= MIN_VIEWS_PER_HOUR and
        metrics["comments_per_hour"] >= MIN_COMMENTS_PER_HOUR and
        metrics["likes_per_hour"] >= MIN_LIKES_PER_HOUR
    )

def process_data(search_items, video_details):
    """
    Combine search results and video details into structured data with hourly metrics.
    """
    processed_data = []
    
    for item, details in zip(search_items, video_details):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        stats = details["statistics"]
        
        # Calculate hourly metrics
        hourly_metrics = calculate_hourly_metrics(snippet["publishedAt"], stats)
        
        # Check if video meets criteria
        if not meets_criteria(hourly_metrics, stats):
            continue
            
        processed_data.append({
            "video_id": video_id,
            "title": snippet["title"],
            "description": snippet["description"],
            "published_at": snippet["publishedAt"],
            "channel_id": snippet["channelId"],
            "channel_title": snippet["channelTitle"],
            "views": stats.get("viewCount", 0),
            "likes": stats.get("likeCount", 0),
            "comments": stats.get("commentCount", 0),
            "views_per_hour": round(hourly_metrics["views_per_hour"], 2),
            "likes_per_hour": round(hourly_metrics["likes_per_hour"], 2),
            "comments_per_hour": round(hourly_metrics["comments_per_hour"], 2),
            "hours_since_published": round(hourly_metrics["hours_since_published"], 2),
            "url": f"https://youtube.com/watch?v={video_id}"
        })
    
    return processed_data

def main():
    # Step 1: Search videos by keyword
    search_items = search_videos_by_keyword(SEARCH_KEYWORD, MAX_RESULTS)
    video_ids = [item["id"]["videoId"] for item in search_items]
    
    # Step 2: Get detailed video stats
    video_details = get_video_details(video_ids)
    
    # Step 3: Process data and create DataFrame
    processed_data = process_data(search_items, video_details)
    
    # Create pandas DataFrame
    df = pd.DataFrame(processed_data)
    
    # Display the DataFrame
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_rows', None)     # Show all rows
    pd.set_option('display.width', None)        # Don't wrap wide columns
    pd.set_option('display.max_colwidth', None) # Don't truncate column content
    
    print("\nDataFrame Info:")
    print(df.info())
    
    print("\nFirst few rows of the DataFrame:")
    print(df.head())
    
    # Print some basic statistics
    print("\nBasic statistics for numeric columns:")
    print(df.describe())
    
    return df

if __name__ == "__main__":
    df = main()