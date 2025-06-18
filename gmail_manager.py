import streamlit as st
import pandas as pd
import re

# --- Page Configuration ---
st.set_page_config(page_title="Gmail Manager AI", page_icon="📩", layout="wide")

# --- Styling ---
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
st.sidebar.markdown("🔍 Analyze emails for deadlines, tags, and sender info!")
st.sidebar.success("📅 Deadlines are saved in your calendar table.")

# --- Title ---
st.title("📬 Gmail Manager AI")
st.subheader("Simplify your inbox — AI that organizes deadlines for you ✨")

# --- Tag Extraction (excluding 'Deadline') ---
def tag_email(text):
    tags = []
    if "project" in text.lower(): tags.append("Project")
    if "meeting" in text.lower(): tags.append("Meeting")
    if "reminder" in text.lower(): tags.append("Reminder")
    return tags or ["General"]

# --- Date Extraction ---
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

# --- Reply Generator ---
def generate_reply(text):
    if "submit" in text.lower():
        return "Thank you! I’ll submit it by the deadline."
    elif "meeting" in text.lower():
        return "Noted. I’ll be there."
    else:
        return "Got it. Thank you!"

# --- Sender Name Input ---
sender = st.text_input("📧 Who is the email from?", placeholder="e.g. Prof. Rao")

# --- Email Input ---
email_input = st.text_area("📥 Paste the email content below:", height=200)

# --- Process Email ---
if st.button("🧠 Process Email"):
    if not email_input.strip():
        st.warning("⚠️ Please paste the email first.")
    elif not sender.strip():
        st.warning("📧 Please enter the sender name.")
    else:
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        reply = generate_reply(email_input)

        st.markdown("### ✅ Analysis Result")
        st.markdown(f"**🕓 Deadline:** `{deadline}`")
        st.markdown(f"**🏷️ Tags:** `{', '.join(tags)}`")
        st.markdown(f"**💬 Auto-Reply:** _{reply}_")

        # Save only if deadline exists
        if deadline != "No deadline found":
            entry = {
                "Date/Deadline": deadline,
                "Tags": ", ".join(tags),
                "From": sender
            }

            try:
                df = pd.read_csv("calendar.csv")
            except FileNotFoundError:
                df = pd.DataFrame(columns=["Date/Deadline", "Tags", "From"])

            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
            df.to_csv("calendar.csv", index=False)
            st.success("📅 Saved to calendar.")
        else:
            st.info("📭 No deadline found, so it was not added to the calendar.")

# --- Calendar View ---
# --- Calendar View ---
st.markdown("---")
with st.expander("📅 View Saved Calendar"):
    try:
        df = pd.read_csv("calendar.csv")
        expected_cols = {"Date/Deadline", "Tags", "From"}

        if expected_cols.issubset(df.columns):
            df = df[["Date/Deadline", "Tags", "From"]]
            df = df.sort_values("Date/Deadline")
            st.markdown("### 🗓️ Calendar Entries (sorted by date):")
            st.dataframe(df.style.set_properties(**{
                'background-color': '#fffdf7',
                'color': '#333',
                'border-color': '#ddd',
                'text-align': 'center'
            }), use_container_width=True)
        else:
            st.info("📭 Calendar is empty or has outdated format.")
    except FileNotFoundError:
        st.info("📭 No calendar entries found yet.")


# --- Footer ---
st.markdown("---")
st.caption("🚀 Made with ❤️ by Lahiri | Gmail Manager AI")



