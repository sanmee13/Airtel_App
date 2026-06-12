import streamlit as st
import pandas as pd

# Define the authorized Admin Email (Replace this with YOUR GitHub email)
ADMIN_EMAIL = "sanchimeena13@gmail.com"

# Set up the page title and layout
st.set_page_config(page_title="Customer Interest Finder", layout="centered")

st.title("📱 Mobile Number Interest Lookup")
st.write("Enter a mobile number below to see the top 10 rated interests associated with it.")

# --- AUTOMATIC ADMIN CHECK ---
# Streamlit automatically passes user info if they are logged into Streamlit Cloud
user_email = st.context.headers.get("X-Streamlit-User-Email")

# Initialize data variable
data = None

# Only show the sidebar if the logged-in user matches the admin email
if user_email == ADMIN_EMAIL:
    st.sidebar.header("⚙️ Admin Controls")
    st.sidebar.write(f"Logged in as: `{user_email}`")
    
    # File uploader widget
    uploaded_file = st.sidebar.file_uploader("Upload Daily Excel File", type=["xlsx", "xls"])

    @st.cache_data(show_spinner="Processing Excel data...")
    def load_data(file):
        try:
            df = pd.read_excel(file)
            if 'Mobile Number' in df.columns:
                df['Mobile Number'] = df['Mobile Number'].astype(str).str.strip()
            return df
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            return None

    if uploaded_file is not None:
        data = load_data(uploaded_file)
        # We store the data in session state so it stays loaded for normal users
        st.session_state['cached_dataframe'] = data
        st.sidebar.success("✅ Excel file loaded and updated!")
    
    if st.sidebar.button("🔄 Clear App Cache"):
        st.cache_data.clear()
        if 'cached_dataframe' in st.session_state:
            del st.session_state['cached_dataframe']
        st.rerun()

# --- RETRIEVE DATA FOR USERS ---
# If the admin has uploaded data into the session, regular users can access it
if 'cached_dataframe' in st.session_state:
    data = st.session_state['cached_dataframe']


# --- FRONTEND / USER SEARCH INTERFACE ---
if data is not None:
    expected_cols = ['Mobile Number', 'Interest', 'Rating']
    if not all(col in data.columns for col in expected_cols):
        st.error(f"The Excel sheet must contain these exact columns: {expected_cols}")
    else:
        # Search Box Component (Visible to Everyone)
        search_input = st.text_input("Enter Mobile Number:", placeholder="e.g., 9876543210").strip()

        if search_input:
            result_df = data[data['Mobile Number'] == search_input]

            if not result_df.empty:
                st.subheader(f"🎯 Top 10 Interests for {search_input}")
                top_10 = result_df.sort_values(by='Rating', ascending=False).head(10)
                top_10 = top_10.reset_index(drop=True)
                top_10.index = top_10.index + 1
                st.table(top_10[['Interest', 'Rating']])
            else:
                st.info("ℹ️ No data found for this mobile number.")
else:
    # This shows if a regular user lands on the page before the admin has uploaded the daily file
    st.info("ℹ️ Service is temporarily offline or data is being refreshed by the admin. Please check back shortly.")
