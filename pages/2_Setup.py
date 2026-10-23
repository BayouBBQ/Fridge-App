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
        st.success("Setup saved!")
        st.rerun()
else:
    st.success("Setup complete.")
    st.write("Locations:", st.session_state.get("locations", []))
    if st.button("Reset Setup"):
        st.session_state.setup_done = False
        st.rerun()
