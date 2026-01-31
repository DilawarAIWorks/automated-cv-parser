import streamlit as st
import requests

st.set_page_config(page_title="Job Application OCR", layout="wide")
st.title("📄 Job Application & CV Parser")

# --- USER INPUTS ---
col1, col2 = st.columns(2)

with col1:
    role = st.selectbox("Select Role", ["Python Developer", "Data Scientist", "Project Manager", "DevOps Engineer"])
    email = st.text_input("Email Address", placeholder="name@example.com")

message = st.text_area("Cover Letter / Message", height=150, placeholder="Write your application message here...")

uploaded_file = st.file_uploader("Upload CV (PDF / DOCX / Image)", type=["pdf", "docx", "png", "jpg", "jpeg"])

# --- PROCESS BUTTON ---
if st.button("Submit Application"):
    if not uploaded_file:
        st.warning("Please upload a CV file first.")
    elif not email:
        st.warning("Please enter your email address.")
    else:
        with st.spinner("Processing Application & Extracting Text..."):
            try:
                # 1. Prepare File
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                
                # 2. Prepare Form Data (Role, Email, Message)
                data = {
                    "role": role,
                    "email": email,
                    "user_message": message
                }
                
                # 3. Send Everything to Backend
                response = requests.post(
                    "http://127.0.0.1:8000/extract-text/",
                    files=files,
                    data=data  # Sending the text fields here
                )

                if response.status_code == 200:
                    st.success("Application Submitted & Sent to n8n!")
                    st.markdown("### Final Output Data:")
                    st.text_area("Result", response.text, height=600)
                else:
                    st.error(f"Backend Error ({response.status_code})")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("🚨 Connection Error: Is the backend (main.py) running?")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")