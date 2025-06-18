import streamlit as st
import pandas as pd
import re
from datetime import datetime
from streamlit_calendar import calendar

# --- PAGE CONFIG ---
st.set_page_config(page_title="Gmail Manager AI", page_icon="📩", layout="wide")

# --- Stylish CSS ---
st.markdown("""
    <style>
        body {
            background-color: #1e1e2f;
            color: white;
        }
        .main {
            background-color: #1e1e2f;
        }
        .block-container {
            padding: 2rem;
        }
        h1 {
            background: linear-gradient(to right, #00c6ff, #0072ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stTextArea > div > textarea {
            background-color: #2e2e3e;
            color: #fff;
        }
        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #ff6b6b;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("📂 Gmail Manager AI")
st.sidebar.markdown("🔍 Analyze emails for deadlines, tags, and sender info!")

# --- HELPER FUNCTIONS ---
def extract_date(text):
    patterns = [
        r'\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December))\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s*\d{4})?\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return "No deadline found"

def tag_email(text):
    tags = []
    if "project" in text.lower(): tags.append("Project")
    if "submit" in text.lower(): tags.append("Submission")
    if "meeting" in text.lower(): tags.append("Meeting")
    if "reminder" in text.lower(): tags.append("Reminder")
    return tags or ["General"]

def extract_sender(text):
    match = re.search(r"From:\s*(.*?)(<.*?>)?\\n", text)
    if match:
        return match.group(1).strip()
    return "Unknown Sender"

def convert_to_date(date_str):
    try:
        return datetime.strptime(date_str, "%B %d").date().replace(year=datetime.now().year)
    except:
        return None

# --- MAIN PANEL ---
st.markdown("<h1 style='text-align: center;'>📨 Gmail Manager AI</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #bbb;'>Your AI-powered email productivity booster</h4>", unsafe_allow_html=True)
email_input = st.text_area("Paste your email content below:", height=200)

# --- PROCESS BUTTON ---
if st.button("🧠 Process Email"):
    if email_input.strip() == "":
        st.warning("⚠️ Please paste an email first.")
    else:
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        sender = extract_sender(email_input)

        st.markdown("### ✅ Analysis Result")
        st.markdown(f"**🕓 Deadline:** `{deadline}`")
        st.markdown(f"**🏷️ Tags:** `{', '.join(tags)}`")
        st.markdown(f"**📨 From:** {sender}")

        if deadline != "No deadline found":
            entry = {
                "Date": deadline,
                "Tags": ", ".join(tags),
                "From": sender
            }
            try:
                df = pd.read_csv("calendar.csv")
            except FileNotFoundError:
                df = pd.DataFrame(columns=entry.keys())

            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
            df.to_csv("calendar.csv", index=False)
            st.success("📅 Saved to calendar.")
        else:
            st.info("📭 No deadline found, so it was not added to the calendar.")

# --- DEADLINE VISUAL CALENDAR ---
st.sidebar.markdown("### 🗓️ Visual Calendar")
try:
    df = pd.read_csv("calendar.csv")
    if not df.empty:
        df.drop_duplicates(inplace=True)
        deadline_dates = [convert_to_date(date_str) for date_str in df["Date"] if convert_to_date(date_str)]

        event_list = [
            {
                "title": row["Tags"],
                "start": convert_to_date(row["Date"]).strftime("%Y-%m-%d") if convert_to_date(row["Date"]) else None,
                "description": row["From"]
            }
            for _, row in df.iterrows() if convert_to_date(row["Date"])
        ]

        calendar_options = {
            "editable": False,
            "height": 300,
            "initialView": "dayGridMonth"
        }

        calendar(events=event_list, options=calendar_options)

        st.sidebar.markdown("### 📌 Upcoming Deadlines")
        for _, row in df.iterrows():
            st.sidebar.markdown(f"**{row['Date']}** — 🏷️ {row['Tags']}<br>📨 {row['From']}", unsafe_allow_html=True)
    else:
        st.sidebar.info("📭 No calendar entries yet.")
except FileNotFoundError:
    st.sidebar.info("📭 No calendar entries yet.")
