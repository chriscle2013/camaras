# Usa una imagen base con Python 3.9
FROM python:3.9-slim-buster

# Instala las dependencias del sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libglib2.0-0 \
    ffmpeg

# Copia los archivos de tu app
COPY . /app
WORKDIR /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expon el puerto y corre la app de Streamlit
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app_streamlit.py"]
