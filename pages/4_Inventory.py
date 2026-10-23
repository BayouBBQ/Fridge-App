import streamlit as st
from supabase import create_client
import csv
import io
from datetime import datetime

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Inventory")

if "user_name" not in st.session_state or not st.session_state.user_name:
    st.warning("Please select a user on the Home page first.")
    st.stop()

st.write(f"Inventory for **{st.session_state.user_name}**")

try:
    response = supabase.table("inventory").select("*").eq("user_name", st.session_state.user_name).order("added", desc=True).execute()
    rows = response.data
    if rows:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Item", "Quantity", "Location", "Added"])
        for row in rows:
            writer.writerow([row.get("name",""), row.get("quantity",""), row.get("location",""), row.get("added","")])
        st.download_button("Download Inventory (CSV)", output.getvalue(), f"inventory_{st.session_state.user_name}_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        for row in rows:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {row['name']} — {row['location']}")
            with col2:
                if st.button("Delete", key=f"del{row['id']}"):
                    supabase.table("inventory").delete().eq("id", row['id']).execute()
                    st.rerun()
    else:
        st.info("No items yet.")
except Exception as e:
    st.error(f"Error: {e}")
