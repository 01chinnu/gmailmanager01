import streamlit as st
import pandas as pd
import re
from datetime import datetime
# main.py

def summarize_email(email):
    subject = email.get("subject", "").strip()
    body = email.get("body", "").strip()
    full_text = (subject + " " + body).lower()

    # Custom logic-based summarization
    if "internship" in full_text or "collaboration" in full_text:
        summary = (
            "The sender is expressing interest in collaborating or applying for an internship. "
            "They are likely offering their skills or requesting an opportunity to contribute."
        )
    elif "submit" in full_text or "submission" in full_text:
        summary = (
            "The sender is requesting the submission of a document or report by a specific deadline."
        )
    elif "meeting" in full_text:
        summary = (
            "The sender is either scheduling, confirming, or discussing a meeting."
        )
    elif "update" in full_text or "status" in full_text:
        summary = (
            "The sender is asking for a progress update or report."
        )
    elif "issue" in full_text or "problem" in full_text:
        summary = (
            "The sender is asking if any problems were encountered or offering help in case of issues."
        )
    else:
        summary = (
            "The sender is communicating a general message, likely requiring acknowledgement or follow-up."
        )

    # Extract deadline if mentioned
    deadline_match = re.search(r'\bby (\w+day|\d{1,2}\w{2}|\d{1,2}/\d{1,2})\b', full_text, re.IGNORECASE)
    deadline = deadline_match.group(1) if deadline_match else "No deadline found"

    # Tags based on content
    tags = []
    for keyword, tag in {
        "project": "Project",
        "report": "Report",
        "meeting": "Meeting",
        "collaboration": "Collaboration",
        "internship": "Internship",
        "submission": "Submission",
        "problem": "Issue",
    }.items():
        if keyword in full_text:
            tags.append(tag)

    # Suggested reply
    if "let me know" in full_text or "please respond" in full_text:
        reply = "Acknowledge the message and respond with the requested info or confirmation."
    elif "submit" in full_text:
        reply = "Confirm the submission and deadline."
    elif "interested" in full_text or "collaboration" in full_text:
        reply = "Respond positively and request further details like resume or proposal."
    else:
        reply = "Got it. Thank you!"

    return {
        "📋 Summary": summary,
        "📅 Deadline": deadline,
        "🏷️ Tags": tags if tags else ["General"],
        "💬 Suggested Reply": reply
    }

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
