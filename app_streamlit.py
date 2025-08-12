Aquí está el código completo y final para tu archivo app_streamlit.py. Este código incluye toda la lógica para la conexión a la cámara, la interfaz de usuario con Streamlit y la detección de movimiento.

Código Final de app_streamlit.py
Python

import streamlit as st
import cv2
import imutils
import numpy as np

# --- Título y configuración de la interfaz ---
st.title("Sistema de Vigilancia con Streamlit")
st.write("Configura la URL de tu cámara IP y presiona 'Iniciar'.")

# Campo para que el usuario ingrese la URL de la cámara
camera_url = st.text_input(
    "URL de la cámara IP", 
    value="http://192.168.1.26:8080/video", 
    help="Ingresa la dirección completa de tu cámara IP (por ejemplo: http://192.168.1.100:8080/video)"
)

# Placeholders para los botones y el video
col1, col2 = st.columns(2)
start_button = col1.button("Iniciar Vigilancia")
stop_button = col2.button("Detener Vigilancia")
video_placeholder = st.empty()

# --- Detección de movimiento ---
def detect_motion(frame, avg_frame):
    # Pre-procesamiento para detección de movimiento
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Si el frame promedio es nulo, lo inicializamos
    if avg_frame is None:
        avg_frame = gray.copy().astype("float")
        return None, avg_frame

    # Calcula la diferencia entre el frame actual y el promedio
    cv2.accumulateWeighted(gray, avg_frame, 0.5)
    frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg_frame))
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Encuentra los contornos del movimiento
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    motion_detected = False
    for c in cnts:
        # Filtra contornos pequeños para evitar falsos positivos
        if cv2.contourArea(c) > 500:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            motion_detected = True
            
    return frame, avg_frame

# --- Bucle principal de la aplicación ---
# Usamos st.session_state para controlar el estado de la app entre interacciones
if "is_running" not in st.session_state:
    st.session_state.is_running = False

if start_button:
    st.session_state.is_running = True

if stop_button:
    st.session_state.is_running = False
    
if st.session_state.is_running:
    st.write("Transmisión en vivo iniciada...")
    cap = cv2.VideoCapture(camera_url)
    avg_frame = None

    if not cap.isOpened():
        st.error("No se pudo conectar a la cámara. Verifica la URL y la conexión.")
        st.session_state.is_running = False
    else:
        while st.session_state.is_running:
            success, frame = cap.read()
            if not success:
                st.warning("Se perdió la conexión con la cámara.")
                st.session_state.is_running = False
                break

            # Procesar el frame para la detección de movimiento
            processed_frame, avg_frame = detect_motion(frame, avg_frame)
            
            # Muestra el frame en el placeholder de Streamlit
            if processed_frame is not None:
                video_placeholder.image(processed_frame, channels="BGR", use_column_width=True)
        
        cap.release()
    
if not st.session_state.is_running:
    st.write("Transmisión detenida.")
