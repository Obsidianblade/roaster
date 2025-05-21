import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time
from io import BytesIO
from streamlit_calendar import calendar
import base64

# Custom CSS for blue and white 3D glowing UI
def set_custom_theme():
    st.markdown("""
    <style>
        /* Main App Theme */
        .main, .css-1d391kg {
            background-color: #f0f8ff;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #0066cc;
            text-shadow: 0 0 10px rgba(0, 102, 204, 0.3);
            font-weight: bold;
        }
        
        /* Cards and containers with 3D effect */
        .css-1r6slb0, .css-12oz5g7, .stDataFrame, .css-1d391kg, div[data-testid="stForm"] {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2), 
                        0 0 20px rgba(0, 102, 204, 0.1);
            background: linear-gradient(145deg, #ffffff, #f0f8ff);
            border: 1px solid rgba(0, 102, 204, 0.1);
            padding: 1rem;
            margin: 0.5rem 0;
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
        
        /* Sidebar styling */
        .css-1d391kg, [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0066cc, #004c99);
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdown"] {
            color: white;
        }
        
        [data-testid="stSidebarNav"] {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
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
        
        /* Certificate styling */
        .certificate {
            background: linear-gradient(145deg, #fff8e8, #fffdf5);
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }
        
        .certificate h1 {
            color: #8b4513;
            font-family: "Palatino Linotype", "Book Antiqua", Palatino, serif;
        }
    </style>
    """, unsafe_allow_html=True)

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

# Function to generate a certificate
def generate_certificate(student_name, hours_completed, date_completed):
    certificate_html = f"""
    <div class="certificate">
        <h1>Certificate of Achievement</h1>
        <h2>This is to certify that</h2>
        <h1>{student_name}</h1>
        <h2>has successfully completed</h2>
        <h1>{hours_completed} hours</h1>
        <h2>of Student Representative Group service</h2>
        <p>Awarded on {date_completed}</p>
        <p><strong>SRG Roster Management System</strong></p>
    </div>
    """
    return certificate_html

# Set page configuration
st.set_page_config(page_title="SRG Roster Manager", layout="wide")
set_custom_theme()

st.sidebar.title("📋 SRG Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Student Portal", "Lecturer Login"])

# Initialize session state variables
if "users" not in st.session_state:
    st.session_state.users = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "certificates" not in st.session_state:
    st.session_state.certificates = {}
if "default_calendar_view" not in st.session_state:
    st.session_state.default_calendar_view = "dayGridMonth"

# Status colors for calendar
status_colors = {
    "Confirmed": "#28a745",  # Enhanced green
    "To Be Attend": "#ffc107",  # Enhanced yellow
    "Declined": "#dc3545"  # Enhanced red
}

# Home page
if page == "Home":
    st.title("🏫 SRG Roster Management System")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to the SRG Roster Management System
        
        This advanced system helps manage student rosters and shift schedules efficiently.
        
        #### Features:
        - Student availability submission
        - Shift management for lecturers
        - Interactive calendar views
        - Downloadable reports
        - SRG STAR dashboard
        - Certificate for 30+ hours of service
        
        Choose **Student Portal** or **Lecturer Login** from the sidebar to get started.
        """)
    
    with col2:
        st.image("https://via.placeholder.com/400x300?text=SRG+Roster+System", use_column_width=True)

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

    # Availability section for logged-in users
    if st.session_state.current_user:
        student_tabs = st.tabs(["Submit Availability", "My Schedule", "My Certificate"])
        
        with student_tabs[0]:
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
                # Keep old shifts if they exist
                old_shifts = st.session_state.users[st.session_state.current_user].get("shifts", [])
                # Only keep shifts that are not in the current week
                week_dates = [week_start + timedelta(days=i) for i in range(7)]
                week_dates_str = [date.strftime("%Y-%m-%d") for date in week_dates]
                old_shifts = [shift for shift in old_shifts if shift["date"] not in week_dates_str]
                # Add new shifts
                new_shifts = old_shifts + shifts
                st.session_state.users[st.session_state.current_user]["shifts"] = new_shifts
                st.success("Shifts submitted successfully! Your availability has been recorded.")
        
        with student_tabs[1]:
            st.subheader("📆 My Schedule")
            
            # Calendar view options
            calendar_view = st.radio(
                "Calendar View", 
                ["Month", "Week", "Day"], 
                horizontal=True
            )
            
            # Map the selected view to FullCalendar view options
            calendar_view_map = {
                "Month": "dayGridMonth",
                "Week": "timeGridWeek",
                "Day": "timeGridDay"
            }
            
            # Display calendar for the student
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
            
            # Calculate total hours
            total_hours = 0
            for shift in student_data.get("shifts", []):
                if shift["status"] == "Confirmed":
                    start = datetime.strptime(shift["start"], "%H:%M:%S")
                    end = datetime.strptime(shift["end"], "%H:%M:%S")
                    hours = (end - start).seconds / 3600
                    total_hours += hours
            
            # Display total hours
            st.metric("Total Confirmed Hours", f"{total_hours:.2f}")
            
            # Fix for the calendar display issue - make sure it renders properly
            st.markdown("""
            <style>
            /* Critical fix for calendar display */
            .fc-view-harness {
                height: 600px !important;
                min-height: 500px !important;
            }
            .fc-scrollgrid-sync-inner {
                background-color: #f8f9fa;
            }
            .fc-col-header-cell {
                background-color: #0066cc;
                color: white;
            }
            .fc-col-header-cell a {
                color: white !important;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display calendar with the selected view
            calendar_options = {
                "initialView": calendar_view_map[calendar_view],
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay"
                },
                "slotDuration": "00:30:00",
                "slotLabelFormat": {
                    "hour": "numeric",
                    "minute": "2-digit",
                    "omitZeroMinute": False,
                    "meridiem": "short"
                },
                "allDaySlot": False,
                "height": 600,
                "expandRows": True,
                "stickyHeaderDates": True
            }
            
            try:
                calendar(events=events, options=calendar_options, key="student_calendar")
            except Exception as e:
                st.error(f"Error loading calendar: {e}")
                st.info("Try submitting some shifts first to see your calendar.")
        
        with student_tabs[2]:
            st.subheader("🏆 My Certificate")
            
            # Calculate total hours for the student
            total_hours = 0
            for shift in student_data.get("shifts", []):
                if shift["status"] == "Confirmed":
                    start = datetime.strptime(shift["start"], "%H:%M:%S")
                    end = datetime.strptime(shift["end"], "%H:%M:%S")
                    hours = (end - start).seconds / 3600
                    total_hours += hours
            
            if total_hours >= 30:
                st.success("Congratulations! You have completed 30+ hours of service and are eligible for a certificate.")
                
                # Generate certificate if not already generated
                student_id = st.session_state.current_user
                if student_id not in st.session_state.certificates:
                    date_completed = datetime.now().strftime("%d %B %Y")
                    st.session_state.certificates[student_id] = {
                        "name": student_data["name"],
                        "hours": round(total_hours, 2),
                        "date": date_completed
                    }
                
                # Display certificate
                certificate = generate_certificate(
                    student_data["name"],
                    round(total_hours, 2),
                    st.session_state.certificates[student_id]["date"]
                )
                st.markdown(certificate, unsafe_allow_html=True)
                
                # Button to download as PDF (placeholder - would need additional libraries to actually generate PDF)
                st.download_button(
                    label="📥 Download Certificate",
                    data="Certificate data would go here",
                    file_name=f"SRG_Certificate_{student_data['name']}.pdf",
                    mime="application/pdf",
                    disabled=True,  # Disabled as actual PDF generation is not implemented
                )
                st.info("Note: PDF download is a placeholder. In a real app, this would generate an actual PDF file.")
            else:
                st.info(f"You have completed {total_hours:.2f} hours. Complete 30 hours to receive a certificate.")
                # Show progress
                st.progress(min(total_hours / 30, 1.0))

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
        tab1, tab2, tab3, tab4 = st.tabs(["Manage Shifts", "Calendar View", "SRG STAR Dashboard", "Reports"])
        
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
            
            # Calendar view options
            calendar_view = st.radio(
                "Calendar View", 
                ["Month", "Week", "Day"], 
                horizontal=True,
                key="lecturer_calendar_view"
            )
            
            # Map the selected view to FullCalendar view options
            calendar_view_map = {
                "Month": "dayGridMonth",
                "Week": "timeGridWeek",
                "Day": "timeGridDay"
            }
            
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
            
            # Add dummy event if no events are available to ensure calendar renders
            if not all_events:
                today = datetime.today()
                tomorrow = today + timedelta(days=1)
                all_events.append({
                    "title": "Demo Event (9:00 AM - 5:00 PM)",
                    "start": f"{today.strftime('%Y-%m-%d')}T09:00:00",
                    "end": f"{today.strftime('%Y-%m-%d')}T17:00:00",
                    "color": "#cccccc",
                    "extendedProps": {
                        "status": "Demo",
                        "name": "Demo Event"
                    }
                })
                st.info("No actual events available. A demo event has been added for visualization purposes.")
            
            # Create a container for the calendar with proper height
            st.markdown('<div class="calendar-container"></div>', unsafe_allow_html=True)
            
            # Display calendar with advanced options within a container
            calendar_options = {
                "initialView": calendar_view_map[calendar_view],
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay"
                },
                "plugins": ["dayGrid", "timeGrid"],
                "slotDuration": "00:30:00",
                "slotLabelFormat": {
                    "hour": "numeric",
                    "minute": "2-digit",
                    "omitZeroMinute": False,
                    "meridiem": "short"
                },
                "allDaySlot": False,
                "nowIndicator": True,
                "height": 680,
                "aspectRatio": 1.8,
                "contentHeight": 650,
                "expandRows": True,
                "stickyHeaderDates": True,
                "handleWindowResize": True
            }
            
            try:
                calendar(events=all_events, options=calendar_options, key="lecturer_calendar")
                
                # Add some space after the calendar
                st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading calendar: {e}")
                st.info("Please add some student shifts and refreshing the page to see the calendar."): 600px !important;
            }
            .fc-scrollgrid-sync-inner {
                background-color: #f8f9fa;
            }
            .fc-col-header-cell {
                background-color: #0066cc;
                color: white;
            }
            .fc-col-header-cell a {
                color: white !important;
                font-weight: bold;
            }
            .fc-timegrid-slot {
                height: 40px !important;
            }
            .fc-timegrid-slot-label {
                font-weight: bold;
            }
            .fc-daygrid-day-number {
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create a placeholder for calendar to ensure it's given proper space
            calendar_placeholder = st.empty()
            
            # Display calendar with advanced options within the placeholder
            with calendar_placeholder:
                calendar_options = {
                    "initialView": calendar_view_map[calendar_view],
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,timeGridWeek,timeGridDay"
                    },
                    "plugins": ["dayGrid", "timeGrid"],
                    "slotDuration": "00:30:00",
                    "slotLabelFormat": {
                        "hour": "numeric",
                        "minute": "2-digit",
                        "omitZeroMinute": False,
                        "meridiem": "short"
                    },
                    "allDaySlot": False,
                    "nowIndicator": True,
                    "height": 700,
                    "aspectRatio": 1.8,
                    "contentHeight": 650,
                    "expandRows": True,
                    "stickyHeaderDates": True,
                    "handleWindowResize": True
                }
                
                try:
                    calendar(events=all_events, options=calendar_options, key="lecturer_calendar")
                    
                    # Add a message to confirm calendar is working
                    st.success("Calendar loaded successfully. If you don't see it, please refresh the page.")
                except Exception as e:
                    st.error(f"Error loading calendar: {e}")
                    st.info("Try adding some student shifts and refreshing the page to see the calendar.")
        
        with tab3:
            st.subheader("🌟 SRG STAR Dashboard")
            
            # Calculate hours for each student
            student_hours = []
            for student_id, data in st.session_state.users.items():
                total_hours = 0
                for shift in data.get("shifts", []):
                    if shift["status"] == "Confirmed":
                        start = datetime.strptime(shift["start"], "%H:%M:%S")
                        end = datetime.strptime(shift["end"], "%H:%M:%S")
                        hours = (end - start).seconds / 3600
                        total_hours += hours
                
                student_hours.append({
                    "Student ID": student_id,
                    "Name": data["name"],
                    "Total Hours": round(total_hours, 2)
                })
            
            # Create DataFrame and sort by hours
            df_hours = pd.DataFrame(student_hours)
            if not df_hours.empty:
                df_hours = df_hours.sort_values("Total Hours", ascending=False)
                
                # Display top students
                st.subheader("🏆 Top Performing Students")
                
                # Create columns for metric display
                cols = st.columns(min(3, len(df_hours)))
                for i, col in enumerate(cols):
                    if i < len(df_hours):
                        with col:
                            st.metric(
                                label=f"{i+1}. {df_hours.iloc[i]['Name']}", 
                                value=f"{df_hours.iloc[i]['Total Hours']} hours"
                            )
                
                # Create a bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(
                    df_hours['Name'], 
                    df_hours['Total Hours'],
                    color=['#28a745' if i == 0 else '#0066cc' if i == 1 else '#ffc107' if i == 2 else '#6c757d' for i in range(len(df_hours))]
                )
                
                # Add data labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width()/2.,
                        height + 0.3,
                        f'{height:.1f}',
                        ha='center',
                        va='bottom',
                        fontweight='bold'
                    )
                
                ax.set_ylabel('Hours')
                ax.set_title('Student Hours Completed')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                st.pyplot(fig)
                
                # Display the data table
                st.subheader("Student Hours Details")
                st.dataframe(df_hours, use_container_width=True)
            else:
                st.info("No student data available yet.")
        
        with tab4:
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
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_hours = df_summary["Hours"].sum()
                    st.metric("Total Confirmed Hours", f"{total_hours:.2f}")
                
                with col2:
                    avg_hours = df_summary["Hours"].mean()
                    st.metric("Average Shift Length", f"{avg_hours:.2f}")
                
                with col3:
                    student_count = df_summary["Student ID"].nunique()
                    st.metric("Active Students", f"{student_count}")
                
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
