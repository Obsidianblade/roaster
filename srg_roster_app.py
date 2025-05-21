import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
import base64
from streamlit_calendar import calendar

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

# Shared CSS for cards & buttons
st.markdown("""
    <style>
        .css-1r6slb0, .css-12oz5g7, .stDataFrame {
            background: rgba(255,255,255,0.85);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 1rem;
        }
        .stButton > button {
            background: #0066cc;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
        }
        .stButton > button:hover {
            background: #0052a3;
        }
    </style>
""", unsafe_allow_html=True)

# --- Navigation ---
page = set_header_nav("VU LOGO.png")

# --- Session State Init ---
if "users" not in st.session_state:
    st.session_state.users = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

status_colors = {"Confirmed": "#28a745", "To Be Attend": "#ffc107", "Declined": "#dc3545"}

time_options = get_time_options()

# --- Home ---
if page == "Home":
    st.title("🏫 SRG Roster Management System")
    st.markdown("Welcome! Use the menu above to navigate.")

# --- Student Portal ---
elif page == "Student Portal":
    st.title("🧑‍🎓 Student Portal")
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
    if st.session_state.current_user:
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
                    st.selectbox("Start", options=time_options, key=f"start_{i}")
                with col2:
                    st.selectbox("End", options=time_options, key=f"end_{i}")
                s = datetime.strptime(st.session_state[f"start_{i}"], "%I:%M %p").time()
                e = datetime.strptime(st.session_state[f"end_{i}"], "%I:%M %p").time()
                if s < e:
                    shifts.append({"date": day.strftime("%Y-%m-%d"), "day": day.strftime("%A"), "start": s.strftime("%H:%M:%S"), "end": e.strftime("%H:%M:%S"), "display": f"{st.session_state[f'start_{i}']}–{st.session_state[f'end_{i}']}", "status": "To Be Attend"})
                else:
                    st.warning("End time must be after start time")
        if st.button("Submit Shifts"):
            st.session_state.users[st.session_state.current_user]["shifts"] = shifts
            st.success("Submitted!")
        # Student calendar
        events = [
            {"title": st.session_state.users[st.session_state.current_user]["name"], "start": f"{sh['date']}T{sh['start']}", "end": f"{sh['date']}T{sh['end']}", "color": status_colors[sh['status']]} for sh in st.session_state.users[st.session_state.current_user]["shifts"]
        ]
        st.subheader("📆 My Schedule")
        calendar(events=events, options={"initialView": "dayGridWeek"})

# --- Lecturer Portal ---
elif page == "Lecturer Portal":
    st.title("👩‍🏫 Lecturer Portal")
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

        # Tabs
        tab1, tab2, tab3 = st.tabs(["Manage Shifts","Calendar View","Reports"])

        with tab1:
            st.subheader("📋 Manage Student Shifts")
            for sid, data in st.session_state.users.items():
                with st.expander(f"{data['name']} (ID: {sid})"):
                    if data.get("shifts"):
                        df = pd.DataFrame(data["shifts"])
                        for i in range(len(df)):
                            col1, col2, col3 = st.columns([2,2,1])
                            with col1:
                                date_fmt = datetime.strptime(df.loc[i,"date"],"%Y-%m-%d").strftime("%d %b %Y")
                                st.write(f"**{df.loc[i,'day']} ({date_fmt})**")
                            with col2:
                                st.write(df.loc[i,'display'])
                            with col3:
                                new_status = st.selectbox("Status", ["To Be Attend","Confirmed","Declined"], index=["To Be Attend","Confirmed","Declined"].index(df.loc[i,"status"]), key=f"status_{sid}_{i}")
                                df.at[i,"status"] = new_status
                        st.session_state.users[sid]["shifts"] = df.to_dict("records")
                    else:
                        st.info("No shifts submitted.")

        with tab2:
            st.subheader("📆 Complete Roster Calendar")
            all_events = []
            for sid, data in st.session_state.users.items():
                for sh in data.get("shifts", []):
                    all_events.append({
                        "title": f"{data['name']} ({sh['display']})",
                        "start": f"{sh['date']}T{sh['start']}",
                        "end":   f"{sh['date']}T{sh['end']}",
                        "color": status_colors[sh['status']]})
            # Wrap calendar in white container for visibility
            st.markdown('<div style="background: rgba(255,255,255,0.9); padding: 1rem; border-radius: 8px;">', unsafe_allow_html=True)
            calendar(events=all_events, options={"initialView":"dayGridMonth"})
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
                st.metric("Total Confirmed Hours", f"{df['Hours'].sum():.2f}")
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                    df.to_excel(writer, sheet_name="Weekly Summary", index=False)
                    wb = writer.book
                    ws = writer.sheets["Weekly Summary"]
                    header_fmt = wb.add_format({"bold": True, "bg_color": "#0066cc", "font_color": "white", "border": 1})
                    for col_num, col_name in enumerate(df.columns):
                        ws.write(0, col_num, col_name, header_fmt)
                st.download_button(label="📥 Download Excel Summary", data=buf.getvalue(), file_name="SRG_weekly_summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("No confirmed shifts to display.")
