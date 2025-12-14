import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import io
import cv2
from streamlit_container_width import st_container_width


def get_width_px(x, default: int = 900) -> int:
    """
    streamlit-container-width может вернуть:
    - число (width)
    - dict (например {"width": ..., ...})
    - None (пока не измерилось)
    """
    if x is None:
        return default
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, dict):
        # самый ожидаемый формат
        if "width" in x and isinstance(x["width"], (int, float)):
            return int(x["width"])
        # на всякий случай — первый попавшийся числовой value
        for v in x.values():
            if isinstance(v, (int, float)):
                return int(v)
    return default


st.set_page_config(page_title="Создание маски", layout="wide")
st.title("Выделение области для изменения")
st.markdown("Загрузите фото, выделите область для изменения.")

uploaded_file = st.file_uploader("Выберите изображение:", type=["png", "jpg", "jpeg"])
if not uploaded_file:
    st.info("Загрузите изображение, чтобы начать.")
    st.stop()

# 1) Load original
image = Image.open(uploaded_file).convert("RGB")

# 2) Settings
st.sidebar.header("Настройки кисти")
stroke_width = st.sidebar.slider("Толщина", 1, 100, 40)

stroke_color = st.sidebar.color_picker("Цвет кисти", "#4E4E4E")

# Фикс против "усиления" на пересечениях: кисть непрозрачная (без альфы) [web:93]
stroke_color_solid = stroke_color  # "#RRGGBB"

st.sidebar.markdown("---")
blur_radius = st.sidebar.slider("Размытие маски (px)", 0, 50, 15)

# Layout
col1, col2 = st.columns([1.5, 1], gap="large")

st.subheader("Редактор")

# 3) Fit to available container width (measure inside the column) [web:123]
available = st_container_width(key="canvas_col_width")

available_w = get_width_px(available, default=900)

# небольшой запас под padding/границы
max_width = max(200, available_w - 24)

if image.width > max_width:
    ratio = max_width / image.width
    disp_w = int(max_width)
    disp_h = int(image.height * ratio)
    display_image = image.resize((disp_w, disp_h))
    scale_factor = image.width / disp_w
else:
    display_image = image
    disp_w, disp_h = image.size
    scale_factor = 1.0

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",
    stroke_width=stroke_width,
    stroke_color=stroke_color_solid,  # непрозрачный цвет
    background_image=display_image,
    update_streamlit=True,
    height=disp_h,
    width=disp_w,
    drawing_mode="freedraw",
    key="canvas_stable",
)

st.subheader("Результат")

if canvas_result.image_data is None:
    st.info("Нарисуйте область на изображении слева.")
    st.stop()

img_data = canvas_result.image_data  # RGBA drawing layer; background not included [web:123]
alpha = img_data[:, :, 3].astype(np.uint8)

if np.max(alpha) <= 0:
    st.info("Нарисуйте область на изображении слева.")
    st.stop()

# 4) Binary mask: where drawn -> 255
mask = np.where(alpha > 0, 255, 0).astype(np.uint8)

# 5) Back to original size
if scale_factor != 1.0:
    mask = cv2.resize(mask, (image.width, image.height), interpolation=cv2.INTER_NEAREST)

# 6) Blur mask if needed
if blur_radius > 0:
    k = blur_radius * 2 + 1
    mask = cv2.GaussianBlur(mask, (k, k), blur_radius)

mask_img = Image.fromarray(mask)

# Download mask
buf_mask = io.BytesIO()
mask_img.save(buf_mask, format="PNG")
st.download_button(
    "⬇️ Скачать маску PNG",
    data=buf_mask.getvalue(),
    file_name="mask.png",
    mime="image/png",
)
