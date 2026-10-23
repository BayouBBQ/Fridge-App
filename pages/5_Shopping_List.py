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

# Manual add
if "manual_shopping" not in st.session_state:
    st.session_state.manual_shopping = []

new_item = st.text_input("Add item manually")
if st.button("Add to list") and new_item.strip():
    st.session_state.manual_shopping.append(new_item.strip())
    st.rerun()

if st.session_state.manual_shopping:
    st.write("**Manually added items:**")
    for i, item in enumerate(st.session_state.manual_shopping):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"• {item}")
        with col2:
            if st.button("Remove", key=f"rem{i}"):
                st.session_state.manual_shopping.pop(i)
                st.rerun()

st.divider()

# CSV comparison
st.subheader("Compare with previous scan")
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
        st.success("No missing items detected from the previous scan.")
