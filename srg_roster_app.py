
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO
from streamlit_calendar import calendar

st.set_page_config(page_title="SRG Roster Manager", layout="wide")
st.sidebar.title("📋 SRG Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Student Portal", "Admin Portal"])

if "users" not in st.session_state:
    st.session_state.users = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

status_colors = {
    "Confirmed": "green",
    "Pending": "yellow",
    "Declined": "red"
}

if page == "Home":
    st.title("🏫 SRG Roster Management System")
    st.markdown("Choose **Student Portal** or **Admin Portal** from the sidebar.")

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
                st.success(f"Logged in as {student_name}")
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

elif page == "Admin Portal":
    st.title("🧑‍💼 Admin Login")
    if not st.session_state.admin_logged_in:
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_user == "demo" and admin_pass == "demo":
                st.session_state.admin_logged_in = True
                st.success("Admin logged in")
            else:
                st.error("Invalid credentials")

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
                        new_status = st.selectbox("Status", ["Pending", "Confirmed", "Declined"],
                            index=["Pending", "Confirmed", "Declined"].index(df.loc[i, "status"]),
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
