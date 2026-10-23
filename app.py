import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Fridge Scanner")

# Navigation buttons
st.subheader("Menu")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Setup"):
        st.switch_page("pages/2_Setup.py")
with col2:
    if st.button("Scan"):
        st.switch_page("pages/3_Scan.py")
with col3:
    if st.button("Inventory"):
        st.switch_page("pages/4_Inventory.py")
with col4:
    if st.button("Shopping List"):
        st.switch_page("pages/5_Shopping_List.py")

st.divider()

# Users section
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
    st.rerun()

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
    st.info("Select or add a user to continue.")
       
      
