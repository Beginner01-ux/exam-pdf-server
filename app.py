import streamlit as st
import pandas as pd
import requests
import re

# ===== CONFIGURATION =====
SHEET_ID = "1ttb4YRnZeQVLihZUC1B3J6VDzqbPcuMKcbQIsxLduco"

# ===== HELPER FUNCTIONS =====
def convert_drive_url_to_direct_download(url):
    """
    Converts standard Google Drive share/view URLs into direct download URLs.
    Example:
    From: https://drive.google.com/file/d/1A2B3C.../view?usp=sharing
    To:   https://drive.google.com/uc?export=download&id=1A2B3C...
    """
    if not isinstance(url, str):
        return ""
    
    file_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if file_id_match:
        file_id = file_id_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    return url.strip()

# ===== PAGE SETUP =====
st.set_page_config(page_title="Exam PDF Access", layout="centered")
st.title("Student Database Portal")
st.caption("by: MANISH LOHANA")
st.write("Enter your serial number to download your exam paper.")

# ===== LOAD DATA FROM GOOGLE SHEET =====
@st.cache_data
def load_sheet_data():
    try:
        # Google Visualization API endpoint for reliable CSV extraction
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None

# ===== MAIN APP =====
df = load_sheet_data()

if df is not None:
    serial_input = st.text_input("Enter your Serial Number:", placeholder="e.g., MGM75000001")
    
    if serial_input:
        cleaned_input = serial_input.strip()
        
        # Verify column names exist in the sheet
        if 'serial_number' in df.columns and 'pdf_url' in df.columns:
            # Match serial numbers while stripping whitespace on both sides
            result = df[df['serial_number'].astype(str).str.strip() == cleaned_input]
            
            if len(result) > 0:
                raw_pdf_url = result.iloc[0]['pdf_url']
                download_url = convert_drive_url_to_direct_download(raw_pdf_url)
                
                st.success("✓ Serial number found!")
                
                try:
                    with st.spinner("Preparing your document download..."):
                        response = requests.get(download_url, timeout=10)
                        
                    if response.status_code == 200:
                        st.download_button(
                            label=" Download Your Exam Paper",
                            data=response.content,
                            file_name=f"exam_{cleaned_input}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Failed to fetch PDF. Ensure the PDF file in Google Drive has General Access set to 'Anyone with the link'.")
                except Exception as e:
                    st.error(f"Error connecting to PDF source: {e}")
            else:
                st.error("❌ Serial number not found. Please check and try again.")
        else:
            st.error("❌ Database column mismatch. Make sure Row 1 of your Google Sheet has 'serial_number' and 'pdf_url'.")
else:
    st.error("Unable to connect to database. Please check configuration.")

