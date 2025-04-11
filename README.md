# YouTube Channel Analysis Tool

A Python tool for analyzing YouTube channels and videos, with a focus on finding channels with contact information.

## Features

- Search YouTube videos by keyword
- Analyze channel and video statistics
- Filter videos by:
  - Minimum and maximum views
  - Minimum and maximum subscribers
  - Minimum views per hour
  - Minimum comments per hour
  - Minimum likes per hour
  - Maximum hours since published
  - Email presence in channel description
  - Transcript availability
- Save results in CSV, Excel, or JSON format
- Extract contact information from channel descriptions
- Generate personalized emails for outreach
- Detailed progress tracking and analysis summary

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube.git
cd youtube
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your YouTube API key:
```
API_KEY=your_youtube_api_key_here
```

## Configuration

Edit `config.yaml` to customize the analysis:

```yaml
# Search Settings
search:
  keyword: "software engineer day in the life"  # The term to search for
  max_results: 50  # Number of videos to analyze

# Filter Settings
filters:
  min_views: 100  # Minimum total views
  max_views: 1000000  # Maximum total views
  min_subscribers: 100  # Minimum subscribers
  max_subscribers: 100000  # Maximum subscribers
  min_views_per_hour: 0.05  # Minimum views per hour
  min_comments_per_hour: 0.001  # Minimum comments per hour
  min_likes_per_hour: 0.001  # Minimum likes per hour
  max_hours_since_published: 17520  # Maximum hours since video was published (2 years)
  require_email_found: true  # Only save channels with emails
  require_transcript: false  # Whether to require transcripts

# Output Settings
output:
  directory: "results"  # Directory to save output files
  save_csv: true  # Whether to save results as CSV files
  save_excel: false  # Whether to save results as Excel file
  save_json: false  # Whether to save results as JSON file

# Analysis Settings
analysis:
  include_channel_stats: true  # Whether to include channel statistics
  include_video_stats: true  # Whether to include video statistics
  include_engagement_metrics: true  # Whether to calculate engagement metrics
  include_sentiment_analysis: false  # Whether to perform sentiment analysis on comments
```

## Usage

Run the analysis:
```bash
python executables/run_analysis.py
```

The tool will:
1. Search for videos matching your keyword
2. Process each video and its channel:
   - Check subscriber count
   - Verify view count
   - Calculate engagement metrics
   - Extract transcripts
   - Find contact information
3. Generate personalized emails for qualified channels
4. Save results to the specified output directory
5. Display a detailed progress report and analysis summary

## Output

The tool generates several files:
1. `youtube_channels.csv` - Contains channel information and contact details
2. `youtube_videos.csv` - Contains video statistics and engagement metrics
3. `youtube_email_content.csv` - Contains generated email templates for outreach

## Progress Tracking

The tool provides detailed progress information:
- Number of videos processed
- Channel details and subscriber counts
- Transcript availability
- Engagement metrics
- Email generation status
- Final analysis summary

## Requirements

- Python 3.8+
- YouTube Data API v3 key
- Dependencies listed in `requirements.txt`

## License

MIT License
