"""YouTube Channel Analysis Package.

This package provides tools for analyzing YouTube channels and videos
using the YouTube Data API and Google Cloud Storage.
"""

from executables.youtube_api import YouTubeAPIConfig, YouTubeAPI
from executables.channel_analysis import ChannelAnalysisConfig, ChannelAnalyzer
from executables.google_storage import GoogleStorageConfig, GoogleStorage

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT" 