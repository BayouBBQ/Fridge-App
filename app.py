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

# --- Users Section (main page) ---
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

st.divider()

# Require a user
if "user_name" not in st.session_state or not st.session_state.user_name:
    st.info("Select or add a user above to continue.")
    st.stop()

st.write(f"### Hello, **{st.session_state.user_name}**")

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
        st.session_state.locations = fridge_freezer + pantry
        st.session_state.setup_done = True
        st.success("Setup saved!")
        st.rerun()

else:
    language = st.radio("Language", ["English", "עברית"], horizontal=True)
    prompt = "List all visible food items as bullet points with estimated quantity." if language == "English" else "רשום את כל פריטי המזון הגלויים כנקודות עם כמות משוערת."

    st.subheader("Upload Photo for Each Location")
    photo_uploads = {}
    for i, loc in enumerate(st.session_state.locations):
        uploaded = st.file_uploader(f"Photo for {loc}", type=["jpg", "png", "jpeg"], key=f"photo_{i}")
        if uploaded:
            photo_uploads[loc] = uploaded
            st.image(uploaded, width=200)

    if photo_uploads and st.button("Analyze All Photos"):
        with st.spinner("Analyzing..."):
            all_results = []
            for loc, uploaded in photo_uploads.items():
                bytes_data = uploaded.getvalue()
                base64_image = base64.b64encode(bytes_data).decode()
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}]
                )
                result = response.choices[0].message.content
                st.write(f"**{loc}:**")
                st.write(result)
                all_results.append((loc, result))
            st.session_state['analysis_results'] = all_results

    if 'analysis_results' in st.session_state and st.button("Save All Items"):
        total_saved = 0
        for loc, text in st.session_state['analysis_results']:
            items = re.findall(r'[-•*]\s*(.+?)(?=\n|$)', text)
            for item in items:
                if item.strip():
                    supabase.table("inventory").insert({
                        "name": item.strip()[:200],
                        "quantity": "as detected",
                        "location": loc,
                        "user_name": st.session_state.user_name
                    }).execute()
                    total_saved += 1
        st.success(f"Saved {total_saved} items to the cloud!")
        if 'analysis_results' in st.session_state:
            del st.session_state['analysis_results']

    st.subheader("Current Inventory")
    try:
        response = supabase.table("inventory").select("*").eq("user_name", st.session_state.user_name).order("added", desc=True).execute()
        rows = response.data
        if rows:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Item", "Quantity", "Location", "Added"])
            for row in rows:
                writer.writerow([row.get("name",""), row.get("quantity",""), row.get("location",""), row.get("added","")])
            csv_data = output.getvalue()
            
            st.download_button(
                label="Download Inventory (CSV)",
                data=csv_data,
                file_name=f"inventory_{st.session_state.user_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
            for row in rows:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {row['name']} — {row['location']}")
                with col2:
                    if st.button("Delete", key=f"del{row['id']}"):
                        supabase.table("inventory").delete().eq("id", row['id']).execute()
                        st.rerun()
        else:
            st.info("No items yet for this user.")
    except Exception as e:
        st.error(f"Could not load inventory: {e}")
        rows = []

    st.subheader("Compare with Previous Scan (Shopping List)")
    previous_file = st.file_uploader("Upload previous inventory CSV", type=["csv"])
    if previous_file and rows:
        previous_items = set()
        content = previous_file.getvalue().decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        next(reader, None)
        for row in reader:
            if row and row[0].strip():
                previous_items.add(row[0].strip().lower())
        
        current_items = {row['name'].strip().lower() for row in rows}
        missing = previous_items - current_items
        
        if missing:
            st.write("**Possible shopping list (missing from current scan):**")
            for item in sorted(missing):
                st.write(f"• {item}")
        else:
            st.success("No missing items detected compared to the previous scan.")

    if st.button("Reset Setup"):
        st.session_state.setup_done = False
        st.rerun()
      
