"""
Configuration management for the YouTube Lead Generation System.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application."""
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # YouTube API Configuration
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_API_QUOTA_LIMIT: int = int(os.getenv("YOUTUBE_API_QUOTA_LIMIT", "10000"))
    
    # Titan Email Configuration
    TITAN_EMAIL_API_KEY: str = os.getenv("TITAN_EMAIL_API_KEY", "")
    TITAN_EMAIL_DOMAIN: str = os.getenv("TITAN_EMAIL_DOMAIN", "")
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> Dict[str, str]:
        """
        Validate the configuration and return any missing required settings.
        
        Returns:
            Dict[str, str]: Dictionary of missing required settings and their descriptions.
        """
        missing: Dict[str, str] = {}
        
        if not cls.GOOGLE_CLOUD_PROJECT:
            missing["GOOGLE_CLOUD_PROJECT"] = "Google Cloud Project ID"
        if not cls.GOOGLE_APPLICATION_CREDENTIALS:
            missing["GOOGLE_APPLICATION_CREDENTIALS"] = "Path to Google Cloud credentials file"
        if not cls.YOUTUBE_API_KEY:
            missing["YOUTUBE_API_KEY"] = "YouTube Data API key"
        if not cls.TITAN_EMAIL_API_KEY:
            missing["TITAN_EMAIL_API_KEY"] = "Titan Email API key"
        if not cls.TITAN_EMAIL_DOMAIN:
            missing["TITAN_EMAIL_DOMAIN"] = "Titan Email domain"
        if not cls.DB_HOST:
            missing["DB_HOST"] = "Database host"
        if not cls.DB_NAME:
            missing["DB_NAME"] = "Database name"
        if not cls.DB_USER:
            missing["DB_USER"] = "Database user"
        if not cls.DB_PASSWORD:
            missing["DB_PASSWORD"] = "Database password"
            
        return missing

# Create a singleton instance
config = Config() 