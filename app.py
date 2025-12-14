import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import io
import cv2

# Устанавливаем конфигурацию для мобильных устройств
st.set_page_config(
    page_title="Создание маски",
    layout="wide",
    initial_sidebar_state="collapsed"  # Сворачиваем sidebar на мобильных
)

# CSS для адаптивности
st.markdown("""
<style>
    /* Основные стили для мобильных */
    @media (max-width: 768px) {
        .main > div {
            padding-left: 5px !important;
            padding-right: 5px !important;
        }
        
        .stButton > button {
            width: 100% !important;
            margin: 5px 0;
        }
        
        .stDownloadButton > button {
            width: 100% !important;
            font-size: 16px !important;
            padding: 12px !important;
        }
        
        /* Увеличиваем область касания для слайдеров */
        div[data-baseweb="slider"] {
            padding: 10px 0;
        }
        
        /* Улучшаем отображение заголовков */
        h1, h2, h3 {
            font-size: 1.5em !important;
            text-align: center;
        }
    }
    
    /* Общие улучшения */
    .stSlider > div > div > div {
        background-color: #f0f2f6;
    }
    
    /* Контейнер для канваса */
    .canvas-container {
        margin: 0 auto;
        max-width: 100%;
    }
    
    /* Кнопки с большими отступами */
    .big-button {
        padding: 12px 0 !important;
        margin: 8px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Создание маски")
st.markdown("Загрузите фото и выделите область для изменения")

# Основной контейнер
main_container = st.container()

with main_container:
    # Загрузка файла с улучшенным UX
    uploaded_file = st.file_uploader(
        "📱 Выберите изображение",
        type=["png", "jpg", "jpeg"],
        help="Нажмите для выбора фото из галереи"
    )
    
    if not uploaded_file:
        st.info("👆 Загрузите изображение, чтобы начать работу")
        st.stop()

    # Загружаем изображение
    image = Image.open(uploaded_file).convert("RGB")
    
    # Адаптивный размер для мобильных
    screen_width = st.session_state.get('screen_width', 400)
    
    # Рассчитываем размеры для отображения
    max_display_width = min(600, screen_width - 40)  # Оставляем отступы
    if image.width > max_display_width:
        ratio = max_display_width / image.width
        disp_w = int(max_display_width)
        disp_h = int(image.height * ratio)
        display_image = image.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
        scale_factor = image.width / disp_w
    else:
        display_image = image
        disp_w, disp_h = image.size
        scale_factor = 1.0
    
    # Настройки в аккордеоне для экономии места
    with st.expander("⚙️ Настройки кисти", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            stroke_width = st.slider(
                "Толщина кисти",
                min_value=5,
                max_value=100,
                value=30,
                help="Размер кисти для рисования"
            )
        
        with col2:
            stroke_color = st.color_picker(
                "Цвет кисти",
                "#4E4E4E",
                help="Выберите цвет для рисования маски"
            )
        
        blur_radius = st.slider(
            "Размытие границ",
            min_value=0,
            max_value=50,
            value=15,
            help="Сглаживание краев маски"
        )
    
    # Инструкция
    st.info("✍️ Нарисуйте область на изображении ниже. Используйте палец для рисования.")
    
    # Канвас для рисования
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=display_image,
        update_streamlit=True,
        height=disp_h,
        width=disp_w,
        drawing_mode="freedraw",
        key="canvas_mobile",
        point_display_radius=0,  # Убираем точки для лучшего касания
    )
    
    # Кнопки управления
    col_bt1, col_bt2, col_bt3 = st.columns(3)
    
    with col_bt1:
        if st.button("🔄 Очистить", use_container_width=True):
            st.rerun()
    
    with col_bt2:
        if st.button("✏️ Новая кисть", use_container_width=True):
            stroke_width = 30
            st.rerun()
    
    with col_bt3:
        if st.button("💾 Сохранить", use_container_width=True):
            st.success("Маска сохранена!")
    
    # Обработка и отображение результата
    if canvas_result.image_data is not None:
        img_data = canvas_result.image_data
        alpha = img_data[:, :, 3].astype(np.uint8)
        
        if np.max(alpha) > 0:
            # Создаем маску
            mask = np.where(alpha > 0, 255, 0).astype(np.uint8)
            
            # Масштабируем к исходному размеру
            if scale_factor != 1.0:
                mask = cv2.resize(mask, (image.width, image.height), 
                                interpolation=cv2.INTER_NEAREST)
            
            # Применяем размытие если нужно
            if blur_radius > 0:
                k = blur_radius * 2 + 1
                mask = cv2.GaussianBlur(mask, (k, k), blur_radius)
            
            # Создаем изображение маски
            mask_img = Image.fromarray(mask)
            
            # Показываем превью
            st.subheader("👀 Предпросмотр маски")
            col_preview1, col_preview2 = st.columns(2)
            
            with col_preview1:
                st.image(display_image, caption="Исходное изображение", use_column_width=True)
            
            with col_preview2:
                # Показываем маску в уменьшенном размере для мобильных
                preview_size = (300, int(300 * image.height / image.width))
                mask_preview = mask_img.resize(preview_size, Image.Resampling.NEAREST)
                st.image(mask_preview, caption="Созданная маска", use_column_width=True)
            
            # Кнопка скачивания
            buf_mask = io.BytesIO()
            mask_img.save(buf_mask, format="PNG")
            
            st.download_button(
                label="📥 Скачать маску (PNG)",
                data=buf_mask.getvalue(),
                file_name="mask.png",
                mime="image/png",
                use_container_width=True,
                type="primary"
            )
        else:
            st.warning("Нарисуйте область на изображении выше")

# Добавляем скрипт для определения ширины экрана
st.markdown("""
<script>
function updateScreenWidth() {
    const width = window.innerWidth;
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: width
    }, '*');
}

// Обновляем при загрузке и изменении размера
window.addEventListener('load', updateScreenWidth);
window.addEventListener('resize', updateScreenWidth);
</script>
""", unsafe_allow_html=True)