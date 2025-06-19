import streamlit as st
import pandas as pd
import re
from datetime import datetime
# main.py

# 🔽 Add the summarize_email function here
def summarize_email(email):
    subject = email.get("subject", "")
    body = email.get("body", "")
    full_text = subject + " " + body

    # Basic summary logic
    summary = ""
    if "submit" in full_text.lower():
        summary = "The sender is requesting a submission."
    elif "meeting" in full_text.lower():
        summary = "The sender is informing or requesting about a meeting."
    elif "update" in full_text.lower():
        summary = "The sender is asking for a status update."
    else:
        summary = "General communication from the sender."

    # Extract deadline
    deadline_match = re.search(r'\bby (\w+day|\d{1,2}\w{2}|\d{1,2}/\d{1,2})\b', full_text, re.IGNORECASE)
    deadline = deadline_match.group(1) if deadline_match else "No deadline found"

    # Tags
    tags = []
    if "report" in full_text.lower():
        tags.append("Report")
    if "project" in full_text.lower():
        tags.append("Project")
    if "submission" in full_text.lower():
        tags.append("Submission")
    if "meeting" in full_text.lower():
        tags.append("Meeting")

    # Suggested reply
    if "submit" in full_text.lower():
        reply = "Acknowledge the request and confirm the submission date."
    elif "let me know" in full_text.lower():
        reply = "Confirm and respond if there are any issues."
    else:
        reply = "Got it. Thank you!"

    return {
        "📋 Summary": summary,
        "📅 Deadline": deadline,
        "🏷️ Tags": tags if tags else ["General"],
        "💬 Suggested Reply": reply
    }

# 🔽 Then, wherever you process or display emails:
if __name__ == "__main__":
    email = {
        "subject": "Submit Final Report",
        "body": "Hi team, please ensure that the final report is submitted by Friday. Let me know if you face any issues. Thanks!"
    }

    result = summarize_email(email)
    for key, value in result.items():
        print(f"{key}: {value}")


# -- Helper Functions --
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

# -- Streamlit UI --
st.title("📩 Gmail Manager AI")

st.markdown("This AI assistant reads your emails and pulls out deadlines, tags, and replies.")

email_input = st.text_area("📬 Paste your email here:", height=200)

if st.button("🧠 Process Email"):
    if email_input.strip() == "":
        st.warning("Please paste an email first.")
    else:
        # Process
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        reply = generate_reply(email_input)
        summary = email_input[:80] + "..."

        # Save to calendar.csv (without auto-reply and summary)
        calendar_entry = {
            "Date/Deadline": deadline,
            "Tags": ", ".join(tags)
        }

        try:
            df = pd.read_csv("calendar.csv")
        except FileNotFoundError:
            df = pd.DataFrame(columns=calendar_entry.keys())

        df = pd.concat([df, pd.DataFrame([calendar_entry])], ignore_index=True)
        df.to_csv("calendar.csv", index=False)

        # Display Results (Auto-reply and summary separately)
        st.success("✅ Email analyzed and added to calendar.")
        st.write("**📅 Deadline:**", deadline)
        st.write("**🏷️ Tags:**", ", ".join(tags))
        st.write("**💬 Suggested Reply:**", reply)
        st.write("**📝 Email Summary:**", summary)

        with st.expander("📁 View Calendar"):
            st.dataframe(df)
