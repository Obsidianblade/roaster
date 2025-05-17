
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="SRG Roster Manager", layout="centered")

st.title("📋 SRG Roster Management System")

# Initialize session state for roster
if "roster" not in st.session_state:
    st.session_state.roster = pd.DataFrame(columns=["Date", "Name", "Availability", "Status"])

# Student Input Form
st.header("🧑‍🎓 Student Availability Submission")
with st.form("availability_form"):
    name = st.text_input("Your Name")
    shift_date = st.date_input("Shift Date", value=date.today())
    availability = st.selectbox("Availability", ["Yes", "No"])
    submitted = st.form_submit_button("Submit")

    if submitted:
        if name:
            st.session_state.roster.loc[len(st.session_state.roster)] = [shift_date, name, availability, ""]
            st.success("✅ Availability submitted successfully!")
        else:
            st.warning("⚠️ Please enter your name.")

# Admin Section for Shift Confirmation
st.header("🧑‍💼 Admin Shift Confirmation")
if not st.session_state.roster.empty:
    for i, row in st.session_state.roster.iterrows():
        col1, col2 = st.columns([2, 3])
        with col1:
            st.write(f"{row['Date']} - {row['Name']} (Available: {row['Availability']})")
        with col2:
            status = st.selectbox("Status", ["", "Confirmed", "Not Avail"], key=f"status_{i}")
            st.session_state.roster.at[i, "Status"] = status

# Display Final Roster
st.header("📆 Final Roster Overview")
if not st.session_state.roster.empty:
    def highlight_status(val):
        if val == "Confirmed":
            return "background-color: lightgreen"
        elif val == "Not Avail":
            return "background-color: lightcoral"
        elif val == "Yes":
            return "background-color: lightyellow"
        return ""

    st.dataframe(st.session_state.roster.style.applymap(highlight_status, subset=["Availability", "Status"]))

# Summary Report
st.header("📊 Summary: Confirmed Hours per Student")
confirmed = st.session_state.roster[st.session_state.roster["Status"] == "Confirmed"]
if not confirmed.empty:
    summary = confirmed.groupby("Name").size().reset_index(name="Confirmed Shifts")
    summary["Estimated Hours"] = summary["Confirmed Shifts"] * 2  # assuming 2 hours per shift
    st.table(summary)
else:
    st.info("No confirmed shifts yet.")
