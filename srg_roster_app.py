
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import io

st.set_page_config(page_title="SRG Roster Management", layout="wide")

# Constants
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
HOURS = list(range(9, 18))  # 9AM–5PM

# Session state initialization
if "users" not in st.session_state:
    st.session_state.users = {}  # {student_id: {"name": ..., "shifts": {(day, hour): "Available"/"Confirmed"}}}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Sidebar login
st.sidebar.title("SRG Login")
login_role = st.sidebar.radio("Login as", ["Student", "Admin"])

if login_role == "Student":
    sid = st.sidebar.text_input("Student ID")
    name = st.sidebar.text_input("Full Name")
    if st.sidebar.button("Login / Register"):
        if sid and name:
            st.session_state.current_user = sid
            if sid not in st.session_state.users:
                st.session_state.users[sid] = {"name": name, "shifts": {}}
            st.success(f"Logged in as {name}")

elif login_role == "Admin":
    admin_user = st.sidebar.text_input("Username")
    admin_pass = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login as Admin"):
        if admin_user == "demo" and admin_pass == "demo":
            st.session_state.admin_logged_in = True
            st.success("Admin logged in")
        else:
            st.error("Invalid admin credentials")

# Student view
if st.session_state.current_user:
    user_id = st.session_state.current_user
    user_data = st.session_state.users[user_id]
    st.title(f"🧑‍🎓 SRG Weekly Availability for {user_data['name']}")

    for hour in HOURS:
        cols = st.columns(len(DAYS))
        for i, day in enumerate(DAYS):
            key = f"{user_id}_{day}_{hour}"
            status = user_data["shifts"].get((day, hour), "")
            if status == "Confirmed":
                cols[i].success("✔️ Confirmed")
            elif status == "Available":
                if cols[i].button("🟨 Pending", key=key):
                    del user_data["shifts"][(day, hour)]
                else:
                    cols[i].info("⏳ Available")
            else:
                if cols[i].button(f"{day} {hour}:00", key=key):
                    user_data["shifts"][(day, hour)] = "Available"

# Admin view
elif st.session_state.admin_logged_in:
    st.title("🧑‍🏫 Admin Panel - Confirm Shifts")

    for sid, data in st.session_state.users.items():
        st.subheader(f"{data['name']} (ID: {sid})")
        for hour in HOURS:
            cols = st.columns(len(DAYS))
            for i, day in enumerate(DAYS):
                key = f"admin_{sid}_{day}_{hour}"
                status = data["shifts"].get((day, hour), "")
                if status == "Available":
                    if cols[i].button("Confirm", key=key):
                        data["shifts"][(day, hour)] = "Confirmed"
                elif status == "Confirmed":
                    cols[i].success("✔️")
                else:
                    cols[i].write("—")

    # Weekly summary
    st.subheader("📊 Weekly Hours Summary")
    summary_data = []
    for sid, data in st.session_state.users.items():
        total_hours = sum(1 for v in data["shifts"].values() if v == "Confirmed")
        summary_data.append({"Student ID": sid, "Name": data["name"], "Confirmed Hours": total_hours})
    df_summary = pd.DataFrame(summary_data)
    st.table(df_summary)
