import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import json
import pickle
from pathlib import Path

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
        border-radius: 8px;
        font-weight: 600;
    }
    .post-card {
        background: rgba(59, 130, 246, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 8px;
        margin: 3px 0;
        border: 1px solid rgba(147, 197, 253, 0.3);
        cursor: pointer;
        transition: all 0.2s;
    }
    .post-card:hover {
        background: rgba(59, 130, 246, 0.5);
        border-color: rgba(147, 197, 253, 0.6);
        transform: translateY(-2px);
    }
    .post-title {
        color: white;
        font-weight: bold;
        font-size: 12px;
        margin-bottom: 3px;
        line-height: 1.3;
    }
    .calendar-day {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 8px;
        min-height: 140px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .calendar-day-empty {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        padding: 8px;
        min-height: 140px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .day-number {
        color: white;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 8px;
        text-align: center;
        padding: 4px;
        background: rgba(59, 130, 246, 0.2);
        border-radius: 8px;
    }
    .day-header {
        color: rgba(255, 255, 255, 0.9);
        font-weight: 600;
        font-size: 14px;
        text-align: center;
        padding: 12px 0;
        background: rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        margin-bottom: 10px;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }
    .platform-badge {
        font-size: 14px;
        margin-right: 4px;
    }
    a {
        color: #60a5fa !important;
        text-decoration: none !important;
    }
    a:hover {
        color: #93c5fd !important;
        text-decoration: underline !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
CONTENT_TYPES = ['Carousel', 'Video', 'Image', 'Reel', 'Story', 'Article', 'Infographic']
STATUSES = ['Draft', 'Copy Ready', 'Scheduled', 'Published']
PLATFORMS = ['Instagram', 'Facebook', 'LinkedIn', 'Twitter', 'TikTok', 'YouTube']

# File-based storage path
STORAGE_FILE = Path("calendar_data.pkl")

# Storage functions using file-based persistence
def load_posts():
    """Load posts from file storage"""
    try:
        if STORAGE_FILE.exists():
            with open(STORAGE_FILE, 'rb') as f:
                data = pickle.load(f)
                return data.get('posts', []), data.get('next_id', 1)
        return [], 1
    except Exception as e:
        st.error(f"Error loading posts: {str(e)}")
        return [], 1

def save_posts(posts, next_id):
    """Save posts to file storage"""
    try:
        with open(STORAGE_FILE, 'wb') as f:
            pickle.dump({'posts': posts, 'next_id': next_id}, f)
        return True
    except Exception as e:
        st.error(f"Error saving posts: {str(e)}")
        return False

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts, st.session_state.next_id = load_posts()

if 'next_id' not in st.session_state:
    st.session_state.next_id = 1

if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now()

if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False

if 'editing_post' not in st.session_state:
    st.session_state.editing_post = None

if 'viewing_post' not in st.session_state:
    st.session_state.viewing_post = None

def get_calendar_data(year, month):
    """Get calendar data for the given month with Sunday as first day"""
    # Set Sunday as first day of week
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    return cal

def get_posts_for_date(date_str):
    """Get all posts for a specific date"""
    return [p for p in st.session_state.posts if p['date'] == date_str]

def add_post(post_data):
    """Add a new post"""
    post_data['id'] = st.session_state.next_id
    st.session_state.posts.append(post_data)
    st.session_state.next_id += 1
    save_posts(st.session_state.posts, st.session_state.next_id)

def update_post(post_id, post_data):
    """Update an existing post"""
    for i, post in enumerate(st.session_state.posts):
        if post['id'] == post_id:
            post_data['id'] = post_id
            st.session_state.posts[i] = post_data
            break
    save_posts(st.session_state.posts, st.session_state.next_id)

def delete_post(post_id):
    """Delete a post"""
    st.session_state.posts = [p for p in st.session_state.posts if p['id'] != post_id]
    save_posts(st.session_state.posts, st.session_state.next_id)

def clear_all_posts():
    """Clear all posts from storage"""
    st.session_state.posts = []
    st.session_state.next_id = 1
    save_posts([], 1)

def import_posts(imported_posts):
    """Import posts from JSON"""
    # Reassign IDs to avoid conflicts
    for post in imported_posts:
        post['id'] = st.session_state.next_id
        st.session_state.next_id += 1
    
    st.session_state.posts.extend(imported_posts)
    save_posts(st.session_state.posts, st.session_state.next_id)

# Header
col1, col2, col3 = st.columns([2, 3, 2])
with col1:
    st.title("📅 Content Calendar")
with col3:
    if st.button("➕ New Post", type="primary", use_container_width=True):
        st.session_state.show_modal = True
        st.session_state.editing_post = None
        st.session_state.viewing_post = None
        st.rerun()

# Month navigation
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col1:
    if st.button("← Previous", use_container_width=True):
        current = st.session_state.current_date
        st.session_state.current_date = current - timedelta(days=current.day)
        st.rerun()

with nav_col2:
    st.markdown(f"<h2 style='text-align: center; color: #a855f7;'>{st.session_state.current_date.strftime('%B %Y')}</h2>", unsafe_allow_html=True)

with nav_col3:
    if st.button("Next →", use_container_width=True):
        current = st.session_state.current_date
        days_in_month = calendar.monthrange(current.year, current.month)[1]
        st.session_state.current_date = current + timedelta(days=days_in_month - current.day + 1)
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Calendar grid
year = st.session_state.current_date.year
month = st.session_state.current_date.month
cal_data = get_calendar_data(year, month)

# Day headers
days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
cols = st.columns(7)
for i, day in enumerate(days):
    with cols[i]:
        st.markdown(f"<div class='day-header'>{day}</div>", unsafe_allow_html=True)

# Calendar days
for week in cal_data:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.markdown("<div class='calendar-day-empty'></div>", unsafe_allow_html=True)
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                day_posts = get_posts_for_date(date_str)
                
                container_html = "<div class='calendar-day'>"
                container_html += f"<div class='day-number'>{day}</div>"
                st.markdown(container_html, unsafe_allow_html=True)
                
                # Add post button
                if st.button("➕", key=f"add_{date_str}", help="Add post", use_container_width=True):
                    st.session_state.show_modal = True
                    st.session_state.editing_post = None
                    st.session_state.viewing_post = None
                    st.session_state.selected_date = date_str
                    st.rerun()
                
                # Display posts as clickable cards
                for post in day_posts:
                    post_html = f"<div class='post-card'>"
                    post_html += f"<div class='post-title'>{post['title'][:35]}{'...' if len(post['title']) > 35 else ''}</div>"
                    
                    if post.get('platforms'):
                        post_html += "<div class='platform-badge'>"
                        for platform in post.get('platforms', []):
                            emoji = {'Instagram': '📷', 'Facebook': '📘', 'LinkedIn': '💼', 'Twitter': '🐦', 'TikTok': '🎵', 'YouTube': '📹'}.get(platform, '📱')
                            post_html += f"{emoji}"
                        post_html += "</div>"
                    
                    post_html += "</div>"
                    st.markdown(post_html, unsafe_allow_html=True)
                    
                    if st.button("👁️ View", key=f"view_{post['id']}", use_container_width=True):
                        st.session_state.viewing_post = post
                        st.session_state.show_modal = False
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)

# View Post Modal
if st.session_state.viewing_post and not st.session_state.show_modal:
    post = st.session_state.viewing_post
    
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📄 {post['title']}")
    with col2:
        edit_col, close_col = st.columns(2)
        with edit_col:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.editing_post = post
                st.session_state.show_modal = True
                st.session_state.viewing_post = None
                st.rerun()
        with close_col:
            if st.button("✖️ Close", use_container_width=True):
                st.session_state.viewing_post = None
                st.rerun()
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("**📅 Date:**")
        st.write(datetime.strptime(post['date'], '%Y-%m-%d').strftime('%B %d, %Y'))
        
        if post.get('content_pillar'):
            st.markdown("**🎯 Content Pillar:**")
            st.info(post['content_pillar'])
        
        if post.get('status'):
            st.markdown("**📊 Status:**")
            status_colors = {
                'Draft': '🟡',
                'Copy Ready': '🔵',
                'Scheduled': '🟠',
                'Published': '🟢'
            }
            st.write(f"{status_colors.get(post['status'], '⚪')} {post['status']}")
    
    with info_col2:
        if post.get('link'):
            st.markdown("**🔗 Link:**")
            st.markdown(f"[Open Link]({post['link']})")
        
        if post.get('content_type'):
            st.markdown("**🎨 Content Type:**")
            st.write(post['content_type'])
        
        if post.get('platforms'):
            st.markdown("**📱 Platforms:**")
            platforms_text = " ".join([
                {'Instagram': '📷', 'Facebook': '📘', 'LinkedIn': '💼', 'Twitter': '🐦', 'TikTok': '🎵', 'YouTube': '📹'}.get(p, '📱') + f" {p}"
                for p in post['platforms']
            ])
            st.write(platforms_text)
    
    if post.get('notes'):
        st.markdown("**📝 Notes:**")
        st.write(post['notes'])
    
    if post.get('comments'):
        st.markdown("**💬 Comments:**")
        st.info(post['comments'])

# Add/Edit Post Modal
if st.session_state.show_modal:
    st.markdown("---")
    if st.session_state.editing_post:
        st.subheader("✏️ Edit Post")
        post = st.session_state.editing_post
    else:
        st.subheader("➕ New Post")
        post = {}
    
    with st.form("post_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title *", value=post.get('title', ''), placeholder="e.g., Men Get Breast Cancer Too!")
            link = st.text_input("Link (Google Docs, Canva, etc.)", value=post.get('link', ''), placeholder="https://docs.google.com/...")
            date = st.date_input("Date *", value=datetime.strptime(post.get('date', st.session_state.get('selected_date', datetime.now().strftime('%Y-%m-%d'))), '%Y-%m-%d') if post.get('date') or st.session_state.get('selected_date') else datetime.now())
            content_pillar = st.text_input("Content Pillar", value=post.get('content_pillar', ''), placeholder="e.g., International Health Day, Duchess Health Tips")
        
        with col2:
            status = st.selectbox("Status", STATUSES, index=STATUSES.index(post['status']) if post.get('status') in STATUSES else 0)
            content_type = st.selectbox("Content Type", [''] + CONTENT_TYPES, index=CONTENT_TYPES.index(post['content_type'])+1 if post.get('content_type') in CONTENT_TYPES else 0)
            platforms = st.multiselect("Platforms", PLATFORMS, default=post.get('platforms', []))
        
        notes = st.text_area("Notes", value=post.get('notes', ''), height=100, placeholder="Additional details, hashtags, mentions, etc.")
        
        comments = st.text_area("Comments", value=post.get('comments', ''), height=100, placeholder="Internal comments, feedback, approvals, etc.")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            submit = st.form_submit_button("💾 Save Post", type="primary", use_container_width=True)
        with col2:
            if st.session_state.editing_post:
                delete = st.form_submit_button("🗑️ Delete", use_container_width=True)
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
                'notes': notes,
                'comments': comments
            }
            
            if st.session_state.editing_post:
                update_post(st.session_state.editing_post['id'], post_data)
                st.success("✅ Post updated!")
            else:
                add_post(post_data)
                st.success("✅ Post created!")
            
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

# Sidebar
with st.sidebar:
    # Brand logo and name
    try:
        # Try to load the logo image
        st.image("purple_crayola_logo.png", width=150)
        st.markdown("<h2 style='text-align: center; color: #7c3aed; margin: 0 0 20px 0; font-size: 28px; font-weight: 600;'>Purple Crayola</h2>", unsafe_allow_html=True)
    except:
        # Fallback if logo not found
        st.markdown("""
            <div style='text-align: center; margin-bottom: 30px;'>
                <div style='background: #7c3aed; border-radius: 20px; width: 80px; height: 80px; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;'>
                    <span style='font-size: 50px; color: white; font-weight: bold;'>P</span>
                </div>
                <h2 style='color: #7c3aed; margin: 0; font-size: 28px; font-weight: 600;'>Purple Crayola</h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("📊 Calendar Stats")
    st.metric("Total Posts", len(st.session_state.posts))
    st.success("💾 Auto-saved")
    
    if st.session_state.posts:
        status_counts = {}
        for post in st.session_state.posts:
            status = post.get('status', 'Draft')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.subheader("By Status")
        for status, count in status_counts.items():
            st.write(f"{status}: {count}")
        
        platform_counts = {}
        for post in st.session_state.posts:
            for platform in post.get('platforms', []):
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        st.subheader("By Platform")
        for platform, count in platform_counts.items():
            emoji = {'Instagram': '📷', 'Facebook': '📘', 'LinkedIn': '💼', 'Twitter': '🐦', 'TikTok': '🎵', 'YouTube': '📹'}.get(platform, '📱')
            st.write(f"{emoji} {platform}: {count}")
    
    st.markdown("---")
    st.subheader("📥 Backup")
    
    if st.button("📤 Export", use_container_width=True):
        json_data = json.dumps(st.session_state.posts, indent=2)
        st.download_button(
            label="⬇️ Download",
            data=json_data,
            file_name=f"calendar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("📂 Import", type=['json'])
    if uploaded_file is not None:
        try:
            imported_posts = json.load(uploaded_file)
            import_posts(imported_posts)
            st.success(f"✅ Imported {len(imported_posts)} posts!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    if st.button("🗑️ Clear All", use_container_width=True):
        if st.checkbox("⚠️ Confirm deletion"):
            clear_all_posts()
            st.success("✅ Cleared!")
            st.rerun()