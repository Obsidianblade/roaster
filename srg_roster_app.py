import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
import base64
from streamlit_calendar import calendar
import streamlit.components.v1 as components

# --- Helper Functions ---
def set_page_container_style():
    """Set the overall page container styles for a professional look."""
    st.markdown("""
        <style>
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 1200px;
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            ::-webkit-scrollbar-track {
                background: #f1f5f9;
                border-radius: 5px;
            }
            ::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 5px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #94a3b8;
            }
        </style>
    """, unsafe_allow_html=True)


def set_background(image_path):
    """Set the app background using a local image with proper overlay."""
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
        <style>
            .stApp {{
                background: linear-gradient(rgba(249, 250, 251, 0.92), rgba(249, 250, 251, 0.94)), 
                            url("data:image/png;base64,{b64}") no-repeat center center fixed;
                background-size: cover;
            }}
        </style>
    """, unsafe_allow_html=True)


def create_modern_header():
    """Create a modern header with logo and title."""
    header_container = st.container()
    with header_container:
        cols = st.columns([1, 6, 1])
        with cols[0]:
            st.image("VU LOGO.png", width=60)
        with cols[1]:
            st.markdown("""
                <h1 style="color: #0f172a; margin-bottom: 0; padding-bottom: 0; font-size: 28px; font-weight: 600;">
                    SRG Roster Management System
                </h1>
                <p style="color: #64748b; margin-top: 0; padding-top: 0; font-size: 15px;">
                    Efficiently manage student resource schedules
                </p>
            """, unsafe_allow_html=True)
    return header_container


def get_time_options():
    """Return 30-minute interval times in 12-hour format."""
    opts = []
    for h in range(6, 22):
        for m in (0, 30):
            t = time(h, m)
            s = t.strftime("%I:%M %p").lstrip("0")
            opts.append(s)
    return opts


def create_nav_menu():
    """Create a modern horizontal navigation menu."""
    nav_html = """
    <nav style="background-color: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
                margin-bottom: 20px; padding: 5px 15px;">
        <ul style="display: flex; list-style-type: none; padding: 0; margin: 0; align-items: center;">
            <li style="margin-right: 15px;">
                <a href="?page=home" id="home-link" 
                   style="text-decoration: none; color: #64748b; padding: 10px 15px; display: inline-block; 
                   border-radius: 6px; font-weight: 500;">
                   <span style="margin-right: 5px;">🏠</span>Home
                </a>
            </li>
            <li style="margin-right: 15px;">
                <a href="?page=student" id="student-link" 
                   style="text-decoration: none; color: #64748b; padding: 10px 15px; display: inline-block; 
                   border-radius: 6px; font-weight: 500;">
                   <span style="margin-right: 5px;">🧑‍🎓</span>Student Portal
                </a>
            </li>
            <li>
                <a href="?page=lecturer" id="lecturer-link" 
                   style="text-decoration: none; color: #64748b; padding: 10px 15px; display: inline-block; 
                   border-radius: 6px; font-weight: 500;">
                   <span style="margin-right: 5px;">👩‍🏫</span>Lecturer Portal
                </a>
            </li>
        </ul>
    </nav>
    
    <script>
        // Get the current page from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const page = urlParams.get('page') || 'home';
        
        // Highlight the active link
        document.getElementById(page + '-link').style.backgroundColor = '#f1f5f9';
        document.getElementById(page + '-link').style.color = '#0f172a';
    </script>
    """
    st.markdown(nav_html, unsafe_allow_html=True)


def create_card(title, content, icon=None, button=None, button_link=None):
    """Create a professional card component with optional icon and button."""
    icon_html = f'<span style="font-size: 24px; margin-right: 10px;">{icon}</span>' if icon else ''
    button_html = f'''
    <a href="{button_link}" style="display: inline-block; margin-top: 15px; padding: 8px 16px; 
        background-color: #3b82f6; color: white; text-decoration: none; 
        border-radius: 6px; font-size: 14px; font-weight: 500;">
        {button}
    </a>
    ''' if button else ''
    
    card_html = f'''
    <div style="background-color: white; border-radius: 8px; padding: 20px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            {icon_html}
            <h3 style="margin: 0; color: #0f172a; font-size: 18px; font-weight: 600;">{title}</h3>
        </div>
        <div style="color: #334155; font-size: 15px;">
            {content}
        </div>
        {button_html}
    </div>
    '''
    return st.markdown(card_html, unsafe_allow_html=True)


def create_stats_card(label, value, delta=None, color="#3b82f6"):
    """Create a professional statistics card."""
    delta_html = ''
    if delta:
        delta_color = "#16a34a" if float(delta) >= 0 else "#dc2626"
        delta_icon = "↑" if float(delta) >= 0 else "↓"
        delta_html = f'''
        <div style="color: {delta_color}; font-size: 14px; margin-top: 5px;">
            {delta_icon} {delta}%
        </div>
        '''
    
    card_html = f'''
    <div style="background-color: white; border-radius: 8px; padding: 20px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 100%;">
        <div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">
            {label}
        </div>
        <div style="font-size: 24px; font-weight: 600; color: #0f172a;">
            {value}
        </div>
        {delta_html}
    </div>
    '''
    return st.markdown(card_html, unsafe_allow_html=True)


def render_user_card(name, role, status="Active"):
    """Create a user profile card."""
    status_color = "#16a34a" if status == "Active" else "#dc2626"
    html = f'''
    <div style="display: flex; align-items: center; background-color: white; 
            border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
            margin-bottom: 15px;">
        <div style="width: 40px; height: 40px; border-radius: 50%; 
                background-color: #e2e8f0; display: flex; justify-content: center; 
                align-items: center; margin-right: 15px; font-size: 16px; 
                color: #64748b; font-weight: 500;">
            {name[0]}
        </div>
        <div style="flex-grow: 1;">
            <div style="font-weight: 500; color: #0f172a;">{name}</div>
            <div style="font-size: 14px; color: #64748b;">{role}</div>
        </div>
        <div style="padding: 4px 8px; background-color: rgba(22, 163, 74, 0.1); 
                border-radius: 4px; font-size: 12px; color: {status_color};">
            {status}
        </div>
    </div>
    '''
    return st.markdown(html, unsafe_allow_html=True)


def create_tab_navigation(tabs):
    """Create professional-looking tab navigation."""
    tab_html = '''
    <div style="display: flex; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0;">
    '''
    
    for i, tab in enumerate(tabs):
        tab_id = tab.lower().replace(' ', '-')
        active_class = 'active-tab' if i == 0 else ''
        tab_html += f'''
        <div id="{tab_id}-tab" 
             onclick="switchTab('{tab_id}')" 
             class="custom-tab {active_class}"
             style="padding: 10px 20px; cursor: pointer; color: #64748b; 
                    font-weight: 500; position: relative;">
            {tab}
        </div>
        '''
    
    tab_html += '''
    </div>
    
    <style>
        .custom-tab.active-tab {
            color: #3b82f6 !important;
            font-weight: 600 !important;
        }
        
        .custom-tab.active-tab::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 100%;
            height: 2px;
            background-color: #3b82f6;
        }
        
        .custom-tab:hover {
            color: #3b82f6 !important;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
    </style>
    
    <script>
        function switchTab(tabId) {
            // Hide all tab contents
            const tabContents = document.getElementsByClassName('tab-content');
            for (let i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            // Remove active class from all tabs
            const tabs = document.getElementsByClassName('custom-tab');
            for (let i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active-tab');
            }
            
            // Show selected tab content and mark tab as active
            document.getElementById(tabId + '-content').classList.add('active');
            document.getElementById(tabId + '-tab').classList.add('active-tab');
        }
    </script>
    '''
    
    st.markdown(tab_html, unsafe_allow_html=True)
    
    # Create content containers for each tab
    for tab in tabs:
        tab_id = tab.lower().replace(' ', '-')
        display = "block" if tab == tabs[0] else "none"
        st.markdown(f'''
        <div id="{tab_id}-content" class="tab-content {'active' if tab == tabs[0] else ''}" 
             style="display: {display};">
        </div>
        ''', unsafe_allow_html=True)


def render_button(label, action=None, color="primary", size="medium", full_width=False):
    """Create a professional button with different color options."""
    colors = {
        "primary": "#3b82f6",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "info": "#06b6d4"
    }
    
    sizes = {
        "small": "padding: 6px 12px; font-size: 14px;",
        "medium": "padding: 8px 16px; font-size: 15px;",
        "large": "padding: 10px 20px; font-size: 16px;"
    }
    
    bg_color = colors.get(color, "#3b82f6")
    size_style = sizes.get(size, sizes["medium"])
    width = "width: 100%;" if full_width else ""
    
    return st.markdown(f'''
    <button
        onclick="{action if action else ''}"
        style="background-color: {bg_color}; color: white; border: none; 
               border-radius: 6px; font-weight: 500; cursor: pointer;
               {size_style} {width} transition: all 0.2s ease;
               box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        {label}
    </button>
    ''', unsafe_allow_html=True)


def create_input_group(label, input_type="text", id=None, placeholder=None):
    """Create a professional form input group."""
    html = f'''
    <div style="margin-bottom: 15px;">
        <label style="display: block; font-size: 14px; color: #334155; 
                       margin-bottom: 5px; font-weight: 500;"
               for="{id}">
            {label}
        </label>
        <input type="{input_type}" 
               id="{id}" 
               name="{id}" 
               placeholder="{placeholder if placeholder else ''}"
               style="display: block; width: 100%; padding: 8px 12px;
                      border-radius: 6px; border: 1px solid #cbd5e1;
                      background-color: #f8fafc; font-size: 15px;
                      color: #0f172a; transition: all 0.2s ease;">
    </div>
    '''
    return st.markdown(html, unsafe_allow_html=True)


# --- Page Setup ---
st.set_page_config(page_title="SRG Roster Manager", layout="wide")
set_page_container_style()
set_background("VUCOVER.png")

# Modern Professional UI Styling
st.markdown("""
    <style>
        /* Base styling */
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                         Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #0f172a;
            font-weight: 600;
        }
        
        /* Card styling */
        .card {
            background-color: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }
        
        /* Input styling */
        .stTextInput > div > div > input, .stSelectbox > div > div > input {
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            padding: 8px 12px;
        }
        
        .stTextInput > div > div > input:focus, .stSelectbox > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            padding: 8px 16px;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background-color: #2563eb;
            box-shadow: 0 2px 5px rgba(37, 99, 235, 0.2);
        }
        
        /* Form styling */
        .stForm {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Calendar styling */
        .calendar-container {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background-color: white;
            padding: 20px;
        }
        
        .fc .fc-toolbar-title {
            font-size: 1.2em;
            color: #0f172a;
        }
        
        .fc .fc-button-primary {
            background-color: #3b82f6;
            border-color: #3b82f6;
        }
        
        .fc .fc-button-primary:hover {
            background-color: #2563eb;
            border-color: #2563eb;
        }
        
        .fc-day-today {
            background-color: rgba(59, 130, 246, 0.1) !important;
        }
        
        .fc-event {
            border-radius: 4px;
        }
        
        /* Custom select box */
        .custom-select {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        
        /* Success message */
        .success-message {
            padding: 12px 16px;
            background-color: rgba(16, 185, 129, 0.1);
            border-left: 4px solid #10b981;
            border-radius: 4px;
            color: #065f46;
            margin-bottom: 16px;
        }
        
        /* Warning message */
        .warning-message {
            padding: 12px 16px;
            background-color: rgba(245, 158, 11, 0.1);
            border-left: 4px solid #f59e0b;
            border-radius: 4px;
            color: #92400e;
            margin-bottom: 16px;
        }
        
        /* Error message */
        .error-message {
            padding: 12px 16px;
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #ef4444;
            border-radius: 4px;
            color: #b91c1c;
            margin-bottom: 16px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 500;
            color: #0f172a;
            background-color: white;
            border-radius: 6px;
        }
        
        .streamlit-expanderContent {
            border: none !important;
            background-color: white;
        }
        
        /* Container styling */
        .stContainer {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* Status badge */
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .status-confirmed {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
        }
        
        .status-pending {
            background-color: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
        }
        
        .status-declined {
            background-color: rgba(239, 68, 68, 0.1);
            color: #ef4444;
        }
        
        /* Table styling */
        .stDataFrame {
            border: none !important;
        }
        
        .stDataFrame [data-testid="stTable"] {
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .stDataFrame [data-testid="stTable"] th {
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 500;
            text-align: left;
            padding: 10px 15px;
        }
        
        .stDataFrame [data-testid="stTable"] td {
            padding: 10px 15px;
            border-bottom: 1px solid #e2e8f0;
            color: #334155;
        }
        
        .stDataFrame [data-testid="stTable"] tr:last-child td {
            border-bottom: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- Session State Init ---
if "users" not in st.session_state:
    st.session_state.users = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "calendar_view" not in st.session_state:
    st.session_state.calendar_view = "timeGridWeek"
if "page" not in st.session_state:
    st.session_state.page = "home"
if "notification" not in st.session_state:
    st.session_state.notification = None

status_colors = {
    "Confirmed": "#10b981", 
    "To Be Attend": "#f59e0b", 
    "Declined": "#ef4444"
}

time_options = get_time_options()

# Create header
header = create_modern_header()

# Get URL parameters for navigation
query_params = st.experimental_get_query_params()
if "page" in query_params:
    st.session_state.page = query_params["page"][0]

# Create navigation
create_nav_menu()

# Display notifications if any
if st.session_state.notification:
    notification_type, message = st.session_state.notification
    if notification_type == "success":
        st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
    elif notification_type == "warning":
        st.markdown(f'<div class="warning-message">{message}</div>', unsafe_allow_html=True)
    elif notification_type == "error":
        st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
    # Clear the notification after displaying it
    st.session_state.notification = None

# --- Home Page ---
if st.session_state.page == "home":
    # Welcome section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        create_card(
            title="Welcome to SRG Roster Management System",
            content="""
            <p>A professional platform for managing student resource group schedules efficiently.</p>
            <ul style="padding-left: 20px; margin-top: 15px;">
                <li>Students can submit their weekly availability</li>
                <li>Lecturers can manage and confirm shifts</li>
                <li>View interactive calendars with time scheduling</li>
                <li>Generate reports and export data</li>
            </ul>
            """,
            icon="📊",
            button="Get Started",
            button_link="?page=student"
        )
    
    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNNDAgNDBIMTYwVjE2MEg0MFY0MFoiIGZpbGw9IiMzYjgyZjYiLz4KPHBhdGggZD0iTTYwIDYwSDg1Vjg1SDYwVjYwWiIgZmlsbD0id2hpdGUiLz4KPHBhdGggZD0iTTk1IDYwSDEyMFY4NUg5NVY2MFoiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0xMzAgNjBIMTU1Vjg1SDEzMFY2MFoiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik02MCA5NUg4NVYxMjBINjBWOTVaIiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNOTUgOTVIMTIwVjEyMEg5NVY5NVoiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0xMzAgOTVIMTU1VjEyMEgxMzBWOTVaIiBmaWxsPSIjZGZmZGZmIi8+CjxwYXRoIGQ9Ik02MCAxMzBIODVWMTU1SDYwVjEzMFoiIGZpbGw9IiNkZmZkZmYiLz4KPHBhdGggZD0iTTk1IDEzMEgxMjBWMTU1SDk1VjEzMFoiIGZpbGw9IiNkZmZkZmYiLz4KPHBhdGggZD0iTTEzMCAxMzBIMTU1VjE1NUgxMzBWMTMwWiIgZmlsbD0iI2RmZmRmZiIvPgo8L3N2Zz4=" width="200">
        </div>
        """, unsafe_allow_html=True)
    
    # Feature cards
    st.markdown("<h2 style='margin-top: 30px; margin-bottom: 20px;'>Key Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_card(
            title="Student Availability",
            content="Students can easily submit their weekly availability to participate in resource group activities.",
            icon="🗓️"
        )
    
    with col2:
        create_card(
            title="Interactive Calendar",
            content="View and manage schedules using our interactive calendar with multiple viewing options.",
            icon="📅"
        )
    
    with col3:
        create_card(
            title="Reporting Tools",
            content="Generate reports and export data for analysis and record-keeping purposes.",
            icon="📈"
        )
    
    # Stats section
    st.markdown("<h2 style='margin-top: 30px; margin-bottom: 20px;'>System Statistics</h2>", 
                unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_stats_card("Total Students", str(len(st.session_state.users)))
    
    with col2:
        # Calculate total shifts
        total_shifts = sum(len(data.get("shifts", [])) for data in st.session_state.users.values())
        create_stats_card("Total Shifts", str(total_shifts))
    
    with col3:
        # Calculate confirmed shifts
        confirmed_shifts = sum(
            sum(1 for shift in data.get("shifts", []) if shift.get("status") == "Confirmed")
            for data in st.session_state.users.values()
        )
        create_stats_card("Confirmed Shifts", str(confirmed_shifts))
    
    with col4:
        # Calculate confirmation rate
        confirmation_rate = round((confirmed_shifts / total_shifts * 100) if total_shifts > 0 else 0, 1)
        create_stats_card("Confirmation Rate", f"{confirmation_rate}%", delta="2.5")

# --- Student Portal ---
elif st.session_state.page == "student":
    st.markdown("<h2>Student Portal</h2>", unsafe_allow_html=True)
    
    # Login / Logout section
    if st.session_state.current_user:
        st.markdown(f"""
        <div style="background-color: white; border-radius: 8px; padding: 20px; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; 
                            background-color: #3b82f6; display: flex; justify-content: center; 
                            align-items: center; margin-right: 15px; color: white; font-weight: 500;">
                        {st.session_state.users[st.session_state.current_user]['name'][0]}
                    </div>
                    <div>
                        <div style="font-weight: 500; color: #0f172a;">
                            {st.session_state.users[st.session_state.current_user]['name']}
                        </div>
                        <div style="font-size: 14px; color: #64748b;">Student ID: {st.session_state.current_user}</div>
                    </div>
                </div>
                <div>
                    <form action="?page=student&logout=true" method="post">
                        <button type="submit" 
                                style="background-color: #f1f5f9; color: #64748b; border: none; 
                                       border-radius: 6px; padding: 8px 16px; font-weight: 500; 
                                       cursor: pointer;">
                            Sign Out
                        </button>
                    </form>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check for logout action
        query_params = st.experimental_get_query_params()
        if "logout" in query_params and query_params["logout"][0] == "true":
            st.session_state.current_user = None
            st.experimental_set_query_params(page="student")
            st.experimental_rerun()
        
        # Student availability and calendar tabs
        create_tab_navigation(["Weekly Availability", "My Schedule"])
        
        # Weekly Availability Tab
        st.markdown("""
        <div id="weekly-availability-content" class="tab-content active">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; 
                           margin-bottom: 20px; font-weight: 600;">
                    📅 Enter Weekly Availability
                </h3>
            """, unsafe_allow_html=True)
            
            today = datetime.today()
            week_start = today - timedelta(days=today.weekday())
            shifts = []
            
            for i in range(7):
                day = week_start + timedelta(days=i)
                day_name = day.strftime('%A')
                day_date = day.strftime('%d %b')
                
                st.markdown(f"""
                <div style="margin-bottom: 15px; padding-bottom: 15px; 
                        border-bottom: 1px solid #f1f5f9;">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="font-weight: 500; color: #0f172a; flex-grow: 1;">
                            {day_name} <span style="color: #64748b; font-weight: normal; 
                                                  font-size: 14px;">({day_date})</span>
                        </div>
                """, unsafe_allow_html=True)
                
                avail_key = f"avail_{i}"
                if avail_key not in st.session_state:
                    st.session_state[avail_key] = False
                
                st.checkbox("Available", key=avail_key, 
                         help=f"Check if you're available on {day_name}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.session_state[avail_key]:
                    col_s, col_e = st.columns(2)
                    with col_s:
                        start_key = f"start_{i}"
                        if start_key not in st.session_state:
                            st.session_state[start_key] = time_options[0]
                        st.selectbox("Start", options=time_options, key=start_key)
                    
                    with col_e:
                        end_key = f"end_{i}"
                        if end_key not in st.session_state:
                            st.session_state[end_key] = time_options[4]  # Default to 2 hours later
                        st.selectbox("End", options=time_options, key=end_key)
                    
                    s = datetime.strptime(st.session_state[start_key], "%I:%M %p").time()
                    e = datetime.strptime(st.session_state[end_key], "%I:%M %p").time()
                    
                    if s < e:
                        shifts.append({
                            "date": day.strftime("%Y-%m-%d"),
                            "day": day.strftime("%A"),
                            "start": s.strftime("%H:%M:%S"),
                            "end": e.strftime("%H:%M:%S"),
                            "display": f"{st.session_state[start_key]}–{st.session_state[end_key]}",
                            "status": "To Be Attend"
                        })
                    else:
                        st.markdown("""
                        <div style="padding: 8px 12px; background-color: rgba(245, 158, 11, 0.1); 
                                border-radius: 4px; font-size: 14px; color: #92400e; 
                                margin-top: 10px;">
                            End time must be after start time
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            submit_shifts = st.button("Submit Availability", 
                                   help="Submit your available shifts for the week")
            
            if submit_shifts:
                if shifts:
                    st.session_state.users[st.session_state.current_user]["shifts"] = shifts
                    st.session_state.notification = ("success", "Your availability has been submitted successfully!")
                    st.experimental_rerun()
                else:
                    st.markdown("""
                    <div style="padding: 12px 16px; background-color: rgba(245, 158, 11, 0.1); 
                            border-left: 4px solid #f59e0b; border-radius: 4px; 
                            color: #92400e; margin-top: 15px;">
                        Please select at least one available time slot
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; margin-bottom: 20px; 
                           font-weight: 600;">
                    ℹ️ Guide to Submission
                </h3>
                <ul style="padding-left: 20px; color: #334155;">
                    <li style="margin-bottom: 10px;">
                        Check the days you are available to work
                    </li>
                    <li style="margin-bottom: 10px;">
                        Select start and end times for each available day
                    </li>
                    <li style="margin-bottom: 10px;">
                        Submit your availability for lecturer review
                    </li>
                    <li style="margin-bottom: 10px;">
                        Check your schedule tab to see confirmed shifts
                    </li>
                </ul>
                <div style="margin-top: 20px; padding: 12px 16px; 
                        background-color: rgba(59, 130, 246, 0.1); border-radius: 4px; 
                        color: #1e40af;">
                    <strong>Note:</strong> Submit your availability at least one week in advance
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # My Schedule Tab
        st.markdown("""
        <div id="my-schedule-content" class="tab-content">
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; 
                           margin-bottom: 20px; font-weight: 600;">
                    📆 My Schedule
                </h3>
        """, unsafe_allow_html=True)
        
        # Calendar view options using modern UI
        view_options = ["timeGridWeek", "dayGridMonth", "timeGridDay"]
        view_labels = ["Weekly", "Monthly", "Daily"]
        
        st.markdown("""
        <div style="display: flex; margin-bottom: 20px;">
            <div style="font-size: 14px; color: #64748b; margin-right: 10px; 
                    display: flex; align-items: center;">
                View:
            </div>
        """, unsafe_allow_html=True)
        
        for i, (option, label) in enumerate(zip(view_options, view_labels)):
            is_active = st.session_state.calendar_view == option
            bg_color = "#3b82f6" if is_active else "transparent"
            text_color = "white" if is_active else "#64748b"
            
            if st.button(
                label, 
                key=f"view_{option}",
                help=f"Switch to {label} view",
                type="primary" if is_active else "secondary"
            ):
                st.session_state.calendar_view = option
                st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Prepare calendar events
        events = [
            {
                "title": st.session_state.users[st.session_state.current_user]["name"],
                "start": f"{sh['date']}T{sh['start']}",
                "end":   f"{sh['date']}T{sh['end']}",
                "color": status_colors[sh['status']]
            }
            for sh in st.session_state.users[st.session_state.current_user].get("shifts", [])
        ]
        
        # Display calendar with modern styling
        calendar(
            events=events, 
            options={
                "initialView": st.session_state.calendar_view,
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "timeGridWeek,dayGridMonth,timeGridDay"
                },
                "slotMinTime": "06:00:00",
                "slotMaxTime": "22:00:00",
                "height": 600,
                "allDaySlot": False,
                "slotDuration": "00:30:00",
                "slotLabelFormat": {
                    "hour": "numeric",
                    "minute": "2-digit",
                    "omitZeroMinute": False,
                    "meridiem": "short"
                },
                "nowIndicator": True,
                "buttonText": {
                    "today": "Today",
                    "week": "Week",
                    "day": "Day",
                    "month": "Month"
                },
                "themeSystem": "standard",
                "eventTimeFormat": {
                    "hour": "numeric",
                    "minute": "2-digit",
                    "meridiem": "short"
                }
            }
        )
        
        st.markdown("""
            </div>
            
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; 
                           margin-bottom: 20px; font-weight: 600;">
                    📋 Shift Status Legend
                </h3>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #10b981; 
                                border-radius: 4px; margin-right: 8px;"></div>
                        <span style="color: #334155; font-size: 14px;">Confirmed</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #f59e0b; 
                                border-radius: 4px; margin-right: 8px;"></div>
                        <span style="color: #334155; font-size: 14px;">To Be Attend</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #ef4444; 
                                border-radius: 4px; margin-right: 8px;"></div>
                        <span style="color: #334155; font-size: 14px;">Declined</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Login Form with modern styling
        st.markdown("""
        <div style="max-width: 450px; margin: 0 auto; background-color: white; 
                border-radius: 8px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; text-align: center; margin-bottom: 25px; 
                    color: #0f172a; font-size: 20px;">
                Student Login
            </h3>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.text_input("Student ID", key="login_id", 
                         placeholder="Enter your student ID")
            st.text_input("Full Name", key="login_name", 
                         placeholder="Enter your full name")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.form_submit_button("Register", 
                                    help="Create a new account if you don't have one")
            with col2:
                submit = st.form_submit_button("Login", 
                                            help="Login to access your account")
        
        if submit or st.session_state.get("submit_login", False):
            st.session_state.submit_login = False
            sid = st.session_state.login_id
            name = st.session_state.login_name
            
            if sid and name:
                st.session_state.current_user = sid
                st.session_state.users.setdefault(sid, {"name": name, "shifts": []})
                st.experimental_rerun()
            else:
                st.markdown("""
                <div style="padding: 12px 16px; background-color: rgba(239, 68, 68, 0.1); 
                        border-left: 4px solid #ef4444; border-radius: 4px; 
                        color: #b91c1c; margin-top: 15px;">
                    Please enter both your Student ID and Full Name
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)

# --- Lecturer Portal ---
elif st.session_state.page == "lecturer":
    st.markdown("<h2>Lecturer Portal</h2>", unsafe_allow_html=True)
    
    # Login / Logout section with modern styling
    if not st.session_state.admin_logged_in:
        st.markdown("""
        <div style="max-width: 450px; margin: 0 auto; background-color: white; 
                border-radius: 8px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; text-align: center; margin-bottom: 25px; 
                    color: #0f172a; font-size: 20px;">
                Lecturer Login
            </h3>
        """, unsafe_allow_html=True)
        
        with st.form("admin_login"):
            st.text_input("Username", key="admin_user", placeholder="Enter your username")
            st.text_input("Password", type="password", key="admin_pass", 
                         placeholder="Enter your password")
            
            login_button = st.form_submit_button("Login", 
                                              help="Login to access the lecturer portal")
        
        if login_button:
            if st.session_state.admin_user == "demo" and st.session_state.admin_pass == "demo":
                st.session_state.admin_logged_in = True
                st.session_state.notification = ("success", "Logged in successfully!")
                st.experimental_rerun()
            else:
                st.markdown("""
                <div style="padding: 12px 16px; background-color: rgba(239, 68, 68, 0.1); 
                        border-left: 4px solid #ef4444; border-radius: 4px; 
                        color: #b91c1c; margin-top: 15px;">
                    Invalid credentials. Please try again.
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Admin Header with logout button
        st.markdown("""
        <div style="background-color: white; border-radius: 8px; padding: 20px; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; 
                            background-color: #3b82f6; display: flex; justify-content: center; 
                            align-items: center; margin-right: 15px; color: white; font-weight: 500;">
                        L
                    </div>
                    <div>
                        <div style="font-weight: 500; color: #0f172a;">Lecturer Admin</div>
                        <div style="font-size: 14px; color: #64748b;">Staff Account</div>
                    </div>
                </div>
                <div>
                    <form action="?page=lecturer&logout=true" method="post">
                        <button type="submit" 
                                style="background-color: #f1f5f9; color: #64748b; border: none; 
                                       border-radius: 6px; padding: 8px 16px; font-weight: 500; 
                                       cursor: pointer;">
                            Sign Out
                        </button>
                    </form>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check for logout action
        query_params = st.experimental_get_query_params()
        if "logout" in query_params and query_params["logout"][0] == "true":
            st.session_state.admin_logged_in = False
            st.experimental_set_query_params(page="lecturer")
            st.experimental_rerun()
        
        # Dashboard tabs with modern styling
        create_tab_navigation(["Manage Shifts", "Calendar View", "Reports"])
        
        # Manage Shifts Tab
        st.markdown("""
        <div id="manage-shifts-content" class="tab-content active">
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; margin-bottom: 20px; 
                        font-weight: 600;">
                    📋 Manage Student Shifts
                </h3>
        """, unsafe_allow_html=True)
        
        if not st.session_state.users:
            st.info("No students have registered yet.")
        else:
            for sid, data in st.session_state.users.items():
                with st.expander(f"{data['name']} (ID: {sid})"):
                    if data.get("shifts"):
                        st.markdown("""
                        <div style="margin-bottom: 10px; font-size: 14px; color: #64748b;">
                            Click on a status to update it
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Create a more modern shift management interface
                        df = pd.DataFrame(data["shifts"])
                        for i in range(len(df)):
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; padding: 12px; 
                                    background-color: #f8fafc; border-radius: 6px; 
                                    margin-bottom: 10px;">
                                <div style="flex: 2; padding-right: 10px;">
                                    <div style="font-weight: 500; color: #0f172a;">
                                        {df.loc[i,'day']} ({datetime.strptime(df.loc[i,"date"],"%Y-%m-%d").strftime("%d %b %Y")})
                                    </div>
                                </div>
                                <div style="flex: 2; padding-right: 10px;">
                                    <div style="color: #334155;">
                                        {df.loc[i,'display']}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            status_key = f"status_{sid}_{i}"
                            
                            current_status = st.selectbox(
                                "Status",
                                ["To Be Attend", "Confirmed", "Declined"],
                                index=["To Be Attend", "Confirmed", "Declined"].index(df.loc[i,"status"]),
                                key=status_key
                            )
                            
                            df.at[i, "status"] = current_status
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Update the shifts with new status values
                        st.session_state.users[sid]["shifts"] = df.to_dict("records")
                        
                        if st.button("Save Changes", key=f"save_{sid}"):
                            st.success("Changes saved successfully!")
                    else:
                        st.info("No shifts submitted yet.")
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Calendar View Tab
        st.markdown("""
        <div id="calendar-view-content" class="tab-content">
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; margin-bottom: 20px; 
                           font-weight: 600;">
                    📆 Complete Roster Calendar
                </h3>
        """, unsafe_allow_html=True)
        
        # Calendar view options with modern styling
        view_options = ["timeGridWeek", "dayGridMonth", "timeGridDay"]
        view_labels = ["Weekly", "Monthly", "Daily"]
        
        st.markdown("""
        <div style="display: flex; margin-bottom: 20px;">
            <div style="font-size: 14px; color: #64748b; margin-right: 10px; 
                    display: flex; align-items: center;">
                View:
            </div>
        """, unsafe_allow_html=True)
        
        for i, (option, label) in enumerate(zip(view_options, view_labels)):
            is_active = st.session_state.calendar_view == option
            bg_color = "#3b82f6" if is_active else "transparent"
            text_color = "white" if is_active else "#64748b"
            
            if st.button(
                label, 
                key=f"admin_view_{option}",
                help=f"Switch to {label} view",
                type="primary" if is_active else "secondary"
            ):
                st.session_state.calendar_view = option
                st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Gather all events for the admin calendar
        all_events = []
        for sid, data in st.session_state.users.items():
            for sh in data.get("shifts", []):
                all_events.append({
                    "title": f"{data['name']} ({sh['display']})",
                    "start": f"{sh['date']}T{sh['start']}",
                    "end":   f"{sh['date']}T{sh['end']}",
                    "color": status_colors[sh['status']]
                })
        
        # Modern styled calendar
        calendar(
            events=all_events, 
            options={
                "initialView": st.session_state.calendar_view,
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "timeGridWeek,dayGridMonth,timeGridDay"
                },
                "slotMinTime": "06:00:00",
                "slotMaxTime": "22:00:00",
                "height": 700,
                "allDaySlot": False,
                "slotDuration": "00:30:00",
                "slotLabelFormat": {
                    "hour": "numeric",
                    "minute": "2-digit",
                    "omitZeroMinute": False,
                    "meridiem": "short"
                },
                "nowIndicator": True,
                "buttonText": {
                    "today": "Today",
                    "week": "Week",
                    "day": "Day",
                    "month": "Month"
                },
                "themeSystem": "standard",
                "eventTimeFormat": {
                    "hour": "numeric",
                    "minute": "2-digit",
                    "meridiem": "short"
                }
            }
        )
        
        st.markdown("""
            </div>
            
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; 
                           margin-bottom: 20px; font-weight: 600;">
                    📋 Shift Status Legend
                </h3>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #10b981; 
                                border-radius: 4px; margin-right: 8px;"></div>
                        <span style="color: #334155; font-size: 14px;">Confirmed</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #f59e0b; 
                                border-radius: 4px; margin-right: 8px;"></div>
                        <span style="color: #334155; font-size: 14px;">To Be Attend</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #ef4444; 
                                border-radius: 4px; margin-right: 8px;"></div>
                        <span style="color: #334155; font-size: 14px;">Declined</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Reports Tab
        st.markdown("""
        <div id="reports-content" class="tab-content">
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; margin-bottom: 20px; 
                           font-weight: 600;">
                    📊 Confirmed Shifts Report
                </h3>
        """, unsafe_allow_html=True)
        
        # Gather all confirmed shifts
        records = []
        for sid, data in st.session_state.users.items():
            for sh in data.get("shifts", []):
                if sh["status"] == "Confirmed":
                    hrs = round((datetime.strptime(sh["end"], "%H:%M:%S") - 
                               datetime.strptime(sh["start"], "%H:%M:%S")).seconds/3600, 2)
                    records.append({
                        "Student ID": sid,
                        "Name": data["name"],
                        "Date": datetime.strptime(sh["date"], "%Y-%m-%d").strftime("%d %b %Y"),
                        "Day": sh["day"],
                        "Time": sh["display"],
                        "Hours": hrs
                    })
        
        # Create a DataFrame with the records
        df = pd.DataFrame(records)
        
        if not df.empty:
            # Modern styled dataframe
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Summary stats with modern cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                create_stats_card(
                    "Total Confirmed Hours", 
                    f"{df['Hours'].sum():.2f} hrs",
                    color="#10b981"
                )
            
            with col2:
                create_stats_card(
                    "Total Confirmed Shifts", 
                    f"{len(df)}",
                    color="#3b82f6"
                )
            
            with col3:
                create_stats_card(
                    "Average Shift Length", 
                    f"{df['Hours'].mean():.2f} hrs",
                    color="#8b5cf6"
                )
            
            # Excel download button with modern styling
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Weekly Summary", index=False)
                wb = writer.book
                ws = writer.sheets["Weekly Summary"]
                header_fmt = wb.add_format({"bold": True, "bg_color": "#3b82f6", "font_color": "white", "border": 1})
                for col_num, col_name in enumerate(df.columns):
                    ws.write(0, col_num, col_name, header_fmt)
            
            st.download_button(
                label="📥 Download Excel Summary", 
                data=buf.getvalue(), 
                file_name="SRG_weekly_summary.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the shift summary in Excel format"
            )
        else:
            st.info("No confirmed shifts to display.")
        
        st.markdown("""
            </div>
            
            <div style="background-color: white; border-radius: 8px; padding: 20px; 
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; font-size: 18px; color: #0f172a; margin-bottom: 20px; 
                           font-weight: 600;">
                    📈 Weekly Overview
                </h3>
                
                <div style="margin-bottom: 20px;">
                    <canvas id="shiftsChart" width="400" height="200"></canvas>
                </div>
                
                <script>
                document.addEventListener('DOMContentLoaded', function() {
                    var ctx = document.getElementById('shiftsChart').getContext('2d');
                    var shiftsChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                            datasets: [{
                                label: 'Confirmed Shifts',
                                data: [3, 5, 4, 6, 2, 1, 0],
                                backgroundColor: '#3b82f6'
                            }, {
                                label: 'Pending Shifts',
                                data: [2, 1, 3, 0, 4, 2, 1],
                                backgroundColor: '#f59e0b'
                            }, {
                                label: 'Declined Shifts',
                                data: [0, 1, 0, 2, 1, 0, 0],
                                backgroundColor: '#ef4444'
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: {
                                    stacked: true
                                },
                                y: {
                                    stacked: true,
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                });
                </script>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; 
              text-align: center; font-size: 14px; color: #64748b;">
    <div style="margin-bottom: 10px;">SRG Roster Management System © 2025</div>
    <div style="display: flex; justify-content: center; gap: 20px;">
        <a href="#" style="color: #64748b; text-decoration: none;">Terms</a>
        <a href="#" style="color: #64748b; text-decoration: none;">Privacy</a>
        <a href="#" style="color: #64748b; text-decoration: none;">Help</a>
        <a href="#" style="color: #64748b; text-decoration: none;">Contact</a>
    </div>
</footer>
""", unsafe_allow_html=True)
