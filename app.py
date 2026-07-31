import streamlit as st
import pandas as pd
import requests

# ===== CONFIGURATION =====
SHEET_URL = "https://docs.google.com/spreadsheets/d/1xrfzqniGY199m9g9Jf97hmDQUa_a54KexIiur2-frDU/edit"
SHEET_NAME = "exam_serial_numbers"

# ===== PAGE SETUP =====
st.set_page_config(page_title="Exam PDF Access", layout="centered")
st.title("Student Database Portal")
st.caption("by: MANISH LOHANA")
st.write("Enter your serial number to download your exam paper.")

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
        cleaned_input = serial_input.strip()
        
        # Clean both data column and input to prevent whitespace mismatched searches
        result = df[df['serial_number'].astype(str).str.strip() == cleaned_input]
        
        if len(result) > 0:
            pdf_url = result.iloc[0]['pdf_url']
            st.success("✓ Serial number found!")
            
            # Direct download button to avoid Streamlit nested button refresh bug
            try:
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    st.download_button(
                        label=" Download Your Exam Paper",
                        data=response.content,
                        file_name=f"exam_{cleaned_input}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Failed to fetch PDF from the provided URL. Please verify the file link in your sheet.")
            except Exception:
                st.error("Error connecting to PDF source. Please check the network connection.")
        else:
            st.error("❌ Serial number not found. Please check and try again.")
else:
    st.error("Unable to connect to database. Please contact administrator.")

