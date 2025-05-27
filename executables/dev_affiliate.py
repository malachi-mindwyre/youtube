import sqlite3
import os
import secrets
import string

class AffiliateDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Save to the existing 'results' folder inside your current working directory
            results_dir = os.path.join(os.getcwd(), 'results')
            # Make sure the folder exists
            os.makedirs(results_dir, exist_ok=True)
            self.db_path = os.path.join(results_dir, 'affiliate_program.db')
        else:
            self.db_path = db_path
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        #Affiliate Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                referral_id TEXT UNIQUE NOT NULL,
                affiliate_link TEXT UNIQUE NOT NULL
            )
        ''')
        
        # YouTube data tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_videos (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                channel_id TEXT,
                published_at TEXT,
                views INTEGER,
                likes INTEGER,
                comments INTEGER,
                engagement_rate REAL,
                has_transcript BOOLEAN,
                has_email BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_channels (
                channel_id TEXT PRIMARY KEY,
                channel_title TEXT,
                subscribers INTEGER,
                total_videos INTEGER,
                total_views INTEGER,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_email_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                channel_title TEXT,
                email TEXT,
                email_subject TEXT,
                email_body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES youtube_channels (channel_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                transcript_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES youtube_videos (video_id)
            )
        ''')
        

        conn.commit()
        conn.close()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def generate_referral_id(self, name: str = None) -> str:
        """Generate unique referral ID."""
        if name:
            # Use first 4 letters of name + random
            clean_name = ''.join(c for c in name if c.isalpha())[:4].upper()
            random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            referral_id = f"{clean_name}{random_part}"
        else:
            # Generate 8 character random ID
            referral_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        # Ensure uniqueness
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT referral_id FROM affiliates WHERE referral_id = ?", (referral_id,))
        
        if cursor.fetchone():
            conn.close()
            return self.generate_referral_id(name)  # Try again
        
        conn.close()
        return referral_id
    
    def generate_affiliate_link(self, referral_id: str) -> str:
            return f"https://mindwyre.org/?ref={referral_id}"

if __name__ == '__main__':
    db = AffiliateDatabase()
    relative_path = os.path.relpath(db.db_path, os.getcwd())
    print(f"Database initialized at: {relative_path}")