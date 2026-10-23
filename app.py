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

selected_user = st.selectbox("Select existing user", [""] + existing_users)
if selected_user and selected_user != st.session_state.get("user_name"):
    st.session_state.user_name = selected_user
    # If no layout is loaded, send to Setup; otherwise go to Scan
    if not st.session_state.get("locations"):
        st.session_state.setup_done = False
        st.switch_page("pages/2_Setup.py")
    else:
        st.session_state.setup_done = True
        st.switch_page("pages/3_Scan.py")

new_user = st.text_input("Or add new user")
if st.button("Add and use new user") and new_user.strip():
    st.session_state.user_name = new_user.strip()
    st.session_state.setup_done = False
    st.switch_page("pages/2_Setup.py")

if existing_users:
    user_to_delete = st.selectbox("Delete a user", [""] + existing_users)
    if st.button("Delete selected user") and user_to_delete:
        supabase.table("inventory").delete().eq("user_name", user_to_delete).execute()
        st.success(f"Deleted {user_to_delete}")
        if st.session_state.get("user_name") == user_to_delete:
            st.session_state.user_name = ""
        st.rerun()

if st.session_state.get("user_name"):
    st.success(f"Current user: **{st.session_state.user_name}**")
else:
    st.info("Select an existing user or add a new one.")
       
      
