from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import uuid
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "PLACEHOLDER_KEY"))

# Predefined Users
USERS = {
    'leader1@gmail.com': {
        'password': 'leader123',
        'role': 'leader',
        'name': 'Rahul Sharma',
        'reg_no': '20BCE1001',
        'department': 'Computer Science'
    },
    'leader2@gmail.com': {
        'password': 'leader123',
        'role': 'leader',
        'name': 'Priya Patel',
        'reg_no': '20BCE1002',
        'department': 'Information Technology'
    },
    'member1@gmail.com': {
        'password': 'member123',
        'role': 'member',
        'name': 'Amit Kumar',
        'reg_no': '21BCE2001',
        'department': 'Computer Science'
    },
    'member2@gmail.com': {
        'password': 'member123',
        'role': 'member',
        'name': 'Sneha Gupta',
        'reg_no': '21BCE2002',
        'department': 'Electronics'
    },
    'member3@gmail.com': {
        'password': 'member123',
        'role': 'member',
        'name': 'Rohan Das',
        'reg_no': '20BCE3001',
        'department': 'Mechanical'
    },
    'member4@gmail.com': {
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
        'title': 'Welcome Mixer & Orientation',
        'date': '2026-03-20',
        'description': 'An introductory session for new members to learn about our club\'s goals and upcoming activities.',
        'host_email': 'leader1@gmail.com',
        'participants': ['member1@gmail.com', 'member2@gmail.com']
    }
}

# In-memory blogs storage
BLOGS = [
    {
        'id': 'blog1',
        'title': 'How to Make the Most of Your Club Membership',
        'author': 'Rahul Sharma',
        'date': 'March 14, 2026',
        'description': 'Learn about the various opportunities and resources available to you as a member of the SCM System.'
    },
    {
        'id': 'blog2',
        'title': 'Effective Leadership and Coordination',
        'author': 'Priya Patel',
        'date': 'March 12, 2026',
        'description': 'A guide for leaders and active members on how to organize successful club events and activities.'
    }
]

# In-memory projects storage
PROJECTS = {}

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

@app.route('/edit_member/<email>', methods=['GET', 'POST'])
def edit_member(email):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
        
    member = USERS.get(email)
    if not member:
        flash('Member not found', 'error')
        return redirect(url_for('leader_dashboard'))
        
    if request.method == 'POST':
        member['name'] = request.form.get('name')
        member['reg_no'] = request.form.get('reg_no')
        member['department'] = request.form.get('department')
        member['password'] = request.form.get('password')
        
        flash('Member details updated successfully!', 'success')
        return redirect(url_for('leader_dashboard'))
        
    return render_template('edit_member.html', user=current_user, member=member, member_email=email)

@app.route('/delete_member/<email>')
def delete_member(email):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_user = USERS.get(session['user'])
    if not current_user or current_user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
        
    if email in USERS:
        del USERS[email]
        flash('Member removed successfully!', 'success')
    else:
        flash('Member not found', 'error')
        
    return redirect(url_for('leader_dashboard'))

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
        
    return render_template('events.html', user=user, email=session['user'], role=user['role'], events=EVENTS)

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
    if not current_user:
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


@app.route('/submit_project', methods=['GET', 'POST'])
def submit_project():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        tech_used = request.form.get('tech_used')
        demo_link = request.form.get('demo_link')
        
        project_id = str(uuid.uuid4())[:8]
        PROJECTS[project_id] = {
            'title': title,
            'description': description,
            'key_focus': tech_used,
            'demo_link': demo_link,
            'submitter_email': session['user'],
            'submitter_name': user['name'],
            'department': user['department'],
            'date': datetime.now().strftime("%B %d, %Y"),
            'status': 'Pending Review'
        }
        flash('Your project has been submitted for leader review.', 'success')
        return redirect(url_for('my_submissions'))
        
    return render_template('submit_project.html', user=user, role=user['role'])

@app.route('/my_submissions')
def my_submissions():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
    
    my_projects = {pid: p for pid, p in PROJECTS.items() if p['submitter_email'] == session['user']}
    return render_template('my_submissions.html', user=user, projects=my_projects, role=user['role'])

@app.route('/project_reviews')
def project_reviews():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    return render_template('project_reviews.html', user=user, projects=PROJECTS, role=user['role'])

@app.route('/community_showcase')
def community_showcase():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user:
        return redirect(url_for('login'))
    
    published_projects = {pid: p for pid, p in PROJECTS.items() if p['status'] == 'Published'}
    return render_template('community_showcase.html', user=user, projects=published_projects, role=user['role'])

@app.route('/approve_project/<project_id>')
def approve_project(project_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    if project_id in PROJECTS:
        PROJECTS[project_id]['status'] = 'Approved'
        flash(f"Project '{PROJECTS[project_id]['title']}' approved.", 'success')
    return redirect(url_for('project_reviews'))

@app.route('/reject_project/<project_id>')
def reject_project(project_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    if project_id in PROJECTS:
        PROJECTS[project_id]['status'] = 'Rejected'
        flash(f"Project '{PROJECTS[project_id]['title']}' rejected.", 'success')
    return redirect(url_for('project_reviews'))

@app.route('/publish_project/<project_id>')
def publish_project(project_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    if project_id in PROJECTS:
        PROJECTS[project_id]['status'] = 'Published'
        flash(f"Project '{PROJECTS[project_id]['title']}' published to showcase.", 'success')
    return redirect(url_for('project_reviews'))

@app.route('/unpublish_project/<project_id>')
def unpublish_project(project_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    if project_id in PROJECTS:
        PROJECTS[project_id]['status'] = 'Approved'
        flash(f"Project '{PROJECTS[project_id]['title']}' removed from showcase.", 'success')
    return redirect(url_for('community_showcase'))

@app.route('/delete_project/<project_id>')
def delete_project(project_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = USERS.get(session['user'])
    if not user or user['role'] != 'leader':
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))
    
    if project_id in PROJECTS:
        title = PROJECTS[project_id]['title']
        del PROJECTS[project_id]
        flash(f"Project '{title}' removed.", 'success')
    return redirect(url_for('project_reviews'))


@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_data = USERS.get(session['user'])
    if not user_data:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are the official AI Assistant for the Smart Club Management System (SCM System). "
                               f"You help students and leaders manage their club activities and coordination. "
                               f"The user you are talking to is {user_data['name']}, a {user_data['role']} in the {user_data['department']} department. "
                               f"Be helpful, professional, and concise. "
                               f"**CRITICAL: Do NOT use Markdown formatting like asterisks (**) for bolding or headers.** "
                               f"Instead, use clear line breaks, capital letters for headings, and simple plain-text bullet points (*) for organization."
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=False
        )
        return jsonify({'response': completion.choices[0].message.content})
    except Exception as e:
        print(f"Chat Error: {str(e)}")
        return jsonify({'error': "Assistant is currently resting. Please check API key."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
