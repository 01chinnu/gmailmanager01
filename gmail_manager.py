import streamlit as st
import pandas as pd
import re

# --- Page Config ---
st.set_page_config(page_title="Gmail Manager AI", page_icon="📩", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
        .main {background-color: #f7f9fc; padding: 20px; border-radius: 10px;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("📂 Gmail Manager AI")
st.sidebar.markdown("🔍 Analyze emails for deadlines, tags, and sender info!")
st.sidebar.success("📅 Deadlines are saved in your calendar table.")

# --- Title ---
st.title("📬 Gmail Manager AI")
st.subheader("Your AI-powered email assistant ✨")

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

def extract_sender(text):
    match = re.search(r"From:\s*(.*?)(<.*?>)?", text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        email = match.group(2).strip() if match.group(2) else ""
        return f"{name} {email}".strip()
    return "Unknown Sender"

def tag_email(text):
    tags = []
    if "project" in text.lower(): tags.append("Project")
    if "meeting" in text.lower(): tags.append("Meeting")
    if "reminder" in text.lower(): tags.append("Reminder")
    return tags or ["General"]

def generate_reply(text):
    if "submit" in text.lower():
        return "Thank you! I’ll submit it by the deadline."
    elif "meeting" in text.lower():
        return "Noted. I’ll be there."
    else:
        return "Got it. Thank you!"

# --- Email Input ---
email_input = st.text_area("📥 Paste your email content here:", height=200)

# --- Process Button ---
if st.button("🧠 Process Email"):
    if email_input.strip() == "":
        st.warning("⚠️ Please paste an email first.")
    else:
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        reply = generate_reply(email_input)
        sender = extract_sender(email_input)

        st.markdown("### ✅ Analysis Result")
        st.markdown(f"**🕓 Deadline:** `{deadline}`")
        st.markdown(f"**🏷️ Tags:** `{', '.join(tags)}`")
        st.markdown(f"**💬 Auto-Reply:** _{reply}_")
        st.markdown(f"**📧 From:** `{sender}`")

        # Save if deadline exists
        if deadline != "No deadline found":
            calendar_entry = {
                "Date/Deadline": deadline,
                "Tags": ", ".join(tags),
                "From": sender
            }

            try:
                df = pd.read_csv("calendar.csv")
            except FileNotFoundError:
                df = pd.DataFrame(columns=calendar_entry.keys())

            df = pd.concat([df, pd.DataFrame([calendar_entry])], ignore_index=True)
            df.to_csv("calendar.csv", index=False)
            st.success("📅 Saved to calendar.")
        else:
            st.info("📭 No deadline found, so it was not added to the calendar.")

# --- View Calendar ---
st.markdown("---")
with st.expander("📅 View Saved Calendar"):
    try:
        df = pd.read_csv("calendar.csv")
        expected_cols = {"Date/Deadline", "Tags", "From"}
        if expected_cols.issubset(df.columns) and not df.empty:
            df = df[["Date/Deadline", "Tags", "From"]]
            df = df.sort_values("Date/Deadline")
            st.markdown("### 🗓️ Calendar Entries")
            st.dataframe(df.style.set_properties(**{
                'background-color': '#fffdf7',
                'color': '#333',
                'border-color': '#ddd',
                'text-align': 'center'
            }), use_container_width=True)
        else:
            st.info("📭 Calendar is empty or missing required fields.")
    except FileNotFoundError:
        st.info("📭 No calendar entries yet.")

# --- Footer ---
st.markdown("---")
