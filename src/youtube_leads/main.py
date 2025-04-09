"""
Main module for the YouTube Lead Generation System.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

from .youtube_scraper import YouTubeScraper
from .email_manager import EmailManager
from .database import DatabaseManager
from .config import config

class LeadGenerationSystem:
    """Main class for the lead generation system."""
    
    def __init__(self) -> None:
        """Initialize the lead generation system."""
        self.youtube = YouTubeScraper()
        self.email = EmailManager()
        self.db = DatabaseManager()
        
    def process_keywords(
        self,
        user_id: str,
        keywords: List[str],
        max_results: int = 50
    ) -> Dict:
        """
        Process keywords to find potential leads.
        
        Args:
            user_id: User ID
            keywords: List of keywords to search
            max_results: Maximum number of results per keyword
            
        Returns:
            Dictionary containing processing results
        """
        results = {
            'total_videos': 0,
            'leads_found': 0,
            'emails_sent': 0,
            'errors': []
        }
        
        for keyword in keywords:
            try:
                # Search for videos
                videos = self.youtube.search_videos(keyword, max_results)
                results['total_videos'] += len(videos)
                
                for video in videos:
                    try:
                        # Get video details
                        video_details = self.youtube.get_video_details(video['video_id'])
                        
                        # Get channel details
                        channel_details = self.youtube.get_channel_details(video['channel_id'])
                        
                        # Extract email from description
                        email = self.youtube.extract_email(video_details['description'])
                        if not email:
                            email = self.youtube.extract_email(channel_details['description'])
                            
                        if email:
                            # Add lead to database
                            lead_result = self.db.add_lead(
                                user_id=user_id,
                                channel_id=video['channel_id'],
                                email=email
                            )
                            
                            if lead_result['status'] == 'success':
                                results['leads_found'] += 1
                                
                                # Generate and send email
                                email_content = self.email.generate_personalized_email(
                                    video_data=video_details,
                                    channel_data=channel_details
                                )
                                
                                email_result = self.email.send_email(
                                    to_email=email,
                                    subject=email_content['subject'],
                                    body=email_content['body']
                                )
                                
                                if email_result['status'] == 'success':
                                    # Add email to database
                                    self.db.add_email(
                                        lead_id=lead_result['lead_id'],
                                        subject=email_content['subject'],
                                        body=email_content['body'],
                                        message_id=email_result['message_id']
                                    )
                                    results['emails_sent'] += 1
                                    
                    except Exception as e:
                        results['errors'].append(f"Error processing video {video['video_id']}: {str(e)}")
                        
            except Exception as e:
                results['errors'].append(f"Error processing keyword '{keyword}': {str(e)}")
                
        return results
        
    def get_analytics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get analytics for a specific user.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dictionary containing analytics data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.db.get_analytics(user_id, start_date, end_date)
        
    def update_lead_status(
        self,
        lead_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Update a lead's status.
        
        Args:
            lead_id: Lead ID
            status: New status
            notes: Optional notes
            
        Returns:
            Dictionary containing update status
        """
        return self.db.update_lead_status(lead_id, status, notes)
        
    def get_leads_by_status(
        self,
        user_id: str,
        status: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get leads by status.
        
        Args:
            user_id: User ID
            status: Lead status
            limit: Maximum number of leads to return
            
        Returns:
            List of lead dictionaries
        """
        return self.db.get_leads_by_status(user_id, status, limit)
        
    def track_email_response(self, message_id: str) -> Dict:
        """
        Track an email's response status.
        
        Args:
            message_id: Titan Email message ID
            
        Returns:
            Dictionary containing tracking information
        """
        return self.email.track_email_response(message_id) 