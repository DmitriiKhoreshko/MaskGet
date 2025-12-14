# Source - https://stackoverflow.com/a
# Posted by RoseGod
# Retrieved 2025-12-14, License - CC BY-SA 4.0

import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.title("Signature")

def signaturefunk():
    
    st.write("Canvas")

    canvas_result = st_canvas(
            fill_color="#eee",
            stroke_width=5,
            stroke_color="black",
            background_color="white",
            update_streamlit=False,
            height=200,
            width=700,
            drawing_mode="freedraw",
        )
    
    st.write("Image of the canvs")
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data)

signaturefunk()
