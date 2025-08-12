import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Cámaras IP - Celulares", layout="wide")
st.title("📹 Visualización de múltiples cámaras IP desde celulares")

# Lista de URLs de tus celulares
# Ejemplo: "http://192.168.1.101:8080/video"
urls = {
    "Celular 1": "http://192.168.1.101:8080/video",
    "Celular 2": "http://192.168.1.102:8080/video",
    "Celular 3": "http://192.168.1.103:8080/video"
}

# Número de columnas en pantalla
num_cols = 2
cols = st.columns(num_cols)

for idx, (nombre, url) in enumerate(urls.items()):
    col = cols[idx % num_cols]  # Distribuir en columnas

    try:
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        cap.release()

        if ret:
            # Convertir a RGB para mostrar en Streamlit
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            col.image(frame, caption=nombre, use_container_width=True)
        else:
            col.error(f"No se pudo conectar a {nombre}")
    except Exception as e:
        col.error(f"Error con {nombre}: {e}")
