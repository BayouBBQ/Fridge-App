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

col1, col2 = st.columns(2)
with col1:
    selected_user = st.selectbox("Select existing user", [""] + existing_users)
with col2:
    new_user = st.text_input("Or add new user")

if st.button("Use this user"):
    if new_user.strip():
        st.session_state.user_name = new_user.strip()
    elif selected_user:
        st.session_state.user_name = selected_user
    st.rerun()

if existing_users:
    user_to_delete = st.selectbox("Delete a user (removes all their data)", [""] + existing_users)
    if st.button("Delete selected user") and user_to_delete:
        supabase.table("inventory").delete().eq("user_name", user_to_delete).execute()
        st.success(f"Deleted all data for {user_to_delete}")
        if st.session_state.get("user_name") == user_to_delete:
            st.session_state.user_name = ""
        st.rerun()

if "user_name" in st.session_state and st.session_state.user_name:
    st.success(f"Current user: **{st.session_state.user_name}**")
    st.info("Use the sidebar to go to Setup, Scan, Inventory, or Shopping List.")
else:
    st.info("Select or add a user above to continue.")
       
      
