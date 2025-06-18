import streamlit as st
import pandas as pd
import re
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="Gmail Manager AI", page_icon="📩", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("📂 Gmail Manager AI")
    st.markdown("🔍 Analyze emails for deadlines, tags, and sender info!")

    st.markdown("### 🗓️ Visual Calendar")
    try:
        df = pd.read_csv("calendar.csv")
        df = df[df["Date/Deadline"] != "No deadline found"]

        def convert_to_date(date_str):
            try:
                return datetime.strptime(date_str, "%B %d").date().replace(year=datetime.now().year)
            except:
                return None

        event_list = [
            {
                "title": row["Tags"],
                "start": convert_to_date(row["Date/Deadline"]).strftime("%Y-%m-%d") if convert_to_date(row["Date/Deadline"]) else None,
                "description": row["From"]
            }
            for _, row in df.iterrows() if convert_to_date(row["Date/Deadline"])
        ]

        calendar_options = {
            "editable": False,
            "height": 300,
            "initialView": "dayGridMonth"
        }

        calendar(events=event_list, options=calendar_options)

        st.markdown("### 📌 Upcoming Deadlines")
        for _, row in df.iterrows():
            st.markdown(f"**{row['Date/Deadline']}** — 🏷️ {row['Tags']}<br>📨 {row['From']}", unsafe_allow_html=True)

        if st.button("📅 Download Calendar (.ics)"):
            from ics import Calendar, Event
            cal = Calendar()
            for _, row in df.iterrows():
                e = Event()
                e.name = f"{row['Tags']} - {row['From']}"
                try:
                    date_obj = datetime.strptime(row["Date/Deadline"], "%B %d")
                    e.begin = f"{date_obj.strftime('%Y-%m-%d')}T09:00:00"
                except:
                    continue
                e.duration = {"hours": 1}
                cal.events.add(e)

            with open("gmail_calendar.ics", "w") as f:
                f.writelines(cal.serialize_iter())
            with open("gmail_calendar.ics", "rb") as f:
                st.download_button("📅 Click to Download .ics", f, file_name="gmail_calendar.ics")

    except FileNotFoundError:
        st.info("📅 No calendar entries yet.")

# --- Main Area ---
st.title("📨 Gmail Manager AI")
st.subheader("Your AI-powered email assistant")

def extract_date(text):
    patterns = [
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s*\d{4})?\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group().strip()
    return "No deadline found"

def tag_email(text):
    tags = []
    if "project" in text.lower(): tags.append("Project")
    if "submit" in text.lower(): tags.append("Submission")
    if "meeting" in text.lower(): tags.append("Meeting")
    if "reminder" in text.lower(): tags.append("Reminder")
    return tags or ["General"]

def extract_sender(text):
    match = re.search(r"from:\s*([^\n\r]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown Sender"

email_input = st.text_area("Paste your email content below:", height=200)

if st.button("🧠 Process Email"):
    if not email_input.strip():
        st.warning("⚠️ Please paste an email first.")
    else:
        deadline = extract_date(email_input)
        tags = tag_email(email_input)
        sender = extract_sender(email_input)

        st.markdown("### ✅ Analysis Result")
        st.markdown(f"**🕒 Deadline:** `{deadline}`")
        st.markdown(f"**🏷️ Tags:** `{', '.join(tags)}`")
        st.markdown(f"**📩 From:** _{sender}_")

        if deadline != "No deadline found":
            new_entry = {
                "Date/Deadline": deadline,
                "Tags": ", ".join(tags),
                "From": sender
            }
            try:
                df = pd.read_csv("calendar.csv")
            except FileNotFoundError:
                df = pd.DataFrame(columns=new_entry.keys())

            if not ((df["Date/Deadline"] == new_entry["Date/Deadline"]) &
                    (df["Tags"] == new_entry["Tags"]) &
                    (df["From"] == new_entry["From"])).any():
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                df.to_csv("calendar.csv", index=False)
                st.success("📅 Saved to calendar.")
            else:
                st.info("ℹ️ Already exists in calendar.")
        else:
            st.info("📅 No deadline found, so it was not added.")
