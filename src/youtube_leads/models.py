"""
SQLAlchemy models for the lead generation system.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    """User model for storing user information."""
    
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    subscription_status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_active = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    leads = relationship("Lead", back_populates="user")
    
class Lead(Base):
    """Lead model for storing YouTube creator information."""
    
    __tablename__ = 'leads'
    
    lead_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    channel_id = Column(String, nullable=False)
    email = Column(String)
    status = Column(String, nullable=False, default='new')
    notes = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="leads")
    emails = relationship("Email", back_populates="lead")
    
class Email(Base):
    """Email model for storing sent emails."""
    
    __tablename__ = 'emails'
    
    email_id = Column(String, primary_key=True)
    lead_id = Column(String, ForeignKey('leads.lead_id'), nullable=False)
    subject = Column(String, nullable=False)
    content = Column(String, nullable=False)
    message_id = Column(String, nullable=False)
    sent_at = Column(DateTime, nullable=False, default=datetime.now)
    response_received = Column(Boolean, default=False)
    response_content = Column(String)
    
    # Relationships
    lead = relationship("Lead", back_populates="emails")
    
class Analytics(Base):
    """Analytics model for storing daily metrics."""
    
    __tablename__ = 'analytics'
    
    analytics_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    date = Column(DateTime, nullable=False)
    leads_generated = Column(Integer, nullable=False, default=0)
    emails_sent = Column(Integer, nullable=False, default=0)
    responses_received = Column(Integer, nullable=False, default=0)
    conversions = Column(Integer, nullable=False, default=0)
    
    # Relationships
    user = relationship("User") 