import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Med-Alert Dashboard", layout="wide")

# --- 1. EMAIL CONFIGURATION ---
# Change these to your real details if you want real emails!
SIMULATION_MODE = True 
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"

# --- 2. DATABASE LOGIC ---
if 'med_data' not in st.session_state:
    st.session_state.med_data = pd.DataFrame({
        "Patient": ["Sarah Jenkins", "Baby Leo"],
        "Medicine": ["Insulin", "Polio Vaccine"],
        "Time": ["09:00", "14:30"],
        "Status": ["Taken", "Pending"]
    })

# --- 3. THE REMINDER FUNCTION ---
def send_alert(row):
    subject = f"🔔 MED-ALERT: {row['Medicine']} Due!"
    body = f"Hello, it is time for the {row['Medicine']} for {row['Patient']}."
    
    if SIMULATION_MODE:
        st.toast(f"SIMULATION: Email sent for {row['Medicine']}!") # Popup in browser
        print(f"DEBUG: Alert sent for {row['Medicine']}")
    else:
        # Standard Email Code
        msg = MIMEText(body)
        msg['Subject'] = subject
        # ... (Email sending logic here)

# --- 4. HEADER & SIDEBAR ---
st.title("🏥 Med-Alert: Smart Tracker")

with st.sidebar:
    st.header("Add New Entry")
    p_name = st.sidebar.text_input("Patient Name")
    m_name = st.sidebar.text_input("Medication Name")
    r_time = st.sidebar.time_input("Reminder Time", datetime.now())
    
    if st.sidebar.button("Add to Schedule"):
        new_entry = pd.DataFrame({"Patient": [p_name], "Medicine": [m_name], 
                                  "Time": [r_time.strftime("%H:%M")], "Status": ["Pending"]})
        st.session_state.med_data = pd.concat([st.session_state.med_data, new_entry], ignore_index=True)

# --- 5. THE "SMART" CHECKER ---
st.write("### Today's Schedule")

# This checks if the current time matches any scheduled time
current_time = datetime.now().strftime("%H:%M")

for index, row in st.session_state.med_data.iterrows():
    if row['Time'] == current_time and row['Status'] == "Pending":
        send_alert(row)
        # Update status so it doesn't send 100 emails in the same minute
        st.session_state.med_data.at[index, 'Status'] = "Alert Sent"

# Display Table
st.table(st.session_state.med_data)

if st.button("Check for Reminders Now"):
    st.rerun()