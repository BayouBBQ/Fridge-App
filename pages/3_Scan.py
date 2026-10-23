import streamlit as st
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
