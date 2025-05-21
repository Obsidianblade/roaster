
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Shift Calendar", layout="wide")

# Initialize global state
if "users" not in st.session_state:
    st.session_state.users = {}  # Format: {student_id: {"name": ..., "shifts": {(day, hour): "student"/"confirmed"}}}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HOURS = list(range(9, 18))  # 9AM to 5PM

# Login system
st.sidebar.title("Login")
login_type = st.sidebar.radio("Login as", ["Student", "Admin"])

if login_type == "Student":
    student_id = st.sidebar.text_input("Student ID")
    student_name = st.sidebar.text_input("Name")
    if st.sidebar.button("Login / Register"):
        if student_id and student_name:
            st.session_state.current_user = student_id
            if student_id not in st.session_state.users:
                st.session_state.users[student_id] = {"name": student_name, "shifts": {}}
            st.success(f"Logged in as {student_name}")

elif login_type == "Admin":
    admin_user = st.sidebar.text_input("Username")
    admin_pass = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Admin Login"):
        if admin_user == "demo" and admin_pass == "demo":
            st.session_state.admin_logged_in = True
            st.success("Admin logged in")
        else:
            st.error("Invalid admin credentials")

# Student view
if st.session_state.current_user:
    user_id = st.session_state.current_user
    user_data = st.session_state.users[user_id]
    st.header(f"🧑‍🎓 Shift Calendar for {user_data['name']}")

    for hour in HOURS:
        cols = st.columns(7)
        for i, day in enumerate(DAYS):
            key = f"{user_id}_{day}_{hour}"
            label = f"{day} {hour}:00"
            current = user_data["shifts"].get((day, hour), "")
            if current == "confirmed":
                cols[i].success("✔️")
            elif current == "student":
                if cols[i].button("🟨", key=key):
                    del user_data["shifts"][(day, hour)]
                else:
                    cols[i].info("⏳")
            else:
                if cols[i].button(label, key=key):
                    user_data["shifts"][(day, hour)] = "student"

# Admin view
elif st.session_state.admin_logged_in:
    st.header("🧑‍🏫 Admin Shift Approval Panel")

    for sid, data in st.session_state.users.items():
        st.subheader(f"{data['name']} (ID: {sid})")
        for hour in HOURS:
            cols = st.columns(7)
            for i, day in enumerate(DAYS):
                key = f"admin_{sid}_{day}_{hour}"
                status = data["shifts"].get((day, hour), "")
                if status == "student":
                    if cols[i].button("Approve", key=key):
                        data["shifts"][(day, hour)] = "confirmed"
                elif status == "confirmed":
                    cols[i].success("✔️")
                else:
                    cols[i].write("—")

    st.subheader("📊 Weekly Summary")
    summary_data = []
    for sid, data in st.session_state.users.items():
        total_hours = sum(1 for val in data["shifts"].values() if val == "confirmed")
        summary_data.append({"Student ID": sid, "Name": data["name"], "Total Hours": total_hours})
    df_summary = pd.DataFrame(summary_data)
    st.table(df_summary)
