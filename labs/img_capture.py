import os                                               # Para crear carpetas y construir rutas de guardado de imágenes
import cv2                                              # OpenCV para acceder al stream de video, capturar frames y guardar imágenes
import time                                             # Para espaciar capturas con delays entre cada toma

# Dirección RTSP de la cámara (modificá esta línea con tus datos reales de usuario, IP y puerto)
RTSP_URL = "rtsp://usuario:contraseña@IP:PUERTO/stream1"

def capturar_y_guardar_foto(filename):
    """
    Captura un único fotograma desde el stream RTSP y lo guarda como imagen en disco.

    Args:
        filename (str): Ruta completa donde se guardará la imagen capturada.
    
    Returns:
        bool: True si la imagen fue capturada y guardada correctamente, False si hubo error.
    """
    cap = cv2.VideoCapture(RTSP_URL)                   # Inicializa la conexión al stream
    ret, frame = cap.read()                            # Captura el fotograma actual
    cap.release()                                      # Libera el recurso de cámara

    if ret:
        cv2.imwrite(filename, frame)                   # Guarda el fotograma como imagen JPEG
        print(f"✅ Imagen guardada: {filename}")
        return True
    else:
        print("❌ Error al capturar la imagen desde la cámara.")
        return False

def captura_automatica(person_name, num_images=20, interval=3):
    """
    🧠 Captura automáticamente múltiples imágenes desde el stream cada ciertos segundos.

    Args:
        person_name (str): Nombre de la persona, usado para nombrar carpeta e imágenes.
        num_images (int): Cantidad total de imágenes a capturar.
        interval (int): Tiempo en segundos entre cada captura.
    """
    if not person_name:
        print("⚠️ El nombre está vacío. Abortando.")
        return

    # Ruta donde se guardarán las imágenes (crea dataset/person_name si no existe)
    save_path = os.path.join("dataset", person_name)
    os.makedirs(save_path, exist_ok=True)                               # Crea carpeta si no existe

    print(f"\n📸 Iniciando captura de {num_images} imágenes cada {interval} segundos para '{person_name}'...\n")

    for i in range(num_images):
        filename = os.path.join(save_path, f"{person_name}_{i+1}.jpg")  # Construye nombre del archivo
        capturar_y_guardar_foto(filename)                               # Llama a función para capturar y guardar
        time.sleep(interval)                                            # Espera antes de la siguiente captura

    print("\n✅ Captura finalizada.")

if __name__ == "__main__":
    # Punto de entrada si se ejecuta este script como principal
    # Reemplazá "NombreDeLaPersona" por la etiqueta deseada
    captura_automatica("NombreDeLaPersona")

