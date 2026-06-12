import streamlit as st
import pandas as pd

# 🔑 Fetches the password securely from Streamlit's hidden Secrets dashboard
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# Set up the page title and layout
st.set_page_config(
    page_title="Customer Interest Finder", 
    layout="centered",
    initial_sidebar_state="collapsed" # Keeps it closed by default
)

# --- THE MAGIC SIDEBAR CONTROLLER ---
# Check if '?admin=true' is in the website URL
is_admin_url = st.query_params.get("admin") == "true"

if not is_admin_url:
    # If they are NOT using the admin URL, inject CSS to completely wipe out the sidebar & toggle button
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none !important;}
            [data-testid="collapsedControl"] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- THE GLOBAL DATA STORE ---
@st.cache_resource
def get_global_data():
    return {"df": None}

global_store = get_global_data()


# --- ADMIN LOGIN SIDEBAR (Only operates if using the admin URL) ---
if is_admin_url:
    st.sidebar.header("⚙️ Admin Controls")
    admin_login = st.sidebar.text_input("Enter Admin Password:", type="password")

    if admin_login == ADMIN_PASSWORD:
        st.sidebar.success("🔓 Admin Access Granted!")
        
        uploaded_file = st.sidebar.file_uploader("Upload Daily Excel File", type=["xlsx", "xls"])

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                if 'Mobile Number' in df.columns:
                    df['Mobile Number'] = df['Mobile Number'].astype(str).str.strip()
                
                global_store["df"] = df
                st.sidebar.success("✅ Excel file pushed to live servers!")
            except Exception as e:
                st.sidebar.error(f"Error loading file: {e}")
        
        if st.sidebar.button("🔄 Clear Live Data"):
            global_store["df"] = None
            st.cache_resource.clear()
            st.sidebar.info("Live data cleared.")
            st.rerun()
    else:
        if admin_login:
            st.sidebar.error("❌ Incorrect Password")


# --- RETRIEVE DATA FOR USERS ---
data = global_store["df"]


# --- FRONTEND / USER SEARCH INTERFACE (Visible to Everyone) ---
st.title("📱 Mobile Number Interest Lookup")
st.write("Enter a mobile number below to see the top 10 rated interests associated with it.")

if data is not None:
    expected_cols = ['Mobile Number', 'Interest', 'Rating']
    if not all(col in data.columns for col in expected_cols):
        st.error(f"The Excel sheet must contain these exact columns: {expected_cols}")
    else:
        # Search Box
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
    st.info("ℹ️ Service is temporarily offline or data is being refreshed by the admin. Please check back shortly.")
