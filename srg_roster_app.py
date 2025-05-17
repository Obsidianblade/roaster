
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------
# Authentication
# -------------------------------
st.set_page_config(page_title="SRG Roster Calendar", layout="wide")
st.title("📅 SRG Weekly Roster Calendar")

# Dummy login
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if username != "demo" or password != "demo":
    st.warning("Enter demo/demo to login")
    st.stop()

user_type = st.radio("Login as:", ["Student", "Admin"])

# -------------------------------
# Initialize Roster Data
# -------------------------------
if "week_start" not in st.session_state:
    st.session_state.week_start = datetime.today() - timedelta(days=datetime.today().weekday())
if "roster_data" not in st.session_state:
    days = [st.session_state.week_start + timedelta(days=i) for i in range(7)]
    st.session_state.roster_data = pd.DataFrame(columns=["Name", "Date", "Hours", "Status"])

# -------------------------------
# Student View
# -------------------------------
if user_type == "Student":
    st.subheader("🧑‍🎓 Submit Your Weekly Availability")
    name = st.text_input("Your Name")
    for i in range(7):
        day = st.session_state.week_start + timedelta(days=i)
        hours = st.number_input(f"{day.strftime('%A (%d %b)')}", min_value=0, max_value=12, value=0, step=1, key=f"student_{i}")
        if hours > 0 and name:
            st.session_state.roster_data = st.session_state.roster_data.append({
                "Name": name,
                "Date": day.strftime('%Y-%m-%d'),
                "Hours": hours,
                "Status": "Pending"
            }, ignore_index=True)
    if st.button("Submit Weekly Availability"):
        st.success("✅ Availability Submitted")

# -------------------------------
# Admin View
# -------------------------------
if user_type == "Admin":
    st.subheader("🧑‍💼 Admin: Review & Confirm Shifts")
    df = st.session_state.roster_data
    if df.empty:
        st.info("No availability submitted yet.")
    else:
        for i, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.text(row["Name"])
            with col2:
                st.text(row["Date"])
            with col3:
                st.text(f"{int(row['Hours'])} hrs")
            with col4:
                new_status = st.selectbox("Status", ["Pending", "Confirmed", "Declined"], index=["Pending", "Confirmed", "Declined"].index(row["Status"]), key=f"status_{i}")
                st.session_state.roster_data.at[i, "Status"] = new_status

# -------------------------------
# Summary
# -------------------------------
st.subheader("📊 Summary Report")
if not st.session_state.roster_data.empty:
    summary = st.session_state.roster_data[st.session_state.roster_data["Status"] == "Confirmed"]
    if not summary.empty:
        report = summary.groupby("Name")["Hours"].sum().reset_index()
        report.columns = ["Name", "Total Confirmed Hours"]
        st.table(report)
    else:
        st.info("No confirmed shifts yet.")
