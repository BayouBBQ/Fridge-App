import streamlit as st

st.title("Setup")

if "user_name" not in st.session_state or not st.session_state.user_name:
    st.warning("Please select a user on the Home page first.")
    st.stop()

st.write(f"Setting up for **{st.session_state.user_name}**")

if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False

if not st.session_state.setup_done:
    make = st.text_input("Make", "LG")
    model = st.text_input("Model", "GR-B708XL")
    
    if st.button("Generate Fridge & Freezer Layout"):
        make_clean = make.strip().lower()
        model_clean = model.strip().lower().replace(" ", "").replace("-", "")
        if "lg" in make_clean and "grb708xl" in model_clean:
            st.session_state.fridge_freezer = [
                "Fridge Top Shelf", "Fridge Middle Shelf", "Fridge Bottom Shelf",
                "Fridge Vegetable Drawer Left", "Fridge Vegetable Drawer Right",
                "Fridge Door Left Top", "Fridge Door Left Middle", "Fridge Door Left Bottom",
                "Fridge Door Right Top", "Fridge Door Right Middle", "Fridge Door Right Bottom",
                "Freezer Left Top", "Freezer Left Bottom", "Freezer Right Top", "Freezer Right Bottom",
                "Freezer Door Left", "Freezer Door Right"
            ]
            st.success("LG GR-B708XL layout loaded!")
        else:
            st.session_state.fridge_freezer = ["Fridge Top Shelf", "Fridge Middle Shelf", "Fridge Bottom Shelf", "Fridge Door", "Freezer"]
            st.info("Generic layout loaded.")

    pantry_text = st.text_area("Pantry locations (one per line)", "Pantry Shelf 1\nPantry Shelf 2\nPantry Shelf 3\nPantry Floor", height=150)

    if st.button("Save Full Setup"):
        fridge_freezer = st.session_state.get("fridge_freezer", [])
        pantry = [line.strip() for line in pantry_text.split("\n") if line.strip()]
        st.session_state.locations = fridge_freezer + pantry
        st.session_state.setup_done = True
        st.success("Setup saved! Going to Scan...")
        st.switch_page("pages/3_Scan.py")
else:
    st.success("Setup complete.")
    st.write("Locations:", st.session_state.get("locations", []))
    if st.button("Go to Scan"):
        st.switch_page("pages/3_Scan.py")
    if st.button("Reset Setup"):
        st.session_state.setup_done = False
        st.rerun()port streamlit as st
from openai import OpenAI
from supabase import create_client
import base64
import re

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Scan")

if "user_name" not in st.session_state or not st.session_state.user_name:
    st.warning("Please select a user on the Home page first.")
    st.stop()
if not st.session_state.get("setup_done"):
    st.warning("Please complete Setup first.")
    st.stop()

st.write(f"Scanning for **{st.session_state.user_name}**")

language = st.radio("Language", ["English", "עברית"], horizontal=True)
prompt = "List all visible food items as bullet points with estimated quantity." if language == "English" else "רשום את כל פריטי המזון הגלויים כנקודות עם כמות משוערת."

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
    st.success(f"Saved {total_saved} items!")
    del st.session_state['analysis_results']
