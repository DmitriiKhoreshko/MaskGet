import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import io
import cv2
import base64
from streamlit_container_width import st_container_width


def extract_width_px(container_width_result, default: int = 900) -> int:
    # streamlit-container-width can return dict/number/None [web:123]
    if container_width_result is None:
        return default
    if isinstance(container_width_result, (int, float)):
        return int(container_width_result)
    if isinstance(container_width_result, dict):
        w = container_width_result.get("width")
        if isinstance(w, (int, float)):
            return int(w)
        for v in container_width_result.values():
            if isinstance(v, (int, float)):
                return int(v)
    return default


def pil_to_data_url(pil_img: Image.Image) -> str:
    """PIL -> data URL. Passing string avoids Streamlit internal image_to_url path [web:21]."""
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


st.set_page_config(page_title="Создание маски", layout="wide")
st.title("Создание маски")
st.markdown("Загрузите фото, выберите кисть и рисуйте. Пересечения не усиливают цвет в редакторе.")

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
stroke_color_solid = stroke_color  # непрозрачный (без альфы) => без усиления при перекрытии

st.sidebar.markdown("---")
blur_radius = st.sidebar.slider("Размытие маски (px)", 0, 50, 15)
mask_threshold = st.sidebar.slider("Порог маски (после blur)", 0, 255, 10)

col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    st.subheader("Редактор")

    # measure available width inside column
    cw = st_container_width(key="canvas_col_width")
    available_w_px = extract_width_px(cw, default=900)

    max_width = max(200, available_w_px - 24)

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

    # KEY FIX for Streamlit Cloud: use data-URL string as background_image [web:1]
    bg_data_url = pil_to_data_url(display_image)

    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color_solid,
        background_image=bg_data_url,   # str => bypass image_to_url path [web:21]
        update_streamlit=True,
        height=disp_h,
        width=disp_w,
        drawing_mode="freedraw",
        key="canvas_stable",
    )

with col2:
    st.subheader("Результат")

    if canvas_result.image_data is None:
        st.info("Нарисуйте область на изображении слева.")
        st.stop()

    img_data = canvas_result.image_data
    alpha = img_data[:, :, 3].astype(np.uint8)

    if np.max(alpha) <= 0:
        st.info("Нарисуйте область на изображении слева.")
        st.stop()

    # Binary mask
    mask = np.where(alpha > 0, 255, 0).astype(np.uint8)

    # Back to original size
    if scale_factor != 1.0:
        mask = cv2.resize(mask, (image.width, image.height), interpolation=cv2.INTER_NEAREST)

    # Blur if needed
    if blur_radius > 0:
        k = blur_radius * 2 + 1
        mask = cv2.GaussianBlur(mask, (k, k), blur_radius)

    mask_img = Image.fromarray(mask)

    # Preview: blackout on original
    orig_np = np.array(image).astype(np.uint8)
    sel = mask > mask_threshold
    preview = orig_np.copy()
    preview[sel] = (0, 0, 0)
    preview_img = Image.fromarray(preview)

    st.image(preview_img, caption="Превью: выделенная область — чёрная", use_container_width=True)

    buf_prev = io.BytesIO()
    preview_img.save(buf_prev, format="PNG")
    st.download_button(
        "⬇️ Скачать превью PNG",
        data=buf_prev.getvalue(),
        file_name="preview_blackout.png",
        mime="image/png",
    )

    buf_mask = io.BytesIO()
    mask_img.save(buf_mask, format="PNG")
    st.download_button(
        "⬇️ Скачать маску PNG",
        data=buf_mask.getvalue(),
        file_name="mask.png",
        mime="image/png",
    )
