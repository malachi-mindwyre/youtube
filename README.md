# YouTube Video & Channel Analysis Toolkit

A safety-critical Python application for analyzing YouTube videos and channels, following NASA's Power of Ten safety principles and clean code practices.

## Safety-Critical Guidelines

This project strictly adheres to safety-critical Python guidelines, including:

- No recursion
- Maximum function complexity: 10 decision points
- No `eval()`, `exec()`, or `globals()`/`locals()`
- No `goto` emulation patterns
- Maximum 1 level of nested loops
- No `break` or `continue` in nested loops
- Maximum 1 `return` statement per function
- No monkey-patching
- No metaclasses
- Limited list/dictionary comprehensions
- Explicit loop bounds
- Strict resource management
- Comprehensive validation and assertions
- Type safety and static analysis

## Features

*   **Video Analysis**
    *   Search YouTube videos by keyword
    *   Filter by engagement metrics (views, likes, comments per hour)
    *   Detailed video statistics and metadata
    *   Configurable filtering criteria

*   **Channel Analysis**
    *   Comprehensive channel statistics
    *   Subscriber count, total views, video count
    *   Channel metadata (creation date, country, description)
    *   Contact information extraction (emails, social media links)

*   **Data Management**
    *   Pandas DataFrame integration
    *   Optional Google Cloud Storage support
    *   Environment-based configuration
    *   Type-safe data handling

## Project Structure

```
.
├── .env                    # Environment variables (API keys)
├── .gitignore             # Git ignore rules
├── README.md              # This documentation
├── requirements.txt       # Python dependencies
├── executables/
│   ├── youtube_api.py     # Video search and analysis
│   ├── channel_analysis.py # Channel information extraction
│   ├── combined_youtube_analysis_script.py # Main analysis script
│   └── google_storage.py  # GCP integration (optional)
└── jupyter/
    └── youtube_api.ipynb  # Interactive analysis notebook
```

## Prerequisites

*   Python 3.9 or higher
*   YouTube Data API v3 key
*   (Optional) Google Cloud Storage access

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone git@github.com:malachi-mindwyre/youtube.git
    cd youtube
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    *   Create a `.env` file in the project root
    *   Add your YouTube API key:
        ```
        API_KEY=your_api_key_here
        ```
    *   Get an API key from [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com)

## Usage

### Basic Analysis

1.  **Run the Combined Analysis:**
    ```bash
    python executables/combined_youtube_analysis_script.py
    ```
    This will:
    *   Search for videos matching the default keyword
    *   Filter videos based on engagement metrics
    *   Analyze associated channels
    *   Display results in the console

2.  **Customize Analysis:**
    Modify the `YouTubeAPIConfig` class in `youtube_api.py` to adjust:
    *   Search keywords
    *   Minimum views and engagement thresholds
    *   Maximum results per search

### Advanced Usage

1.  **Interactive Analysis:**
    ```bash
    jupyter notebook jupyter/youtube_api.ipynb
    ```

2.  **Google Cloud Storage Integration:**
    ```python
    from executables.google_storage import upload_to_gcp_bucket
    
    # Upload results to GCP
    upload_to_gcp_bucket(
        source_file="results.csv",
        bucket_name="your-bucket",
        destination_blob_name="youtube-analysis/results.csv"
    )
    ```

## Code Quality

This project adheres to strict coding standards:

*   NASA's Power of Ten rules for safety-critical systems
*   Clean code principles
*   Comprehensive type hints
*   Extensive error handling
*   Input validation and assertions
*   No global variables
*   Maximum 2 levels of nesting
*   Small, focused functions
*   Proper resource management

## Dependencies

*   `google-api-python-client`: YouTube Data API interaction
*   `google-cloud-storage`: GCP integration
*   `pandas`: Data manipulation
*   `numpy`: Numerical operations
*   `python-dateutil`: Date/time handling
*   `pytz`: Timezone support
*   `python-dotenv`: Environment variable management

## Contributing

1.  Create a feature branch
2.  Make your changes
3.  Ensure all tests pass
4.  Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YouTube Data API
- Google Cloud Platform
- Python safety-critical development community
