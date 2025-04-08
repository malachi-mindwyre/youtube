# YouTube Video & Channel Analysis Toolkit

This project provides a set of Python scripts to search for YouTube videos based on keywords, filter them by engagement metrics, and extract detailed information about the associated channels, including potential contact information.

## Features

*   **Keyword-Based Video Search:** Finds YouTube videos relevant to a specified search term.
*   **Engagement Filtering:** Filters videos based on configurable criteria like minimum total views, views per hour, likes per hour, and comments per hour.
*   **Detailed Channel Analysis:** Retrieves comprehensive data for the channels associated with the filtered videos, including:
    *   Subscriber count, total views, total videos
    *   Creation date, country
    *   Channel description
    *   Keywords
    *   Custom URL
*   **Contact Information Extraction:** Attempts to extract email addresses and social media links (Instagram, Twitter, Facebook, TikTok, LinkedIn, Website) from channel descriptions.
*   **Data Output:** Uses pandas DataFrames to structure the collected video and channel data.
*   **Google Cloud Storage Integration:** Includes a utility function to upload files to a GCP bucket (optional usage).
*   **Jupyter Notebook:** Provides a notebook environment for interactive analysis and development based on the video search script.

## Project Structure

```
.
├── .gitignore             # Specifies intentionally untracked files (e.g., .env)
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── executables/
│   ├── channel_analysis.py # Script to fetch detailed channel information
│   ├── combined_youtube_analysis_script.py # Main script to run video search and channel analysis
│   ├── google_storage.py  # Utility for uploading files to Google Cloud Storage
│   └── youtube_api.py     # Script to search and filter YouTube videos by keyword
└── jupyter/
    └── youtube_api.ipynb  # Jupyter notebook version for video search and analysis
```

## Setup

1.  **Prerequisites:**
    *   Python 3.x
    *   pip (Python package installer)

2.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up Environment Variables:**
    *   Create a file named `.env` in the project's root directory.
    *   Add your YouTube Data API v3 key to the `.env` file:
        ```
        API_KEY=YOUR_YOUTUBE_API_KEY
        ```
    *   You can obtain an API key from the [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com). Make sure to enable the "YouTube Data API v3".

## Usage

1.  **Configure Scripts (Optional):**
    *   Modify `executables/youtube_api.py` or `jupyter/youtube_api.ipynb` to change the `SEARCH_KEYWORD` or adjust the filtering criteria (`MIN_VIEWS`, `MIN_VIEWS_PER_HOUR`, etc.).

2.  **Run the Main Analysis Script:**
    Execute the combined script to perform both video searching/filtering and channel analysis:
    ```bash
    python executables/combined_youtube_analysis_script.py
    ```
    This will print sample DataFrames for the collected video and channel data to the console. You can modify the script to save the DataFrames to files (e.g., CSV) if needed.

3.  **Use the Jupyter Notebook:**
    For interactive analysis of the video search part:
    ```bash
    jupyter notebook jupyter/youtube_api.ipynb
    ```

4.  **Google Cloud Storage Upload (Manual):**
    If you need to upload a file (e.g., a CSV export of the results) to GCP:
    *   Ensure you have authenticated with GCP (e.g., via `gcloud auth application-default login`).
    *   Use the `upload_to_gcp_bucket` function from `executables/google_storage.py` within another script or interactively.

## Dependencies

*   `google-api-python-client`: For interacting with the YouTube Data API.
*   `google-cloud-storage`: For interacting with Google Cloud Storage.
*   `pandas`: For data manipulation and analysis (DataFrames).
*   `numpy`: Numerical Python library (often a dependency of pandas).
*   `python-dateutil`: For parsing dates/times.
*   `pytz`: For handling timezones.
*   `python-dotenv`: For loading environment variables from the `.env` file.
