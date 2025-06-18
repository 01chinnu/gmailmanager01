import streamlit as st
import pandas as pd
import re

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Gmail Manager AI",
    page_icon="📩",
    layout="wide"
)

# --- CSS Styling ---
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
            padding: 20px;
            border-radius: 10px;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("📂 Gmail Manager AI")
st.sidebar.markdown("🔍 Analyze emails for deadlines, tags, and generate replies!")
st.sidebar.success("📅 Deadlines are auto-saved in your calendar 📥")

# --- Title & Subtitle ---
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

def tag_email(text):
    tags = []
    if "project" in text.lower(): tags.append("Project")
    if "submit" in text.lower(): tags.append("Deadline")
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

# --- Text Area for Email Input ---
email_input = st.text_area(
    "📥 Paste your email content here:",
    placeholder="Hi Lahiri, please submit your AI project by June 21st at 5 PM...",
    height=200
)

# --- Button to Process ---
if st.button("🧠 Process Email"):
    if email_input.strip() == "":
        st.warning("⚠️ Please paste an email first.")
    else:
        # Process email
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        reply = generate_reply(email_input)

        st.markdown("### ✅ Analysis Result")
        st.markdown(f"**🕓 Deadline:** `{deadline}`")
        st.markdown(f"**🏷️ Tags:** `{', '.join(tags)}`")
        st.markdown(f"**💬 Auto-Reply:** _{reply}_")

        # Save only if deadline exists
        if deadline != "No deadline found":
            calendar_entry = {
                "Date/Deadline": deadline,
                "Tags": ", ".join(tags),
                "Auto-Reply": reply,
                "Summary": email_input[:80] + "..."
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

# --- View Calendar Section ---
st.markdown("---")
with st.expander("📅 View Saved Calendar"):
    try:
        df = pd.read_csv("calendar.csv")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 No calendar entries yet.")
    except FileNotFoundError:
        st.info("📭 No calendar entries yet.")

# --- Footer ---
st.markdown("---")

