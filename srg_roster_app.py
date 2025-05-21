import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
from streamlit_calendar import calendar

st.set_page_config(page_title="SRG Roster Manager", layout="wide")
st.markdown("""
    <style>
       st.markdown("""
    <style>
        body {
            background-color: #f4f9ff;
            color: #00274d;
            font-family: 'Segoe UI', sans-serif;
        }

        .stApp {
            background-color: #f4f9ff;
        }

        .stButton > button {
            background: linear-gradient(145deg, #1d4ed8, #3b82f6);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 20px;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            font-size: 16px;
        }

        .stButton > button:hover {
            background: linear-gradient(145deg, #2563eb, #60a5fa);
            box-shadow: 0 6px 14px rgba(59, 130, 246, 0.5);
        }

        input, .stSelectbox div div, .stTimeInput input {
            background-color: #ffffff !important;
            border: 1px solid #d1e3ff !important;
            border-radius: 8px !important;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            padding: 8px;
        }

        .stSidebar {
            background: linear-gradient(to bottom, #1e3a8a, #2563eb);
            color: white;
        }

        .stSidebar .css-1d391kg, .stSidebar .css-1lcbmhc {
            color: white;
        }

        .css-1v3fvcr {
            font-size: 20px;
            font-weight: bold;
        }

        .block-container {
            padding: 2rem 3rem;
        }
    </style>
""", unsafe_allow_html=True)
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("📋 SRG Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Student Portal", "Lecturer Login"])

if "users" not in st.session_state:
    st.session_state.users = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

status_colors = {
    "Confirmed": "green",
    "To Be Attend": "yellow",
    "Declined": "red"
}

def get_rounded_times():
    times = []
    for hour in range(6, 22):
        times.append(time(hour, 0))
        times.append(time(hour, 30))
    return times

rounded_times = get_rounded_times()

def format_time(t):
    return t.strftime("%I:%M %p")

if page == "Home":
    st.title("🏫 SRG Roster Management System")
    st.markdown("Choose **Student Portal** or **Lecturer Login** from the sidebar.")

elif page == "Student Portal":
    st.title("🧑‍🎓 Student Login / Registration")
    if st.session_state.current_user:
        st.success(f"Logged in as {st.session_state.users[st.session_state.current_user]['name']}")
        if st.button("Logout"):
            st.session_state.current_user = None
            st.experimental_rerun()
    else:
        with st.form("student_login"):
            student_id = st.text_input("Student ID")
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

    if st.session_state.current_user:
        st.subheader("📅 Enter Weekly Availability")
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        shifts = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            st.markdown(f"**{day.strftime('%A (%d %b)')}**")
            available = st.checkbox(f"I'm available on {day.strftime('%A')}", key=f"available_{i}", value=True)
            if available:
                col1, col2 = st.columns(2)
                with col1:
                    start_time = st.selectbox(f"Start Time - {day.strftime('%A')}", options=rounded_times, key=f"start_{i}")
                with col2:
                    end_time = st.selectbox(f"End Time - {day.strftime('%A')}", options=rounded_times, key=f"end_{i}")
                if start_time < end_time:
                    shifts.append({
                        "date": day.strftime("%Y-%m-%d"),
                        "day": day.strftime("%A"),
                        "start": str(start_time),
                        "end": str(end_time),
                        "status": "To Be Attend"
                    })

        if st.button("Submit Weekly Shifts"):
            st.session_state.users[st.session_state.current_user]["shifts"] = shifts
            st.success("Shifts submitted!")

        student_data = st.session_state.users[st.session_state.current_user]
        events = [
            {
                "title": student_data["name"],
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
            for shift in student_data["shifts"]
        ]
        st.subheader("📆 My Calendar View")
        calendar(events=events, options={"initialView": "dayGridMonth"})

elif page == "Lecturer Login":
    st.title("👩‍🏫 Lecturer Login")
    if not st.session_state.admin_logged_in:
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_user == "demo" and admin_pass == "demo":
                st.session_state.admin_logged_in = True
                st.success("Lecturer logged in")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
    else:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()

    if st.session_state.admin_logged_in:
        st.subheader("📋 Manage Shifts")
        for student_id, data in st.session_state.users.items():
            st.markdown(f"### {data['name']} (ID: {student_id})")
            if isinstance(data["shifts"], list) and data["shifts"]:
                df = pd.DataFrame(data["shifts"])
                for i in range(len(df)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"{df.loc[i, 'day']} - {df.loc[i, 'date']}: {df.loc[i, 'start']} to {df.loc[i, 'end']}")
                    with col2:
                        new_status = st.selectbox("Status", ["To Be Attend", "Confirmed", "Declined"],
                            index=["To Be Attend", "Confirmed", "Declined"].index(df.loc[i, "status"]),
                            key=f"status_{student_id}_{i}")
                        df.at[i, "status"] = new_status
                st.session_state.users[student_id]["shifts"] = df.to_dict(orient="records")
            else:
                st.info("No shifts submitted.")

        st.subheader("📆 All Shifts on Calendar")
        all_events = []
        for student_id, data in st.session_state.users.items():
            for shift in data["shifts"]:
                all_events.append({
                    "title": data["name"],
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
        calendar(events=all_events, options={"initialView": "dayGridMonth"})

        st.subheader("📊 Weekly Summary Report")
        records = []
        for student_id, data in st.session_state.users.items():
            for shift in data["shifts"]:
                if shift["status"] == "Confirmed":
                    start = datetime.strptime(shift["start"], "%H:%M:%S")
                    end = datetime.strptime(shift["end"], "%H:%M:%S")
                    hours = (end - start).seconds / 3600
                    records.append({
                        "Student ID": student_id,
                        "Name": data["name"],
                        "Date": shift["date"],
                        "Day": shift["day"],
                        "Start Time": shift["start"],
                        "End Time": shift["end"],
                        "Status": shift["status"],
                        "Hours": hours
                    })

        df_summary = pd.DataFrame(records)
        st.dataframe(df_summary)

        if not df_summary.empty:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_summary.to_excel(writer, index=False, sheet_name="Weekly Summary")
            st.download_button(
                label="📥 Download Excel Summary",
                data=buffer.getvalue(),
                file_name="weekly_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
