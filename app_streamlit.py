import streamlit as st
import cv2
import imutils
import numpy as np

# Título de la aplicación
st.title("Sistema de Vigilancia con Streamlit")

# URL de la cámara IP (reemplaza esto con la IP de tu celular)
camera_url = "http://192.168.1.26:8080/video"

# Placeholder para la visualización del video
video_placeholder = st.empty()

# Botón para iniciar/detener la transmisión
start_button = st.button("Iniciar Vigilancia")
stop_button = st.button("Detener Vigilancia")

# Variables para control del estado
is_running = False
cap = None

# Función de detección de movimiento
def detect_motion(frame, avg_frame):
    # Pre-procesamiento del frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

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
        if cv2.contourArea(c) > 500: # Umbral de área del contorno
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            motion_detected = True
            
    return frame, avg_frame

# Bucle principal de la aplicación
if start_button:
    is_running = True
    st.session_state.is_running = True
    
if stop_button:
    is_running = False
    st.session_state.is_running = False
    if cap is not None:
        cap.release()

if 'is_running' in st.session_state and st.session_state.is_running:
    st.write("Transmisión en vivo iniciada...")
    cap = cv2.VideoCapture(camera_url)
    avg_frame = None

    while st.session_state.is_running:
        success, frame = cap.read()
        if not success:
            st.warning("No se pudo conectar con la cámara. Verifique la URL.")
            break

        # Opcional: Procesar el frame para la detección de movimiento
        processed_frame, avg_frame = detect_motion(frame, avg_frame)
        if processed_frame is not None:
            frame_to_show = processed_frame
        else:
            frame_to_show = frame
        
        # Muestra el frame en el placeholder de Streamlit
        video_placeholder.image(frame_to_show, channels="BGR", use_column_width=True)
    
    if 'is_running' in st.session_state and not st.session_state.is_running:
        st.write("Transmisión detenida.")
        cap.release()
