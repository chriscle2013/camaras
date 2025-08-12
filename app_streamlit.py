# app.py
import streamlit as st
import cv2
import numpy as np
import requests
import time
from PIL import Image
import threading

st.set_page_config(page_title="IP Cam Viewer", layout="centered")
st.title("📷 Viewer - Cámaras IP (celular)")

# --- Sidebar: configuración ---
method = st.sidebar.selectbox("Método de lectura", ["OpenCV VideoCapture", "MJPEG (requests)"])
camera_url = st.sidebar.text_input("URL cámara (ej. http://192.168.1.26:8080/video)", value="")
cols = st.sidebar.multiselect("Modo de diseño", ["Pantalla única", "Grid (2x)"])
st.sidebar.markdown("Si la cámara requiere user:pass puedes usar: http://user:pass@IP:8080/video")

if 'running' not in st.session_state:
    st.session_state['running'] = False
if 'thread' not in st.session_state:
    st.session_state['thread'] = None

placeholder = st.empty()

# --- helpers ---
@st.cache_resource
def make_cv_capture(url):
    cap = cv2.VideoCapture(url)
    return cap

def release_cv_capture(url):
    try:
        cap = make_cv_capture(url)
        cap.release()
    except Exception:
        pass

def stream_opencv(url):
    cap = make_cv_capture(url)
    while st.session_state.get('running', False):
        if not cap.isOpened():
            time.sleep(0.5)
            continue
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.2)
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        placeholder.image(frame, use_column_width=True)
        time.sleep(0.03)
    try:
        cap.release()
    except:
        pass

def stream_mjpeg(url):
    try:
        r = requests.get(url, stream=True, timeout=10)
    except Exception as e:
        st.error(f"Error conectando: {e}")
        st.session_state['running'] = False
        return
    bytes_buf = b''
    for chunk in r.iter_content(chunk_size=1024):
        if not st.session_state.get('running', False):
            break
        if chunk:
            bytes_buf += chunk
            a = bytes_buf.find(b'\xff\xd8')  # SOI
            b = bytes_buf.find(b'\xff\xd9')  # EOI
            if a != -1 and b != -1 and b > a:
                jpg = bytes_buf[a:b+2]
                bytes_buf = bytes_buf[b+2:]
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    continue
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                placeholder.image(img, use_column_width=True)
    try:
        r.close()
    except:
        pass

def start_thread(url, method):
    if not url:
        st.warning("Introduce la URL de la cámara en el sidebar.")
        return
    if st.session_state['thread'] and st.session_state['thread'].is_alive():
        return
    st.session_state['running'] = True
    if method == "OpenCV VideoCapture":
        th = threading.Thread(target=stream_opencv, args=(url,), daemon=True)
    else:
        th = threading.Thread(target=stream_mjpeg, args=(url,), daemon=True)
    st.session_state['thread'] = th
    th.start()

def stop_stream():
    st.session_state['running'] = False
    # allow thread to exit gracefully
    time.sleep(0.5)
    # try to release resources
    try:
        release_cv_capture(camera_url)
    except:
        pass

# --- Controls ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Iniciar stream"):
        start_thread(camera_url, method)
with col2:
    if st.button("Detener"):
        stop_stream()

st.write("Estado:", "▶️ Corriendo" if st.session_state['running'] else "⏸️ Detenido")
st.write("Consejo: prueba primero en tu ordenador local con `streamlit run app.py` y la URL del celular en la misma Wi-Fi.")
