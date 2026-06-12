import streamlit as pd
import streamlit as st
import pandas as pd

# 🔑 SET YOUR CHOSEN ADMIN PASSWORD HERE
ADMIN_PASSWORD = "Password123"

# Set up the page title and layout
st.set_page_config(page_title="Customer Interest Finder", layout="centered")

st.title("📱 Mobile Number Interest Lookup")
st.write("Enter a mobile number below to see the top 10 rated interests associated with it.")

# --- THE GLOBAL DATA STORE ---
# We use st.cache_resource so that the uploaded data is shared across ALL users globally
@st.cache_resource
def get_global_data():
    return {"df": None}

global_store = get_global_data()


# --- ADMIN LOGIN SIDEBAR ---
st.sidebar.header("⚙️ Admin Controls")
admin_login = st.sidebar.text_input("Enter Admin Password:", type="password")

if admin_login == ADMIN_PASSWORD:
    st.sidebar.success("🔓 Admin Access Granted!")
    
    # File uploader widget - ONLY appears when password is correct
    uploaded_file = st.sidebar.file_uploader("Upload Daily Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Process the Excel file
            df = pd.read_excel(uploaded_file)
            if 'Mobile Number' in df.columns:
                df['Mobile Number'] = df['Mobile Number'].astype(str).str.strip()
            
            # Save it to the GLOBAL store so everyone can see it instantly
            global_store["df"] = df
            st.sidebar.success("✅ Excel file pushed to live servers!")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
    
    # Admin clear button to wipe the global data
    if st.sidebar.button("🔄 Clear Live Data"):
        global_store["df"] = None
        st.cache_resource.clear()
        st.sidebar.info("Live data cleared.")
        st.rerun()
else:
    if admin_login:
        st.sidebar.error("❌ Incorrect Password")


# --- RETRIEVE DATA FOR USERS ---
# Fetch data from the global store
data = global_store["df"]


# --- FRONTEND / USER SEARCH INTERFACE ---
if data is not None:
    expected_cols = ['Mobile Number', 'Interest', 'Rating']
    if not all(col in data.columns for col in expected_cols):
        st.error(f"The Excel sheet must contain these exact columns: {expected_cols}")
    else:
        # Search Box Component (Visible to Everyone once data is loaded)
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
