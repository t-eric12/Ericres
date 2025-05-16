import streamlit as st
import pandas as pd
from PIL import Image
import base64
from datetime import datetime
import time
import sqlite3
import hashlib
import os
#python.exe -m streamlit run name.py
# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    
    # Users table for admin login
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT)''')
    
    # Profile table
    c.execute('''CREATE TABLE IF NOT EXISTS profile
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  location TEXT,
                  phone TEXT,
                  university TEXT,
                  field TEXT,
                  bio TEXT,
                  email TEXT,
                  github TEXT,
                  linkedin TEXT,
                  profile_pic BLOB)''')
    
    # Skills table
    c.execute('''CREATE TABLE IF NOT EXISTS skills
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  skill TEXT UNIQUE,
                  level INTEGER)''')
    
    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  type TEXT,
                  year TEXT,
                  description TEXT,
                  link TEXT,
                  image BLOB)''')
    
    # Testimonials table
    c.execute('''CREATE TABLE IF NOT EXISTS testimonials
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT,
                  author TEXT)''')
    
    # Timeline table
    c.execute('''CREATE TABLE IF NOT EXISTS timeline
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  year TEXT,
                  title TEXT,
                  description TEXT)''')
    
    # Posts table for blog
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  content TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  image BLOB)''')
    
    # Insert default admin if not exists
    try:
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  ('admin', hashed_password))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

init_db()

# Page configuration
st.set_page_config(
    page_title="Digital Portfolio",
    page_icon="👨‍🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for animations and styling
def local_css():
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        background-color: #f5f5f5;        
    }
    .title {
        text-align: center;
        color: #1E88E5;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        animation: fadeIn 1.5s;
        background-color: #454E62;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
    .subtitle {
        text-align: center;
        color: #424242;
        font-size: 1.5rem;
        margin-bottom: 2rem;
        animation: fadeIn 2s;
    }
    .profile-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        animation: fadeIn 1s;
        background-color: #f9f9f9;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .profile-image {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 1rem;
        border: 4px solid #1E88E5;
    }
    .project-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .skills-container {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        animation: fadeIn 1s;
    }
    .testimonial-card {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1E88E5;
    }
    .contact-form {
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        animation: fadeIn 1s;
    }
    .timeline-item {
        border-left: 2px solid #1E88E5;
        padding-left: 20px;
        padding-bottom: 20px;
        position: relative;
    }
    .timeline-item:before {
        content: '';
        position: absolute;
        left: -10px;
        top: 0;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background-color: #1E88E5;
    }
    .social-icons {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }
    .social-icon {
        font-size: 24px;
        color: #1E88E5;
        text-decoration: none;
    }
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
    }
    .post-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .dashboard-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Database functions
def get_profile():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT * FROM profile LIMIT 1")
    profile = c.fetchone()
    conn.close()
    
    if profile:
        return {
            'name': profile[1],
            'location': profile[2],
            'phone': profile[3],
            'university': profile[4],
            'field': profile[5],
            'bio': profile[6],
            'email': profile[7],
            'github': profile[8],
            'linkedin': profile[9],
            'profile_pic': profile[10]
        }
    else:
        # Default profile
        default_profile = {
            'name': 'TUYISENGE Eric',
            'location': 'Ruhengeri, Rwanda',
            'phone': '+250 789595211',
            'university': 'INES-Ruhengeri',
            'field': 'BSc Computer Science, Year 3',
            'bio': 'I am a passionate technology enthusiast with a focus on AI and software development. I enjoy solving complex problems and building innovative solutions.',
            'email': 'tuyisengeeric034@gmail.com',
            'github': 'https://github.com/t-eric12',
            'linkedin': 'https://linkedin.com/in/tuyisenge-eric-0b1a1b1b4',
            'profile_pic': None
        }
        # Insert default profile
        conn = sqlite3.connect('portfolio.db')
        c = conn.cursor()
        c.execute('''INSERT INTO profile 
                    (name, location, phone, university, field, bio, email, github, linkedin, profile_pic)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 tuple(default_profile.values()))
        conn.commit()
        conn.close()
        return default_profile

def update_profile(profile_data):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute('''UPDATE profile SET 
                name=?, location=?, phone=?, university=?, field=?, bio=?, email=?, github=?, linkedin=?, profile_pic=?
                WHERE id=1''',
             (profile_data['name'], profile_data['location'], profile_data['phone'], 
              profile_data['university'], profile_data['field'], profile_data['bio'], 
              profile_data['email'], profile_data['github'], profile_data['linkedin'], 
              profile_data['profile_pic']))
    conn.commit()
    conn.close()

def get_skills():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT skill, level FROM skills")
    skills = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    
    if not skills:
        # Default skills
        default_skills = {
            'Python': 75,
            'JavaScript': 65,
            'HTML/CSS': 80,
            'SQL': 70,
            'Machine Learning': 60,        
            'Web Development': 75,
            'Problem Solving': 85,
        }
        # Insert default skills
        conn = sqlite3.connect('portfolio.db')
        c = conn.cursor()
        for skill, level in default_skills.items():
            c.execute("INSERT INTO skills (skill, level) VALUES (?, ?)", (skill, level))
        conn.commit()
        conn.close()
        return default_skills
    return skills

def update_skills(skills):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("DELETE FROM skills")
    for skill, level in skills.items():
        c.execute("INSERT INTO skills (skill, level) VALUES (?, ?)", (skill, level))
    conn.commit()
    conn.close()

def get_projects():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT title, type, year, description, link, image FROM projects")
    projects = [{
        'title': row[0],
        'type': row[1],
        'year': row[2],
        'description': row[3],
        'link': row[4],
        'image': row[5]
    } for row in c.fetchall()]
    conn.close()
    
    if not projects:
        # Default projects
        default_projects = [
            {
                'title': 'Student Attendance System using Face Recognition',
                'type': 'Group Project',
                'year': 'Year 2',
                'description': 'Developed a facial recognition system for automating student attendance tracking. Used Python, OpenCV, and machine learning algorithms to identify students and record attendance automatically.',
                'link': 'https://github.com/yourusername/gracommento',
                'image': None
            },
            {
                'title': 'E-commerce Web Application',
                'type': 'Individual Project',
                'year': 'Year 1',
                'description': 'Created a responsive e-commerce platform with user authentication, product catalog, shopping cart, and payment integration. Used HTML, CSS, JavaScript, and PHP for development.',
                'link': 'https://github.com/yourusername/ecommerce-app',
                'image': None
            },
            {
                'title': 'graduate connect and mentorship AI-powered recommendation System',
                'type': 'Dissertation/Final Year Project',
                'year': 'Year 3',
                'description': 'Researching and developing an AI system that can analyze patient symptoms and medical history to suggest potential diagnoses. Utilizing machine learning, natural language processing, and medical databases for accurate results.',
                'link': 'https://github.com/yourusername/health-diagnosis-ai',
                'image': None
            }
        ]
        # Insert default projects
        conn = sqlite3.connect('portfolio.db')
        c = conn.cursor()
        for project in default_projects:
            c.execute('''INSERT INTO projects 
                        (title, type, year, description, link, image)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (project['title'], project['type'], project['year'], 
                      project['description'], project['link'], project['image']))
        conn.commit()
        conn.close()
        return default_projects
    return projects

def add_project(project):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute('''INSERT INTO projects 
                (title, type, year, description, link, image)
                VALUES (?, ?, ?, ?, ?, ?)''',
             (project['title'], project['type'], project['year'], 
              project['description'], project['link'], project['image']))
    conn.commit()
    conn.close()

def update_project(project_id, project):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute('''UPDATE projects SET 
                title=?, type=?, year=?, description=?, link=?, image=?
                WHERE id=?''',
             (project['title'], project['type'], project['year'], 
              project['description'], project['link'], project['image'], project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()

def get_testimonials():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT text, author FROM testimonials")
    testimonials = [{'text': row[0], 'author': row[1]} for row in c.fetchall()]
    conn.close()
    
    if not testimonials:
        # Default testimonials
        default_testimonials = [
            {
                'text': 'An exceptionally talented student with great attention to detail. Their work on the AI project was outstanding.',
                'author': 'mr. clement MUNYENTWARI , CEO of ikigugug group ltd'
            },
            {
                'text': 'A brilliant problem solver! Their final year project shows real innovation and technical expertise.',
                'author': 'Dr. Theodore, Project Supervisor'
            }
        ]
        # Insert default testimonials
        conn = sqlite3.connect('portfolio.db')
        c = conn.cursor()
        for testimonial in default_testimonials:
            c.execute("INSERT INTO testimonials (text, author) VALUES (?, ?)", 
                     (testimonial['text'], testimonial['author']))
        conn.commit()
        conn.close()
        return default_testimonials
    return testimonials

def add_testimonial(testimonial):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("INSERT INTO testimonials (text, author) VALUES (?, ?)", 
             (testimonial['text'], testimonial['author']))
    conn.commit()
    conn.close()

def delete_testimonial(testimonial_id):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("DELETE FROM testimonials WHERE id=?", (testimonial_id,))
    conn.commit()
    conn.close()

def get_timeline():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT year, title, description FROM timeline")
    timeline = [{'year': row[0], 'title': row[1], 'description': row[2]} for row in c.fetchall()]
    conn.close()
    
    if not timeline:
        # Default timeline
        default_timeline = [
            {
                'year': '2022',
                'title': 'University Enrollment',
                'description': 'Started BSc in Computer Science at INES-Ruhengeri'
            },
            {
                'year': '2023',
                'title': 'First Programming Competition',
                'description': 'Participated in the ikigugug group ltd'
            },
            {
                'year': '2024',
                'title': 'Internship at Tech Company',
                'description': 'Completed a 2-month internship at a leading software company'
            },
            {
                'year': '2025',
                'title': 'Dissertation Submission',
                'description': 'Working on final year project: graduate connect and mentorship AI-powered recommendation System'
            }
        ]
        # Insert default timeline
        conn = sqlite3.connect('portfolio.db')
        c = conn.cursor()
        for item in default_timeline:
            c.execute("INSERT INTO timeline (year, title, description) VALUES (?, ?, ?)", 
                     (item['year'], item['title'], item['description']))
        conn.commit()
        conn.close()
        return default_timeline
    return timeline

def add_timeline_item(item):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("INSERT INTO timeline (year, title, description) VALUES (?, ?, ?)", 
             (item['year'], item['title'], item['description']))
    conn.commit()
    conn.close()

def delete_timeline_item(item_id):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("DELETE FROM timeline WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def get_posts():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT id, title, content, created_at, image FROM posts ORDER BY created_at DESC")
    posts = [{
        'id': row[0],
        'title': row[1],
        'content': row[2],
        'created_at': row[3],
        'image': row[4]
    } for row in c.fetchall()]
    conn.close()
    return posts

def get_post(post_id):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT id, title, content, created_at, image FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()
    conn.close()
    
    if post:
        return {
            'id': post[0],
            'title': post[1],
            'content': post[2],
            'created_at': post[3],
            'image': post[4]
        }
    return None

def add_post(post):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, content, image) VALUES (?, ?, ?)", 
             (post['title'], post['content'], post['image']))
    conn.commit()
    conn.close()

def update_post(post_id, post):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("UPDATE posts SET title=?, content=?, image=? WHERE id=?", 
             (post['title'], post['content'], post['image'], post_id))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user is not None

# Session state initialization
if 'profile' not in st.session_state:
    st.session_state.profile = get_profile()

if 'skills' not in st.session_state:
    st.session_state.skills = get_skills()

if 'projects' not in st.session_state:
    st.session_state.projects = get_projects()

if 'testimonials' not in st.session_state:
    st.session_state.testimonials = get_testimonials()

if 'timeline' not in st.session_state:
    st.session_state.timeline = get_timeline()

if 'posts' not in st.session_state:
    st.session_state.posts = get_posts()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize contacts if not already present
if "contacts" not in st.session_state:
    st.session_state.contacts = []

# Now safe to use
st.metric("Contacts", len(st.session_state.contacts))

# Function to enable file downloads
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">Download {file_label}</a>'
    return href

# Navigation
def main_navigation():
    st.sidebar.title("Navigation")
    if st.session_state.logged_in:
        page = st.sidebar.radio("Go to", ["Home", "Posts", "Projects", "Skills & Achievements", 
                                         "Timeline", "Testimonials", "Contact", "Dashboard"])
    else:
        page = st.sidebar.radio("Go to", ["Home", "Posts", "Projects", "Skills & Achievements", 
                                         "Timeline", "Testimonials", "Contact","Dashboard"])
    return page

page = main_navigation()

# Home Page
if page == "Home":
    st.markdown('<h1 class="title">Digital Portfolio</h1>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="subtitle">Welcome to my professional journey</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        # Display profile image
        if st.session_state.profile['profile_pic']:
            profile_image = Image.open(st.session_state.profile['profile_pic'])
        else:
            try:
                profile_image = Image.open("AAA.jpg")
            except:
                profile_image = None
        
        if profile_image:
            st.image(profile_image, width=200, caption="")
        
        # Download resume button
        resume_file = "MIS.pdf"  # You need to have this file in your project directory
        try:
            with open(resume_file, "rb") as pdf_file:
                PDFbyte = pdf_file.read()
            st.download_button(
                label="Download Resume",
                data=PDFbyte,
                file_name="MIS.pdf",
                mime="application/pdf"
            )
        except:
            st.write("Resume PDF not available. Please upload your resume.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        st.markdown(f"# {st.session_state.profile['name']}")
        st.markdown(f"**Location**: {st.session_state.profile['location']}")
        st.markdown(f"**Phone**: {st.session_state.profile['phone']}")
        st.markdown(f"**University**: {st.session_state.profile['university']}")
        st.markdown(f"**Field of Study**: {st.session_state.profile['field']}")
        st.markdown("### About Me")
        st.markdown(st.session_state.profile['bio'])
        
        # Social media links
        st.markdown("### Connect With Me")
        st.markdown(
            f"""
            <div class="social-icons">
                <a href="{st.session_state.profile['github']}" target="_blank" class="social-icon">
                    <i class="fab fa-github"></i> GitHub
                </a>
                <a href="{st.session_state.profile['linkedin']}" target="_blank" class="social-icon">
                    <i class="fab fa-linkedin"></i> LinkedIn
                </a>
                <a href="mailto:{st.session_state.profile['email']}" class="social-icon">
                    <i class="fas fa-envelope"></i> Email
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

# Posts Page (Blog)
elif page == "Posts":
    st.markdown('<h1 class="title">My Posts</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sharing my thoughts and experiences</p>', unsafe_allow_html=True)
    
    # Display all posts
    for post in st.session_state.posts:
        st.markdown(f"""
        <div class="post-card">
            <h2>{post['title']}</h2>
            <p><small>Posted on: {post['created_at']}</small></p>
            <p>{post['content'][:200]}...</p>
            <a href="#post-{post['id']}">Read more</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed view when a post is selected
    selected_post_id = st.query_params.get("post", [None])[0]  # Updated line
    if selected_post_id:
        post = get_post(int(selected_post_id))
        if post:
            st.markdown(f"""
            <div class="post-card">
                <h2>{post['title']}</h2>
                <p><small>Posted on: {post['created_at']}</small></p>
                {f'<img src="data:image/jpeg;base64,{base64.b64encode(post["image"]).decode()}" width="300">' if post['image'] else ''}
                <p>{post['content']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Post not found")

# Projects Page
elif page == "Projects":
    st.markdown('<h1 class="title">My Projects</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Showcasing my technical journey and achievements</p>', unsafe_allow_html=True)
    
    # Project filtering
    project_categories = ["All"] + list(set([project['year'] for project in st.session_state.projects])) + \
                        list(set([project['type'] for project in st.session_state.projects]))
    
    selected_category = st.selectbox("Filter projects by:", project_categories)
    
    filtered_projects = st.session_state.projects if selected_category == "All" else \
                       [project for project in st.session_state.projects 
                        if selected_category in [project['year'], project['type']]]
    
    for project in filtered_projects:
        st.markdown(f"""
        <div class="project-card">
            <h2>{project['title']}</h2>
            <p><strong>Type:</strong> {project['type']}</p>
            <p><strong>Year:</strong> {project['year']}</p>
            <p>{project['description']}</p>
            <a href="{project['link']}" target="_blank">View Project</a>
        </div>
        """, unsafe_allow_html=True)
       
# Skills & Achievements Page
elif page == "Skills & Achievements":
    st.markdown('<h1 class="title">Skills & Achievements</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="skills-container">', unsafe_allow_html=True)
        st.markdown("### Technical Skills")
        for skill, level in st.session_state.skills.items():
            st.markdown(f"**{skill}**")
            st.progress(level/100)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="skills-container">', unsafe_allow_html=True)
        st.markdown("### Certifications & Achievements")
        st.markdown("- **Google Data Analytics Certification**")      
        st.markdown("- **Dean's List Award for Academic Excellence**")
        st.markdown("- **Best Student Project Award 2023**")
        st.markdown("- **Scholarship Recipient for Academic Excellence**")
        st.markdown('</div>', unsafe_allow_html=True)

# Timeline Page
elif page == "Timeline":
    st.markdown('<h1 class="title">My Academic Journey</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">A timeline of important milestones</p>', unsafe_allow_html=True)
    
    for item in st.session_state.timeline:
        st.markdown(f"""
        <div class="timeline-item">
            <h3>{item['year']} - {item['title']}</h3>
            <p>{item['description']}</p>
        </div>
        """, unsafe_allow_html=True)

# Testimonials Page
elif page == "Testimonials":
    st.markdown('<h1 class="title">Testimonials</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">What others say about me</p>', unsafe_allow_html=True)
    
    for testimonial in st.session_state.testimonials:
        st.markdown(f"""
        <div class="testimonial-card">
            <p style="font-style: italic;">"{testimonial['text']}"</p>
            <p style="text-align: right; font-weight: bold;">— {testimonial['author']}</p>
        </div>
        """, unsafe_allow_html=True)
    # Add admin check before showing the add testimonial form
    if not st.session_state.logged_in:
      
        st.stop()
    # Add a new testimonial
    st.markdown("### Add a New Testimonial")
    with st.form("new_testimonial"):
        new_testimonial_text = st.text_area("Testimonial")
        new_testimonial_author = st.text_input("Author")
        submit_testimonial = st.form_submit_button("Add Testimonial")
        
        if submit_testimonial and new_testimonial_text and new_testimonial_author:
            add_testimonial({
                'text': new_testimonial_text,
                'author': new_testimonial_author
            })
            st.session_state.testimonials = get_testimonials()
            st.success("Testimonial added successfully!")
            time.sleep(1)
            st.experimental_rerun()

# Contact Page
elif page == "Contact":
    st.markdown('<h1 class="title">Contact Me</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="contact-form">', unsafe_allow_html=True)
        st.markdown("### Get In Touch")
        
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Your Message")
            submit_button = st.form_submit_button("Send Message")
            
            if submit_button:
                st.success("Thank you for your message! I will get back to you soon.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="contact-form">', unsafe_allow_html=True)
        st.markdown("### Contact Information")
        st.markdown(f"**Email:** {st.session_state.profile['email']}")
        st.markdown(f"**Phone:** {st.session_state.profile['phone']}")
        st.markdown(f"**GitHub:** [{st.session_state.profile['github'].split('/')[-1]}]({st.session_state.profile['github']})")
        st.markdown(f"**LinkedIn:** [{st.session_state.profile['linkedin'].split('/')[-1]}]({st.session_state.profile['linkedin']})")
        st.markdown("**Location:** INES-Ruhengeri, Rwanda")
        st.markdown('</div>', unsafe_allow_html=True)

# Dashboard Page
elif page == "Dashboard":
    # Add logout button to sidebar
    if st.session_state.logged_in:
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    # Login modal
    if not st.session_state.logged_in and page == "Dashboard":
        with st.form("login_form"):
            st.markdown("### Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if authenticate(username, password):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    if not st.session_state.logged_in:
     
        st.stop()
    
    st.markdown('<h1 class="title">Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Dashboard stats
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.metric("Projects", len(st.session_state.projects))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.metric("Posts", len(st.session_state.posts))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.metric("Testimonials", len(st.session_state.testimonials))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.metric("Timeline Items", len(st.session_state.timeline))
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.metric("Skills", len(st.session_state.skills))
        st.markdown('</div>', unsafe_allow_html=True)
    with col6:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.metric("Contacts", len(st.session_state.contacts))
        st.markdown('</div>', unsafe_allow_html=True)        
    
    # Management tabs
    #tab1, tab2, tab3, tab4, tab5 = st.tabs(["Profile", "Projects", "Posts", "Testimonials", "Timeline"])
     # Modify the Dashboard tabs to include Contact and Skills management
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Profile", "Projects", "Posts", "Testimonials", "Timeline", "Contacts", "Skills"])

    with tab1:
        st.markdown("### Profile Management")
        with st.form("profile_management"):
            name = st.text_input("Full Name", st.session_state.profile['name'])
            location = st.text_input("Location", st.session_state.profile['location'])
            phone = st.text_input("Phone", st.session_state.profile['phone'])
            university = st.text_input("University", st.session_state.profile['university'])
            field = st.text_input("Field of Study", st.session_state.profile['field'])
            bio = st.text_area("Bio", st.session_state.profile['bio'])
            email = st.text_input("Email", st.session_state.profile['email'])
            github = st.text_input("GitHub URL", st.session_state.profile['github'])
            linkedin = st.text_input("LinkedIn URL", st.session_state.profile['linkedin'])
            
            profile_pic = st.file_uploader("Upload profile picture", type=["jpg", "jpeg", "png"])
            
            submitted = st.form_submit_button("Update Profile")
            
            if submitted:
                profile_data = {
                    'name': name,
                    'location': location,
                    'phone': phone,
                    'university': university,
                    'field': field,
                    'bio': bio,
                    'email': email,
                    'github': github,
                    'linkedin': linkedin,
                    'profile_pic': profile_pic
                }
                
                # Save profile picture if uploaded
                if profile_pic is not None:
                    with open("profile_pic.jpg", "wb") as f:
                        f.write(profile_pic.getbuffer())
                    profile_data['profile_pic'] = "profile_pic.jpg"
                else:
                    profile_data['profile_pic'] = st.session_state.profile['profile_pic']
                
                update_profile(profile_data)
                st.session_state.profile = get_profile()
                st.success("Profile updated successfully!")
    
    with tab2:
        st.markdown("### Project Management")
        
        # Add new project
        st.markdown("#### Add New Project")
        with st.form("add_project"):
            new_project_title = st.text_input("Title")
            new_project_type = st.text_input("Type")
            new_project_year = st.text_input("Year")
            new_project_description = st.text_area("Description")
            new_project_link = st.text_input("Link")
            new_project_image = st.file_uploader("Project Image", type=["jpg", "jpeg", "png"])
            
            submitted = st.form_submit_button("Add Project")
            
            if submitted:
                project = {
                    'title': new_project_title,
                    'type': new_project_type,
                    'year': new_project_year,
                    'description': new_project_description,
                    'link': new_project_link,
                    'image': new_project_image.read() if new_project_image else None
                }
                add_project(project)
                st.session_state.projects = get_projects()
                st.success("Project added successfully!")
        
        # Edit/Delete projects
        st.markdown("#### Manage Existing Projects")
        for project in st.session_state.projects:
            with st.expander(project['title']):
                with st.form(f"edit_project_{project['title']}"):
                    edited_title = st.text_input("Title", project['title'])
                    edited_type = st.text_input("Type", project['type'])
                    edited_year = st.text_input("Year", project['year'])
                    edited_description = st.text_area("Description", project['description'])
                    edited_link = st.text_input("Link", project['link'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Project"):
                            updated_project = {
                                'title': edited_title,
                                'type': edited_type,
                                'year': edited_year,
                                'description': edited_description,
                                'link': edited_link,
                                'image': project['image']
                            }
                            update_project(project['id'], updated_project)
                            st.session_state.projects = get_projects()
                            st.success("Project updated successfully!")
                    
                    with col2:
                        if st.form_submit_button("Delete Project"):
                            delete_project(project['id'])
                            st.session_state.projects = get_projects()
                            st.success("Project deleted successfully!")
    
    with tab3:
        st.markdown("### Post Management")
        
        # Add new post
        st.markdown("#### Add New Post")
        with st.form("add_post"):
            new_post_title = st.text_input("Title")
            new_post_content = st.text_area("Content")
            new_post_image = st.file_uploader("Post Image", type=["jpg", "jpeg", "png"])
            
            submitted = st.form_submit_button("Add Post")
            
            if submitted:
                post = {
                    'title': new_post_title,
                    'content': new_post_content,
                    'image': new_post_image.read() if new_post_image else None
                }
                add_post(post)
                st.session_state.posts = get_posts()
                st.success("Post added successfully!")
        
        # Edit/Delete posts
        st.markdown("#### Manage Existing Posts")
        for post in st.session_state.posts:
            with st.expander(post['title']):
                with st.form(f"edit_post_{post['id']}"):
                    edited_title = st.text_input("Title", post['title'])
                    edited_content = st.text_area("Content", post['content'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Post"):
                            updated_post = {
                                'title': edited_title,
                                'content': edited_content,
                                'image': post['image']
                            }
                            update_post(post['id'], updated_post)
                            st.session_state.posts = get_posts()
                            st.success("Post updated successfully!")
                    
                    with col2:
                        if st.form_submit_button("Delete Post"):
                            delete_post(post['id'])
                            st.session_state.posts = get_posts()
                            st.success("Post deleted successfully!")
    
    with tab4:
        st.markdown("### Testimonial Management")
        
        # Add new testimonial
        st.markdown("#### Add New Testimonial")
        with st.form("add_testimonial"):
            new_testimonial_text = st.text_area("Testimonial Text")
            new_testimonial_author = st.text_input("Author")
            
            submitted = st.form_submit_button("Add Testimonial")
            
            if submitted:
                testimonial = {
                    'text': new_testimonial_text,
                    'author': new_testimonial_author
                }
                add_testimonial(testimonial)
                st.session_state.testimonials = get_testimonials()
                st.success("Testimonial added successfully!")
        
        # Delete testimonials
        st.markdown("#### Manage Existing Testimonials")
        for testimonial in st.session_state.testimonials:
            with st.expander(testimonial['author']):
                st.markdown(f'"{testimonial["text"]}"')
                if st.button(f"Delete Testimonial from {testimonial['author']}"):
                    delete_testimonial(testimonial['id'])
                    st.session_state.testimonials = get_testimonials()
                    st.success("Testimonial deleted successfully!")
    
    with tab5:
        st.markdown("### Timeline Management")
        
        # Add new timeline item
        st.markdown("#### Add New Timeline Item")
        with st.form("add_timeline_item"):
            new_item_year = st.text_input("Year")
            new_item_title = st.text_input("Title")
            new_item_description = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Timeline Item")
            
            if submitted:
                item = {
                    'year': new_item_year,
                    'title': new_item_title,
                    'description': new_item_description
                }
                add_timeline_item(item)
                st.session_state.timeline = get_timeline()
                st.success("Timeline item added successfully!")
        
        # Delete timeline items
        st.markdown("#### Manage Existing Timeline Items")
        for item in st.session_state.timeline:
            with st.expander(f"{item['year']} - {item['title']}"):
                st.markdown(item['description'])
                if st.button(f"Delete {item['year']} - {item['title']}"):
                    delete_timeline_item(item['id'])
                    st.session_state.timeline = get_timeline()
                    st.success("Timeline item deleted successfully!")
 # Modify the get_contacts function
        def get_contacts():
            conn = sqlite3.connect('portfolio.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS contacts
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          email TEXT,
                          message TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          replied INTEGER DEFAULT 0)''')
            c.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            contacts = [{
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'message': row[3],
                'created_at': row[4],
                'replied': row[5]
            } for row in c.fetchall()]
            conn.close()
            return contacts

        def mark_contact_replied(contact_id):
            conn = sqlite3.connect('portfolio.db')
            c = conn.cursor()
            c.execute("UPDATE contacts SET replied = 1 WHERE id = ?", (contact_id,))
            conn.commit()
            conn.close()

        def add_skill(skill, level):
            conn = sqlite3.connect('portfolio.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO skills (skill, level) VALUES (?, ?)", (skill, level))
                conn.commit()
            except sqlite3.IntegrityError:
                c.execute("UPDATE skills SET level = ? WHERE skill = ?", (level, skill))
                conn.commit()
            conn.close()

        def delete_skill(skill):
            conn = sqlite3.connect('portfolio.db')
            c = conn.cursor()
            c.execute("DELETE FROM skills WHERE skill = ?", (skill,))
            conn.commit()
            conn.close()

       
        # Add these inside the Dashboard section after the Timeline tab
        with tab6:
            st.markdown("### Contact Messages")
            contacts = get_contacts()
            
            for contact in contacts:
                with st.expander(f"From: {contact['name']} ({contact['email']})"):
                    st.write(f"Message: {contact['message']}")
                    st.write(f"Received: {contact['created_at']}")
                    status = "Replied" if contact['replied'] else "Not Replied"
                    st.write(f"Status: {status}")
                    
                    if not contact['replied']:
                        if st.button(f"Mark as Replied - {contact['id']}"):
                            mark_contact_replied(contact['id'])
                            st.success("Marked as replied!")
                            time.sleep(1)
                            st.rerun()

        with tab7:
            st.markdown("### Skills Management")
            
            # Add new skill
            with st.form("add_skill"):
                new_skill = st.text_input("Skill Name")
                skill_level = st.slider("Skill Level", 0, 100, 50)
                if st.form_submit_button("Add/Update Skill"):
                    add_skill(new_skill, skill_level)
                    st.session_state.skills = get_skills()
                    st.success("Skill added/updated successfully!")
            
            # Manage existing skills
            st.markdown("#### Current Skills")
            for skill, level in st.session_state.skills.items():
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.write(skill)
                with col2:
                    st.progress(level/100)
                with col3:
                    if st.button(f"Delete {skill}"):
                        delete_skill(skill)
                        st.session_state.skills = get_skills()
                        st.success(f"Deleted {skill}")
                        st.rerun()
# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; background-color: #f5f5f5; border-radius: 10px;">
    <p>&copy; 2025 - Digital Portfolio | Created by TUYISENGE Eric</p>
</div>
""", unsafe_allow_html=True)