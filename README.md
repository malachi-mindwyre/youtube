# YouTube Lead Generation System

A SaaS platform for automated YouTube lead generation and affiliate marketing. The system identifies potential YouTube creators, extracts their contact information, generates personalized emails based on video content, and manages affiliate link distribution.

## Features

- YouTube video and channel data scraping
- Email extraction from video and channel descriptions
- Personalized email generation based on video content
- Lead tracking and management
- Analytics and performance metrics
- Cloud-based data storage
- Titan Email integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-leads.git
cd youtube-leads
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your credentials:
```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# YouTube API Configuration
YOUTUBE_API_KEY=your-youtube-api-key
YOUTUBE_API_QUOTA_LIMIT=10000

# Titan Email Configuration
TITAN_EMAIL_API_KEY=your-titan-api-key
TITAN_EMAIL_DOMAIN=your-domain.com

# Database Configuration
DB_HOST=your-db-host
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

## Usage

1. Initialize the database:
```python
from youtube_leads.database import DatabaseManager

db = DatabaseManager()
db.create_tables()
```

2. Create a lead generation system instance:
```python
from youtube_leads.main import LeadGenerationSystem

system = LeadGenerationSystem()
```

3. Process keywords to find leads:
```python
results = system.process_keywords(
    user_id="user123",
    keywords=["python programming", "data science"],
    max_results=50
)
print(results)
```

4. Get analytics:
```python
analytics = system.get_analytics(
    user_id="user123",
    days=30
)
print(analytics)
```

## Project Structure

```
youtube-leads/
├── src/
│   └── youtube_leads/
│       ├── __init__.py
│       ├── config.py
│       ├── youtube_scraper.py
│       ├── email_manager.py
│       ├── database.py
│       ├── models.py
│       └── main.py
├── tests/
│   └── ...
├── requirements.txt
├── README.md
└── PROJECT_PLAN.md
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Run type checking:
```bash
mypy src/
```

4. Format code:
```bash
black src/
isort src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@yourdomain.com or create an issue in the repository.
