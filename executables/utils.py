"""Utility functions for YouTube API analysis."""

import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import pytz
from dateutil import parser

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

def extract_email(text: str) -> Optional[str]:
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

def calculate_hours_since_published(published_at: str) -> float:
    """Calculate hours since video was published.
    
    Args:
        published_at: ISO format timestamp string
        
    Returns:
        Hours since publication as float
    """
    try:
        # Parse the published date
        published = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        
        # Get current time in UTC
        current_time = datetime.now(pytz.UTC)
        
        # Calculate time difference in hours
        time_diff = current_time - published
        return time_diff.total_seconds() / 3600
    except Exception as e:
        logging.error(f"Error calculating hours since published: {e}")
        return 0.0

def should_update_channel(existing: Dict[str, Any], new: Dict[str, Any]) -> bool:
    """Determine if channel should be updated based on significant changes."""
    try:
        # Check if any key metric has changed by more than 10%
        metrics = ['subscribers', 'total_videos', 'total_views']
        for metric in metrics:
            if metric in existing and metric in new:
                old_val = float(existing[metric])
                new_val = float(new[metric])
                if old_val > 0:  # Avoid division by zero
                    change_pct = abs(new_val - old_val) / old_val * 100
                    if change_pct >= 10:  # 10% threshold
                        return True
        return False
    except Exception as e:
        logging.error(f"Error in should_update_channel: {e}")
        return True  # Update on error to be safe 