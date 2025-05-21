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
    """Return 30-min interval times in 12-hour format."""
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

# Apply some shared CSS for cards/buttons
st.markdown("""
    <style>
        /* Card containers */
        .css-1r6slb0, .css-12oz5g7, .stDataFrame {
            background: rgba(255,255,255,0.8);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 1rem;
        }
        /* Buttons */
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
        if st.button("Logout"): st.session_state.current_user = None; st.experimental_rerun()
    else:
        with st.form("login"):
            st.text_input("Student ID", key="login_id")
            st.text_input("Full Name", key="login_name")
            if st.form_submit_button("Login / Register"):
                sid = st.session_state.login_id; name = st.session_state.login_name
                if sid and name:
                    st.session_state.current_user = sid
                    st.session_state.users.setdefault(sid, {"name": name, "shifts": []})
                    st.experimental_rerun()
                else: st.warning("Enter both ID and Name.")

    if st.session_state.current_user:
        st.subheader("📅 Enter Weekly Availability")
        today = datetime.today(); week_start = today - timedelta(days=today.weekday())
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
                    shifts.append({"date": day.strftime("%Y-%m-%d"), "day": day.strftime("A"),
                                   "start": s.strftime("%H:%M:%S"), "end": e.strftime("%H:%M:%S"),
                                   "display": f"{st.session_state[f'start_{i}']}–{st.session_state[f'end_{i}']}",
                                   "status": "To Be Attend"})
        if st.button("Submit Shifts"): st.session_state.users[st.session_state.current_user]["shifts"] = shifts; st.success("Submitted!")
        # Calendar
        events = [{"title": st.session_state.users[st.session_state.current_user]["name"],
                   "start": f"{sh['date']}T{sh['start']}", "end": f"{sh['date']}T{sh['end']}",
                   "color": status_colors[sh['status']]} for sh in st.session_state.users[st.session_state.current_user]["shifts"]]
        calendar(events=events, options={"initialView":"dayGridWeek"})

# --- Lecturer Portal ---
elif page == "Lecturer Portal":
    st.title("👩‍🏫 Lecturer Portal")
    if not st.session_state.admin_logged_in:
        user = st.text_input("Username", key="admin_user"); pwd = st.text_input("Password", type="password", key="admin_pass")
        if st.button("Login"): 
            if user=="demo" and pwd=="demo": st.session_state.admin_logged_in=True; st.experimental_rerun()
            else: st.error("Invalid.")
    else:
        st.success("Logged in as Lecturer")
        if st.button("Logout"): st.session_state.admin_logged_in=False; st.experimental_rerun()
        # Show full calendar for all students
        all_events = []
        for sid, data in st.session_state.users.items():
            for sh in data.get("shifts", []):
                all_events.append({"title": f"{data['name']} ({sh['display']})",
                                   "start": f"{sh['date']}T{sh['start']}",
                                   "end": f"{sh['date']}T{sh['end']}",
                                   "color": status_colors[sh['status']]
                                  })
        calendar(events=all_events, options={"initialView":"dayGridMonth"})
        # Reports
        df = pd.DataFrame([{
            "Student": data['name'],
            "Date": sh['date'],
            "Time": sh['display'],
            "Status": sh['status']
        } for sid,data in st.session_state.users.items() for sh in data.get('shifts',[]) if sh['status']=='Confirmed'])
        if not df.empty:
            st.subheader("📊 Confirmed Shifts Report")
            st.dataframe(df, use_container_width=True)
            buf=BytesIO(); with pd.ExcelWriter(buf, engine="xlsxwriter") as w: df.to_excel(w, index=False)
            st.download_button("Download Excel", buf.getvalue(), "report.xlsx", "application/vnd.ms-excel")
