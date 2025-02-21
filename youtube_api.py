import os
from datetime import datetime
import csv
from googleapiclient.discovery import build

# Configuration
API_KEY = "AIzaSyARWIN06r9b64WOSExMea7OoT2Xx6-ce9w"
SEARCH_KEYWORD = "influencer marketing"  # Example keyword
MAX_RESULTS = 50  # Max allowed per API call

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

def process_data(search_items, video_details):
    """
    Combine search results and video details into structured data.
    """
    processed_data = []
    for item, details in zip(search_items, video_details):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        stats = details["statistics"]
        
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
            "url": f"https://youtube.com/watch?v={video_id}"
        })
    return processed_data

def save_to_csv(data, filename_prefix="youtube_videos"):
    """
    Save data to a CSV file with timestamped filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    fieldnames = data[0].keys() if data else []
    
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved data to {filename}")
    return filename

def main():
    # Step 1: Search videos by keyword
    search_items = search_videos_by_keyword(SEARCH_KEYWORD, MAX_RESULTS)
    video_ids = [item["id"]["videoId"] for item in search_items]
    
    # Step 2: Get detailed video stats
    video_details = get_video_details(video_ids)
    
    # Step 3: Process and save data
    processed_data = process_data(search_items, video_details)
    csv_filename = save_to_csv(processed_data)
    
    # (Optional: Add GCP Bucket upload here in next phase)

if __name__ == "__main__":
    main()