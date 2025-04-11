from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import os
import pandas as pd
from googleapiclient.discovery import build
from dateutil import parser
import pytz
from dotenv import load_dotenv
import yaml
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from googleapiclient.errors import HttpError
import traceback

def has_email(text: str) -> bool:
    """Check if text contains an email address.
    
    Args:
        text: Text to check for email addresses
        
    Returns:
        bool: True if email found, False otherwise
    """
    if not text:
        return False
    # Simple email regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.search(email_pattern, text))

class YouTubeAPIConfig:
    """Configuration for YouTube API analysis."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY not found in .env file")
        
        # Search settings
        self.search_query = "day in the life of a software engineer"
        self.max_results = 50
        
        # Filter settings
        self.min_views = 500
        self.max_views = 500000
        self.min_subscribers = 500
        self.max_subscribers = 50000
        self.min_views_per_hour = 0.1
        self.min_comments_per_hour = 0.005
        self.min_likes_per_hour = 0.005
        self.max_hours_since_published = 17520
        self.require_email_found = True
        self.require_transcript = False
        
        # Output settings
        self.output_directory = "results"
        self.save_csv = True
        self.save_excel = False
        self.save_json = False
        
        # Try to load from config file
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                
            # Search settings
            if 'search' in config:
                self.search_query = config['search'].get('keyword', self.search_query)
                self.max_results = config['search'].get('max_results', self.max_results)
            
            # Filter settings
            if 'filters' in config:
                self.min_views = config['filters'].get('min_views', self.min_views)
                self.max_views = config['filters'].get('max_views', self.max_views)
                self.min_subscribers = config['filters'].get('min_subscribers', self.min_subscribers)
                self.max_subscribers = config['filters'].get('max_subscribers', self.max_subscribers)
                self.min_views_per_hour = config['filters'].get('min_views_per_hour', self.min_views_per_hour)
                self.min_comments_per_hour = config['filters'].get('min_comments_per_hour', self.min_comments_per_hour)
                self.min_likes_per_hour = config['filters'].get('min_likes_per_hour', self.min_likes_per_hour)
                self.max_hours_since_published = config['filters'].get('max_hours_since_published', self.max_hours_since_published)
                self.require_email_found = config['filters'].get('require_email_found', self.require_email_found)
                self.require_transcript = config['filters'].get('require_transcript', self.require_transcript)
            
            # Output settings
            if 'output' in config:
                self.output_directory = config['output'].get('directory', self.output_directory)
                self.save_csv = config['output'].get('save_csv', self.save_csv)
                self.save_excel = config['output'].get('save_excel', self.save_excel)
                self.save_json = config['output'].get('save_json', self.save_json)
                
        except Exception as e:
            print(f"Error loading config.yaml: {str(e)}")
            print("Using default configuration values")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)
    
    def validate(self):
        """Validate configuration settings."""
        assert self.api_key, "API key must be set"
        assert self.min_views >= 0, "min_views must be non-negative"
        assert self.max_views > self.min_views, "max_views must be greater than min_views"
        assert self.min_subscribers >= 0, "min_subscribers must be non-negative"
        assert self.max_subscribers > self.min_subscribers, "max_subscribers must be greater than min_subscribers"
        assert self.min_views_per_hour >= 0, "min_views_per_hour must be non-negative"
        assert self.min_comments_per_hour >= 0, "min_comments_per_hour must be non-negative"
        assert self.min_likes_per_hour >= 0, "min_likes_per_hour must be non-negative"
        assert self.max_hours_since_published > 0, "max_hours_since_published must be positive"

class YouTubeAPI:
    """Class for interacting with YouTube Data API."""
    def __init__(self, config: YouTubeAPIConfig) -> None:
        self.config = config
        self.config.validate()
        self.youtube = build("youtube", "v3", developerKey=self.config.api_key)

    def search_videos(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search for videos using the YouTube API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of video search results
        """
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='viewCount'  # Sort by view count to get popular videos
            ).execute()
            
            # Extract video IDs
            video_ids = []
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])
            
            if not video_ids:
                print(f"No videos found for query: {query}")
                return []
            
            # Get video details
            video_details = self.get_video_details(video_ids)
            if not video_details:
                print("No video details found")
                return []
            
            # Combine search results with video details
            results = []
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_id = item['id']['videoId']
                    # Find matching video details
                    video_detail = next((v for v in video_details if v['id'] == video_id), None)
                    if video_detail:
                        result = {
                            'video_id': video_id,
                            'title': item['snippet']['title'],
                            'published_at': item['snippet']['publishedAt'],
                            'channel_id': item['snippet']['channelId'],
                            'channel_title': item['snippet']['channelTitle'],
                            'views': int(video_detail['statistics'].get('viewCount', 0)),
                            'likes': int(video_detail['statistics'].get('likeCount', 0)),
                            'comments': int(video_detail['statistics'].get('commentCount', 0))
                        }
                        results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching videos: {e}")
            return []

    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Get detailed information for a list of videos."""
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids)
            ).execute()
            
            return response.get('items', [])
        except Exception as e:
            print(f"Error getting video details: {e}")
            return []

    def get_channel_details(self, channel_ids: List[str]) -> List[Dict]:
        """Get detailed information for a list of channels."""
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics',
                id=','.join(channel_ids)
            ).execute()
            
            return response.get('items', [])
        except Exception as e:
            print(f"Error getting channel details: {e}")
            return []

    def calculate_hourly_metrics(self, published_at: str, stats: Dict[str, str]) -> Dict[str, float]:
        """Calculate engagement metrics per hour since video publication."""
        assert isinstance(published_at, str), "Published at must be a string"
        assert isinstance(stats, dict), "Stats must be a dictionary"
        
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

    def meets_criteria(self, metrics: Dict[str, float], stats: Dict[str, str]) -> bool:
        """Check if video meets minimum engagement criteria."""
        assert isinstance(metrics, dict), "Metrics must be a dictionary"
        assert isinstance(stats, dict), "Stats must be a dictionary"
        
        views = int(stats.get("viewCount", 0))
        return (
            views >= self.config.min_views and
            metrics["views_per_hour"] >= self.config.min_views_per_hour and
            metrics["comments_per_hour"] >= self.config.min_comments_per_hour and
            metrics["likes_per_hour"] >= self.config.min_likes_per_hour and
            metrics["hours_since_published"] <= self.config.max_hours_since_published
        )

    def get_video_transcript(self, video_id: str) -> Tuple[Optional[str], str]:
        """Fetch transcript for a video if available.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Tuple of (transcript text, status message)
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en'])
            formatter = TextFormatter()
            return formatter.format_transcript(transcript.fetch()), "success"
        except Exception as e:
            if "No transcripts were found" in str(e):
                return None, "no_transcript"
            elif "Subtitles are disabled" in str(e):
                return None, "subtitles_disabled"
            else:
                return None, f"error: {str(e)}"

    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text using regex.
        
        Args:
            text: Text to search for email address
            
        Returns:
            First email address found or None if no email found
        """
        if not text:
            return None
            
        # Common email patterns
        email_patterns = [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Standard email
            r'[a-zA-Z0-9._%+-]+\[at\][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # [at] format
            r'[a-zA-Z0-9._%+-]+\s*\(at\)\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # (at) format
        ]
        
        for pattern in email_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Clean up the email if it's in a special format
                email = matches[0].replace('[at]', '@').replace('(at)', '@').strip()
                return email
                
        return None

    def generate_email(self, video_data: Dict, channel_data: Dict, transcript_status: str) -> Dict:
        """Generate personalized email using template.
        
        Args:
            video_data: Dictionary containing video information
            channel_data: Dictionary containing channel information
            transcript_status: Status of transcript retrieval
            
        Returns:
            Dictionary containing email content and metadata
        """
        # Load email template
        with open('email_templates/affiliate_marketing_template.txt', 'r') as f:
            template = f.read()
        
        # Calculate average views per video
        avg_views = channel_data['total_views'] / channel_data['total_videos'] if channel_data['total_videos'] > 0 else 0
        
        # Extract key topic from video title
        key_topic = video_data['title'].split('|')[0].split('-')[0].strip()
        
        # Fill in template
        email_content = template.format(
            channel_title=channel_data['channel_title'],
            channel_name=channel_data['channel_title'].split()[0],  # First name
            video_title=video_data['title'],
            key_topic=key_topic,
            views=video_data['views'],
            likes=video_data['likes'],
            subscriber_count=channel_data['subscribers'],
            product_name="[Your Product Name]",  # Replace with actual product
            commission_rate="15",  # Replace with actual commission rate
            key_moment="[Key moment from transcript]" if transcript_status == "success" else "content",
            contact_email="[Your Contact Email]",  # Replace with actual email
            your_name="[Your Name]",  # Replace with actual name
            total_videos=channel_data['total_videos'],
            views_per_video=int(avg_views)
        )
        
        # Create email record
        email_record = {
            'video_id': video_data['video_id'],
            'channel_id': channel_data['channel_id'],
            'channel_email': channel_data['email'],
            'generated_at': datetime.now().isoformat(),
            'transcript_status': transcript_status,
            'email_content': email_content
        }
        
        return email_record

    def process_video_data(self, video_data: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Process video data and return DataFrames for videos, channels, transcripts, and emails.
        
        Args:
            video_data: List of video data from search results
            
        Returns:
            Tuple of (videos DataFrame, channels DataFrame, transcripts DataFrame, emails DataFrame)
        """
        if not video_data:
            print("No video data to process")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        print(f"\nProcessing {len(video_data)} videos...")
        
        # Lists to store processed data
        video_records = []
        channel_records = []
        transcript_data = []
        email_records = []
        
        # Track unique channel IDs
        unique_channel_ids = set()
        
        # Process each video
        for i, video in enumerate(video_data, 1):
            print(f"\rProcessing video {i}/{len(video_data)}...", end="")
            
            # Extract video data
            video_id = video['video_id']
            channel_id = video['channel_id']
            
            # Get channel details if not already processed
            if channel_id not in unique_channel_ids:
                print(f"\nFetching details for channel: {video['channel_title']}")
                channel_details = self.get_channel_details([channel_id])
                if channel_details:
                    channel_info = channel_details[0]
                    subscribers = int(channel_info['statistics'].get('subscriberCount', 0))
                    
                    # Skip channels that don't meet subscriber requirements
                    if subscribers < self.config.min_subscribers or subscribers > self.config.max_subscribers:
                        print(f"  Skipping channel: {subscribers} subscribers (outside range)")
                        continue
                        
                    channel_records.append({
                        'channel_id': channel_id,
                        'channel_title': video['channel_title'],
                        'subscribers': subscribers,
                        'total_videos': int(channel_info['statistics'].get('videoCount', 0)),
                        'total_views': int(channel_info['statistics'].get('viewCount', 0)),
                        'email': self.extract_email(channel_info.get('snippet', {}).get('description', ''))
                    })
                    unique_channel_ids.add(channel_id)
                    print(f"  Added channel: {subscribers} subscribers")
            
            # Skip videos that don't meet view requirements
            if video['views'] < self.config.min_views or video['views'] > self.config.max_views:
                print(f"\n  Skipping video: {video['views']} views (outside range)")
                continue
            
            # Get transcript if available
            print(f"\n  Checking transcript for video: {video['title']}")
            transcript, transcript_status = self.get_video_transcript(video_id)
            
            if transcript:
                transcript_data.append({
                    'video_id': video_id,
                    'transcript': transcript,
                    'status': transcript_status
                })
                print(f"  Found transcript: {transcript_status}")
            
            # Calculate time-based metrics
            published_at = datetime.strptime(video['published_at'], '%Y-%m-%dT%H:%M:%SZ')
            hours_since_published = (datetime.utcnow() - published_at).total_seconds() / 3600
            
            # Skip videos that are too old
            if hours_since_published > self.config.max_hours_since_published:
                print(f"\n  Skipping video: {hours_since_published:.1f} hours old (too old)")
                continue
            
            # Calculate hourly metrics
            views_per_hour = video['views'] / hours_since_published if hours_since_published > 0 else 0
            likes_per_hour = video['likes'] / hours_since_published if hours_since_published > 0 else 0
            comments_per_hour = video['comments'] / hours_since_published if hours_since_published > 0 else 0
            
            # Skip videos that don't meet hourly metrics requirements
            if (views_per_hour < self.config.min_views_per_hour or
                likes_per_hour < self.config.min_likes_per_hour or
                comments_per_hour < self.config.min_comments_per_hour):
                print(f"\n  Skipping video: Low engagement (views/hour: {views_per_hour:.1f})")
                continue
            
            # Add video record
            video_records.append({
                'video_id': video_id,
                'title': video['title'],
                'published_at': published_at,
                'channel_id': channel_id,
                'channel_title': video['channel_title'],
                'views': video['views'],
                'likes': video['likes'],
                'comments': video['comments'],
                'views_per_hour': views_per_hour,
                'likes_per_hour': likes_per_hour,
                'comments_per_hour': comments_per_hour,
                'hours_since_published': hours_since_published,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'has_transcript': bool(transcript),
                'transcript_status': transcript_status
            })
            print(f"  Added video: {video['views']} views, {views_per_hour:.1f} views/hour")
            
            # Generate email if channel has email
            if channel_id in [c['channel_id'] for c in channel_records if c['email']]:
                channel_info = next(c for c in channel_records if c['channel_id'] == channel_id)
                email_record = self.generate_email(
                    video_records[-1],
                    channel_info,
                    transcript_status
                )
                email_records.append(email_record)
                print(f"  Generated email for: {channel_info['email']}")
        
        print("\n")  # New line after progress indicator
        
        # Create DataFrames
        videos_df = pd.DataFrame(video_records) if video_records else pd.DataFrame()
        channels_df = pd.DataFrame(channel_records) if channel_records else pd.DataFrame()
        transcripts_df = pd.DataFrame(transcript_data) if transcript_data else pd.DataFrame()
        emails_df = pd.DataFrame(email_records) if email_records else pd.DataFrame()
        
        # Filter channels based on email presence if required
        if self.config.require_email_found:
            channels_df = channels_df[channels_df['email'].notna()]
            if len(channels_df) == 0:
                print("No channels found with email addresses")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            videos_df = videos_df[videos_df['channel_id'].isin(channels_df['channel_id'])]
        
        # Print summary
        print(f"\nFound {len(unique_channel_ids)} unique channels")
        print(f"Found {len(channels_df)} channels with emails")
        print(f"Found {len(videos_df)} videos from channels with emails")
        print(f"Found {len(transcript_data)} transcripts")
        print(f"Generated {len(email_records)} emails")
        
        # Print transcript status summary
        if len(videos_df) > 0:
            transcript_status_counts = videos_df['transcript_status'].value_counts()
            print("\nTranscript Status Summary:")
            for status, count in transcript_status_counts.items():
                print(f"- {status}: {count}")
        
        return videos_df, channels_df, transcripts_df, emails_df

    def extract_key_moments(self, video_id: str) -> List[Dict]:
        """Extract key moments from video for personalization."""
        try:
            transcript, _ = self.get_video_transcript(video_id)
            if not transcript:
                return []
            
            # Extract key moments (e.g., specific quotes, topics discussed)
            key_moments = []
            for entry in transcript:
                text = entry['text'].lower()
                # Look for specific patterns that indicate important moments
                if any(keyword in text for keyword in ['amazing', 'incredible', 'important', 'key', 'main']):
                    key_moments.append({
                        'text': entry['text'],
                        'start': entry['start']
                    })
            
            return key_moments[:3]  # Return top 3 key moments
        except Exception as e:
            print(f"Error extracting key moments for video {video_id}: {e}")
            return []

    def generate_personalized_content(self, video_title: str, video_description: str, 
                                   key_moments: List[Dict], channel_name: str) -> Dict:
        """Generate personalized email content and affiliate comment."""
        # Extract topics from title and description
        topics = self.extract_topics(video_title, video_description)
        
        # Generate personalized email content
        personalized = f"""Hi {channel_name},

I recently watched your video "{video_title}" and was really impressed by your content. Specifically, I loved how you discussed {topics[0]} and {topics[1]}. 

The moment where you said "{key_moments[0]['text'] if key_moments else 'something insightful'}" really resonated with me. It's clear you have a deep understanding of the subject.

I'd love to collaborate with you on promoting our product that aligns perfectly with your content. We can provide you with an affiliate link and a ready-to-use comment to pin on your video.

Would you be interested in discussing this opportunity?

Best regards,
[Your Name]"""
        
        # Generate affiliate comment
        affiliate_comment = f"""Thanks for watching! If you found this video helpful, check out [Product Name] - it's helped me [specific benefit]. Use my affiliate link: [Affiliate Link]

Don't forget to watch my other video on [related topic]: [Video Link]"""
        
        return {
            'personalized': personalized,
            'affiliate_comment': affiliate_comment
        }

    def extract_topics(self, title: str, description: str) -> List[str]:
        """Extract main topics from title and description."""
        # Simple topic extraction - can be enhanced with NLP
        text = f"{title} {description}".lower()
        topics = []
        
        # Look for common topic indicators
        if 'marketing' in text:
            topics.append('marketing strategies')
        if 'business' in text:
            topics.append('business growth')
        if 'social media' in text:
            topics.append('social media marketing')
        if 'content' in text:
            topics.append('content creation')
        if 'brand' in text:
            topics.append('brand building')
        
        return topics[:2] if topics else ['your expertise', 'your insights']

    def process_channel_data(self, channel_details: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, set]:
        """Process channel data into structured format.
        
        Returns:
            Tuple containing:
            - DataFrame with channel data
            - Set of channel IDs that have email addresses
        """
        processed_data = []
        channels_with_email = set()
        
        for channel in channel_details:
            snippet = channel["snippet"]
            stats = channel["statistics"]
            
            # Extract email from description
            description = snippet.get("description", "")
            email = ""
            if has_email(description):
                email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)[0]
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
                "channel_url": f"https://www.youtube.com/channel/{channel['id']}",
                "last_updated": datetime.now(pytz.UTC).isoformat()
            })
        
        return pd.DataFrame(processed_data), channels_with_email

    def should_update_channel(self, existing: pd.Series, new: pd.Series, threshold: float = 0.1) -> bool:
        """Determine if channel data should be updated based on significant changes.
        
        Args:
            existing: Existing channel data
            new: New channel data
            threshold: Minimum relative change to consider significant (default 10%)
            
        Returns:
            bool: True if update needed, False otherwise
        """
        # Always update if email changed from empty to non-empty
        if not existing['email'] and new['email']:
            return True
            
        # Check for significant changes in numeric values
        for field in ['subscribers', 'total_views', 'total_videos']:
            if existing[field] == 0:
                if new[field] > 0:
                    return True
            else:
                relative_change = abs(new[field] - existing[field]) / existing[field]
                if relative_change > threshold:
                    return True
                    
        # Check for changes in text fields
        for field in ['channel_title', 'custom_url', 'country']:
            if existing[field] != new[field]:
                return True
                
        return False

    def merge_dataframes(self, existing_df: pd.DataFrame, new_df: pd.DataFrame, key: str, 
                        update_all: bool = False) -> pd.DataFrame:
        """Merge existing and new data, intelligently handling updates.
        
        Args:
            existing_df: Existing DataFrame
            new_df: New DataFrame
            key: Primary key for merging ('video_id' or 'channel_id')
            update_all: Whether to update all records or check for significant changes
            
        Returns:
            pd.DataFrame: Merged DataFrame
        """
        # Add last_updated field to new data if not present
        if 'last_updated' not in new_df.columns:
            new_df['last_updated'] = datetime.now(pytz.UTC).isoformat()
            
        if existing_df.empty:
            return new_df
            
        # For videos and transcripts, always update with new data
        if update_all or key == 'video_id':
            return pd.concat([existing_df, new_df]).drop_duplicates(subset=[key], keep='last')
            
        # For channels, check each record for significant changes
        merged_data = []
        existing_channels = existing_df.set_index(key).to_dict('index')
        new_channels = new_df.set_index(key).to_dict('index')
        
        # Process all channels
        all_channels = set(existing_channels.keys()) | set(new_channels.keys())
        for channel_id in all_channels:
            if channel_id in existing_channels and channel_id in new_channels:
                existing = pd.Series(existing_channels[channel_id])
                new = pd.Series(new_channels[channel_id])
                if self.should_update_channel(existing, new):
                    merged_data.append(new_channels[channel_id])
                else:
                    merged_data.append(existing_channels[channel_id])
            elif channel_id in new_channels:
                merged_data.append(new_channels[channel_id])
            else:
                merged_data.append(existing_channels[channel_id])
                
        return pd.DataFrame(merged_data)

    def save_results(self, channels: List[Dict], videos: List[Dict], email_content: List[Dict]) -> None:
        """Save results to CSV and/or Excel files.
        
        Args:
            channels: List of channel data dictionaries
            videos: List of video data dictionaries
            email_content: List of email content dictionaries
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.config.output_directory, exist_ok=True)
        
        # Define file paths with fixed names
        channels_file = os.path.join(self.config.output_directory, 'youtube_channels.csv')
        videos_file = os.path.join(self.config.output_directory, 'youtube_videos.csv')
        email_file = os.path.join(self.config.output_directory, 'youtube_email_content.csv')
        excel_file = os.path.join(self.config.output_directory, 'youtube_analysis.xlsx')
        
        # Convert data to DataFrames
        df_channels = pd.DataFrame(channels) if channels else pd.DataFrame()
        df_videos = pd.DataFrame(videos) if videos else pd.DataFrame()
        df_email = pd.DataFrame(email_content) if email_content else pd.DataFrame()
        
        # Add last_updated timestamp if not present
        current_time = datetime.now(pytz.UTC).isoformat()
        for df in [df_channels, df_videos, df_email]:
            if not df.empty and 'last_updated' not in df.columns:
                df['last_updated'] = current_time
        
        # Load existing data if files exist
        if os.path.exists(channels_file):
            existing_channels = pd.read_csv(channels_file)
            df_channels = self.merge_dataframes(existing_channels, df_channels, 'channel_id')
        
        if os.path.exists(videos_file):
            existing_videos = pd.read_csv(videos_file)
            df_videos = self.merge_dataframes(existing_videos, df_videos, 'video_id', update_all=True)
        
        if os.path.exists(email_file):
            existing_email = pd.read_csv(email_file)
            df_email = self.merge_dataframes(existing_email, df_email, 'channel_id')
        
        # Save to CSV if enabled
        if self.config.save_csv:
            if not df_channels.empty:
                df_channels.to_csv(channels_file, index=False)
                print(f"Channel data saved to {channels_file}")
            
            if not df_videos.empty:
                df_videos.to_csv(videos_file, index=False)
                print(f"Video data saved to {videos_file}")
            
            if not df_email.empty:
                df_email.to_csv(email_file, index=False)
                print(f"Email content saved to {email_file}")
        
        # Save to Excel if enabled
        if self.config.save_excel:
            try:
                # Create Excel file with all sheets
                with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
                    if not df_channels.empty:
                        df_channels.to_excel(writer, sheet_name='Channels', index=False)
                    if not df_videos.empty:
                        df_videos.to_excel(writer, sheet_name='Videos', index=False)
                    if not df_email.empty:
                        df_email.to_excel(writer, sheet_name='Email Content', index=False)
                print(f"All data saved to {excel_file}")
            except Exception as e:
                print(f"Error saving Excel file: {e}")

    def analyze(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Run complete YouTube analysis."""
        # Search for videos
        video_data = self.search_videos(self.config.search_query, self.config.max_results)
        if not video_data:
            raise ValueError("No videos found matching criteria")
        
        # Process video data and extract key details
        videos_df, channels_df, transcripts_df, emails_df = self.process_video_data(video_data)
        
        # Save results
        if videos_df.shape[0] > 0 or channels_df.shape[0] > 0 or emails_df.shape[0] > 0:
            self.save_results(
                channels=channels_df.to_dict('records'),
                videos=videos_df.to_dict('records'),
                email_content=emails_df.to_dict('records')
            )
        
        return videos_df, channels_df, emails_df

    def calculate_hours_since_published(self, published_at: str) -> float:
        """Calculate hours since video was published.
        
        Args:
            published_at: ISO format timestamp string
            
        Returns:
            Hours since publication as float
        """
        try:
            publish_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            current_time = datetime.now(pytz.UTC)
            time_diff = current_time - publish_time
            return time_diff.total_seconds() / 3600  # Convert to hours
        except Exception as e:
            print(f"Error calculating hours since published: {e}")
            return 0.0

    def analyze_channels(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Analyze YouTube channels based on search results.
        
        Returns:
            Tuple of (videos DataFrame, channels DataFrame, transcripts DataFrame, emails DataFrame)
        """
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=self.config.search_query,
                type="video",
                part="id,snippet",
                maxResults=self.config.max_results,
                order="date"  # Get recent videos first
            ).execute()
            
            if not search_response.get('items'):
                print("No videos found matching search criteria")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
            # Extract video IDs and get video details
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get video details in batches of 50 (API limit)
            video_details = {}
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                response = self.youtube.videos().list(
                    part="statistics,contentDetails",
                    id=",".join(batch_ids)
                ).execute()
                
                for item in response.get('items', []):
                    video_details[item['id']] = item
            
            if not video_details:
                print("No video details found")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
            # Process video data
            video_data = []
            for item in search_response['items']:
                video_id = item['id']['videoId']
                if video_id in video_details:
                    details = video_details[video_id]
                    video_data.append({
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'channel_id': item['snippet']['channelId'],
                        'channel_title': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'views': int(details['statistics'].get('viewCount', 0)),
                        'likes': int(details['statistics'].get('likeCount', 0)),
                        'comments': int(details['statistics'].get('commentCount', 0))
                    })
            
            if not video_data:
                print("No videos found matching criteria")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
            print(f"Found {len(video_data)} videos matching search criteria")
            
            # Process video data and return DataFrames
            return self.process_video_data(video_data)
            
        except HttpError as e:
            print(f"YouTube API error: {e.resp.status} - {e.content}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            print(f"Error analyzing channels: {str(e)}")
            traceback.print_exc()
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def main() -> pd.DataFrame:
    """Main function to execute the YouTube video analysis."""
    config = YouTubeAPIConfig(
        api_key="YOUR_API_KEY",
        search_query="Your Search Query",
        max_results=50,
        save_csv=True,
        save_excel=True,
        save_json=True
    )
    youtube_api = YouTubeAPI(config)
    
    try:
        # Step 1: Search videos by keyword
        search_items = youtube_api.search_videos(
            config.search_query, 
            config.max_results
        )
        video_ids = [item["id"]["videoId"] for item in search_items]
        
        # Step 2: Get detailed video stats
        video_details = youtube_api.get_video_details(video_ids)
        
        # Step 3: Process data and create DataFrame
        processed_data, transcripts_data = youtube_api.process_video_data(search_items)
        
        # Create pandas DataFrame
        videos_df = pd.DataFrame(processed_data)
        transcripts_df = pd.DataFrame(transcripts_data)
        
        # Configure pandas display options
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print("\nDataFrame Info:")
        print(videos_df.info())
        print(transcripts_df.info())
        
        print("\nFirst few rows of the DataFrame:")
        print(videos_df.head())
        print(transcripts_df.head())
        
        print("\nBasic statistics for numeric columns:")
        print(videos_df.describe())
        print(transcripts_df.describe())
        
        return videos_df, transcripts_df
        
    except Exception as e:
        raise RuntimeError(f"Failed to execute YouTube analysis: {str(e)}")

if __name__ == "__main__":
    videos_df, transcripts_df = main()