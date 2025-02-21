import os
from datetime import datetime
import pandas as pd
from googleapiclient.discovery import build
import re
import json
from dotenv import load_dotenv

# Configuration
load_dotenv()  

API_KEY = os.getenv("API_KEY") 

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

def extract_email_from_text(text):
    """
    Extract email addresses from text using regex.
    """
    if not text:
        return None
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return ', '.join(emails) if emails else None

def extract_social_links(text):
    """
    Extract social media and other links from text.
    """
    if not text:
        return {}
    
    social_patterns = {
        'instagram': r'(?:instagram\.com|instagr\.am)/([^/\s]+)',
        'twitter': r'(?:twitter\.com|x\.com)/([^/\s]+)',
        'facebook': r'facebook\.com/([^/\s]+)',
        'tiktok': r'tiktok\.com/@([^/\s]+)',
        'linkedin': r'linkedin\.com/(?:in|company)/([^/\s]+)',
        'website': r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?'
    }
    
    links = {}
    for platform, pattern in social_patterns.items():
        matches = re.findall(pattern, text, re.I)
        if matches:
            links[platform] = ', '.join(matches)
    
    return links

def get_channel_details(channel_ids):
    """
    Fetch detailed information about YouTube channels.
    """
    channel_data = []
    
    # Process channels in batches of 50 (API limit)
    for i in range(0, len(channel_ids), 50):
        batch_ids = channel_ids[i:i + 50]
        
        try:
            # Get channel details
            channels_response = youtube.channels().list(
                part="snippet,statistics,brandingSettings",
                id=",".join(batch_ids)
            ).execute()

            for channel in channels_response.get("items", []):
                channel_id = channel["id"]
                snippet = channel["snippet"]
                statistics = channel["statistics"]
                branding = channel.get("brandingSettings", {})
                
                # Get channel's "about" page info
                about_response = youtube.channels().list(
                    part="brandingSettings",
                    id=channel_id
                ).execute()
                
                channel_about = about_response.get("items", [{}])[0].get("brandingSettings", {}).get("channel", {})
                
                # Extract contact information
                description = snippet.get("description", "")
                email = extract_email_from_text(description)
                social_links = extract_social_links(description)
                
                # Get custom URL if available
                custom_url = None
                try:
                    custom_url = f"@{snippet['customUrl']}" if 'customUrl' in snippet else None
                except:
                    pass

                channel_info = {
                    "channel_id": channel_id,
                    "channel_title": snippet.get("title"),
                    "custom_url": custom_url,
                    "creation_date": snippet.get("publishedAt"),
                    "subscribers": statistics.get("subscriberCount"),
                    "total_views": statistics.get("viewCount"),
                    "total_videos": statistics.get("videoCount"),
                    "country": snippet.get("country"),
                    "email": email,
                    "description": description,
                    "keywords": channel_about.get("keywords"),
                    "channel_url": f"https://www.youtube.com/channel/{channel_id}"
                }
                
                # Add social links to channel info
                channel_info.update(social_links)
                
                channel_data.append(channel_info)
                
        except Exception as e:
            print(f"Error processing batch: {e}")
            continue
    
    return channel_data

def process_channels(input_df):
    """
    Process channels from input DataFrame and return detailed channel information.
    """
    # Get unique channel IDs from the input DataFrame
    channel_ids = input_df['channel_id'].unique().tolist()
    
    # Get channel details
    channel_data = get_channel_details(channel_ids)
    
    # Create DataFrame
    df_channels = pd.DataFrame(channel_data)
    
    # Convert numeric columns
    numeric_cols = ['subscribers', 'total_views', 'total_videos']
    for col in numeric_cols:
        df_channels[col] = pd.to_numeric(df_channels[col], errors='coerce')
    
    return df_channels

def main(input_df=None):
    """
    Main function to process channel data.
    Input DataFrame should contain 'channel_id' column.
    """
    if input_df is None or 'channel_id' not in input_df.columns:
        raise ValueError("Input DataFrame required with 'channel_id' column")
    
    # Process channels
    df_channels = process_channels(input_df)
    
    # Display results
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    print("\nChannel Analysis Results:")
    print(f"\nTotal channels analyzed: {len(df_channels)}")
    print("\nFirst few channels:")
    print(df_channels.head())
    
    print("\nChannel Statistics:")
    print(df_channels[['subscribers', 'total_views', 'total_videos']].describe())
    
    # Count channels with contact information
    email_count = df_channels['email'].notna().sum()
    print(f"\nChannels with email addresses: {email_count} ({(email_count/len(df_channels))*100:.1f}%)")
    
    return df_channels

if __name__ == "__main__":
    # If you have the DataFrame from the first script:
    # df_channels = main(df)  # where df is your DataFrame from the first script
    
    # For testing with a single channel ID:
    test_df = pd.DataFrame({'channel_id': ['UC_x5XG1OV2P6uZZ5FSM9Ttw']})  # Google Developers channel
    df_channels = main(test_df)