import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import io

st.set_page_config(page_title="SRG Roster Manager", layout="wide")
st.sidebar.title("📋 SRG Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Student Portal", "Admin Portal"])

# Global state
if "users" not in st.session_state:
    st.session_state.users = {}  # {id: {"name": ..., "password": ..., "shifts": []}}
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Home Page
if page == "Home":
    st.title("🏫 SRG Roster Management System")
    st.markdown("Welcome! Please choose **Student Portal** or **Admin Portal** from the left sidebar.")

# Student Portal
elif page == "Student Portal":
    st.title("🧑‍🎓 Student Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab2:
        new_id = st.text_input("New Student ID")
        new_name = st.text_input("Full Name")
        new_pass = st.text_input("Password", type="password")
        if st.button("Register"):
            if new_id and new_name and new_pass:
                if new_id not in st.session_state.users:
                    st.session_state.users[new_id] = {
                        "name": new_name, "password": new_pass, "shifts": []
                    }
                    st.success("✅ Registered! You can now log in.")
                else:
                    st.warning("⚠️ ID already exists.")

    with tab1:
        login_id = st.text_input("Student ID")
        login_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            user = st.session_state.users.get(login_id)
            if user and user["password"] == login_pass:
                st.session_state.current_user = login_id
                st.success(f"✅ Logged in as {user['name']}")
            else:
                st.error("❌ Invalid ID or password")

    if st.session_state.current_user:
        user_data = st.session_state.users[st.session_state.current_user]
        st.subheader(f"📅 Weekly Availability for {user_data['name']}")
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        shifts = []

        for i in range(7):
            day = week_start + timedelta(days=i)
            st.markdown(f"**{day.strftime('%A (%d %b)')}**")
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input(f"Start - {day.strftime('%A')}", value=time(9, 0), key=f"start_{i}")
            with col2:
                end_time = st.time_input(f"End - {day.strftime('%A')}", value=time(17, 0), key=f"end_{i}")
            if start_time < end_time:
                shifts.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "day": day.strftime("%A"),
                    "start": str(start_time),
                    "end": str(end_time),
                    "status": "Pending"
                })

        if st.button("Submit Weekly Shifts"):
            user_data["shifts"] = shifts
            st.success("✅ Shifts submitted!")

        if user_data["shifts"]:
            st.subheader("📌 Your Submitted Shifts")
            st.table(pd.DataFrame(user_data["shifts"]))

# Admin Portal
elif page == "Admin Portal":
    st.title("🧑‍💼 Admin Login")
    if not st.session_state.admin_logged_in:
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login as Admin"):
            if admin_user == "demo" and admin_pass == "demo":
                st.session_state.admin_logged_in = True
                st.success("✅ Logged in as Admin")
            else:
                st.error("❌ Invalid credentials")

    if st.session_state.admin_logged_in:
        st.subheader("📅 Weekly Calendar View")
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        calendar = { (week_start + timedelta(days=i)).strftime('%Y-%m-%d'): [] for i in range(7) }

        for sid, data in st.session_state.users.items():
            for shift in data["shifts"]:
                if shift["status"] == "Confirmed":
                    calendar[shift["date"]].append(f"{data['name']} ({shift['start']}–{shift['end']})")

        for date_str, shifts in calendar.items():
            st.markdown(f"### {datetime.strptime(date_str, '%Y-%m-%d').strftime('%A, %d %B')}")
            if shifts:
                for shift in shifts:
                    st.markdown(f"- {shift}")
            else:
                st.info("No confirmed shifts")

        st.subheader("✅ Confirm Shifts Per Student")
        for sid, data in st.session_state.users.items():
            if data["shifts"]:
                st.markdown(f"#### {data['name']} (ID: {sid})")
                df = pd.DataFrame(data["shifts"])
                for i in range(len(df)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{df.loc[i, 'day']} ({df.loc[i, 'date']}):** {df.loc[i, 'start']}–{df.loc[i, 'end']}")
                    with col2:
                        new_status = st.selectbox(
                            "Status", ["Pending", "Confirmed", "Declined"],
                            index=["Pending", "Confirmed", "Declined"].index(df.loc[i, "status"]),
                            key=f"{sid}_{i}"
                        )
                        df.at[i, "status"] = new_status
                st.session_state.users[sid]["shifts"] = df.to_dict(orient="records")

        st.subheader("📊 Weekly Summary Report")
        report_data = []
        for sid, data in st.session_state.users.items():
            total_hours = 0
            for shift in data["shifts"]:
                if shift["status"] == "Confirmed":
                    start = datetime.strptime(shift["start"], "%H:%M:%S")
                    end = datetime.strptime(shift["end"], "%H:%M:%S")
                    hours = (end - start).seconds / 3600
                    total_hours += hours
            report_data.append({"Student ID": sid, "Name": data["name"], "Confirmed Hours": total_hours})

        df_report = pd.DataFrame(report_data)
        st.dataframe(df_report)

        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            df_report.to_excel(writer, index=False, sheet_name="Weekly Summary")
        st.download_button("📥 Download Excel Report", data=towrite.getvalue(), file_name="weekly_summary.xlsx")
