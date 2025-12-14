import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import base64

# Загружаем изображение
image = Image.open("test.png")

st.title("Signature")

def pil_to_data_url(pil_img):
    """Конвертирует PIL Image в data:URL для стабильной работы на серверах"""
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

def signaturefunk(image):
    st.write("Canvas")
    
    # Конвертируем в data:URL для обхода image_to_url ошибки
    
    canvas_result = st_canvas(
    fill_color="#eee",
    stroke_width=5,
    stroke_color="black",
    background_image=image,  # PIL.Image.Image
    update_streamlit=False,
    height=200,
    width=700,
    drawing_mode="freedraw",
    key="signature_canvas",
)
    
    st.write("Image of the canvas")
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data)

signaturefunk(image)
