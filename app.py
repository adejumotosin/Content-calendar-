import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import json

# Page configuration
st.set_page_config(
    page_title="Social Media Content Calendar",
    page_icon="📅",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1e293b 0%, #1e40af 50%, #1e293b 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    .post-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .post-title {
        color: white;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 5px;
    }
    .post-pillar {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        margin: 2px 0;
    }
    .pillar-health {
        background: rgba(147, 51, 234, 0.3);
        color: #e9d5ff;
    }
    .pillar-duchess {
        background: rgba(6, 182, 212, 0.3);
        color: #a5f3fc;
    }
    .pillar-product {
        background: rgba(59, 130, 246, 0.3);
        color: #bfdbfe;
    }
    .pillar-info {
        background: rgba(34, 197, 94, 0.3);
        color: #bbf7d0;
    }
    .calendar-day {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 10px;
        min-height: 120px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .day-number {
        color: white;
        font-weight: bold;
        font-size: 16px;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
CONTENT_PILLARS = ['International Health Day', 'Duchess Health Tips', 'Product', 'Info']
CONTENT_TYPES = ['Carousel', 'Video', 'Image', 'Reel', 'Story']
STATUSES = ['Draft', 'Copy Ready', 'Scheduled', 'Published']
PLATFORMS = ['Instagram', 'Facebook', 'LinkedIn', 'Twitter']

PILLAR_CLASSES = {
    'International Health Day': 'pillar-health',
    'Duchess Health Tips': 'pillar-duchess',
    'Product': 'pillar-product',
    'Info': 'pillar-info'
}

# Storage functions using Streamlit's persistent storage
def load_posts():
    """Load posts from persistent storage"""
    try:
        result = st.storage.get('calendar_posts')
        if result and result.get('value'):
            return json.loads(result['value'])
        return []
    except Exception as e:
        st.error(f"Error loading posts: {str(e)}")
        return []

def save_posts(posts):
    """Save posts to persistent storage"""
    try:
        st.storage.set('calendar_posts', json.dumps(posts))
        return True
    except Exception as e:
        st.error(f"Error saving posts: {str(e)}")
        return False

def get_next_post_id():
    """Get the next available post ID"""
    try:
        result = st.storage.get('next_post_id')
        if result and result.get('value'):
            return int(result['value'])
        return 1
    except Exception:
        return 1

def set_next_post_id(post_id):
    """Set the next post ID"""
    try:
        st.storage.set('next_post_id', str(post_id))
    except Exception as e:
        st.error(f"Error setting post ID: {str(e)}")

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts = load_posts()

if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now()

if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False

if 'editing_post' not in st.session_state:
    st.session_state.editing_post = None

def get_calendar_data(year, month):
    """Get calendar data for the given month"""
    cal = calendar.monthcalendar(year, month)
    return cal

def get_posts_for_date(date_str):
    """Get all posts for a specific date"""
    return [p for p in st.session_state.posts if p['date'] == date_str]

def add_post(post_data):
    """Add a new post"""
    next_id = get_next_post_id()
    post_data['id'] = next_id
    st.session_state.posts.append(post_data)
    set_next_post_id(next_id + 1)
    save_posts(st.session_state.posts)

def update_post(post_id, post_data):
    """Update an existing post"""
    for i, post in enumerate(st.session_state.posts):
        if post['id'] == post_id:
            post_data['id'] = post_id
            st.session_state.posts[i] = post_data
            break
    save_posts(st.session_state.posts)

def delete_post(post_id):
    """Delete a post"""
    st.session_state.posts = [p for p in st.session_state.posts if p['id'] != post_id]
    save_posts(st.session_state.posts)

def clear_all_posts():
    """Clear all posts from storage"""
    st.session_state.posts = []
    save_posts([])
    set_next_post_id(1)

def import_posts(imported_posts):
    """Import posts from JSON"""
    # Reassign IDs to avoid conflicts
    next_id = get_next_post_id()
    for post in imported_posts:
        post['id'] = next_id
        next_id += 1
    
    st.session_state.posts.extend(imported_posts)
    set_next_post_id(next_id)
    save_posts(st.session_state.posts)

# Header
col1, col2, col3 = st.columns([2, 3, 2])
with col1:
    st.title("📅 Content Calendar")
with col3:
    if st.button("➕ New Post", type="primary"):
        st.session_state.show_modal = True
        st.session_state.editing_post = None
        st.rerun()

# Month navigation
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col1:
    if st.button("← Previous Month"):
        current = st.session_state.current_date
        st.session_state.current_date = current - timedelta(days=current.day)
        st.rerun()

with nav_col2:
    st.markdown(f"<h2 style='text-align: center; color: white;'>{st.session_state.current_date.strftime('%B %Y')}</h2>", unsafe_allow_html=True)

with nav_col3:
    if st.button("Next Month →"):
        current = st.session_state.current_date
        days_in_month = calendar.monthrange(current.year, current.month)[1]
        st.session_state.current_date = current + timedelta(days=days_in_month - current.day + 1)
        st.rerun()

# Calendar grid
year = st.session_state.current_date.year
month = st.session_state.current_date.month
cal_data = get_calendar_data(year, month)

# Day headers
days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
cols = st.columns(7)
for i, day in enumerate(days):
    with cols[i]:
        st.markdown(f"<div style='text-align: center; color: white; font-weight: bold; padding: 10px;'>{day}</div>", unsafe_allow_html=True)

# Calendar days
for week in cal_data:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.markdown("<div class='calendar-day'></div>", unsafe_allow_html=True)
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                day_posts = get_posts_for_date(date_str)
                
                # Day number and add button
                day_header_col1, day_header_col2 = st.columns([2, 1])
                with day_header_col1:
                    st.markdown(f"<div class='day-number'>{day}</div>", unsafe_allow_html=True)
                with day_header_col2:
                    if st.button("➕", key=f"add_{date_str}", help="Add post"):
                        st.session_state.show_modal = True
                        st.session_state.editing_post = None
                        st.session_state.selected_date = date_str
                        st.rerun()
                
                # Display posts
                for post in day_posts:
                    with st.container():
                        post_html = f"""
                        <div class='post-card'>
                            <div class='post-title'>{post['title'][:30]}...</div>
                        """
                        if post.get('content_pillar'):
                            pillar_class = PILLAR_CLASSES.get(post['content_pillar'], '')
                            post_html += f"<div class='post-pillar {pillar_class}'>{post['content_pillar']}</div>"
                        
                        post_html += "<div style='margin-top: 5px;'>"
                        for platform in post.get('platforms', []):
                            emoji = {'Instagram': '📷', 'Facebook': '📘', 'LinkedIn': '💼', 'Twitter': '🐦'}.get(platform, '📱')
                            post_html += f"<span style='margin-right: 5px;'>{emoji}</span>"
                        post_html += "</div></div>"
                        
                        st.markdown(post_html, unsafe_allow_html=True)
                        
                        if st.button("✏️", key=f"edit_{post['id']}", help="Edit post"):
                            st.session_state.show_modal = True
                            st.session_state.editing_post = post
                            st.rerun()

# Modal for adding/editing posts
if st.session_state.show_modal:
    with st.container():
        st.markdown("---")
        if st.session_state.editing_post:
            st.subheader("✏️ Edit Post")
            post = st.session_state.editing_post
        else:
            st.subheader("➕ New Post")
            post = {}
        
        with st.form("post_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title *", value=post.get('title', ''))
                link = st.text_input("Link (Google Docs, etc.)", value=post.get('link', ''))
                date = st.date_input("Date *", value=datetime.strptime(post.get('date', st.session_state.get('selected_date', datetime.now().strftime('%Y-%m-%d'))), '%Y-%m-%d') if post.get('date') or st.session_state.get('selected_date') else datetime.now())
                content_pillar = st.selectbox("Content Pillar", [''] + CONTENT_PILLARS, index=CONTENT_PILLARS.index(post['content_pillar'])+1 if post.get('content_pillar') in CONTENT_PILLARS else 0)
            
            with col2:
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(post['status']) if post.get('status') in STATUSES else 0)
                content_type = st.selectbox("Content Type", [''] + CONTENT_TYPES, index=CONTENT_TYPES.index(post['content_type'])+1 if post.get('content_type') in CONTENT_TYPES else 0)
                platforms = st.multiselect("Platforms", PLATFORMS, default=post.get('platforms', []))
            
            notes = st.text_area("Notes", value=post.get('notes', ''), height=100)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                submit = st.form_submit_button("💾 Save Post", type="primary", use_container_width=True)
            with col2:
                if st.session_state.editing_post:
                    delete = st.form_submit_button("🗑️ Delete", type="secondary", use_container_width=True)
                else:
                    delete = False
            with col3:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submit and title:
                post_data = {
                    'title': title,
                    'link': link,
                    'date': date.strftime('%Y-%m-%d'),
                    'content_pillar': content_pillar,
                    'status': status,
                    'content_type': content_type,
                    'platforms': platforms,
                    'notes': notes
                }
                
                if st.session_state.editing_post:
                    update_post(st.session_state.editing_post['id'], post_data)
                    st.success("✅ Post updated and saved!")
                else:
                    add_post(post_data)
                    st.success("✅ Post created and saved!")
                
                st.session_state.show_modal = False
                st.session_state.editing_post = None
                if 'selected_date' in st.session_state:
                    del st.session_state.selected_date
                st.rerun()
            
            if delete:
                delete_post(st.session_state.editing_post['id'])
                st.session_state.show_modal = False
                st.session_state.editing_post = None
                st.success("✅ Post deleted!")
                st.rerun()
            
            if cancel:
                st.session_state.show_modal = False
                st.session_state.editing_post = None
                if 'selected_date' in st.session_state:
                    del st.session_state.selected_date
                st.rerun()

# Sidebar with analytics
with st.sidebar:
    st.header("📊 Calendar Stats")
    st.metric("Total Posts", len(st.session_state.posts))
    
    # Storage status indicator
    st.info("💾 Data is automatically saved")
    
    if st.session_state.posts:
        # Status breakdown
        status_counts = {}
        for post in st.session_state.posts:
            status = post.get('status', 'Draft')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.subheader("By Status")
        for status, count in status_counts.items():
            st.write(f"{status}: {count}")
        
        # Platform breakdown
        platform_counts = {}
        for post in st.session_state.posts:
            for platform in post.get('platforms', []):
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        st.subheader("By Platform")
        for platform, count in platform_counts.items():
            emoji = {'Instagram': '📷', 'Facebook': '📘', 'LinkedIn': '💼', 'Twitter': '🐦'}.get(platform, '📱')
            st.write(f"{emoji} {platform}: {count}")
    
    st.markdown("---")
    st.subheader("📥 Backup & Restore")
    
    # Export
    if st.button("📤 Export Backup", use_container_width=True):
        json_data = json.dumps(st.session_state.posts, indent=2)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name=f"calendar_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Import
    uploaded_file = st.file_uploader("📂 Import Backup", type=['json'])
    if uploaded_file is not None:
        try:
            imported_posts = json.load(uploaded_file)
            import_posts(imported_posts)
            st.success(f"✅ Imported {len(imported_posts)} posts!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error importing file: {str(e)}")
    
    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    if st.button("🗑️ Clear All Posts", use_container_width=True, type="secondary"):
        if st.checkbox("⚠️ I understand this will delete ALL posts permanently"):
            clear_all_posts()
            st.success("✅ All posts cleared!")
            st.rerun()