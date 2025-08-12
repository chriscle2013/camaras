import streamlit as st
import cv2
import numpy as np
import time
import requests

st.set_page_config(page_title="Multi IP Cam (ngrok compatible)", layout="wide")
st.title("📹 Multi Cámara - Tiempo real (soporta ngrok)")

st.markdown("""
Pega aquí las URLs (una por línea). Pueden ser:
- URLs ngrok tipo `https://abcd-1234.ngrok-free.app/video`
- URLs locales tipo `http://192.168.0.15:8080/video` (solo si Streamlit corre en la misma LAN)
""")

# --- Inputs ---
urls_text = st.text_area("URLs de cámaras (una por línea):", height=140, placeholder="https://abcd-1234.ngrok-free.app/video\nhttps://efgh-5678.ngrok-free.app/video")
method = st.selectbox("Método preferido (prueba cuál funciona mejor para tu stream):", ["OpenCV VideoCapture", "MJPEG (requests)"])
fps = st.slider("FPS max aprox.", 1, 15, 5)
cols_count = st.slider("Columnas en grid (visual)", 1, 4, 2)

start = st.button("▶️ Iniciar")
stop = st.button("⏹️ Detener")

# --- session state ---
if "running" not in st.session_state:
    st.session_state.running = False
if "placeholders" not in st.session_state:
    st.session_state.placeholders = []

# --- control botones ---
if start and urls_text.strip():
    st.session_state.running = True
    # construir lista de urls
    st.session_state.urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
    # reset placeholders
    st.session_state.placeholders = []
if stop:
    st.session_state.running = False

# --- utilities ---
def try_read_opencv_once(url, timeout_sec=5):
    """Intenta leer un frame con OpenCV VideoCapture (con timeout simple)."""
    cap = cv2.VideoCapture(url)
    start_t = time.time()
    frame = None
    while time.time() - start_t < timeout_sec:
        ret, f = cap.read()
        if ret and f is not None:
            frame = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            break
        time.sleep(0.05)
    try:
        cap.release()
    except:
        pass
    return frame

def try_read_mjpeg_once(url, timeout_sec=5):
    """Intenta leer un frame de MJPEG usando requests (extrae un JPEG)."""
    try:
        r = requests.get(url, stream=True, timeout=timeout_sec)
    except Exception:
        return None
    bytes_buf = b""
    start_t = time.time()
    for chunk in r.iter_content(chunk_size=1024):
        if time.time() - start_t > timeout_sec:
            break
        if chunk:
            bytes_buf += chunk
            a = bytes_buf.find(b'\xff\xd8')
            b = bytes_buf.find(b'\xff\xd9')
            if a != -1 and b != -1 and b > a:
                jpg = bytes_buf[a:b+2]
                bytes_buf = bytes_buf[b+2:]
                arr = np.frombuffer(jpg, dtype=np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                try:
                    r.close()
                except:
                    pass
                if img is not None:
                    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    try:
        r.close()
    except:
        pass
    return None

# --- área de estado ---
status_placeholder = st.empty()

# --- loop principal controlado por Streamlit ---
if st.session_state.running and st.session_state.get("urls"):
    urls = st.session_state["urls"]
    n = len(urls)

    # preparar grid de placeholders (si no existen)
    if not st.session_state.placeholders:
        for i in range(n):
            # crear columnas en grid
            cols = st.columns(cols_count)
            # reuse modulo para posicion
            ph = cols[i % cols_count].empty()
            st.session_state.placeholders.append(ph)

    # mostrar mientras running
    status_placeholder.info(f"Transmisión ON — {n} cámaras — Presiona ⏹️ para detener")
    try:
        while st.session_state.running:
            loop_start = time.time()
            for i, url in enumerate(urls):
                ph = st.session_state.placeholders[i]
                frame = None
                # intentar método preferido primero
                if method == "OpenCV VideoCapture":
                    frame = try_read_opencv_once(url, timeout_sec=1.5)
                    # fallback a MJPEG si OpenCV falla
                    if frame is None:
                        frame = try_read_mjpeg_once(url, timeout_sec=1.5)
                else:
                    frame = try_read_mjpeg_once(url, timeout_sec=1.5)
                    if frame is None:
                        frame = try_read_opencv_once(url, timeout_sec=1.5)

                if frame is not None:
                    ph.image(frame, channels="RGB", use_container_width=True)
                else:
                    ph.warning(f"No hay imagen:\n{url}")

            # controlar FPS aproximado sin bloquear la interfaz demasiado
            elapsed = time.time() - loop_start
            sleep_for = max(0, (1.0 / fps) - elapsed)
            time.sleep(sleep_for)

            # si el usuario detiene desde otra pestaña o acción
            if not st.session_state.running:
                break
    except st.script_runner.StopException:
        # usuario cerró sesión o Streamlit reinició
        st.session_state.running = False
    except Exception as e:
        st.error(f"Error en loop de streaming: {e}")
        st.session_state.running = False

else:
    status_placeholder.info("Introduce URLs (una por línea) y pulsa ▶️ Iniciar")
