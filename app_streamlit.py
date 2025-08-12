import streamlit as st
import cv2
import numpy as np
import requests
import time

st.set_page_config(page_title="IP Cam Viewer", layout="centered")
st.title("📷 Viewer - Cámaras IP (celular)")

# Sidebar
method = st.sidebar.selectbox("Método de lectura", ["OpenCV VideoCapture", "MJPEG (requests)"])
camera_url = st.sidebar.text_input(
    "URL de la cámara",
    placeholder="Ej: http://192.168.1.100:8080/video o https://xxxx.ngrok-free.app/video"
)
fps = st.sidebar.slider("FPS máx.", 1, 30, 10)

start_button = st.sidebar.button("▶️ Iniciar")
stop_button = st.sidebar.button("⏹️ Detener")

# Estado en session_state
if "running" not in st.session_state:
    st.session_state.running = False

# --- Funciones ---
def read_frame_opencv(url):
    """Lee un solo frame usando OpenCV."""
    cap = cv2.VideoCapture(url)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def read_frame_mjpeg(url):
    """Lee un solo frame desde un stream MJPEG."""
    try:
        r = requests.get(url, stream=True, timeout=5)
        bytes_buf = b''
        for chunk in r.iter_content(chunk_size=1024):
            bytes_buf += chunk
            a = bytes_buf.find(b'\xff\xd8')  # JPEG start
            b = bytes_buf.find(b'\xff\xd9')  # JPEG end
            if a != -1 and b != -1:
                jpg = bytes_buf[a:b+2]
                bytes_buf = bytes_buf[b+2:]
                img = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
                r.close()
                if img is not None:
                    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except:
        return None
    return None

# --- Botones ---
if start_button and camera_url:
    st.session_state.running = True
if stop_button:
    st.session_state.running = False

# --- Área de video ---
video_placeholder = st.empty()

# --- Bucle controlado por Streamlit ---
if st.session_state.running and camera_url:
    while st.session_state.running:
        if method == "OpenCV VideoCapture":
            frame = read_frame_opencv(camera_url)
        else:
            frame = read_frame_mjpeg(camera_url)

        if frame is not None:
            video_placeholder.image(frame, channels="RGB", use_container_width=True)
        else:
            st.warning("No se pudo leer el frame. Verifica la URL o la conexión.")

        time.sleep(1 / fps)
else:
    st.info("Introduce la URL y pulsa ▶️ Iniciar para ver el stream.")
