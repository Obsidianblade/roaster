import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
import base64
from streamlit_calendar import calendar
import streamlit.components.v1 as components

# --- Helper Functions ---
def set_background(image_path):
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

def get_time_options():
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

time_options = get_time_options()

# --- State Init ---
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

status_colors = {"Confirmed": "#10b981", "To Be Attend": "#f59e0b", "Declined": "#ef4444"}

# --- Navigation Bar ---
def render_nav():
    st.markdown("""
    <div style='display:flex; align-items:center; justify-content:space-between; background:white; padding:0.5rem 1rem; border-radius:8px;'>
        <div style='display:flex; align-items:center; gap:0.5rem;'>
            <img src='VU LOGO.png' width='32' />
            <span style='font-weight:700; font-size:1.25rem;'>SRG Roster Manager</span>
        </div>
        <div style='display:flex; gap:1rem;'>
    """, unsafe_allow_html=True)
    pages = ["Home", "Student Portal", "Lecturer Portal"]
    for p in pages:
        if st.button(p, key=p):
            st.session_state.active_page = p
            st.experimental_rerun()
        # active styling via JS not needed
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Home Page ---
def render_home():
    st.markdown("""
    <div style='padding:1rem; background:rgba(255,255,255,0.85); border-radius:10px;'>
        <h1>Welcome to SRG Roster Manager</h1>
        <p>A modern interface for submitting availability and managing shifts.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Student Portal ---
def render_student_portal():
    st.subheader("🧑‍🎓 Student Portal")
    if not st.session_state.current_user:
        with st.form("login_form"):
            student_id = st.text_input("Student ID")
            student_name = st.text_input("Full Name")
            submitted = st.form_submit_button("Login / Register")
            if submitted:
                if student_id and student_name:
                    st.session_state.current_user = student_id
                    st.session_state.users.setdefault(student_id, {"name": student_name, "shifts": []})
                    st.experimental_rerun()
                else:
                    st.warning("Enter both ID and Name.")
    else:
        st.success(f"Logged in as {st.session_state.users[st.session_state.current_user]['name']}")
        if st.button("Logout"): 
            st.session_state.current_user = None
            st.experimental_rerun()

        st.markdown("<div style='background:white; padding:1rem; border-radius:8px;'>", unsafe_allow_html=True)
        st.subheader("📅 Enter Weekly Availability")
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        shifts = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            st.markdown(f"**{day.strftime('%A (%d %b)')}**")
            if st.checkbox("Available", key=f"avail_{i}"):
                col1, col2 = st.columns(2)
                with col1:
                    start = st.selectbox("Start", options=time_options, key=f"start_{i}")
                with col2:
                    end = st.selectbox("End", options=time_options, key=f"end_{i}")
                s = datetime.strptime(start, "%I:%M %p").time()
                e = datetime.strptime(end, "%I:%M %p").time()
                if s < e:
                    shifts.append({
                        "date": day.strftime("%Y-%m-%d"),
                        "day": day.strftime("%A"),
                        "start": s.strftime("%H:%M:%S"),
                        "end": e.strftime("%H:%M:%S"),
                        "display": f"{start} – {end}",
                        "status": "To Be Attend"
                    })
                else:
                    st.warning("End time must be after start time")
        if st.button("Submit Shifts"):
            st.session_state.users[st.session_state.current_user]["shifts"] = shifts
            st.success("Shifts submitted!")
        st.markdown("</div>", unsafe_allow_html=True)

        # Display calendar
        student = st.session_state.current_user
        events = [
            {"title": st.session_state.users[student]['name'],
             "start": f"{sh['date']}T{sh['start']}",
             "end":   f"{sh['date']}T{sh['end']}",
             "color": status_colors[sh['status']]}
            for sh in st.session_state.users[student]['shifts']]
        st.markdown("<div class='calendar-container'>", unsafe_allow_html=True)
        calendar(events=events, options={"initialView": st.session_state.get('calendar_view','timeGridWeek')})
        st.markdown("</div>", unsafe_allow_html=True)

# --- Lecturer Portal ---
def render_lecturer_portal():
    st.subheader("👩‍🏫 Lecturer Portal")
    if not st.session_state.admin_logged_in:
        user = st.text_input("Username")
        pwd  = st.text_input("Password", type="password")
        if st.button("Login"):
            if user=='demo' and pwd=='demo':
                st.session_state.admin_logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    else:
        st.success("Logged in as Lecturer")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()

        tabs = st.tabs(["Manage Shifts","Calendar View","Reports"])
        # Manage
        with tabs[0]:
            st.subheader("📋 Manage Student Shifts")
            for sid, data in st.session_state.users.items():
                with st.expander(f"{data['name']} (ID: {sid})"):
                    df = pd.DataFrame(data['shifts']) if data['shifts'] else pd.DataFrame()
                    if not df.empty:
                        for i in df.index:
                            cols = st.columns([2,2,1])
                            cols[0].write(f"{df.at[i,'day']} ({df.at[i,'date']})")
                            cols[1].write(df.at[i,'display'])
                            new = cols[2].selectbox("Status",
                                ["To Be Attend","Confirmed","Declined"],
                                index=["To Be Attend","Confirmed","Declined"].index(df.at[i,'status']),
                                key=f"st_{sid}_{i}")
                            df.at[i,'status'] = new
                        st.session_state.users[sid]['shifts'] = df.to_dict('records')
                    else:
                        st.info("No shifts.")
        # Calendar
        with tabs[1]:
            st.subheader("📆 Complete Roster Calendar")
            all_events = []
            for sid, data in st.session_state.users.items():
                for sh in data['shifts']:
                    all_events.append({
                        "title": f"{data['name']} ({sh['display']})",
                        "start": f"{sh['date']}T{sh['start']}",
                        "end":   f"{sh['date']}T{sh['end']}",
                        "color": status_colors[sh['status']]})
            calendar(events=all_events, options={"initialView": st.session_state.get('calendar_view','dayGridMonth')})
        # Reports
        with tabs[2]:
            st.subheader("📊 Confirmed Shifts Report")
            records = []
            for sid, data in st.session_state.users.items():
                for sh in data['shifts']:
                    if sh['status']== 'Confirmed':
                        hrs = round((datetime.strptime(sh['end'],"%H:%M:%S") - datetime.strptime(sh['start'],"%H:%M:%S")).seconds/3600,2)
                        records.append({
                            'Student ID':sid,'Name':data['name'],
                            'Date':datetime.strptime(sh['date'],"%Y-%m-%d").strftime("%d %b %Y"),
                            'Time':sh['display'],'Hours':hrs})
            df = pd.DataFrame(records)
            if not df.empty:
                st.dataframe(df,use_container_width=True)
                st.metric("Total Hours",f"{df['Hours'].sum():.2f}")
                buf=BytesIO()
                with pd.ExcelWriter(buf,engine='xlsxwriter') as writer:
                    df.to_excel(writer,index=False,sheet_name='Summary')
                    ws=writer.sheets['Summary']
                    fmt=writer.book.add_format({'bold':True,'bg_color':'#6366f1','font_color':'white'})
                    for i, col in enumerate(df.columns): ws.write(0,i,col,fmt)
                st.download_button("Download Excel",buf.getvalue(),"report.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("No confirmed shifts.")

# --- Main ---
render_nav()
if st.session_state.active_page == 'Home':
    render_home()
elif st.session_state.active_page == 'Student Portal':
    render_student_portal()
else:
    render_lecturer_portal()
