from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Predefined Users
USERS = {
    'gfgleader1@gmail.com': {
        'password': 'leader123',
        'role': 'leader',
        'name': 'Rahul Sharma',
        'reg_no': '20BCE1001',
        'department': 'Computer Science'
    },
    'gfgleader2@gmail.com': {
        'password': 'leader123',
        'role': 'leader',
        'name': 'Priya Patel',
        'reg_no': '20BCE1002',
        'department': 'Information Technology'
    },
    'gfgmember1@gmail.com': {
        'password': 'member123',
        'role': 'member',
        'name': 'Amit Kumar',
        'reg_no': '21BCE2001',
        'department': 'Computer Science'
    },
    'gfgmember2@gmail.com': {
        'password': 'member123',
        'role': 'member',
        'name': 'Sneha Gupta',
        'reg_no': '21BCE2002',
        'department': 'Electronics'
    },
    'gfgmember3@gmail.com': {
        'password': 'member123',
        'role': 'member',
        'name': 'Rohan Das',
        'reg_no': '22BCE3001',
        'department': 'Mechanical'
    },
    'gfgmember4@gmail.com': {
        'password': 'member123',
        'role': 'member',
        'name': 'Neha Singh',
        'reg_no': '22BCE3002',
        'department': 'Computer Science'
    }
}

# In-memory events storage
EVENTS = {
    'evt1': {
        'title': 'Introduction to Data Structures',
        'date': '2026-03-20',
        'description': 'A workshop covering the basics of arrays, linked lists, and trees.',
        'host_email': 'gfgleader1@gmail.com',
        'participants': ['gfgmember1@gmail.com', 'gfgmember2@gmail.com']
    }
}

@app.route('/')
def index():
    if 'user' in session:
        user = USERS.get(session['user'])
        if user and user['role'] == 'leader':
            return redirect(url_for('leader_dashboard'))
        elif user and user['role'] == 'member':
            return redirect(url_for('member_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = USERS.get(email)
        if user and user['password'] == password:
            session['user'] = email
            if user['role'] == 'leader':
                return redirect(url_for('leader_dashboard'))
            else:
                return redirect(url_for('member_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/leader_dashboard')
def leader_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
        
    members = {k: v for k, v in USERS.items() if v['role'] == 'member'}
    leaders = {k: v for k, v in USERS.items() if v['role'] == 'leader'}
    
    return render_template('leader_dashboard.html', 
                           user=user, 
                           members=members, 
                           total_members=len(members),
                           total_events=len(EVENTS),
                           events=EVENTS)

@app.route('/member_dashboard')
def member_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
        
    return render_template('member_dashboard.html', user=user, email=session['user'], events=EVENTS)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        reg_no = request.form.get('reg_no')
        department = request.form.get('department')
        password = request.form.get('password')
        
        if email in USERS:
            flash('Email already exists', 'error')
        else:
            USERS[email] = {
                'name': name,
                'password': password,
                'role': 'member',
                'reg_no': reg_no,
                'department': department
            }
            flash('Member added successfully!', 'success')
            return redirect(url_for('leader_dashboard'))
            
    return render_template('add_member.html', user=current_user)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        description = request.form.get('description')
        
        event_id = str(uuid.uuid4())[:8]
        EVENTS[event_id] = {
            'title': title,
            'date': date,
            'description': description,
            'host_email': session['user'],
            'participants': []
        }
        flash('Event created successfully!', 'success')
        return redirect(url_for('leader_dashboard'))
        
    return render_template('create_event.html', user=current_user)

@app.route('/join_event/<event_id>')
def join_event(event_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'member':
        flash('Only members can join events', 'error')
        return redirect(url_for('member_dashboard'))
        
    if event_id in EVENTS:
        if session['user'] not in EVENTS[event_id]['participants']:
            EVENTS[event_id]['participants'].append(session['user'])
            flash('Successfully joined the event!', 'success')
        else:
            flash('You have already joined this event.', 'error')
    else:
        flash('Event not found.', 'error')
        
    return redirect(url_for('member_dashboard'))

@app.route('/view_event/<event_id>')
def view_event(event_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
        
    if event_id not in EVENTS:
        flash('Event not found.', 'error')
        return redirect(url_for('leader_dashboard'))
        
    event = EVENTS[event_id]
    
    # Get participant details
    participants = []
    for email in event['participants']:
        if email in USERS:
            participants.append({'email': email, **USERS[email]})
            
    return render_template('view_event.html', user=current_user, event=event, participants=participants)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
