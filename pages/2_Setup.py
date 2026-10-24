import streamlit as st
from supabase import create_client
import json

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

lang = st.session_state.get("language", "English")

if lang == "עברית":
    title = "הגדרות"
    setting_up = "מגדיר עבור"
    make_label = "יצרן"
    model_label = "דגם"
    generate_label = "צור פריסת מקרר ומקפיא"
    pantry_label = "מיקומי מזווה (אחד בכל שורה)"
    save_label = "שמור הגדרות"
    complete_msg = "ההגדרות הושלמו. עובר לסריקה..."
    pantry_default = "מדף מזווה 1\nמדף מזווה 2\nמדף מזווה 3\nרצפת מזווה"
else:
    title = "Setup"
    setting_up = "Setting up for"
    make_label = "Make"
    model_label = "Model"
    generate_label = "Generate Fridge & Freezer Layout"
    pantry_label = "Pantry locations (one per line)"
    save_label = "Save Full Setup"
    complete_msg = "Setup already complete. Going to Scan..."
    pantry_default = "Pantry Shelf 1\nPantry Shelf 2\nPantry Shelf 3\nPantry Floor"

st.title(title)

if "user_name" not in st.session_state or not st.session_state.user_name:
    st.warning("Please select a user on the Home page first." if lang == "English" else "אנא בחר משתמש בעמוד הבית תחילה.")
    st.stop()

st.write(f"{setting_up} **{st.session_state.user_name}**")

if "setup_done" not in st.session_state:
    st.session_state.setup_done = False

if st.session_state.setup_done:
    st.success(complete_msg)
    st.switch_page("pages/3_Scan.py")

make = st.text_input(make_label, "LG")
model = st.text_input(model_label, "GR-B708XL")

if st.button(generate_label):
    make_clean = make.strip().lower()
    model_clean = model.strip().lower().replace(" ", "").replace("-", "")
    if "lg" in make_clean and "grb708xl" in model_clean:
        if lang == "עברית":
            st.session_state.fridge_freezer = [
                "מדף עליון במקרר", "מדף אמצעי במקרר", "מדף תחתון במקרר",
                "מגירת ירקות שמאל", "מגירת ירקות ימין",
                "דלת מקרר שמאל עליון", "דלת מקרר שמאל אמצע", "דלת מקרר שמאל תחתון",
                "דלת מקרר ימין עליון", "דלת מקרר ימין אמצע", "דלת מקרר ימין תחתון",
                "מקפיא שמאל עליון", "מקפיא שמאל תחתון", "מקפיא ימין עליון", "מקפיא ימין תחתון",
                "דלת מקפיא שמאל", "דלת מקפיא ימין"
            ]
        else:
            st.session_state.fridge_freezer = [
                "Fridge Top Shelf", "Fridge Middle Shelf", "Fridge Bottom Shelf",
                "Fridge Vegetable Drawer Left", "Fridge Vegetable Drawer Right",
                "Fridge Door Left Top", "Fridge Door Left Middle", "Fridge Door Left Bottom",
                "Fridge Door Right Top", "Fridge Door Right Middle", "Fridge Door Right Bottom",
                "Freezer Left Top", "Freezer Left Bottom", "Freezer Right Top", "Freezer Right Bottom",
                "Freezer Door Left", "Freezer Door Right"
            ]
        st.success("LG GR-B708XL layout loaded!" if lang == "English" else "פריסת LG GR-B708XL נטענה!")
    else:
        st.session_state.fridge_freezer = ["Fridge Top Shelf", "Fridge Middle Shelf", "Fridge Bottom Shelf", "Fridge Door", "Freezer"]
        st.info("Generic layout loaded." if lang == "English" else "פריסה כללית נטענה.")

pantry_text = st.text_area(pantry_label, pantry_default, height=150)

if st.button(save_label):
    fridge_freezer = st.session_state.get("fridge_freezer", [])
    pantry = [line.strip() for line in pantry_text.split("\n") if line.strip()]
    locations = fridge_freezer + pantry
    st.session_state.locations = locations
    st.session_state.setup_done = True
    
    supabase.table("user_settings").delete().eq("user_name", st.session_state.user_name).execute()
    supabase.table("user_settings").insert({
        "user_name": st.session_state.user_name,
        "locations": json.dumps(locations)
    }).execute()
    
    st.switch_page("pages/3_Scan.py")
