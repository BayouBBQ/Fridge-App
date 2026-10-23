import streamlit as st
from supabase import create_client
import csv
import io

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Shopping List")

if "user_name" not in st.session_state or not st.session_state.user_name:
    st.warning("Please select a user on the Home page first.")
    st.stop()

st.write(f"Shopping list for **{st.session_state.user_name}**")

try:
    response = supabase.table("inventory").select("*").eq("user_name", st.session_state.user_name).execute()
    current_rows = response.data
    current_items = {row['name'].strip().lower() for row in current_rows} if current_rows else set()
except:
    current_items = set()

previous_file = st.file_uploader("Upload previous inventory CSV", type=["csv"])
if previous_file:
    previous_items = set()
    content = previous_file.getvalue().decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    next(reader, None)
    for row in reader:
        if row and row[0].strip():
            previous_items.add(row[0].strip().lower())
    
    missing = previous_items - current_items
    if missing:
        st.write("**Items that may need restocking:**")
        for item in sorted(missing):
            st.write(f"• {item}")
    else:
        st.success("No missing items detected.")
