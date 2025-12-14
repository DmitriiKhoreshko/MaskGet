import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import requests
from io import BytesIO

st.title("Signature")

def signaturefunk(background_url):
    st.write("Canvas")
    
    canvas_result = st_canvas(
        fill_color="#eee",
        stroke_width=5,
        stroke_color="black",
        background_image=background_url,  # Используем data URL
        update_streamlit=False,
        height=200,
        width=700,
        drawing_mode="freedraw",
        key="signature_canvas",
    )
    
    st.write("Image of the canvas")
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data)

# Основные исправления:

# 1. Загрузка изображения из URL вместо локального файла
try:
    response = requests.get("https://avatars.mds.yandex.net/i?id=cda43f8d3f42f8297f108945fee84545_l-5031203-images-thumbs&n=13")
    response.raise_for_status()  # Проверяем успешность запроса
    image = Image.open(BytesIO(response.content))
    
    # Запускаем функцию с правильным аргументом (data URL)
    signaturefunk(image)
    
except requests.exceptions.RequestException as e:
    st.error(f"Ошибка при загрузке изображения: {e}")
    st.stop()
except Exception as e:
    st.error(f"Произошла ошибка: {e}")
    st.stop()