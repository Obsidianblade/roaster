import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
import base64
from streamlit_calendar import calendar
import streamlit.components.v1 as components

# --- Helper Functions ---
def set_background(image_path):
    """Set the app background using a local image."""
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
        <style>
            .stApp {{
                background: url("data:image/png;base64,{b64}") no-repeat center center fixed;
                background-size: cover;
            }}
        </style>
    """, unsafe_allow_html=True)


def set_header_nav(logo_path):
    """Display logo and horizontal navigation, return selected page."""
    col_logo, col_nav = st.columns([1, 4], gap="small")
    with col_logo:
        st.image(logo_path, width=80)
    with col_nav:
        page = st.radio("", ["Home", "Student Portal", "Lecturer Portal"], horizontal=True)
    return page


def get_time_options():
    """Return 30-minute interval times in 12-hour format."""
    opts = []
    for h in range(6, 22):
        for m in (0, 30):
            t = time(h, m)
            s = t.strftime("%I:%M %p").lstrip("0")
            opts.append(s)
    return opts

# --- Page Setup ---
st.set_page_config(page_title="SRG Roster Manager", layout="wide")
set_background("VUCOVER.png")

# Enhanced 3D UI CSS - Blue and White with Glowing Effects
st.markdown("""
    <style>
        /* Main containers with 3D effect */
        .css-1r6slb0, .css-12oz5g7, .stDataFrame, .element-container, div[data-testid="stExpander"] {
            background: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(240,248,255,0.85));
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2), 
                        0 4px 8px rgba(0, 102, 204, 0.1),
                        inset 0 0 5px rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 1.2rem;
            margin-bottom: 1rem;
        }
        
        /* Glowing effect on hover */
        .css-1r6slb0:hover, .css-12oz5g7:hover, div[data-testid="stExpander"]:hover {
            box-shadow: 0 8px 32px rgba(0, 102, 204, 0.3),
                        0 0 15px rgba(0, 102, 204, 0.2),
                        inset 0 0 5px rgba(255, 255, 255, 0.8);
            transition: all 0.3s ease;
        }
        
        /* Buttons with 3D effect */
        .stButton > button {
            background: linear-gradient(135deg, #0080ff, #0066cc);
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
            border: none;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3),
                        0 2px 4px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        /* Button hover effect */
        .stButton > button:hover {
            background: linear-gradient(135deg, #0099ff, #0052a3);
            box-shadow: 0 6px 15px rgba(0, 102, 204, 0.4),
                       0 0 8px rgba(0, 102, 204, 0.6),
                       0 0 0 2px rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        /* Button active effect */
        .stButton > button:active {
            transform: translateY(1px);
            box-shadow: 0 2px 8px rgba(0, 102, 204, 0.3);
        }
        
        /* Headers with blue accent */
        h1, h2, h3 {
            color: #0066cc;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding-bottom: 0.3rem;
            border-bottom: 2px solid rgba(0, 102, 204, 0.2);
        }
        
        /* Inputs with 3D effect */
        .stTextInput input, .stSelectbox, .stMultiselect, .stDateInput input {
            border-radius: 8px;
            border: 1px solid rgba(0, 102, 204, 0.2);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05),
                        inset 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        /* Input focus effect */
        .stTextInput input:focus, .stSelectbox:focus, .stMultiselect:focus {
            border-color: #0066cc;
            box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2);
        }
        
        /* Calendar container */
        .calendar-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0, 102, 204, 0.15),
                        0 6px 12px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
            margin-bottom: 20px;
        }
        
        /* Radio buttons */
        .stRadio > div {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            padding: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        /* Success message */
        .element-container div[data-baseweb="notification"] {
            background: linear-gradient(135deg, #a8edbc, #19cc5a);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(25, 204, 90, 0.2);
        }
        
        /* Error message */
        .element-container div[data-baseweb="notification"][kind="negative"] {
            background: linear-gradient(135deg, #ffbbbb, #ff5252);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(255, 82, 82, 0.2);
        }
        
        /* Warning message */
        .element-container div[data-baseweb="notification"][kind="warning"] {
            background: linear-gradient(135deg, #ffecb3, #ffc107);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
        }
        
        /* Custom calendar styling */
        .fc-view-harness {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
        }
        
        .fc-timegrid-slot, .fc-daygrid-day {
            border: 1px solid rgba(0, 102, 204, 0.1) !important;
        }
        
        .fc-day-today {
            background: rgba(0, 102, 204, 0.05) !important;
        }
        
        .fc-toolbar-title {
            color: #0066cc !important;
            font-weight: 600 !important;
        }
        
        .fc-button-primary {
            background: linear-gradient(135deg, #0080ff, #0066cc) !important;
            border: none !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        }
        
        .fc-event {
            border-radius: 6px !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
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

status_colors = {
    "Confirmed": "#28a745", 
    "To Be Attend": "#ffc107", 
    "Declined": "#dc3545"
}

time_options = get_time_options()

# --- Navigation ---
page = set_header_nav("VU LOGO.png")

# --- Home ---
if page == "Home":
    st.title("🏫 SRG Roster Management System")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div style="padding: 20px; animation: pulse 2s infinite;">
            <h2>Welcome to the Enhanced Roster System</h2>
            <p style="font-size: 18px;">A modern 3D interface for managing student resource group schedules efficiently.</p>
            <ul style="font-size: 16px;">
                <li>Students can submit their weekly availability</li>
                <li>Lecturers can manage and confirm shifts</li>
                <li>View interactive calendars with time scheduling</li>
                <li>Generate reports and export data</li>
            </ul>
        </div>
        
        <style>
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(0, 102, 204, 0.4); }
                70% { box-shadow: 0 0 0 10px rgba(0, 102, 204, 0); }
                100% { box-shadow: 0 0 0 0 rgba(0, 102, 204, 0); }
            }
        </style>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <div style="font-size: 80px; color: #0066cc; text-shadow: 0 0 10px rgba(0, 102, 204, 0.5);">
                <i class="fas fa-calendar-check"></i>
            </div>
            <p style="font-size: 16px; margin-top: 20px;">Use the menu above to navigate to your portal</p>
        </div>
        """, unsafe_allow_html=True)

# --- Student Portal ---
elif page == "Student Portal":
    st.title("🧑‍🎓 Student Portal")
    # Login / Logout
    if st.session_state.current_user:
        st.success(f"Logged in as {st.session_state.users[st.session_state.current_user]['name']}")
        if st.button("Logout"):
            st.session_state.current_user = None
            st.experimental_rerun()
    else:
        with st.form("login"):
            st.text_input("Student ID", key="login_id")
            st.text_input("Full Name", key="login_name")
            if st.form_submit_button("Login / Register"):
                sid = st.session_state.login_id
                name = st.session_state.login_name
                if sid and name:
                    st.session_state.current_user = sid
                    st.session_state.users.setdefault(sid, {"name": name, "shifts": []})
                    st.experimental_rerun()
                else:
                    st.warning("Enter both ID and Name.")
    # Availability & Submit
    if st.session_state.current_user:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📅 Enter Weekly Availability")
            today = datetime.today()
            week_start = today - timedelta(days=today.weekday())
            shifts = []
            for i in range(7):
                day = week_start + timedelta(days=i)
                st.markdown(f"**{day.strftime('%A (%d %b)')}**")
                if st.checkbox("Available", key=f"avail_{i}"):
                    col_s, col_e = st.columns(2)
                    with col_s:
                        st.selectbox("Start", options=time_options, key=f"start_{i}")
                    with col_e:
                        st.selectbox("End", options=time_options, key=f"end_{i}")
                    s = datetime.strptime(st.session_state[f"start_{i}"], "%I:%M %p").time()
                    e = datetime.strptime(st.session_state[f"end_{i}"], "%I:%M %p").time()
                    if s < e:
                        shifts.append({
                            "date": day.strftime("%Y-%m-%d"),
                            "day": day.strftime("%A"),
                            "start": s.strftime("%H:%M:%S"),
                            "end": e.strftime("%H:%M:%S"),
                            "display": f"{st.session_state[f'start_{i}']}–{st.session_state[f'end_{i}']}",
                            "status": "To Be Attend"
                        })
                    else:
                        st.warning("End time must be after start time")
            if st.button("Submit Shifts"):
                st.session_state.users[st.session_state.current_user]["shifts"] = shifts
                st.success("Submitted!")
        
        with col2:
            # Student Calendar View with view options
            st.subheader("📆 My Schedule")
            view_options = ["timeGridWeek", "dayGridMonth", "timeGridDay"]
            view_labels = ["Weekly Schedule", "Monthly Calendar", "Daily Schedule"]
            
            view_index = view_options.index(st.session_state.calendar_view) if st.session_state.calendar_view in view_options else 0
            selected_view_index = st.select_slider("Calendar View", options=range(len(view_options)), value=view_index, format_func=lambda x: view_labels[x])
            st.session_state.calendar_view = view_options[selected_view_index]
            
            events = [
                {
                    "title": st.session_state.users[st.session_state.current_user]["name"],
                    "start": f"{sh['date']}T{sh['start']}",
                    "end":   f"{sh['date']}T{sh['end']}",
                    "color": status_colors[sh['status']]
                }
                for sh in st.session_state.users[st.session_state.current_user]["shifts"]
            ]
            
            st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
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
                    }
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)

# --- Lecturer Portal ---
elif page == "Lecturer Portal":
    st.title("👩‍🏫 Lecturer Portal")
    # Login / Logout
    if not st.session_state.admin_logged_in:
        user = st.text_input("Username", key="admin_user")
        pwd  = st.text_input("Password", type="password", key="admin_pass")
        if st.button("Login"):
            if user == "demo" and pwd == "demo":
                st.session_state.admin_logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    else:
        st.success("Logged in as Lecturer")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()

        # Lecturer Tabs
        tab1, tab2, tab3 = st.tabs(["Manage Shifts", "Calendar View", "Reports"])

        with tab1:
            st.subheader("📋 Manage Student Shifts")
            for sid, data in st.session_state.users.items():
                with st.expander(f"{data['name']} (ID: {sid})"):
                    if data.get("shifts"):
                        df = pd.DataFrame(data["shifts"])
                        for i in range(len(df)):
                            col1, col2, col3 = st.columns([2,2,1])
                            with col1:
                                df_date = datetime.strptime(df.loc[i,"date"],"%Y-%m-%d").strftime("%d %b %Y")
                                st.write(f"**{df.loc[i,'day']} ({df_date})**")
                            with col2:
                                st.write(df.loc[i,'display'])
                            with col3:
                                new_status = st.selectbox(
                                    "Status",
                                    ["To Be Attend","Confirmed","Declined"],
                                    index=["To Be Attend","Confirmed","Declined"].index(df.loc[i,"status"]),
                                    key=f"status_{sid}_{i}"
                                )
                                df.at[i,"status"] = new_status
                        st.session_state.users[sid]["shifts"] = df.to_dict("records")
                    else:
                        st.info("No shifts submitted.")

        with tab2:
            st.subheader("📆 Complete Roster Calendar")
            
            # Calendar View Options
            view_options = ["timeGridWeek", "dayGridMonth", "timeGridDay"]
            view_labels = ["Weekly Schedule", "Monthly Calendar", "Daily Schedule"]
            
            view_index = view_options.index(st.session_state.calendar_view) if st.session_state.calendar_view in view_options else 0
            selected_view_index = st.select_slider("Calendar View", options=range(len(view_options)), value=view_index, format_func=lambda x: view_labels[x])
            st.session_state.calendar_view = view_options[selected_view_index]
            
            # Gather all events
            all_events = []
            for sid, data in st.session_state.users.items():
                for sh in data.get("shifts", []):
                    all_events.append({
                        "title": f"{data['name']} ({sh['display']})",
                        "start": f"{sh['date']}T{sh['start']}",
                        "end":   f"{sh['date']}T{sh['end']}",
                        "color": status_colors[sh['status']]
                    })
            
            # Display enhanced calendar with time grid
            st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
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
                    "nowIndicator": True
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.subheader("📊 Confirmed Shifts Report")
            records = []
            for sid, data in st.session_state.users.items():
                for sh in data.get("shifts", []):
                    if sh["status"] == "Confirmed":
                        hrs = round((datetime.strptime(sh["end"], "%H:%M:%S") - datetime.strptime(sh["start"], "%H:%M:%S")).seconds/3600, 2)
                        records.append({
                            "Student ID": sid,
                            "Name": data["name"],
                            "Date": datetime.strptime(sh["date"], "%Y-%m-%d").strftime("%d %b %Y"),
                            "Day": sh["day"],
                            "Time": sh["display"],
                            "Hours": hrs
                        })
            df = pd.DataFrame(records)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Confirmed Hours", f"{df['Hours'].sum():.2f}")
                with col2:
                    st.metric("Total Confirmed Shifts", f"{len(df)}")
                
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name="Weekly Summary", index=False)
                    wb = writer.book
                    ws = writer.sheets["Weekly Summary"]
                    header_fmt = wb.add_format({"bold": True, "bg_color": "#0066cc", "font_color": "white", "border": 1})
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
