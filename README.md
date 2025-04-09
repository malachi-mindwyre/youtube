# YouTube Channel Analysis Tool

A Python tool for analyzing YouTube channels and videos, with a focus on finding channels with contact information.

## Features

- Search YouTube videos by keyword
- Analyze channel and video statistics
- Filter videos by:
  - Minimum views
  - Minimum views per hour
  - Minimum comments per hour
  - Minimum likes per hour
  - Maximum hours since published
  - Email presence in channel description
- Save results in CSV or Excel format
- Extract contact information from channel descriptions

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
  keyword: "influencer marketing"  # The term to search for
  max_results: 100  # Number of videos to analyze

# Filter Settings
filters:
  min_views: 1000  # Minimum total views
  min_views_per_hour: 100.0  # Minimum views per hour
  min_comments_per_hour: 0.1  # Minimum comments per hour
  min_likes_per_hour: 1.0  # Minimum likes per hour
  max_hours_since_published: 8760  # Maximum hours since video was published (1 year)
  require_email_found: true  # Only save channels with emails

# Output Settings
output:
  save_csv: false  # Whether to save results as CSV files
  save_excel: true  # Whether to save results as Excel file
  save_json: false  # Whether to save results as JSON file
  output_directory: "results"  # Directory to save output files
```

## Usage

Run the analysis:
```bash
python notebooks/run_analysis.py
```

The tool will:
1. Search for videos matching your keyword
2. Filter videos based on your criteria
3. Extract channel information
4. Find channels with contact information
5. Save results to the specified output directory

## Output

The tool generates two files:
1. `youtube_videos_[timestamp].csv/xlsx` - Contains video statistics
2. `youtube_channels_[timestamp].csv/xlsx` - Contains channel information and contact details

## Requirements

- Python 3.8+
- YouTube Data API v3 key
- Dependencies listed in `requirements.txt`

## License

MIT License
