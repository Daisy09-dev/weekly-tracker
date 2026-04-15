from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_VERCEL = os.environ.get('VERCEL') == '1'
DEFAULT_DB_PATH = '/tmp/studysystem.db' if IS_VERCEL else os.path.join(BASE_DIR, 'studysystem.db')
DATABASE = os.environ.get('DATABASE_PATH', DEFAULT_DB_PATH)
SCHEMA_FILE = os.path.join(BASE_DIR, 'schema.sql')
IS_PRODUCTION = (
    os.environ.get('FLASK_ENV') == 'production'
    or os.environ.get('RENDER') == 'true'
    or IS_VERCEL
)

app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

# Database initialization
def init_db():
    conn = sqlite3.connect(DATABASE)
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as schema_file:
        conn.executescript(schema_file.read())
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Hash password
def hash_password(password):
    return generate_password_hash(password)

def is_modern_hash(stored_hash):
    return stored_hash.startswith('scrypt:') or stored_hash.startswith('pbkdf2:')

def verify_password(password, stored_hash):
    if is_modern_hash(stored_hash):
        return check_password_hash(stored_hash, password)
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash

init_db()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        raw_password = data.get('password', '')
        email = data.get('email')
        
        if not username or not raw_password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        password = hash_password(raw_password)
        
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                        (username, password, email))
            conn.commit()
            return jsonify({'success': True, 'message': 'Registration successful'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Username already exists'})
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        raw_password = data.get('password', '')
        
        if not username or not raw_password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and verify_password(raw_password, user['password']):
            if not is_modern_hash(user['password']):
                conn.execute(
                    'UPDATE users SET password = ? WHERE id = ?',
                    (hash_password(raw_password), user['id'])
                )
                conn.commit()
            conn.close()
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({'success': True, 'message': 'Login successful'})
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/learn')
def learn():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    lessons = conn.execute('SELECT * FROM lessons ORDER BY difficulty, created_at').fetchall()
    conn.close()
    
    return render_template('learn.html', lessons=lessons)

@app.route('/schedule')
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    sessions = conn.execute(
        'SELECT * FROM study_sessions WHERE user_id = ? ORDER BY scheduled_time DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('schedule.html', sessions=sessions)

@app.route('/practice')
def practice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('practice.html')

# API endpoints
@app.route('/api/lessons', methods=['GET', 'POST'])
def api_lessons():
    conn = get_db()
    
    if request.method == 'POST':
        data = request.get_json()
        conn.execute(
            'INSERT INTO lessons (title, description, sign_type, difficulty) VALUES (?, ?, ?, ?)',
            (data['title'], data['description'], data['sign_type'], data.get('difficulty', 'beginner'))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    lessons = conn.execute('SELECT * FROM lessons').fetchall()
    conn.close()
    return jsonify([dict(lesson) for lesson in lessons])

@app.route('/api/schedule', methods=['GET', 'POST'])
def api_schedule():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    
    if request.method == 'POST':
        data = request.get_json()
        conn.execute(
            'INSERT INTO study_sessions (user_id, topic, duration, scheduled_time, notes) VALUES (?, ?, ?, ?, ?)',
            (session['user_id'], data['topic'], data['duration'], data['scheduled_time'], data.get('notes', ''))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    sessions = conn.execute(
        'SELECT * FROM study_sessions WHERE user_id = ? ORDER BY scheduled_time',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return jsonify([dict(s) for s in sessions])

@app.route('/api/progress/<int:lesson_id>', methods=['POST'])
def update_progress(lesson_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    existing = conn.execute(
        'SELECT * FROM user_progress WHERE user_id = ? AND lesson_id = ?',
        (session['user_id'], lesson_id)
    ).fetchone()
    
    if existing:
        conn.execute(
            'UPDATE user_progress SET practice_count = practice_count + 1, last_practiced = ? WHERE user_id = ? AND lesson_id = ?',
            (datetime.now(), session['user_id'], lesson_id)
        )
    else:
        conn.execute(
            'INSERT INTO user_progress (user_id, lesson_id, practice_count, last_practiced) VALUES (?, ?, 1, ?)',
            (session['user_id'], lesson_id, datetime.now())
        )
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/stats')
def get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    
    total_sessions = conn.execute(
        'SELECT COUNT(*) as count FROM study_sessions WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    completed_sessions = conn.execute(
        'SELECT COUNT(*) as count FROM study_sessions WHERE user_id = ? AND completed = 1',
        (session['user_id'],)
    ).fetchone()['count']
    
    total_practice = conn.execute(
        'SELECT SUM(practice_count) as total FROM user_progress WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()['total'] or 0
    
    conn.close()
    
    return jsonify({
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'total_practice': total_practice
    })

@app.route('/api/complete_session/<int:session_id>', methods=['POST'])
def complete_session(session_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    conn.execute(
        'UPDATE study_sessions SET completed = 1 WHERE id = ? AND user_id = ?',
        (session_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8080))
    print(f'\n🚀 Server starting on http://0.0.0.0:{port}')
    print(f'🌐 Access from browser: http://localhost:{port}')
    print(f'📊 Database: {DATABASE} (SQLite)\n')
    app.run(host='0.0.0.0', port=port, debug=False)
