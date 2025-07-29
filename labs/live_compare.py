import os                                    # Para recorrer la carpeta de embeddings y construir rutas a los archivos .pkl
import cv2                                   # OpenCV para capturar video, convertir color y dibujar sobre los rostros
import pickle                                # Para leer los embeddings serializados en archivos .pkl
import face_recognition                      # Detección y comparación de rostros basada en dlib
import matplotlib.pyplot as plt              # Para mostrar la imagen final con detecciones en ventana gráfica

# Dirección RTSP de la cámara (modificá esta línea con tus datos reales de usuario, IP y puerto)
RTSP_URL = "rtsp://usuario:contraseña@IP:PUERTO/stream1"

# Carpeta donde se almacenan los embeddings faciales registrados
EMBEDDINGS_DIR = "embeddings/"

def cargar_embeddings():
    """
    Carga todos los embeddings desde archivos .pkl presentes en EMBEDDINGS_DIR.

    Returns:
        known_face_encodings (List[np.ndarray]): vectores de características faciales.
        known_face_names (List[str]): etiquetas de cada rostro.
    """
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(EMBEDDINGS_DIR):
        if filename.endswith(".pkl"):
            filepath = os.path.join(EMBEDDINGS_DIR, filename)
            with open(filepath, "rb") as f:
                data = pickle.load(f)
                known_face_encodings.extend(data["encodings"])
                known_face_names.extend([data["name"]] * len(data["encodings"]))

    return known_face_encodings, known_face_names

def capturar_frame():
    """
    Captura un único frame desde el stream RTSP configurado.

    Returns:
        frame (np.ndarray): fotograma BGR de la cámara.
    
    Raises:
        RuntimeError: si no se logra capturar la imagen.
    """
    cap = cv2.VideoCapture(RTSP_URL)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("❌ Error al capturar imagen desde la cámara.")
    
    return frame

def comparar_y_mostrar(frame, known_face_encodings, known_face_names):
    """
    Detecta rostros en el frame y los compara con los embeddings registrados.
    Dibuja bounding boxes y etiquetas, y muestra el resultado con matplotlib.

    Args:
        frame (np.ndarray): imagen original en formato BGR.
        known_face_encodings (List[np.ndarray]): vectores faciales conocidos.
        known_face_names (List[str]): etiquetas correspondientes.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    nombres_detectados = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
        name = "Desconocido"
        if True in matches:
            matched_index = matches.index(True)
            name = known_face_names[matched_index]

        if name not in nombres_detectados or name != "Desconocido":
            nombres_detectados.append(name)

        top, right, bottom, left = face_location
        cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(rgb_frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    plt.imshow(rgb_frame)
    plt.axis("off")
    plt.title(f"Reconocimiento Facial: {', '.join(nombres_detectados) or 'Sin detecciones'}")
    plt.show()

if __name__ == "__main__":
    # Pipeline principal: carga embeddings → captura frame → ejecuta reconocimiento
    encodings, names = cargar_embeddings()
    frame = capturar_frame()
    comparar_y_mostrar(frame, encodings, names)
