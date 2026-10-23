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

# Select user — updates immediately
selected_user = st.selectbox(
    "Select user",
    [""] + existing_users,
    index=0 if "user_name" not in st.session_state else (existing_users.index(st.session_state.user_name) + 1 if st.session_state.get("user_name") in existing_users else 0)
)

if selected_user and selected_user != st.session_state.get("user_name"):
    st.session_state.user_name = selected_user
    st.rerun()

# Add new user
new_user = st.text_input("Or add new user")
if st.button("Add and use new user") and new_user.strip():
    st.session_state.user_name = new_user.strip()
    st.rerun()

# Delete user
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
    st.info("Use the menu to go to Setup, Scan, Inventory, or Shopping List.")
else:
    st.info("Select or add a user above to continue.")
       
      
