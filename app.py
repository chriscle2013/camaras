from flask import Flask, render_template, Response
import cv2
import imutils

app = Flask(__name__)

# URL de la cámara IP (reemplaza esto con la IP de tu celular)
camera_url = "http://192.168.1.100:8080/video"

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    cap = cv2.VideoCapture(camera_url)
    
    # Bucle para leer los frames de la cámara
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Opcional: Detección de movimiento
        # Puedes agregar aquí el código para detectar movimiento con OpenCV

        # Codifica el frame para la transmisión web
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
