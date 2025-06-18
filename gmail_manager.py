import streamlit as st
import pandas as pd
import re
from datetime import datetime
from streamlit_calendar import calendar

# --- PAGE CONFIG ---
st.set_page_config(page_title="Gmail Manager AI", page_icon="📩", layout="wide")

# --- CSS for styling ---
st.markdown("""
    <style>
        body {
            background-color: #1e1e2f;
            color: white;
        }
        .main {
            background-color: #1e1e2f;
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
        }
        .stButton>button:hover {
            background-color: #ff6b6b;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTENT ---
st.sidebar.title("📂 Gmail Manager AI")
st.sidebar.markdown("🔍 Analyze emails for deadlines, tags, and sender info!")

# --- EXPANDER FOR CALENDAR ---
with st.sidebar.expander("📅 View Calendar"):
    try:
        df = pd.read_csv("calendar.csv")
        df.drop_duplicates(inplace=True)
        if not df.empty:
            def convert_to_date(date_str):
                try:
                    return datetime.strptime(date_str, "%B %d").date().replace(year=datetime.now().year)
                except:
                    return None

            events = []
            for _, row in df.iterrows():
                date_obj = convert_to_date(row['Date'])
                if date_obj:
                    events.append({
                        "title": row["Tags"],
                        "start": date_obj.strftime("%Y-%m-%d"),
                        "description": row["From"]
                    })

            calendar(events=events, options={
                "initialView": "dayGridMonth",
                "editable": False,
                "height": 300
            })
        else:
            st.info("📭 No calendar entries yet.")
    except FileNotFoundError:
        st.info("📭 No calendar entries yet.")

# --- UPCOMING DEADLINES ---
st.sidebar.markdown("### 📌 Upcoming Deadlines")
try:
    df = pd.read_csv("calendar.csv")
    if not df.empty:
        for _, row in df.iterrows():
            st.sidebar.markdown(
                f"**📌 {row['Date']}** — 🏷️ {row['Tags']}  \n📨 {row['From']}",
                unsafe_allow_html=True
            )
    else:
        st.sidebar.info("No entries yet.")
except FileNotFoundError:
    st.sidebar.info("No entries yet.")

# --- MAIN TITLE ---
st.markdown("<h1 style='text-align: center;'>📬 Gmail Manager AI</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #bbb;'>Your AI-powered email productivity booster</h4>", unsafe_allow_html=True)

# --- TEXT INPUT ---
email_input = st.text_area("Paste your email content below:", height=200)

# --- FUNCTIONS ---
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
    return match.group(1).strip() if match else "Unknown Sender"

# --- BUTTON ACTION ---
if st.button("🧠 Process Email"):
    if not email_input.strip():
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
            new_entry = {
                "Date": deadline,
                "Tags": ", ".join(tags),
                "From": sender
            }

            try:
                df = pd.read_csv("calendar.csv")
            except FileNotFoundError:
                df = pd.DataFrame(columns=new_entry.keys())

            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv("calendar.csv", index=False)
            st.success("📅 Saved to calendar.")
        else:
            st.info("📭 No deadline found.")
