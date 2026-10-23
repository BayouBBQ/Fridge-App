import streamlit as st
from openai import OpenAI
import base64
import sqlite3
from datetime import datetime
import re

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

conn = sqlite3.connect('inventory.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY,
    name TEXT,
    quantity TEXT,
    location TEXT,
    added TEXT
)''')
conn.commit()

st.title("Fridge Scanner")

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

    # Customizable Pantry
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
    # Main app after setup
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
        now = datetime.now().isoformat()
        total_saved = 0
        for loc, text in st.session_state['analysis_results']:
            items = re.findall(r'[-•*]\s*(.+?)(?=\n|$)', text)
            for item in items:
                if item.strip():
                    cursor.execute("INSERT INTO inventory (name, quantity, location, added) VALUES (?, ?, ?, ?)", 
                                   (item.strip()[:200], "as detected", loc, now))
                    total_saved += 1
        conn.commit()
        st.success(f"Saved {total_saved} items!")
        if 'analysis_results' in st.session_state:
            del st.session_state['analysis_results']

    st.subheader("Current Inventory")
    cursor.execute("SELECT id, name, location FROM inventory ORDER BY added DESC")
    for row in cursor.fetchall():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"• {row[1]} — {row[2]}")
        with col2:
            if st.button("Delete", key=f"del{row[0]}"):
                cursor.execute("DELETE FROM inventory WHERE id=?", (row[0],))
                conn.commit()
                st.rerun()

    if st.button("Reset Setup"):
        st.session_state.setup_done = False
        st.rerun()
