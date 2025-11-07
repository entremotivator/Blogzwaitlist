# app.py
import streamlit as st
import requests
import json
import re
from datetime import datetime

# --- Page setup ---
st.set_page_config(page_title="Blogz.life Waitlist", layout="centered")

# --- Hardcoded webhook URL ---
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook/8e3ca4db-9646-4bac-ac0c-3eee0c7a80a2"

# --- Page Header ---
st.title("🚀 Blogz.life Fast-Track Waitlist")
st.write(
    "Join the **Blogz.life** creator community! Fill out this short form so we can move you up the waitlist faster."
)

# --- Waitlist Form ---
with st.form("waitlist_form", clear_on_submit=False):
    st.subheader("Applicant Information")
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")

    st.subheader("Your Business")
    has_store = st.radio("Do you currently have an online store?", ("Yes", "No"))
    store_name = ""
    if has_store == "Yes":
        store_name = st.text_input("Store Name or Website Link")

    price_range = st.selectbox(
        "Average price range of your products or services:",
        ("Under $50", "$50–$200", "$200–$500", "$500+"),
    )

    sells_courses = st.selectbox(
        "Do you sell online courses or digital products?",
        ("Yes", "No", "Planning to soon"),
    )

    st.subheader("Blogging & Content")
    writes_blogs = st.radio("Do you currently write or publish blogs?", ("Yes", "No"))
    publish_platform = ""
    if writes_blogs == "Yes":
        publish_platform = st.text_input("What platform do you publish on? (e.g., WordPress, Substack, Medium)")

    st.subheader("Goals & Notes")
    goals = st.text_area(
        "What are your main goals for joining Blogz.life?",
        placeholder="Grow your audience, earn from writing, connect with creators..."
    )
    extras = st.text_area("Anything else we should know? (optional)")

    submit = st.form_submit_button("Submit Form")

# --- Email validation helper ---
def valid_email(e: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", e)) if e else False

# --- Handle form submission ---
if submit:
    errors = []
    if not full_name.strip():
        errors.append("Full name is required.")
    if not valid_email(email):
        errors.append("Please enter a valid email address.")
    if has_store == "Yes" and not store_name.strip():
        errors.append("Please enter your store name or website link.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Prepare JSON payload
    payload = {
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "full_name": full_name.strip(),
        "email": email.strip(),
        "has_store": has_store == "Yes",
        "store_name_or_url": store_name.strip() or None,
        "price_range": price_range,
        "sells_courses": sells_courses,
        "writes_blogs": writes_blogs == "Yes",
        "publish_platform": publish_platform.strip() or None,
        "goals": goals.strip() or None,
        "extras": extras.strip() or None,
        "source": "Blogz.life Waitlist Form",
    }

    st.markdown("### 📦 Data Preview")
    st.json(payload)

    # --- Send data to webhook ---
    try:
        headers = {"Content-Type": "application/json"}
        resp = requests.post(WEBHOOK_URL, headers=headers, json=payload, timeout=10)
        if resp.ok:
            st.success("✅ Form submitted successfully to n8n!")
            try:
                st.json(resp.json())
            except Exception:
                st.write("Response text:", resp.text[:500])
        else:
            st.error(f"❌ Failed to send data — status code {resp.status_code}")
            st.text(resp.text[:500])
    except Exception as e:
        st.error(f"Error sending to n8n: {e}")
