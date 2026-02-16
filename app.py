import streamlit as st
import pandas as pd
from datetime import datetime
import pytz  # <--- New library for timezones
import time
import smtplib
from email.message import EmailMessage

# --- SETUP TIMEZONE ---
# Replace 'Asia/Kolkata' with your city if you aren't in India
local_tz = pytz.timezone('Asia/Kolkata') 
current_time = datetime.now(local_tz).strftime("%I:%M %p")

# --- 1. PAGE CONFIG & MEMORY ---
st.set_page_config(page_title="Med-Alerts", page_icon="🏥", layout="wide")

if 'patient_records' not in st.session_state:
    st.session_state.patient_records = []
if 'is_loaded' not in st.session_state:
    st.session_state.is_loaded = False

# --- 2. NOTIFICATION ENGINE ---
def send_email(patient, med):
    msg = EmailMessage()
    msg.set_content(f"⏰ Med-Alert! It's time for {patient} to take {med}.")
    msg["Subject"] = "🚨 Medication Reminder"
    msg["From"] = st.secrets["my_email"]
    msg["To"] = st.secrets["receiver_email"]

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(st.secrets["my_email"], st.secrets["my_app_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- 3. SPLASH SCREEN ---
if not st.session_state.is_loaded:
    st.markdown("<h1 style='text-align: center;'>🏥 Med-Alerts</h1>", unsafe_allow_html=True)
    with st.spinner('Loading Dashboard...'):
        time.sleep(2)
    st.session_state.is_loaded = True
    st.rerun()

# --- 4. DASHBOARD & FORM ---
st.title("👨‍⚕️ Patient Dashboard")

with st.sidebar:
    st.header("Settings")
    if st.button("📧 Send Test Email"):
        if send_email("Test Patient", "Test Medicine"):
            st.success("Test email sent! Check your inbox.")
        else:
            st.error("Failed to send. Check your Secrets setup.")

with st.container(border=True):
    with st.form("med_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Patient Name")
            med = st.text_input("Medicine Name")
        with col2:
            file = st.file_uploader("Upload Prescription", type=['jpg', 'png', 'pdf'])
            med_time = st.time_input("Reminder Time")
        
        if st.form_submit_button("Register"):
            if name and file:
                new_entry = {"Name": name, "Med": med, "Time": med_time.strftime('%I:%M %p'), "Notified": False}
                st.session_state.patient_records.append(new_entry)
                st.success(f"Registered {name} for {med_time.strftime('%I:%M %p')}")
            else:
                st.error("Please fill all fields.")

# --- 5. THE AUTOMATED CHECKER ---
st.divider()
st.subheader("📋 Active Schedule")
current_time = datetime.now().strftime("%I:%M %p")
st.write(f"Current Time: **{current_time}**")

if st.session_state.patient_records:
    df = pd.DataFrame(st.session_state.patient_records)
    st.table(df[["Name", "Med", "Time"]])

    # CHECK IF IT'S TIME TO ALERT
    for record in st.session_state.patient_records:
        if record["Time"] == current_time and not record["Notified"]:
            if send_email(record["Name"], record["Med"]):
                st.toast(f"Alert sent for {record['Name']}!")
                record["Notified"] = True
