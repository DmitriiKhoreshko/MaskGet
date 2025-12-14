import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import base64
import os

def pil_to_data_url(pil_img):
    """Конвертирует PIL Image в data:URL для стабильной работы на серверах"""
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

# Проверяем наличие файла
image_path = "test.png"
if os.path.exists(image_path):
    image = Image.open(image_path)
    background_url = pil_to_data_url(image)  # Конвертируем в data URL
else:
    st.error("Файл test.png не найден! Добавьте его в репозиторий.")
    st.stop()

st.title("Signature")

def pil_to_data_url(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

def signaturefunk(background_url):
    st.write("Canvas")
    
    canvas_result = st_canvas(
        fill_color="#eee",
        stroke_width=5,
        stroke_color="black",
        background_image=background_url,  # Теперь data URL вместо PIL
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
