"""
Simple Affiliate Program
- Create affiliate links for YouTube channels
- Track referrals via URL ?ref= parameter  
- Process Stripe payments with commission tracking
"""

import sqlite3
import uuid
import secrets
import string
from datetime import datetime
from typing import Dict, List, Optional
import stripe
import hashlib
import bcrypt

class SimpleAffiliateProgram:
    def __init__(self, database_path: str = "simple_affiliates.db", stripe_api_key: str = None):
        self.db_path = database_path
        if stripe_api_key:
            stripe.api_key = stripe_api_key
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with simple tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Affiliate table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                referral_id TEXT UNIQUE NOT NULL,
                payout_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                referral_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referral_id) REFERENCES affiliates (referral_id)
            )
        ''')
        
        # Commission table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commissions (
                commission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                referral_id TEXT NOT NULL,
                amount_paid REAL NOT NULL,
                commission_amount REAL NOT NULL,
                paid_boolean BOOLEAN DEFAULT FALSE,
                stripe_payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referral_id) REFERENCES affiliates (referral_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
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
    
    def create_affiliate(self, name: str, email: str, payout_info: str = "") -> Dict:
        """Create new affiliate account."""
        referral_id = self.generate_referral_id(name)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO affiliates (name, email, referral_id, payout_info)
                VALUES (?, ?, ?, ?)
            ''', (name, email, referral_id, payout_info))
            
            affiliate_id = cursor.lastrowid
            conn.commit()
            
            return {
                'id': affiliate_id,
                'name': name,
                'email': email,
                'referral_id': referral_id,
                'affiliate_link': f"https://yoursaas.com?ref={referral_id}",
                'payout_info': payout_info
            }
            
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def create_affiliates_from_youtube_channels(self, channels: List[Dict]) -> List[Dict]:
        """Create affiliate accounts from YouTube channel data."""
        created_affiliates = []
        
        for channel in channels:
            affiliate = self.create_affiliate(
                name=channel.get('channel_title', ''),
                email=channel.get('email', ''),
                payout_info=f"YouTube Channel: {channel.get('channel_title', '')}"
            )
            
            if affiliate:
                created_affiliates.append(affiliate)
        
        return created_affiliates
    
    def create_user(self, email: str, password: str, referral_id: str = None) -> Dict:
        """Create new user account with optional referral."""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, referral_id)
                VALUES (?, ?, ?)
            ''', (email, password_hash, referral_id))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                'id': user_id,
                'email': email,
                'referral_id': referral_id
            }
            
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def process_stripe_payment(self, payment_intent_id: str, commission_rate: float = 0.15) -> Dict:
        """Process Stripe payment and create commission if referral exists."""
        try:
            # Retrieve payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status != 'succeeded':
                return {'error': 'Payment not successful'}
            
            # Get referral_id from metadata
            referral_id = payment_intent.metadata.get('referral_id')
            
            if not referral_id:
                return {'message': 'No referral found'}
            
            # Calculate amounts
            amount_paid = payment_intent.amount / 100  # Stripe uses cents
            commission_amount = amount_paid * commission_rate
            
            # Create commission record
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO commissions (referral_id, amount_paid, commission_amount, stripe_payment_id)
                VALUES (?, ?, ?, ?)
            ''', (referral_id, amount_paid, commission_amount, payment_intent_id))
            
            commission_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'commission_id': commission_id,
                'referral_id': referral_id,
                'amount_paid': amount_paid,
                'commission_amount': commission_amount,
                'stripe_payment_id': payment_intent_id
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_affiliate_stats(self, referral_id: str) -> Dict:
        """Get affiliate performance stats."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get affiliate info
        cursor.execute("SELECT * FROM affiliates WHERE referral_id = ?", (referral_id,))
        affiliate = cursor.fetchone()
        
        if not affiliate:
            conn.close()
            return None
        
        # Get commission stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sales,
                SUM(amount_paid) as total_revenue,
                SUM(commission_amount) as total_commissions,
                SUM(CASE WHEN paid_boolean = 1 THEN commission_amount ELSE 0 END) as paid_commissions,
                SUM(CASE WHEN paid_boolean = 0 THEN commission_amount ELSE 0 END) as unpaid_commissions
            FROM commissions 
            WHERE referral_id = ?
        ''', (referral_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'affiliate': {
                'id': affiliate[0],
                'name': affiliate[1],
                'email': affiliate[2],
                'referral_id': affiliate[3],
                'payout_info': affiliate[4]
            },
            'stats': {
                'total_sales': stats[0] or 0,
                'total_revenue': stats[1] or 0,
                'total_commissions': stats[2] or 0,
                'paid_commissions': stats[3] or 0,
                'unpaid_commissions': stats[4] or 0
            }
        }
    
    def mark_commission_paid(self, commission_id: int) -> bool:
        """Mark commission as paid."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE commissions 
            SET paid_boolean = TRUE 
            WHERE commission_id = ?
        ''', (commission_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_unpaid_commissions(self) -> List[Dict]:
        """Get all unpaid commissions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, a.name, a.email, a.payout_info
            FROM commissions c
            JOIN affiliates a ON c.referral_id = a.referral_id
            WHERE c.paid_boolean = FALSE
            ORDER BY c.created_at DESC
        ''')
        
        commissions = []
        for row in cursor.fetchall():
            commissions.append({
                'commission_id': row[0],
                'referral_id': row[1],
                'amount_paid': row[2],
                'commission_amount': row[3],
                'stripe_payment_id': row[5],
                'created_at': row[6],
                'affiliate_name': row[7],
                'affiliate_email': row[8],
                'payout_info': row[9]
            })
        
        conn.close()
        return commissions

# Flask web routes for handling affiliate tracking
from flask import Flask, request, redirect, session, jsonify

app = Flask(__name__)
affiliate_program = SimpleAffiliateProgram()

@app.route('/')
def home():
    """Main landing page - capture referral from ?ref= parameter."""
    referral_id = request.args.get('ref')
    
    if referral_id:
        # Store referral in session
        session['referral_id'] = referral_id
        print(f"Referral captured: {referral_id}")
    
    # Redirect to your main site (remove ?ref= parameter)
    return redirect("https://yoursaas.com")

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup with referral tracking."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Get referral from session
    referral_id = session.get('referral_id')
    
    # Create user account
    user = affiliate_program.create_user(email, password, referral_id)
    
    if user:
        return jsonify({'success': True, 'user_id': user['id'], 'referral_id': referral_id})
    else:
        return jsonify({'error': 'Failed to create user'}), 400

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook for successful payments."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook (you'll need to set your webhook secret)
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        event = request.get_json()  # Simplified for demo
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent_id = event['data']['object']['id']
            
            # Process the payment and create commission
            result = affiliate_program.process_stripe_payment(payment_intent_id)
            
            print(f"Processed payment: {result}")
            
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/affiliate/<referral_id>/stats')
def affiliate_stats(referral_id):
    """Get affiliate statistics."""
    stats = affiliate_program.get_affiliate_stats(referral_id)
    
    if stats:
        return jsonify(stats)
    else:
        return jsonify({'error': 'Affiliate not found'}), 404

# Example usage functions
def create_affiliates_from_youtube_data():
    """Example: Create affiliates from YouTube channel data."""
    
    # Sample YouTube channel data (from your existing system)
    youtube_channels = [
        {
            'channel_title': 'Tech Review Channel',
            'email': 'contact@techreview.com'
        },
        {
            'channel_title': 'Marketing Tips',
            'email': 'hello@marketingtips.com'
        }
    ]
    
    # Create affiliate accounts
    affiliates = affiliate_program.create_affiliates_from_youtube_channels(youtube_channels)
    
    print("Created Affiliates:")
    for affiliate in affiliates:
        print(f"Name: {affiliate['name']}")
        print(f"Email: {affiliate['email']}")
        print(f"Referral ID: {affiliate['referral_id']}")
        print(f"Affiliate Link: {affiliate['affiliate_link']}")
        print("-" * 40)
    
    return affiliates

def demo_payment_flow():
    """Example: Simulate payment flow with referral."""
    
    # 1. User clicks affiliate link: https://yoursaas.com?ref=TECH1234
    referral_id = "TECH1234"
    
    # 2. User signs up (referral_id stored in session)
    user = affiliate_program.create_user("customer@example.com", "password123", referral_id)
    print(f"User created: {user}")
    
    # 3. User makes payment - you'd set referral_id in Stripe metadata
    # In your payment creation code:
    # stripe.PaymentIntent.create(
    #     amount=2999,  # $29.99
    #     currency='usd',
    #     metadata={'referral_id': referral_id}
    # )
    
    # 4. Payment succeeds - webhook processes commission
    # This would happen automatically via webhook
    
    print("Payment flow demo completed")

if __name__ == "__main__":
    # Demo usage
    print("=== Simple Affiliate Program Demo ===")
    
    # Create some affiliates
    affiliates = create_affiliates_from_youtube_data()
    
    # Demo payment flow
    demo_payment_flow()
    
    # Check stats
    if affiliates:
        stats = affiliate_program.get_affiliate_stats(affiliates[0]['referral_id'])
        print(f"Affiliate stats: {stats}")
    
    # Run Flask app
    app.secret_key = 'your-secret-key'
    app.run(debug=True)