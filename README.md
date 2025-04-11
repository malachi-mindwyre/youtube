# YouTube Analysis Tool

A powerful Python tool for analyzing YouTube channels and generating personalized outreach content.

## Features

- 🔍 Search YouTube videos by keyword
- 📊 Analyze channel and video statistics
- 📧 Generate personalized email templates
- 📝 Process video transcripts
- 📈 Track engagement metrics
- 💾 Export data to CSV and Excel formats
- 🔄 Smart update system for existing data
- 🎯 Configurable filtering criteria

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/youtube-analysis.git
cd youtube-analysis
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up YouTube API credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the YouTube Data API v3
   - Create credentials (API Key)
   - Create a `.env` file and add your API key:
     ```
     YOUTUBE_API_KEY=your_api_key_here
     ```

## Configuration

Edit `config.yaml` to customize the analysis:

```yaml
# Search Settings
search:
  keyword: "your search term"
  max_results: 50

# Filter Settings
filters:
  min_views: 100
  max_views: 1000000
  min_subscribers: 100
  max_subscribers: 100000
  min_views_per_hour: 0.05
  min_comments_per_hour: 0.001
  min_likes_per_hour: 0.001
  max_hours_since_published: 17520
  require_email_found: true
  require_transcript: false

# Output Settings
output:
  directory: "results"
  save_csv: true
  save_excel: true
  save_json: false
```

## Usage

Run the analysis:
```bash
python executables/run_analysis.py
```

## Output Files

The tool generates the following files in the `results` directory:

1. `youtube_channels.csv`: Channel statistics and metrics
2. `youtube_videos.csv`: Detailed video information
3. `youtube_email_content.csv`: Generated email templates
4. `youtube_analysis.xlsx`: Excel workbook with all data (multiple sheets)

## Documentation

- [Executables Documentation](docs/EXECUTABLES.md): Detailed information about the code structure
- [Configuration Guide](docs/CONFIGURATION.md): Complete configuration options
- [API Reference](docs/API.md): YouTube API usage details

## Progress Tracking

The tool maintains state between runs:
- Updates existing channel data when significant changes occur
- Avoids duplicate entries
- Tracks historical metrics
- Smart update system for efficient processing

## Requirements

- Python 3.8+
- YouTube Data API v3 credentials
- Required Python packages (see `requirements.txt`)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Never commit API credentials
- Store sensitive data in environment variables
- Use `.env` for local development
- Follow security best practices

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed
