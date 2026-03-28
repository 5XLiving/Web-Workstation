"""
Authentication routes for membership system
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import bcrypt
import json
import os

bp = Blueprint('auth', __name__)

# Simple JSON-based user storage (replace with database in production)
USERS_FILE = 'data/users.json'

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    
    # Validate email format
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password strength
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Load existing users
    users = load_users()
    
    # Check if user exists
    if email in users:
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    users[email] = {
        'email': email,
        'password': hash_password(password),
        'membership': 'free',  # free or paid
        'created_at': datetime.utcnow().isoformat(),
        'quota': {
            'daily_generations': 1 if data.get('membership') == 'free' else 100,
            'used_today': 0,
            'last_reset': datetime.utcnow().date().isoformat()
        }
    }
    
    # Override membership if specified (for testing)
    if 'membership' in data and data['membership'] in ['free', 'paid']:
        users[email]['membership'] = data['membership']
        users[email]['quota']['daily_generations'] = 1 if data['membership'] == 'free' else 100
    
    save_users(users)
    
    # Create access token
    access_token = create_access_token(identity=email)
    
    return jsonify({
        'message': 'Registration successful',
        'access_token': access_token,
        'user': {
            'email': email,
            'membership': users[email]['membership'],
            'quota': users[email]['quota']
        }
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    
    # Load users
    users = load_users()
    
    # Check if user exists
    if email not in users:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    user = users[email]
    
    # Verify password
    if not verify_password(password, user['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Reset daily quota if needed
    today = datetime.utcnow().date().isoformat()
    if user['quota']['last_reset'] != today:
        user['quota']['used_today'] = 0
        user['quota']['last_reset'] = today
        users[email] = user
        save_users(users)
    
    # Create access token
    access_token = create_access_token(identity=email)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'email': email,
            'membership': user['membership'],
            'quota': user['quota']
        }
    })

@bp.route('/status', methods=['GET'])
@jwt_required()
def status():
    """Get current user status"""
    email = get_jwt_identity()
    users = load_users()
    
    if email not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[email]
    
    # Reset daily quota if needed
    today = datetime.utcnow().date().isoformat()
    if user['quota']['last_reset'] != today:
        user['quota']['used_today'] = 0
        user['quota']['last_reset'] = today
        users[email] = user
        save_users(users)
    
    return jsonify({
        'user': {
            'email': email,
            'membership': user['membership'],
            'quota': user['quota'],
            'remaining': user['quota']['daily_generations'] - user['quota']['used_today']
        }
    })

@bp.route('/upgrade', methods=['POST'])
@jwt_required()
def upgrade():
    """Upgrade user to paid membership"""
    email = get_jwt_identity()
    users = load_users()
    
    if email not in users:
        return jsonify({'error': 'User not found'}), 404
    
    # In production, integrate with payment processor (Stripe, PayPal, etc.)
    # For now, just upgrade directly
    
    users[email]['membership'] = 'paid'
    users[email]['quota']['daily_generations'] = 100
    save_users(users)
    
    return jsonify({
        'message': 'Upgraded to paid membership',
        'user': {
            'email': email,
            'membership': 'paid',
            'quota': users[email]['quota']
        }
    })
