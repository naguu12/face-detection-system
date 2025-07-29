import cv2                                       # OpenCV para capturar video en tiempo real y convertir color (BGR → RGB)
import time                                      # Para controlar delays entre fotogramas y evitar saturar el stream
from PIL import Image                            # Usado para mostrar el fotograma como imagen RGB en ventana externa

# Dirección RTSP de la cámara (modificá esta línea con tus datos reales de usuario, IP y puerto)
rtsp_url = "rtsp://usuario:contraseña@IP:PUERTO/stream1"

# Inicializa el objeto de captura con la URL RTSP especificada
cap = cv2.VideoCapture(rtsp_url)

# Verificamos si la conexión al stream fue exitosa
if not cap.isOpened():
    print("❌ No se pudo conectar al stream.")
else:
    print("✅ Stream en vivo. Presioná Ctrl+C para frenar.")
    
    try:
        # Captura una cantidad definida de frames (en este caso, sólo uno)
        for _ in range(1):                       # Cambiar a mayor valor si querés capturar más de un frame
            ret, frame = cap.read()              # Captura el fotograma actual

            if not ret:
                print("⚠️ No se pudo leer el fotograma.")
                break

            # Convertimos de formato BGR (OpenCV) a RGB (PIL)
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Transformamos el array NumPy en imagen PIL para mostrarla
            pil_img = Image.fromarray(img_rgb)
            pil_img.show()                       # Abre una ventana temporal con el frame capturado

            time.sleep(0.1)                      # Espera corta para controlar el refresco del stream

    except KeyboardInterrupt:
        # 🛑 Permite salir con Ctrl+C de forma limpia
        print("\n🛑 Stream detenido manualmente.")

    finally:
        cap.release()                            # Libera el recurso de la cámara para no bloquear otras instancias

