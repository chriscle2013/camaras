import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Multi Cámaras IP", layout="wide")

st.title("📹 Visualización de Múltiples Cámaras IP con Celulares")
st.markdown("""
Escribe las direcciones de las cámaras en formato:
http://IP_DEL_CELULAR:8080/video

php
Copiar
Editar
Una por línea.
""")

# Entrada de varias URLs
urls_input = st.text_area("Direcciones de cámaras:", height=150, placeholder="http://192.168.0.101:8080/video\nhttp://192.168.0.102:8080/video")
urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

if st.button("Iniciar transmisión") and urls:
    cols = st.columns(len(urls))  # Una columna por cámara

    for i, url in enumerate(urls):
        with cols[i]:
            st.subheader(f"Cámara {i+1}")
            try:
                cap = cv2.VideoCapture(url)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(frame, caption=f"Cámara {i+1}", use_container_width=True)
                else:
                    st.error(f"No se pudo conectar a {url}")
                cap.release()
            except Exception as e:
                st.error(f"Error con {url}: {e}")
else:
    st.info("Introduce las direcciones de las cámaras y pulsa **Iniciar transmisión**.")
