
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from streamlit_calendar import calendar

# Setup
st.set_page_config(page_title="SRG Roster Manager", layout="wide")
st.sidebar.title("📋 SRG Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Student Portal", "Admin Portal"])

# Global state init
if "users" not in st.session_state:
    st.session_state.users = {}  # Format: {student_id: {"name": ..., "shifts": []}}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Page 1: Home
if page == "Home":
    st.title("🏫 SRG Roster Management System")
    st.markdown("Welcome to the Student Roster Management System. Please choose **Student Portal** or **Admin Portal** from the left sidebar.")

# Page 2: Student Portal
elif page == "Student Portal":
    st.title("🧑‍🎓 Student Login / Registration")
    with st.form("student_login"):
        student_id = st.text_input("Student ID")
        student_name = st.text_input("Full Name")
        submitted = st.form_submit_button("Login / Register")

        if submitted:
            if student_id and student_name:
                st.session_state.current_user = student_id
                if student_id not in st.session_state.users:
                    st.session_state.users[student_id] = {"name": student_name, "shifts": []}
                st.success(f"Logged in as {student_name} (ID: {student_id})")
            else:
                st.warning("Please enter both ID and name.")

    if st.session_state.current_user:
        st.subheader("📅 Enter Your Weekly Availability with Time")
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        shifts = []

        for i in range(7):
            day = week_start + timedelta(days=i)
            st.markdown(f"**{day.strftime('%A (%d %b)')}**")
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input(f"Start Time - {day.strftime('%A')}", value=time(9, 0), key=f"start_{i}")
            with col2:
                end_time = st.time_input(f"End Time - {day.strftime('%A')}", value=time(17, 0), key=f"end_{i}")
            if start_time < end_time:
                shifts.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "day": day.strftime("%A"),
                    "start": str(start_time),
                    "end": str(end_time),
                    "status": "Pending"
                })

        if st.button("Submit Weekly Shifts"):
            st.session_state.users[st.session_state.current_user]["shifts"] = shifts
            st.success("✅ Shifts submitted successfully!")

        # Show existing shifts in table
        if st.session_state.users[st.session_state.current_user]["shifts"]:
            st.subheader("📌 Submitted Shifts")
            st.table(pd.DataFrame(st.session_state.users[st.session_state.current_user]["shifts"]))

        # Student calendar view
        student_data = st.session_state.users[st.session_state.current_user]
        events = [
            {
                "title": student_data['name'],
                "start": f"{shift['date']}T{shift['start']}",
                "end": f"{shift['date']}T{shift['end']}",
                "extendedProps": {
                    "status": shift['status'],
                    "start_time": shift['start'],
                    "end_time": shift['end']
                }
            }
            for shift in student_data["shifts"]
        ]
        st.subheader("📆 My Calendar View")
        calendar(events=events, options={"initialView": "dayGridMonth"})

# Page 3: Admin Portal
elif page == "Admin Portal":
    st.title("🧑‍💼 Admin Login")
    if not st.session_state.admin_logged_in:
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_user == "demo" and admin_pass == "demo":
                st.session_state.admin_logged_in = True
                st.success("✅ Logged in as Admin")
            else:
                st.error("❌ Invalid credentials")

    if st.session_state.admin_logged_in:
        st.subheader("📋 All Student Shifts")
        for student_id, data in st.session_state.users.items():
            st.markdown(f"### {data['name']} (ID: {student_id})")
            if isinstance(data["shifts"], list) and data["shifts"]:
                df = pd.DataFrame(data["shifts"])
                for i in range(len(df)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{df.loc[i, 'day']} - {df.loc[i, 'date']}**: {df.loc[i, 'start']} to {df.loc[i, 'end']}")
                    with col2:
                        color_label = {
                            "Pending": "🟨 Pending",
                            "Confirmed": "🟩 Confirmed",
                            "Declined": "🟥 Declined"
                        }
                        new_status = st.selectbox("Status", ["Pending", "Confirmed", "Declined"],
                                                  index=["Pending", "Confirmed", "Declined"].index(df.loc[i, "status"]),
                                                  key=f"status_{student_id}_{i}",
                                                  format_func=lambda x: color_label[x])
                        df.at[i, "status"] = new_status
                st.session_state.users[student_id]["shifts"] = df.to_dict(orient="records")
                st.markdown("---")
            else:
                st.info("No shifts submitted.")

        # Admin calendar view
        st.subheader("📆 Full Calendar View")
        all_events = []
        for student_id, data in st.session_state.users.items():
            for shift in data["shifts"]:
                all_events.append({
                    "title": data["name"],
                    "start": f"{shift['date']}T{shift['start']}",
                    "end": f"{shift['date']}T{shift['end']}",
                    "extendedProps": {
                        "status": shift["status"],
                        "start_time": shift["start"],
                        "end_time": shift["end"]
                    }
                })
        calendar(events=all_events, options={"initialView": "dayGridMonth"})

        # Summary report
        st.subheader("📊 Weekly Summary Report")
        summary = []
        for student_id, data in st.session_state.users.items():
            total_hours = 0
            for shift in data["shifts"]:
                if shift["status"] == "Confirmed":
                    start = datetime.strptime(shift["start"], "%H:%M:%S")
                    end = datetime.strptime(shift["end"], "%H:%M:%S")
                    hours = (end - start).seconds / 3600
                    total_hours += hours
            summary.append({
                "Student ID": student_id,
                "Name": data["name"],
                "Confirmed Hours": total_hours
            })

        st.table(pd.DataFrame(summary))
