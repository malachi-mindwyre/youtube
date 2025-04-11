"""Transcript processing functions for YouTube API analysis."""

from typing import Dict, List, Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_video_transcript(video_id: str) -> Tuple[Optional[str], str]:
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
        return formatter.format_transcript(transcript.fetch()), "found"
    except Exception as e:
        if "No transcripts were found" in str(e):
            return None, "no_transcript"
        elif "Subtitles are disabled" in str(e):
            return None, "subtitles_disabled"
        else:
            return None, f"error: {str(e)}"

def extract_key_moments(video_id: str) -> List[Dict]:
    """Extract key moments from video for personalization.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of key moments with text and timestamp
    """
    try:
        transcript, _ = get_video_transcript(video_id)
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