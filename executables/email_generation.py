"""Email generation functions for YouTube API analysis."""

from typing import Dict, List, Optional
from datetime import datetime
import pytz
import logging
import os

def generate_email(video_data: Dict, channel_data: Dict, transcript_status: str) -> Dict:
    """Generate personalized email using template.
    
    Args:
        video_data: Dictionary containing video information
        channel_data: Dictionary containing channel information
        transcript_status: Status of transcript retrieval
        
    Returns:
        Dictionary containing email content and metadata
    """
    # Load email template
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_templates', 'affiliate_marketing_template.txt')
    with open(template_path, 'r') as f:
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
        'generated_at': datetime.now(pytz.UTC).isoformat(),
        'transcript_status': transcript_status,
        'email_content': email_content
    }
    
    return email_record

def generate_personalized_content(video_title: str, video_description: str, 
                               key_moments: List[Dict], channel_name: str) -> Dict:
    """Generate personalized email content and affiliate comment.
    
    Args:
        video_title: Title of the video
        video_description: Description of the video
        key_moments: List of key moments from the transcript
        channel_name: Name of the channel
        
    Returns:
        Dictionary containing personalized content and affiliate comment
    """
    # Extract topics from title and description
    topics = extract_topics(video_title, video_description)
    
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

def extract_topics(title: str, description: str) -> List[str]:
    """Extract main topics from title and description.
    
    Args:
        title: Video title
        description: Video description
        
    Returns:
        List of main topics
    """
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

def generate_email_content(channel_data: Dict) -> Dict:
    """Generate personalized email content for a YouTube channel.
    
    Args:
        channel_data: Dictionary containing channel information
        
    Returns:
        Dictionary with email subject and body
    """
    try:
        channel_title = channel_data.get('channel_title', '')
        subscribers = channel_data.get('subscribers', 0)
        total_videos = channel_data.get('total_videos', 0)
        total_views = channel_data.get('total_views', 0)
        
        # Convert string values to integers if needed
        if isinstance(subscribers, str) and subscribers.isdigit():
            subscribers = int(subscribers)
        if isinstance(total_videos, str) and total_videos.isdigit():
            total_videos = int(total_videos)
        if isinstance(total_views, str) and total_views.isdigit():
            total_views = int(total_views)
        
        # Generate personalized email content
        subject = f"Collaboration Opportunity with {channel_title}"
        
        body = f"""Hi {channel_title},

I've been following your channel and really appreciate your content. Your {total_videos} videos have reached {total_views} views, and you've built an engaged community of {subscribers} subscribers.

I'd love to explore potential collaboration opportunities that could benefit both our audiences.

Would you be open to discussing this further?

Best regards,
[Your Name]"""
        
        return {
            'channel_id': channel_data.get('channel_id'),
            'channel_title': channel_title,
            'email_subject': subject,
            'email_body': body
        }
        
    except Exception as e:
        logging.error(f"Error generating email content for channel {channel_data.get('channel_title', 'Unknown')}: {e}")
        return {} 