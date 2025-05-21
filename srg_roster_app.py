import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
from streamlit_calendar import calendar
import base64
from PIL import Image
import os

# Hide streamlit sidebar menu
st.set_page_config(page_title="SRG Roster Manager", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for blue and white 3D glowing UI with top navigation
def set_custom_theme():
    st.markdown("""
    <style>
        /* Hide sidebar completely */
        [data-testid="collapsedControl"] {
            display: none;
        }
        
        /* Hide the default Streamlit hamburger menu and "Deployed from" text */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Background image for the entire page */
        .main {
            background-image: url("https://raw.githubusercontent.com/yourusername/srg-roster/main/VUCOVER.png");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        
        /* Add a semi-transparent overlay to improve readability */
        .main::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.85);
            z-index: -1;
        }
        
        /* Create top navigation bar */
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(90deg, #004c99, #0066cc);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
            margin-bottom: 1rem;
        }
        
        .nav-logo {
            display: flex;
            align-items: center;
        }
        
        .nav-logo img {
            height: 40px;
            margin-right: 10px;
        }
        
        .nav-links {
            display: flex;
            gap: 10px;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .nav-link.active {
            background-color: rgba(255, 255, 255, 0.3);
            font-weight: bold;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #0066cc;
            text-shadow: 0 0 10px rgba(0, 102, 204, 0.3);
            font-weight: bold;
        }
        
        /* Cards and containers with 3D effect */
        .css-1r6slb0, .css-12oz5g7, .stDataFrame, div[data-testid="stForm"], .card {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2), 
                        0 0 20px rgba(0, 102, 204, 0.1);
            background: linear-gradient(145deg, #ffffff, #f0f8ff);
            border: 1px solid rgba(0, 102, 204, 0.1);
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Custom card style */
        .custom-card {
            background: linear-gradient(145deg, #ffffff, #f0f8ff);
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2), 
                        0 0 20px rgba(0, 102, 204, 0.1);
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(0, 102, 204, 0.1);
        }
        
        /* Buttons with 3D glowing effect */
        .stButton > button {
            background: linear-gradient(145deg, #0066cc, #0052a3);
            color: white;
            border: none;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 82, 163, 0.3),
                        0 0 15px rgba(0, 102, 204, 0.2);
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            box-shadow: 0 6px 15px rgba(0, 82, 163, 0.4),
                        0 0 20px rgba(0, 102, 204, 0.3);
            transform: translateY(-2px);
        }
        
        /* Calendar and date highlighting */
        .fc-event {
            border-radius: 6px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Success message */
        .stSuccess {
            background: linear-gradient(145deg, #e0f0e0, #d0e8d0);
            border-left: 4px solid #28a745;
            box-shadow: 0 4px 10px rgba(40, 167, 69, 0.2);
        }
        
        /* Form inputs glow effect */
        input, select, textarea, .stSelectbox > div > div, .stTimeInput > div > div {
            border-radius: 8px !important;
            border: 1px solid rgba(0, 102, 204, 0.2) !important;
            box-shadow: 0 0 8px rgba(0, 102, 204, 0.1) !important;
        }
        
        input:focus, select:focus, textarea:focus {
            border: 1px solid #0066cc !important;
            box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2) !important;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1px;
            background-color: #f0f8ff;
            border-radius: 8px;
            padding: 0.5rem;
            box-shadow: 0 2px 6px rgba(0, 102, 204, 0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            color: #0066cc;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin-right: 4px;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding: 1rem;
            border-radius: 0 0 8px 8px;
            background-color: #fff;
            box-shadow: 0 2px 6px rgba(0, 102, 204, 0.1);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #0066cc;
            color: white;
        }
        
        /* Fullcalendar styling */
        .fc .fc-toolbar {
            background: linear-gradient(90deg, #f0f8ff, #e6f2ff);
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 1rem !important;
        }
        
        .fc .fc-button-primary {
            background-color: #0066cc !important;
            border-color: #0052a3 !important;
            box-shadow: 0 2px 5px rgba(0, 82, 163, 0.3) !important;
        }
        
        .fc-theme-standard td, .fc-theme-standard th {
            border-color: rgba(0, 102, 204, 0.1) !important;
        }
        
        .fc-daygrid-day-frame {
            padding: 4px !important;
        }
        
        .fc .fc-daygrid-day.fc-day-today {
            background-color: rgba(0, 102, 204, 0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom HTML for top navigation
    logo_html = """
    <div class="top-nav">
        <div class="nav-logo">
            <img src="https://raw.githubusercontent.com/yourusername/srg-roster/main/VU_LOGO.png" alt="VU Logo">
            <h2 style="color: white; margin: 0;">SRG Roster System</h2>
        </div>
        <div class="nav-links">
            <a href="?page=Home" class="nav-link {home_active}">Home</a>
            <a href="?page=Student_Portal" class="nav-link {student_active}">Student Portal</a>
            <a href="?page=Lecturer_Portal" class="nav-link {lecturer_active}">Lecturer Portal</a>
        </div>
    </div>
    """
    
    # Determine active page for nav highlighting
    current_page = st.experimental_get_query_params().get("page", ["Home"])[0]
    home_active = "active" if current_page == "Home" else ""
    student_active = "active" if current_page == "Student_Portal" else ""
    lecturer_active = "active" if current_page == "Lecturer_Portal" else ""
    
    # Render the navigation
    st.markdown(
        logo_html.format(
            home_active=home_active,
            student_active=student_active,
            lecturer_active=lecturer_active
        ), 
        unsafe_allow_html=True
    )

# Function to create 30-minute interval time options in 12-hour format
def get_time_options():
    options = []
    for hour in range(24):
        for minute in [0, 30]:
            t = time(hour, minute)
            options.append(t.strftime("%I:%M %p").lstrip("0"))
    return options

# Function to convert 24-hour time string to 12-hour format
def format_time_12hr(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return time_obj.strftime("%I:%M %p").lstrip("0")

# Apply custom styling 
set_custom_theme()

# Get the current page from query parameters or use default
query_params = st.experimental_get_query_params()
current_page = query_params.get("page", ["Home"])[0]

# Map URL parameter to page name
page_mapping = {
    "Home": "Home",
    "Student_Portal": "Student Portal",
    "Lecturer_Portal": "Lecturer Login"
}

# Determine which page to show
page = page_mapping.get(current_page, "Home")

# Initialize session state variables
if "users" not in st.session_state:
    st.session_state.users = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Status colors for calendar
status_colors = {
    "Confirmed": "#28a745",  # Enhanced green
    "To Be Attend": "#ffc107",  # Enhanced yellow
    "Declined": "#dc3545"  # Enhanced red
}

# Home page
if page == "Home":
    st.title("🏫 SRG Roster Management System")
    
    st.markdown("""
    <div class="custom-card">
        <h3>Welcome to the SRG Roster Management System</h3>
        <p>This advanced system helps manage student rosters and shift schedules efficiently.</p>
        
        <h4>Features:</h4>
        <ul>
            <li>Student availability submission</li>
            <li>Shift management for lecturers</li>
            <li>Interactive calendar views</li>
            <li>Downloadable reports</li>
        </ul>
        
        <p>Use the navigation menu at the top to get started.</p>
    </div>
    """, unsafe_allow_html=True)

# Student Portal
elif page == "Student Portal":
    st.title("🧑‍🎓 Student Portal")
    
    # Login section
    if st.session_state.current_user:
        st.success(f"Logged in as {st.session_state.users[st.session_state.current_user]['name']}")
        if st.button("Logout"):
            st.session_state.current_user = None
            st.experimental_rerun()
    else:
        st.markdown("""<div class="custom-card">""", unsafe_allow_html=True)
        with st.form("student_login"):
            st.subheader("Login / Registration")
            col1, col2 = st.columns(2)
            
            with col1:
                student_id = st.text_input("Student ID")
            
            with col2:
                student_name = st.text_input("Full Name")
                
            submitted = st.form_submit_button("Login / Register")
            if submitted:
                if student_id and student_name:
                    st.session_state.current_user = student_id
                    if student_id not in st.session_state.users:
                        st.session_state.users[student_id] = {"name": student_name, "shifts": []}
                    st.success(f"Logged in as {student_name}")
                    st.experimental_rerun()
                else:
                    st.warning("Enter both ID and Name.")
        st.markdown("""</div>""", unsafe_allow_html=True)

    # Availability section for logged-in users
    if st.session_state.current_user:
        st.markdown("""<div class="custom-card">""", unsafe_allow_html=True)
        st.subheader("📅 Enter Weekly Availability")
        
        time_options = get_time_options()
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        shifts = []
        
        # Create tabs for each day of the week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        tabs = st.tabs(days)
        
        for i, tab in enumerate(tabs):
            with tab:
                day = week_start + timedelta(days=i)
                available = st.checkbox(f"I'm available on {day.strftime('%A (%d %b)')}", key=f"available_{i}", value=True)
                
                if available:
                    col1, col2 = st.columns(2)
                    with col1:
                        start_time_str = st.selectbox(
                            f"Start Time", 
                            options=time_options,
                            index=time_options.index("9:00 AM") if "9:00 AM" in time_options else 0,
                            key=f"start_{i}"
                        )
                        start_time_obj = datetime.strptime(start_time_str, "%I:%M %p")
                        start_time = start_time_obj.time()
                        
                    with col2:
                        end_time_str = st.selectbox(
                            f"End Time", 
                            options=time_options,
                            index=time_options.index("5:00 PM") if "5:00 PM" in time_options else 16,
                            key=f"end_{i}"
                        )
                        end_time_obj = datetime.strptime(end_time_str, "%I:%M %p")
                        end_time = end_time_obj.time()
                    
                    if start_time < end_time:
                        shifts.append({
                            "date": day.strftime("%Y-%m-%d"),
                            "day": day.strftime("%A"),
                            "start": start_time.strftime("%H:%M:%S"),
                            "end": end_time.strftime("%H:%M:%S"),
                            "start_display": start_time_str,
                            "end_display": end_time_str,
                            "status": "To Be Attend"
                        })
                    else:
                        st.warning("End time must be after start time")

        if st.button("Submit Weekly Shifts"):
            st.session_state.users[st.session_state.current_user]["shifts"] = shifts
            st.success("Shifts submitted successfully! Your availability has been recorded.")
        st.markdown("""</div>""", unsafe_allow_html=True)

        # Display calendar for the student
        st.markdown("""<div class="custom-card">""", unsafe_allow_html=True)
        student_data = st.session_state.users[st.session_state.current_user]
        events = [
            {
                "title": f"{student_data['name']} ({shift['start_display']} - {shift['end_display']})",
                "start": f"{shift['date']}T{shift['start']}",
                "end": f"{shift['date']}T{shift['end']}",
                "color": status_colors.get(shift["status"], "gray"),
                "extendedProps": {
                    "status": shift["status"],
                    "start_time": shift["start"],
                    "end_time": shift["end"],
                    "date": shift["date"]
                }
            }
            for shift in student_data.get("shifts", [])
        ]
        
        st.subheader("📆 My Schedule")
        calendar(events=events, options={"initialView": "dayGridMonth"})
        st.markdown("""</div>""", unsafe_allow_html=True)

# Lecturer Login
elif page == "Lecturer Login":
    st.title("👩‍🏫 Lecturer Portal")
    
    # Login section
    if not st.session_state.admin_logged_in:
        col1, col2 = st.columns(2)
        
        with col1:
            admin_user = st.text_input("Username")
        
        with col2:
            admin_pass = st.text_input("Password", type="password")
            
        if st.button("Login"):
            if admin_user == "demo" and admin_pass == "demo":
                st.session_state.admin_logged_in = True
                st.success("Lecturer logged in successfully")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    else:
        st.success("Logged in as Lecturer")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()

    # Admin dashboard for logged-in lecturers
    if st.session_state.admin_logged_in:
        # Create tabs for different admin functions
        tab1, tab2, tab3 = st.tabs(["Manage Shifts", "Calendar View", "Reports"])
        
        with tab1:
            st.subheader("📋 Manage Student Shifts")
            
            # Display student shifts in a nicer format
            for student_id, data in st.session_state.users.items():
                with st.expander(f"📚 {data['name']} (ID: {student_id})"):
                    if isinstance(data.get("shifts"), list) and data["shifts"]:
                        # Convert shifts to DataFrame
                        df = pd.DataFrame(data["shifts"])
                        for i in range(len(df)):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                display_date = datetime.strptime(df.loc[i, 'date'], "%Y-%m-%d").strftime("%d %b %Y")
                                st.markdown(f"**{df.loc[i, 'day']} ({display_date})**")
                                
                            with col2:
                                start_time_display = format_time_12hr(df.loc[i, 'start']) if 'start_display' not in df.columns else df.loc[i, 'start_display']
                                end_time_display = format_time_12hr(df.loc[i, 'end']) if 'end_display' not in df.columns else df.loc[i, 'end_display']
                                st.markdown(f"Time: {start_time_display} to {end_time_display}")
                                
                            with col3:
                                new_status = st.selectbox("Status", 
                                                        ["To Be Attend", "Confirmed", "Declined"],
                                                        index=["To Be Attend", "Confirmed", "Declined"].index(df.loc[i, "status"]),
                                                        key=f"status_{student_id}_{i}")
                                df.at[i, "status"] = new_status
                        
                        # Update the shifts in session state
                        st.session_state.users[student_id]["shifts"] = df.to_dict(orient="records")
                    else:
                        st.info("No shifts submitted by this student.")
        
        with tab2:
            st.subheader("📆 Complete Roster Calendar")
            
            # Create events for all students
            all_events = []
            for student_id, data in st.session_state.users.items():
                for shift in data.get("shifts", []):
                    start_display = format_time_12hr(shift['start']) if 'start_display' not in shift else shift['start_display']
                    end_display = format_time_12hr(shift['end']) if 'end_display' not in shift else shift['end_display']
                    
                    all_events.append({
                        "title": f"{data['name']} ({start_display} - {end_display})",
                        "start": f"{shift['date']}T{shift['start']}",
                        "end": f"{shift['date']}T{shift['end']}",
                        "color": status_colors.get(shift["status"], "gray"),
                        "extendedProps": {
                            "student_id": student_id,
                            "name": data["name"],
                            "status": shift["status"],
                            "start_time": shift["start"],
                            "end_time": shift["end"],
                            "date": shift["date"]
                        }
                    })
            
            # Display interactive calendar
            calendar(events=all_events, options={"initialView": "dayGridMonth"})
        
        with tab3:
            st.subheader("📊 Weekly Summary Report")
            
            # Create more detailed records for reporting
            records = []
            for student_id, data in st.session_state.users.items():
                for shift in data.get("shifts", []):
                    if shift["status"] == "Confirmed":
                        start = datetime.strptime(shift["start"], "%H:%M:%S")
                        end = datetime.strptime(shift["end"], "%H:%M:%S")
                        hours = (end - start).seconds / 3600
                        
                        start_display = format_time_12hr(shift['start']) if 'start_display' not in shift else shift['start_display']
                        end_display = format_time_12hr(shift['end']) if 'end_display' not in shift else shift['end_display']
                        
                        records.append({
                            "Student ID": student_id,
                            "Name": data["name"],
                            "Date": datetime.strptime(shift["date"], "%Y-%m-%d").strftime("%d %b %Y"),
                            "Day": shift["day"],
                            "Start Time": start_display,
                            "End Time": end_display,
                            "Status": shift["status"],
                            "Hours": round(hours, 2)
                        })
            
            # Create DataFrame and display
            df_summary = pd.DataFrame(records)
            if not df_summary.empty:
                st.dataframe(df_summary, use_container_width=True)
                
                # Summary statistics
                total_hours = df_summary["Hours"].sum()
                st.metric("Total Confirmed Hours", f"{total_hours:.2f}")
                
                # Create Excel download
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df_summary.to_excel(writer, index=False, sheet_name="Weekly Summary")
                    workbook = writer.book
                    worksheet = writer.sheets["Weekly Summary"]
                    
                    # Add some formatting to Excel file
                    header_format = workbook.add_format({
                        'bold': True,
                        'bg_color': '#0066cc',
                        'color': 'white',
                        'border': 1
                    })
                    
                    for col_num, value in enumerate(df_summary.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                st.download_button(
                    label="📥 Download Excel Summary",
                    data=buffer.getvalue(),
                    file_name="SRG_weekly_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No confirmed shifts to display in the report.")
