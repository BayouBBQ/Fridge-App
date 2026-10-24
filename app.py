import streamlit as st
from supabase import create_client
import json

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Fridge Scanner" if st.session_state.get("language", "English") == "English" else "סורק מקרר")

st.subheader("Language / שפה")

if st.button("English", key="btn_en"):
    st.session_state.language = "English"
    st.rerun()

if st.button("עברית", key="btn_he"):
    st.session_state.language = "עברית"
    st.rerun()

lang = st.session_state.get("language", "English")
st.success(f"Selected language: {lang}" if lang == "English" else f"שפה נבחרה: {lang}")

# Translated labels
if lang == "עברית":
    users_label = "משתמשים"
    select_label = "בחר משתמש קיים"
    continue_label = "המשך עם המשתמש הנבחר"
    new_user_label = "או הוסף משתמש חדש"
    add_label = "הוסף משתמש חדש והמשך"
    delete_label = "מחק משתמש"
    delete_btn = "מחק משתמש נבחר"
    current_label = "משתמש נוכחי"
    info_label = "בחר משתמש ולחץ על המשך, או הוסף משתמש חדש."
else:
    users_label = "Users"
    select_label = "Select existing user"
    continue_label = "Continue with selected user"
    new_user_label = "Or add new user"
    add_label = "Add new user and continue"
    delete_label = "Delete a user"
    delete_btn = "Delete selected user"
    current_label = "Current user"
    info_label = "Select a user and click Continue, or add a new user."

st.subheader(users_label)

try:
    users_response = supabase.table("inventory").select("user_name").execute()
    existing_users = sorted(list(set([row["user_name"] for row in users_response.data if row.get("user_name")])))
except:
    existing_users = []

selected_user = st.selectbox(select_label, [""] + existing_users)
if selected_user:
    if st.button(continue_label):
        st.session_state.user_name = selected_user
        try:
            settings = supabase.table("user_settings").select("locations").eq("user_name", selected_user).execute()
            if settings.data and settings.data[0].get("locations"):
                st.session_state.locations = json.loads(settings.data[0]["locations"])
                st.session_state.setup_done = True
                st.switch_page("pages/3_Scan.py")
            else:
                st.session_state.setup_done = False
                st.switch_page("pages/2_Setup.py")
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.setup_done = False
            st.switch_page("pages/2_Setup.py")

new_user = st.text_input(new_user_label)
if st.button(add_label) and new_user.strip():
    st.session_state.user_name = new_user.strip()
    st.session_state.setup_done = False
    st.switch_page("pages/2_Setup.py")

if existing_users:
    user_to_delete = st.selectbox(delete_label, [""] + existing_users)
    if st.button(delete_btn) and user_to_delete:
        supabase.table("inventory").delete().eq("user_name", user_to_delete).execute()
        supabase.table("user_settings").delete().eq("user_name", user_to_delete).execute()
        st.success(f"Deleted {user_to_delete}")
        st.rerun()

if st.session_state.get("user_name"):
    st.success(f"{current_label}: **{st.session_state.user_name}**")
else:
    st.info(info_label)
