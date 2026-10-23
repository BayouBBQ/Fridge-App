import streamlit as st
from openai import OpenAI
from supabase import create_client
import base64
from datetime import datetime
import re
import csv
import io

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Fridge Scanner")

# --- Users Section ---
st.sidebar.header("Users")

# Get existing users
try:
    users_response = supabase.table("inventory").select("user_name").execute()
    existing_users = sorted(list(set([row["user_name"] for row in users_response.data if row.get("user_name")])))
except:
    existing_users = []

# Select or add user
selected_user = st.sidebar.selectbox("Select user", [""] + existing_users)
new_user = st.sidebar.text_input("Or add new user")

if st.sidebar.button("Use this user"):
    if new_user.strip():
        st.session_state.user_name = new_user.strip()
    elif selected_user:
        st.session_state.user_name = selected_user
    st.rerun()

# Delete user
if existing_users:
    user_to_delete = st.sidebar.selectbox("Delete user", [""] + existing_users)
    if st.sidebar.button("Delete selected user") and user_to_delete:
        supabase.table("inventory").delete().eq("user_name", user_to_delete).execute()
        st.sidebar.success(f"Deleted all data for {user_to_delete}")
        if st.session_state.get("user_name") == user_to_delete:
            st.session_state.user_name = ""
        st.rerun()

# Require a user
if "user_name" not in st.session_state or not st.session_state.user_name:
    st.info("Select or add a user in the sidebar to continue.")
    st.stop()

st.write(f"Hello, **{st.session_state.user_name}**")

# Setup Wizard
if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False
    st.session_state.locations = []

if not st.session_state.setup_done:
    st.subheader("Fridge Setup Wizard")
    make = st.text_input("Make", "LG")
    model = st.text_input("Model", "GR-B708XL")
    
    if st.button("Generate Fridge & Freezer Layout"):
        make_clean = make.strip().lower()
        model_clean = model.strip().lower().replace(" ", "").replace("-", "")
        
        if "lg" in make_clean and "grb708xl" in model_clean:
            fridge_freezer = [
                "Fridge Top Shelf",
                "Fridge Middle Shelf",
                "Fridge Bottom Shelf",
                "Fridge Vegetable Drawer Left",
                "Fridge Vegetable Drawer Right",
                "Fridge Door Left Top",
                "Fridge Door Left Middle",
                "Fridge Door Left Bottom",
                "Fridge Door Right Top",
                "Fridge Door Right Middle",
                "Fridge Door Right Bottom",
                "Freezer Left Top",
                "Freezer Left Bottom",
                "Freezer Right Top",
                "Freezer Right Bottom",
                "Freezer Door Left",
                "Freezer Door Right"
            ]
            st.session_state.fridge_freezer = fridge_freezer
            st.success("Fridge & Freezer layout for LG GR-B708XL loaded!")
        else:
            st.session_state.fridge_freezer = [
                "Fridge Top Shelf",
                "Fridge Middle Shelf",
                "Fridge Bottom Shelf",
                "Fridge Door",
                "Freezer"
            ]
            st.info("Generic fridge/freezer layout loaded.")

    st.subheader("Pantry Locations (customize as needed)")
    pantry_default = "Pantry Shelf 1\nPantry Shelf 2\nPantry Shelf 3\nPantry Floor"
    pantry_text = st.text_area("Pantry shelves / locations (one per line)", pantry_default, height=150)

    if st.button("Save Full Setup"):
        fridge_freezer = st.session_state.get("fridge_freezer", [])
        pantry = [line.strip() for line in pantry_text.split("\n") if line.strip()]
      
