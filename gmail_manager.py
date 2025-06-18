import streamlit as st
import pandas as pd
import re

# --- Page Config ---
st.set_page_config(page_title="Gmail Manager AI", page_icon="📩", layout="wide")

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
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\b',
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
    # Try common "From:" pattern
    match = re.search(r"from:\s*([^\n\r]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback if not found
    return "Unknown Sender"

# --- Email Input Area ---
email_input = st.text_area("📥 Paste your email content here:", height=200)

# --- Button ---
if st.button("🧠 Process Email"):
    if email_input.strip() == "":
        st.warning("⚠️ Please paste an email first.")
    else:
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        sender = extract_sender(email_input)

        # Display results
        st.markdown("### ✅ Analysis Result")
        st.markdown(f"**🕓 Deadline:** `{deadline}`")
        st.markdown(f"**🏷️ Tags:** `{', '.join(tags)}`")
        st.markdown(f"**📨 From:** _{sender}_")

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

# --- View Saved Calendar ---
st.markdown("---")
with st.expander("📅 View Saved Calendar"):
    try:
        df = pd.read_csv("calendar.csv")
        if not df.empty:
            st.dataframe(df[["Date/Deadline", "Tags", "From"]], use_container_width=True)
        else:
            st.info("📭 No calendar entries yet.")
    except FileNotFoundError:
        st.info("📭 No calendar entries yet.")
