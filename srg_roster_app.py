
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="SRG Calendar View", layout="wide")

# Constants
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HOURS = list(range(9, 18))  # 9AM–5PM

# Initialize state
if "users" not in st.session_state:
    st.session_state.users = {}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Sidebar login
st.sidebar.title("SRG Login")
role = st.sidebar.radio("Login as", ["Student", "Admin"])

if role == "Student":
    sid = st.sidebar.text_input("Student ID")
    name = st.sidebar.text_input("Full Name")
    if st.sidebar.button("Login / Register"):
        if sid and name:
            st.session_state.current_user = sid
            if sid not in st.session_state.users:
                st.session_state.users[sid] = {"name": name, "grid": {}}
            st.success(f"Logged in as {name}")

elif role == "Admin":
    user = st.sidebar.text_input("Username")
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if user == "demo" and pwd == "demo":
            st.session_state.admin_logged_in = True
            st.success("Admin logged in")

# STUDENT VIEW
if st.session_state.current_user:
    sid = st.session_state.current_user
    student = st.session_state.users[sid]
    st.title(f"🧑‍🎓 Weekly Shift Calendar - {student['name']}")

    for hour in HOURS:
        cols = st.columns(len(DAYS))
        for i, day in enumerate(DAYS):
            key = (day, hour)
            cell_key = f"{sid}_{day}_{hour}"
            current_status = student["grid"].get(key, "None")

            if current_status == "Confirmed":
                cols[i].success("✔️ Confirmed")
            elif current_status == "Pending":
                if cols[i].button("🟨 Cancel", key=cell_key):
                    del student["grid"][key]
                else:
                    cols[i].info("⏳ Pending")
            else:
                if cols[i].button(f"{hour}:00", key=cell_key):
                    student["grid"][key] = "Pending"

# ADMIN VIEW
elif st.session_state.admin_logged_in:
    st.title("🧑‍🏫 Admin Calendar View")

    search = st.text_input("Search student by name")
    filtered = {sid: data for sid, data in st.session_state.users.items() if search.lower() in data["name"].lower()}

    for sid, data in filtered.items():
        st.subheader(f"{data['name']} (ID: {sid})")
        for hour in HOURS:
            cols = st.columns(len(DAYS))
            for i, day in enumerate(DAYS):
                key = (day, hour)
                cell_key = f"admin_{sid}_{day}_{hour}"
                current = data["grid"].get(key, "None")

                if current == "Pending":
                    if cols[i].button("✔️ Approve", key=cell_key):
                        data["grid"][key] = "Confirmed"
                elif current == "Confirmed":
                    cols[i].success("✔️ Confirmed")
                else:
                    cols[i].write("—")

    # Summary table
    st.subheader("📊 Weekly Confirmed Hours Summary")
    summary = []
    for sid, data in st.session_state.users.items():
        confirmed_hours = sum(1 for v in data["grid"].values() if v == "Confirmed")
        summary.append({
            "Student ID": sid,
            "Name": data["name"],
            "Confirmed Hours": confirmed_hours
        })

    st.table(pd.DataFrame(summary))
