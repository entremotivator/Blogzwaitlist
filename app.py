# app.py
import streamlit as st
import requests
import json
import re
from datetime import datetime

st.set_page_config(page_title="Blogz.life Waitlist (n8n)", layout="wide")

st.sidebar.title("Blogz.life — Fast-Track Waitlist")
st.sidebar.write("Fill the form below and send the data to your n8n webhook.")

# n8n webhook URL input (required to send)
WEBHOOK_URL = st.sidebar.text_input(
    "n8n Webhook URL",
    placeholder="https://<your-n8n-instance>/webhook/<your-path>",
    help="Enter your n8n webhook URL here. Example: https://n8n.example.com/webhook/waitlist"
)

# Optional: toggle auto-send preview
AUTO_SEND = st.sidebar.checkbox("Auto-send on submit", value=True)
st.sidebar.markdown("---")
st.sidebar.write("Tip: Put this app behind auth or only use secure webhooks for production.")

# --- Form (entirely in sidebar) ---
with st.sidebar.form("waitlist_form", clear_on_submit=False):
    st.markdown("### Applicant details")
    full_name = st.text_input("Full name", "")
    email = st.text_input("Email address", "")
    store_yes = st.radio("Do you currently have an online store?", ("Yes", "No"))
    store_name = st.text_input("If yes — store name or website link", "")

    st.markdown("### Product & offerings")
    price_range = st.selectbox(
        "Average price range of products/services",
        ("Under $50", "$50–$200", "$200–$500", "$500+")
    )
    sells_courses = st.selectbox("Do you sell online courses or digital products?", ("Yes", "No", "Planning to soon"))

    st.markdown("### Blogging")
    writes_blogs = st.radio("Do you currently write or publish blogs?", ("Yes", "No"))
    publish_platform = st.text_input("What platform do you publish on? (e.g., WordPress, Substack)", "")

    st.markdown("### Goals / extras")
    goals = st.text_area("What are your main goals for joining Blogz.life?", placeholder="Grow audience, monetize writing, connect with creators...")
    extras = st.text_area("Anything else we should know to help move you up the list? (optional)")

    submit_btn = st.form_submit_button("Preview / Submit")

# Helper: simple email validation
def valid_email(e: str) -> bool:
    if not e:
        return False
    # simple RFC-like check (not exhaustive)
    return re.match(r"[^@]+@[^@]+\.[^@]+", e) is not None

# Build payload if user hit submit
if submit_btn:
    # validation
    errors = []
    if not full_name.strip():
        errors.append("Full name is required.")
    if not valid_email(email):
        errors.append("Please enter a valid email address.")
    if store_yes == "Yes" and not store_name.strip():
        errors.append("Please provide your store name or URL (you answered 'Yes' for having a store).")

    if errors:
        for err in errors:
            st.error(err)
        st.stop()

    payload = {
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "full_name": full_name.strip(),
        "email": email.strip(),
        "has_store": store_yes == "Yes",
        "store_name_or_url": store_name.strip() or None,
        "price_range": price_range,
        "sells_courses": sells_courses,
        "writes_blogs": writes_blogs == "Yes",
        "publish_platform": publish_platform.strip() or None,
        "goals": goals.strip() or None,
        "extras": extras.strip() or None,
        # meta (useful for n8n)
        "source": "Blogz.life waitlist sidebar form",
        "app_version": "v1"
    }

    st.markdown("### Payload preview")
    st.json(payload)

    # Send to n8n if webhook present
    if not WEBHOOK_URL:
        st.warning("No n8n webhook URL provided in the sidebar. Paste your webhook URL to enable sending.")
    else:
        if AUTO_SEND:
            try:
                headers = {"Content-Type": "application/json"}
                resp = requests.post(WEBHOOK_URL, headers=headers, json=payload, timeout=10)
                if resp.ok:
                    st.success("Successfully sent the waitlist data to n8n.")
                    st.write("n8n response status:", resp.status_code)
                    # If response contains JSON, show small excerpt
                    try:
                        data = resp.json()
                        st.write("n8n response (JSON):")
                        st.json(data)
                    except Exception:
                        st.write("n8n response text:")
                        st.text(resp.text[:1000])
                else:
                    st.error(f"Failed to send to n8n — status {resp.status_code}")
                    st.write("Response text:")
                    st.text(resp.text[:1000])
            except Exception as e:
                st.error(f"Error when sending to n8n: {e}")
                st.stop()
        else:
            if st.button("Send to n8n now"):
                try:
                    headers = {"Content-Type": "application/json"}
                    resp = requests.post(WEBHOOK_URL, headers=headers, json=payload, timeout=10)
                    if resp.ok:
                        st.success("Successfully sent the waitlist data to n8n.")
                    else:
                        st.error(f"Failed to send to n8n — status {resp.status_code}")
                        st.write(resp.text[:1000])
                except Exception as e:
                    st.error(f"Error when sending to n8n: {e}")

# Minimal UI in main area
st.header("Blogz.life — Fast-Track Waitlist")
st.write("Use the sidebar to complete your application. Data will be sent to the n8n webhook you specify.")
st.info("All fields are optional except name and email; you can preview the JSON payload before sending.")
