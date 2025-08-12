# Usamos una imagen base oficial de Python.
# Python 3.9 es una versión estable y compatible con OpenCV.
FROM python:3.9-slim

# Instala las dependencias del sistema necesarias para OpenCV.
# El comando `libgl1` es lo que te falta y lo que causa el error `libGL.so.1`.
# `libsm6`, `libxext6`, `libxrender1` y `libglib2.0-0` son también necesarias.
RUN apt-get update && apt-get install -y \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libglib2.0-0

# Copia el archivo requirements.txt y lo instala.
# Esto es más eficiente, ya que no se reinstalan si cambian los archivos de la app.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la app.
COPY . .

# Define el comando para correr la app de Streamlit.
EXPOSE 8501
CMD streamlit run app_streamlit.py
