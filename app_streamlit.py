import streamlit as st
import cv2
import tempfile
import os

st.set_page_config(page_title="Multi-Cámara IP", layout="wide")

st.title("📹 Visualizador de múltiples cámaras IP desde celulares")

st.write("Ingresa las direcciones IP de tus celulares (con puerto), separadas por comas. Ejemplo:")
st.code("http://192.168.0.101:8080/video, http://192.168.0.102:8080/video", language="plaintext")

ips_input = st.text_input("Direcciones IP de cámaras:")

if st.button("Conectar cámaras"):
    if not ips_input.strip():
        st.error("⚠️ Por favor ingresa al menos una IP.")
    else:
        urls = [ip.strip() for ip in ips_input.split(",")]

        for idx, url in enumerate(urls, start=1):
            st.subheader(f"📱 Cámara {idx}: {url}")

            try:
                cap = cv2.VideoCapture(url)
                if not cap.isOpened():
                    st.error(f"No se pudo conectar con la cámara {idx}")
                    continue

                ret, frame = cap.read()
                if not ret:
                    st.warning(f"No se pudo recibir imagen de la cámara {idx}")
                    cap.release()
                    continue

                # Guardar frame temporalmente para mostrar en Streamlit
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                cv2.imwrite(temp_file.name, frame)
                st.image(temp_file.name, channels="BGR", use_container_width=True)
                temp_file.close()
                os.unlink(temp_file.name)

                cap.release()

            except Exception as e:
                st.error(f"Error en cámara {idx}: {e}")
