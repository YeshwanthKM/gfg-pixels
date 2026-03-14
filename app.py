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

# In-memory blogs storage
BLOGS = [
    {
        'id': 'blog1',
        'title': 'Getting Started with Data Structures',
        'author': 'Rahul Sharma',
        'date': 'March 14, 2026',
        'description': 'An introduction to data structures and why they are important for coding interviews.'
    },
    {
        'id': 'blog2',
        'title': 'Python Tips for Competitive Programming',
        'author': 'Priya Patel',
        'date': 'March 12, 2026',
        'description': 'Learn helpful built-in functions and libraries in Python that can speed up your problem-solving.'
    }
]

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
                           total_leaders=len(leaders),
                           total_events=len(EVENTS),
                           events=EVENTS)

# Global storage for student queries
QUERIES = []

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    current_user = USERS.get(session['user'])
    if not current_user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        query = {
            'id': str(len(QUERIES) + 1),
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message'),
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        QUERIES.append(query)
        flash('Your query has been submitted successfully. The club team will review it and respond soon.', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html', user=current_user)

@app.route('/view_queries')
def view_queries():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('member_dashboard'))
        
    return render_template('view_queries.html', user=current_user, queries=QUERIES)

@app.route('/delete_query/<query_id>')
def delete_query(query_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('member_dashboard'))
    
    global QUERIES
    QUERIES = [q for q in QUERIES if q['id'] != query_id]
    flash('Query deleted successfully', 'success')
    return redirect(url_for('view_queries'))

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
        return redirect(url_for('events'))
        
    return render_template('create_event.html', user=current_user)

@app.route('/events')
def events():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
        
    return render_template('events.html', user=user, role=user['role'], events=EVENTS)

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
        
    return redirect(url_for('events'))

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
        return redirect(url_for('events'))
        
    event = EVENTS[event_id]
    
    # Get participant details
    participants = []
    for email in event['participants']:
        if email in USERS:
            participants.append({'email': email, **USERS[email]})
            
    return render_template('view_event.html', user=current_user, event=event, participants=participants)


@app.route('/club_info')
def club_info():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
    return render_template('club_info.html', user=user)

@app.route('/learning_resources')
def learning_resources():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
        
    return render_template('learning_resources.html', user=user, role=user['role'])

@app.route('/leaderboard')
def leaderboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
    
    # Get all members and sort them (mock static sort for now)
    members_list = []
    for email, data in USERS.items():
        if data['role'] == 'member':
            members_list.append(data)
    
    # For prototype, we just use the list as is and assign static ranks in template
    return render_template('leaderboard.html', user=user, members=members_list, role=user['role'])

@app.route('/blogs')
def blogs():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('blogs.html', user=user, blogs=BLOGS, role=user['role'])

@app.route('/add_blog', methods=['GET', 'POST'])
def add_blog():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        date = request.form.get('date')
        description = request.form.get('description')
        
        BLOGS.insert(0, {
            'id': str(uuid.uuid4())[:8],
            'title': title,
            'author': author,
            'date': date or datetime.now().strftime("%B %d, %Y"),
            'description': description
        })
        flash('Blog post added successfully!', 'success')
        return redirect(url_for('blogs'))
        
    return render_template('add_blog.html', user=user)

@app.route('/delete_blog/<blog_id>')
def delete_blog(blog_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    global BLOGS
    BLOGS = [blog for blog in BLOGS if blog['id'] != blog_id]
    flash('Blog post deleted.', 'success')
    return redirect(url_for('blogs'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
