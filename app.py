import streamlit as st
import gspread
import pandas as pd
import requests

# ===== CONFIGURATION =====
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xrfzqniGYI99m9g9Jf97hmDQUa_a54Kexliur2-frDU/edit?usp=drivesdk"
SHEET_NAME = "exam_serial_numbers"

# ===== PAGE SETUP =====
st.set_page_config(page_title="Exam PDF Access", layout="centered")
st.title(" Exam Paper Access Portal")
st.write("Enter your serial number to download your exam paper")

# ===== LOAD DATA FROM GOOGLE SHEET =====
@st.cache_data
def load_sheet_data():
    try:
        url = SHEET_URL.replace('/edit', '/export?format=csv')
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# ===== MAIN APP =====
df = load_sheet_data()

if df is not None:
    serial_input = st.text_input("Enter your Serial Number:", placeholder="e.g., 2024001")
    
    if serial_input:
        result = df[df['serial_number'].astype(str) == serial_input.strip()]
        
        if len(result) > 0:
            pdf_url = result.iloc[0]['pdf_url']
            st.success(f"✓ Serial number found!")
            
            if st.button(" Download Your Exam Paper"):
                try:
                    response = requests.get(pdf_url)
                    st.download_button(
                        label="Click here to save PDF",
                        data=response.content,
                        file_name=f"exam_{serial_input}.pdf",
                        mime="application/pdf"
                    )
                except:
                    st.error("Error downloading PDF. Please try again.")
        else:
            st.error("❌ Serial number not found. Please check and try again.")
else:
    st.error("Unable to connect to database. Please contact administrator.")
