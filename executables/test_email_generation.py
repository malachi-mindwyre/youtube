"""Test script for email generation functionality."""

from email_generation import generate_email, generate_personalized_content, generate_email_content
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    """Run test cases for email generation functions."""
    # Sample video data
    video_data = {
        'video_id': 'test123',
        'title': 'How to Grow Your Business with Social Media Marketing',
        'views': 10000,
        'likes': 500
    }
    
    # Sample channel data
    channel_data = {
        'channel_id': 'channel123',
        'channel_title': 'John Smith',
        'email': 'john@example.com',
        'subscribers': 50000,
        'total_videos': 100,
        'total_views': 1000000
    }
    
    # Test generate_email
    try:
        email_record = generate_email(video_data, channel_data, "success")
        print("\nGenerated Email Record:")
        print(f"Video ID: {email_record['video_id']}")
        print(f"Channel ID: {email_record['channel_id']}")
        print(f"Generated At: {email_record['generated_at']}")
        print("\nEmail Content:")
        print(email_record['email_content'])
    except Exception as e:
        logging.error(f"Error in generate_email: {e}")
    
    # Test generate_personalized_content
    try:
        key_moments = [{'text': 'This is a key moment from the video'}]
        content = generate_personalized_content(
            video_data['title'],
            "A detailed description of the video content",
            key_moments,
            channel_data['channel_title']
        )
        print("\nPersonalized Content:")
        print(content['personalized'])
        print("\nAffiliate Comment:")
        print(content['affiliate_comment'])
    except Exception as e:
        logging.error(f"Error in generate_personalized_content: {e}")
    
    # Test generate_email_content
    try:
        email = generate_email_content(channel_data)
        print("\nSimple Email Content:")
        print(f"Subject: {email['email_subject']}")
        print(f"Body: {email['email_body']}")
    except Exception as e:
        logging.error(f"Error in generate_email_content: {e}")

if __name__ == "__main__":
    main() 