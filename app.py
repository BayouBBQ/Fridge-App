import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Fridge Scanner")
st.subheader("Users")

try:
    users_response = supabase.table("inventory").select("user_name").execute()
    existing_users = sorted(list(set([row["user_name"] for row in users_response.data if row.get("user_name")])))
except:
    existing_users = []

selected_user = st.selectbox("Select user", [""] + existing_users)
if selected_user and selected_user != st.session_state.get("user_name"):
    st.session_state.user_name = selected_user
    st.rerun()

new_user = st.text_input("Or add new user")
if st.button("Add and use new user") and new_user.strip():
    st.session_state.user_name = new_user.strip()
    st.session_state.setup_done = False
    st.rerun()

if existing_users:
    user_to_delete = st.selectbox("Delete a user", [""] + existing_users)
    if st.button("Delete selected user") and user_to_delete:
        supabase.table("inventory").delete().eq("user_name", user_to_delete).execute()
        st.success(f"Deleted {user_to_delete}")
        if st.session_state.get("user_name") == user_to_delete:
            st.session_state.user_name = ""
        st.rerun()

# Auto-redirect
if st.session_state.get("user_name"):
    st.success(f"Current user: **{st.session_state.user_name}**")
    
    try:
        check = supabase.table("inventory").select("id").eq("user_name", st.session_state.user_name).limit(1).execute()
        has_data = len(check.data) > 0
    except:
        has_data = False
    
    if not st.session_state.get("setup_done") and not has_data:
        st.info("New user — going to Setup...")
        st.switch_page("pages/2_Setup.py")
    elif has_data or st.session_state.get("setup_done"):
        st.info("Existing user — going to Scan...")
        st.switch_page("pages/3_Scan.py")
else:
    st.info("Select or add a user to continue. Use the sidebar menu to navigate.")
       
      
