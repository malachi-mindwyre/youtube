"""
Database management module for the lead generation system.
"""

from typing import Dict, List, Optional
from datetime import datetime
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from google.cloud.sql.connector import Connector

from .config import config

# Initialize SQLAlchemy base class
Base = declarative_base()

class DatabaseManager:
    """Class for managing database operations."""
    
    def __init__(self) -> None:
        """Initialize the database manager with Google Cloud SQL connection."""
        self.connector = Connector()
        
        # Create connection pool
        self.pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=self.get_conn,
            pool_size=5,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        # Create session factory
        self.Session = sessionmaker(bind=self.pool)
        
    def get_conn(self) -> sqlalchemy.engine.Connection:
        """
        Get a database connection using the Cloud SQL Connector.
        
        Returns:
            SQLAlchemy connection object
        """
        return self.connector.connect(
            config.DB_HOST,
            "pg8000",
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            db=config.DB_NAME
        )
        
    def create_tables(self) -> None:
        """Create all database tables if they don't exist."""
        Base.metadata.create_all(self.pool)
        
    def add_lead(
        self,
        user_id: str,
        channel_id: str,
        email: str,
        status: str = 'new'
    ) -> Dict:
        """
        Add a new lead to the database.
        
        Args:
            user_id: User ID who found the lead
            channel_id: YouTube channel ID
            email: Creator's email address
            status: Lead status (default: 'new')
            
        Returns:
            Dictionary containing the created lead's information
        """
        with self.Session() as session:
            try:
                # Check if lead already exists
                existing = session.execute(
                    text("""
                        SELECT * FROM leads 
                        WHERE user_id = :user_id AND channel_id = :channel_id
                    """),
                    {"user_id": user_id, "channel_id": channel_id}
                ).fetchone()
                
                if existing:
                    return {
                        'status': 'exists',
                        'lead_id': existing.lead_id
                    }
                    
                # Insert new lead
                result = session.execute(
                    text("""
                        INSERT INTO leads (
                            user_id, channel_id, email, status, created_at, updated_at
                        ) VALUES (
                            :user_id, :channel_id, :email, :status, :created_at, :updated_at
                        ) RETURNING lead_id
                    """),
                    {
                        'user_id': user_id,
                        'channel_id': channel_id,
                        'email': email,
                        'status': status,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                )
                
                lead_id = result.fetchone()[0]
                session.commit()
                
                return {
                    'status': 'success',
                    'lead_id': lead_id
                }
                
            except Exception as e:
                session.rollback()
                return {
                    'status': 'error',
                    'error': str(e)
                }
                
    def update_lead_status(
        self,
        lead_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Update a lead's status in the database.
        
        Args:
            lead_id: Lead ID to update
            status: New status
            notes: Optional notes about the update
            
        Returns:
            Dictionary containing update status
        """
        with self.Session() as session:
            try:
                session.execute(
                    text("""
                        UPDATE leads 
                        SET status = :status,
                            notes = :notes,
                            updated_at = :updated_at
                        WHERE lead_id = :lead_id
                    """),
                    {
                        'lead_id': lead_id,
                        'status': status,
                        'notes': notes,
                        'updated_at': datetime.now()
                    }
                )
                
                session.commit()
                return {'status': 'success'}
                
            except Exception as e:
                session.rollback()
                return {
                    'status': 'error',
                    'error': str(e)
                }
                
    def add_email(
        self,
        lead_id: str,
        subject: str,
        body: str,
        message_id: str
    ) -> Dict:
        """
        Add an email record to the database.
        
        Args:
            lead_id: Associated lead ID
            subject: Email subject
            body: Email body
            message_id: Titan Email message ID
            
        Returns:
            Dictionary containing the created email's information
        """
        with self.Session() as session:
            try:
                result = session.execute(
                    text("""
                        INSERT INTO emails (
                            lead_id, subject, content, message_id, sent_at
                        ) VALUES (
                            :lead_id, :subject, :body, :message_id, :sent_at
                        ) RETURNING email_id
                    """),
                    {
                        'lead_id': lead_id,
                        'subject': subject,
                        'body': body,
                        'message_id': message_id,
                        'sent_at': datetime.now()
                    }
                )
                
                email_id = result.fetchone()[0]
                session.commit()
                
                return {
                    'status': 'success',
                    'email_id': email_id
                }
                
            except Exception as e:
                session.rollback()
                return {
                    'status': 'error',
                    'error': str(e)
                }
                
    def get_leads_by_status(
        self,
        user_id: str,
        status: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get leads by status for a specific user.
        
        Args:
            user_id: User ID
            status: Lead status to filter by
            limit: Maximum number of leads to return
            
        Returns:
            List of lead dictionaries
        """
        with self.Session() as session:
            try:
                results = session.execute(
                    text("""
                        SELECT * FROM leads 
                        WHERE user_id = :user_id AND status = :status
                        LIMIT :limit
                    """),
                    {
                        'user_id': user_id,
                        'status': status,
                        'limit': limit
                    }
                ).fetchall()
                
                return [dict(row) for row in results]
                
            except Exception as e:
                return []
                
    def get_analytics(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Get analytics data for a specific user and date range.
        
        Args:
            user_id: User ID
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dictionary containing analytics data
        """
        with self.Session() as session:
            try:
                # Get lead generation metrics
                leads = session.execute(
                    text("""
                        SELECT 
                            COUNT(*) as total_leads,
                            COUNT(CASE WHEN status = 'contacted' THEN 1 END) as contacted_leads,
                            COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads
                        FROM leads
                        WHERE user_id = :user_id
                        AND created_at BETWEEN :start_date AND :end_date
                    """),
                    {
                        'user_id': user_id,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                ).fetchone()
                
                # Get email metrics
                emails = session.execute(
                    text("""
                        SELECT 
                            COUNT(*) as total_emails,
                            COUNT(CASE WHEN response_received = true THEN 1 END) as responses
                        FROM emails e
                        JOIN leads l ON e.lead_id = l.lead_id
                        WHERE l.user_id = :user_id
                        AND e.sent_at BETWEEN :start_date AND :end_date
                    """),
                    {
                        'user_id': user_id,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                ).fetchone()
                
                return {
                    'leads': {
                        'total': leads.total_leads,
                        'contacted': leads.contacted_leads,
                        'converted': leads.converted_leads
                    },
                    'emails': {
                        'sent': emails.total_emails,
                        'responses': emails.responses
                    }
                }
                
            except Exception as e:
                return {
                    'error': str(e)
                } 