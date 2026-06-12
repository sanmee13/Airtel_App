import streamlit as st
import pandas as pd

# Set up the page title and layout
st.set_page_config(page_title="Customer Interest Finder", layout="centered")

st.title("📱 Mobile Number Interest Lookup")
st.write("Enter a mobile number below to see the top 10 rated interests associated with it.")

# --- BACKEND / ADMIN SIDEBAR ---
st.sidebar.header("⚙️ Backend Administration")
st.sidebar.write("Upload the daily updated Excel sheet here.")

# File uploader widget
uploaded_file = st.sidebar.file_uploader("Choose Excel File", type=["xlsx", "xls"])

# Function to load and cache the Excel data
@st.cache_data(show_spinner="Processing Excel data...")
def load_data(file):
    try:
        # Reads the Excel file. Assumes columns are named 'Mobile Number', 'Interest', and 'Rating'
        df = pd.read_excel(file)
        
        # Clean data: ensure Mobile Number is treated as a string to avoid decimal points
        if 'Mobile Number' in df.columns:
            df['Mobile Number'] = df['Mobile Number'].astype(str).str.strip()
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        return None

# Manage data loading state
data = None
if uploaded_file is not None:
    data = load_data(uploaded_file)
    st.sidebar.success("✅ Excel file loaded successfully!")
else:
    st.sidebar.warning("⚠️ Please upload an Excel file to activate the search.")

# Button to manually clear cache and refresh daily data
if st.sidebar.button("🔄 Refresh & Clear Cache"):
    st.cache_data.clear()
    st.rerun()


# --- FRONTEND / USER SEARCH INTERFACE ---
if data is not None:
    # Check if expected columns exist
    expected_cols = ['Mobile Number', 'Interest', 'Rating']
    if not all(col in data.columns for col in expected_cols):
        st.error(f"The Excel sheet must contain these exact columns: {expected_cols}")
    else:
        # Search Box Component
        search_input = st.text_input("Enter Mobile Number:", placeholder="e.g., 9876543210").strip()

        if search_input:
            # Filter rows matching the mobile number
            result_df = data[data['Mobile Number'] == search_input]

            if not result_df.empty:
                st.subheader(f"🎯 Top 10 Interests for {search_input}")
                
                # Sort by 'Rating' descending and grab the top 10
                top_10 = result_df.sort_values(by='Rating', ascending=False).head(10)
                
                # Reset index for clean display (starting from 1 instead of 0)
                top_10 = top_10.reset_index(drop=True)
                top_10.index = top_10.index + 1
                
                # Display the data nicely in a table
                st.table(top_10[['Interest', 'Rating']])
            else:
                st.info("ℹ️ No data found for this mobile number. Please check the number and try again.")
else:
    # Placeholder layout when no file is uploaded yet
    st.info("👈 Please upload the source Excel data file in the sidebar to begin searching.")