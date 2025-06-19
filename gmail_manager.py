import streamlit as st
import pandas as pd
import re
from datetime import datetime

# -- Helper Functions --
def extract_date(text):
    # Simple date pattern (e.g., June 21, 2025 or 21 June)
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

# -- Streamlit UI --
st.title("📩 Gmail Manager AI")

st.markdown("This AI assistant reads your emails and pulls out deadlines, tags, replies, and saves to calendar.")

email_input = st.text_area("📬 Paste your email here:", height=200)

if st.button("🧠 Process Email"):
    if email_input.strip() == "":
        st.warning("Please paste an email first.")
    else:
        # Process
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        reply = generate_reply(email_input)

        # Save to calendar.csv
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

        # Display Results
        st.success("✅ Email analyzed and added to calendar.")
        st.write("**📅 Deadline:**", deadline)
        st.write("**🏷️ Tags:**", ", ".join(tags))
        st.write("**💬 Suggested Reply:**", reply)

        with st.expander("📁 View Calendar"):
            st.dataframe(df)
