if 'analysis_results' in st.session_state and st.button("Save All Items"):
    scan_time = datetime.now().isoformat()
    total_saved = 0
    for loc, text in st.session_state['analysis_results']:
        items = re.findall(r'[-•*]\s*(.+?)(?=\n|$)', text)
        for item in items:
            if item.strip():
                supabase.table("inventory").insert({
                    "name": item.strip()[:200],
                    "quantity": "as detected",
                    "location": loc,
                    "user_name": st.session_state.user_name,
                    "added": scan_time
                }).execute()
                total_saved += 1
    st.success(f"Saved {total_saved} items! Going to Inventory...")
    if 'analysis_results' in st.session_state:
        del st.session_state['analysis_results']
    st.switch_page("pages/4_Inventory.py")


