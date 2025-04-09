# YouTube Analysis Tool

A Python application for analyzing YouTube videos and channels, built with safety-critical guidelines in mind.

## Features

- **Video Analysis**
  - Search videos by keyword
  - Analyze engagement metrics (views, likes, comments)
  - Calculate hourly engagement rates
  - Filter videos by minimum engagement thresholds

- **Channel Analysis**
  - Get channel statistics
  - Analyze subscriber growth
  - Track video performance
  - Export results in multiple formats

## Project Structure

```
youtube/
├── config.yaml              # User configuration file
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
├── executables/            # Core application code
│   ├── youtube_api.py      # YouTube API interaction
│   └── combined_youtube_analysis_script.py  # Main analysis script
└── tests/                  # Test files
    ├── test_combined_analysis.py
    └── test_youtube_api.py
```

## Prerequisites

- Python 3.8+
- YouTube Data API key
- Required Python packages (see requirements.txt)

## Setup

1. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Configure Environment**:
   - Create a `.env` file in the project root
   - Add your YouTube API key:
     ```
     API_KEY=your_youtube_api_key_here
     ```

3. **Configure Analysis**:
   Edit `config.yaml` to customize your analysis:
   ```yaml
   # Search Settings
   search:
     keyword: "your search term"  # What to search for
     max_results: 50             # Number of videos to analyze

   # Filter Settings
   filters:
     min_views: 1000            # Minimum total views
     min_views_per_hour: 5.0    # Minimum views per hour
     min_comments_per_hour: 0.1 # Minimum comments per hour
     min_likes_per_hour: 1.0    # Minimum likes per hour

   # Output Settings
   output:
     save_csv: true            # Save as CSV
     save_excel: false         # Save as Excel
     save_json: false          # Save as JSON
     output_directory: "results" # Where to save files

   # Analysis Settings
   analysis:
     include_channel_stats: true    # Include channel statistics
     include_video_stats: true      # Include video statistics
     include_engagement_metrics: true # Calculate engagement metrics
     include_sentiment_analysis: false # Analyze comment sentiment
   ```

## Usage

1. **Run the Analysis**:
   ```bash
   PYTHONPATH=$PYTHONPATH:. python3 executables/combined_youtube_analysis_script.py
   ```

2. **View Results**:
   - Results are saved in the specified output directory
   - CSV files are created with timestamps
   - Console output shows summary statistics

## Code Quality Standards

This project follows strict safety-critical guidelines:

1. **Control Flow Simplicity**
   - No recursion
   - Maximum 10 decision points per function
   - No eval() or exec()
   - No goto patterns

2. **Resource Management**
   - No global mutable variables
   - All resource access uses context managers
   - Explicit initialization

3. **Function Structure**
   - Maximum 50 lines per function
   - Single responsibility principle
   - Type annotations for all parameters
   - Comprehensive docstrings

4. **Error Handling**
   - All exceptions are caught and handled
   - No silent failures
   - Meaningful error messages

## Dependencies

Core dependencies (see requirements.txt for versions):
- google-api-python-client
- pandas
- numpy
- python-dotenv
- pyarrow
- PyYAML

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YouTube Data API
- Python safety-critical development community
