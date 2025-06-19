from streamlit.components.v1 import html
import streamlit as st
import pandas as pd
import re
from datetime import datetime
from streamlit_calendar import calendar

# --- PAGE CONFIG ---
st.set_page_config(page_title="Gmail Manager AI", page_icon="📩", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
        body { background-color: #1e1e2f; color: white; }
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

# --- SIDEBAR TITLE ---
st.sidebar.title("📂 Gmail Manager AI")
st.sidebar.markdown("🔍 Analyze emails for deadlines, tags, sender info, and priority!")

# --- CALENDAR EXPANDER ---
with st.sidebar.expander("📅 View Calendar", expanded=True):
    try:
        df = pd.read_csv("calendar.csv")
        df.drop_duplicates(inplace=True)

        if not df.empty:
            def convert_to_date(date_str):
                try:
                    if re.search(r'\d{4}', date_str):
                        return datetime.strptime(date_str, "%B %d, %Y").date()
                    else:
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
                        "description": f"{row['From']} | {row.get('Priority', '')}"
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

# --- DEADLINE LIST BELOW CALENDAR ---
st.sidebar.markdown("### 📌 Upcoming Deadlines")
try:
    df = pd.read_csv("calendar.csv")
    if not df.empty:
        for _, row in df.iterrows():
            st.sidebar.markdown(
                f"**📌 {row['Date']}** — 🏷️ {row['Tags']}  \n📨 {row['From']} — {row.get('Priority', '')}",
                unsafe_allow_html=True
            )
    else:
        st.sidebar.info("No entries yet.")
except FileNotFoundError:
    st.sidebar.info("No entries yet.")

# --- MAIN PANEL ---
st.markdown("<h1 style='text-align: center;'>📬 Gmail Manager AI</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #bbb;'>Your AI-powered email productivity booster</h4>", unsafe_allow_html=True)

# --- Email Input ---
email_input = st.text_area("Paste your email content below:", height=200)

# --- Helper Functions ---
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

def score_priority(text):
    score = 0
    text_lower = text.lower()
    if any(word in text_lower for word in ["urgent", "asap", "immediately", "important"]): score += 50
    if any(word in text_lower for word in ["submit", "deadline", "due"]): score += 30
    if "attached" in text_lower or "attachment" in text_lower: score += 10
    if any(name in text_lower for name in ["sir", "ma'am", "professor"]): score += 10
    return min(score, 100)

def generate_reply(text):
    if "submit" in text.lower():
        return "Thank you! I will submit it by the deadline."
    elif "meeting" in text.lower():
        return "Noted. I’ll be there."
    else:
        return "Got it. Thank you!"

def summarize(text):
    return text.strip()[:100] + "..." if len(text.strip()) > 100 else text.strip()

# --- Process Email ---
if st.button("🧠 Process Email"):
    if not email_input.strip():
        st.warning("⚠️ Please paste an email first.")
    else:
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        sender = extract_sender(email_input)
        priority_score = score_priority(email_input)
        auto_reply = generate_reply(email_input)
        summary = summarize(email_input)

        badge = "🔴 High" if priority_score >= 70 else "🟡 Medium" if priority_score >= 40 else "🟢 Low"

        st.markdown("### ✅ Analysis Result")
        st.markdown(f"**🕓 Deadline:** `{deadline}`")
        st.markdown(f"**🏷️ Tags:** `{', '.join(tags)}`")
        st.markdown(f"**📨 From:** {sender}")
        st.markdown(f"**📊 Priority Score:** `{priority_score}` → {badge}")
        st.markdown(f"**💬 Suggested Auto-Reply:** _{auto_reply}_")
        st.markdown(f"**📝 Summary:** {summary}")

        if deadline != "No deadline found":
            new_entry = {
                "Date": deadline,
                "Tags": ", ".join(tags),
                "From": sender,
                "Priority": badge
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
