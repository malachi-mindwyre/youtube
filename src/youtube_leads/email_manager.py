"""
Email management module for the lead generation system.
"""

from typing import Dict, Optional
import titan.email as titan
from datetime import datetime

from .config import config

class EmailManager:
    """Class for managing email communications."""
    
    def __init__(self) -> None:
        """Initialize the email manager with Titan Email credentials."""
        self.client = titan.Client(
            api_key=config.TITAN_EMAIL_API_KEY,
            domain=config.TITAN_EMAIL_DOMAIN
        )
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> Dict:
        """
        Send an email using Titan Email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            from_email: Optional sender email address
            
        Returns:
            Dictionary containing email sending status
            
        Raises:
            Exception: If email sending fails
        """
        try:
            if not from_email:
                from_email = f"noreply@{config.TITAN_EMAIL_DOMAIN}"
                
            response = self.client.send(
                to=to_email,
                from_email=from_email,
                subject=subject,
                body=body
            )
            
            return {
                'status': 'success',
                'message_id': response.get('message_id'),
                'sent_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'sent_at': datetime.now().isoformat()
            }
            
    def generate_personalized_email(
        self,
        video_data: Dict,
        channel_data: Dict,
        transcript: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a personalized email based on video and channel data.
        
        Args:
            video_data: Dictionary containing video information
            channel_data: Dictionary containing channel information
            transcript: Optional video transcript
            
        Returns:
            Dictionary containing subject and body of the email
        """
        # Extract key information
        channel_name = channel_data.get('title', '')
        video_title = video_data.get('title', '')
        subscriber_count = channel_data.get('subscriber_count', 0)
        
        # Generate subject
        subject = f"Collaboration Opportunity for {channel_name}"
        
        # Generate personalized body
        body = f"""Dear {channel_name},

I came across your YouTube channel and was particularly impressed by your video "{video_title}". With your {subscriber_count:,} subscribers, you've built an amazing community!

I represent [Your Company Name], and we're looking to collaborate with creators like yourself who produce high-quality content. We have an exciting affiliate program that could be a great fit for your channel.

Would you be interested in learning more about this opportunity? I'd love to discuss how we can work together to create value for your audience.

Best regards,
[Your Name]
[Your Company Name]
"""
        
        return {
            'subject': subject,
            'body': body
        }
        
    def track_email_response(self, message_id: str) -> Dict:
        """
        Track the status of a sent email.
        
        Args:
            message_id: Titan Email message ID
            
        Returns:
            Dictionary containing email tracking information
        """
        try:
            status = self.client.get_message_status(message_id)
            return {
                'status': 'success',
                'data': status
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            } 