import streamlit as st
from supabase import create_client
from collections import defaultdict

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Shopping List")

if "user_name" not in st.session_state or not st.session_state.user_name:
    st.warning("Please select a user on the Home page first.")
    st.stop()

st.write(f"Shopping list for **{st.session_state.user_name}**")

# Manual add (still available)
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

# Automatic comparison of the two most recent scans
st.subheader("Automatic comparison (latest vs previous scan)")

try:
    response = supabase.table("inventory").select("name, added").eq("user_name", st.session_state.user_name).order("added", desc=True).execute()
    rows = response.data
    
    if not rows:
        st.info("No scans yet.")
    else:
        # Group items by scan time
        scans = defaultdict(set)
        for row in rows:
            scans[row["added"]].add(row["name"].strip().lower())
        
        scan_times = sorted(scans.keys(), reverse=True)
        
        if len(scan_times) < 2:
            st.info("Need at least two scans to compare automatically.")
        else:
            latest = scans[scan_times[0]]
            previous = scans[scan_times[1]]
            missing = previous - latest
            
            st.write(f"Comparing scan from {scan_times[1][:16]} to {scan_times[0][:16]}")
            if missing:
                st.write("**Items that may need restocking:**")
                for item in sorted(missing):
                    st.write(f"• {item}")
            else:
                st.success("No missing items between the last two scans.")
except Exception as e:
    st.error(f"Error loading scans: {e}")
