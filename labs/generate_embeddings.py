import os                                                # Para recorrer carpetas, crear rutas y validar estructuras del dataset
import pickle                                            # Para guardar embeddings como archivos binarios .pkl (serialización rápida y reproducible)
import face_recognition                                  # Librería de reconocimiento facial basada en dlib (detección, extracción de embeddings)

# Carpeta donde se guardarán los archivos .pkl con embeddings serializados
EMBEDDINGS_DIR = "embeddings/"
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)               # Crea la carpeta si no existe

# Carpeta donde están las imágenes organizadas por persona (dataset de entrada)
DATASET_PATH = "dataset/"

def generar_embeddings():
    """
     Genera embeddings faciales para cada persona en el dataset y los guarda como .pkl.
    
    Recorre cada subcarpeta, procesa imágenes, detecta caras y guarda vectores de encodings por persona.
    """

    # Recorremos cada subcarpeta del dataset (una por persona)
    for person_name in os.listdir(DATASET_PATH):
        person_folder = os.path.join(DATASET_PATH, person_name)

        if not os.path.isdir(person_folder):
            continue                                     # Ignora archivos sueltos que no sean carpetas

        # Ruta destino para el archivo .pkl de esa persona
        person_embeddings_path = os.path.join(EMBEDDINGS_DIR, f"{person_name}.pkl")

        if os.path.exists(person_embeddings_path):
            print(f"⚠️ {person_name} ya tiene embeddings guardados. Se omite.")
            continue                                     # Evita reprocesar si ya existen embeddings

        print(f"📸 Procesando imágenes de {person_name}...")

        person_encodings = []                            # Lista de embeddings faciales acumulados

        # Procesamos cada imagen de la carpeta
        for filename in os.listdir(person_folder):
            image_path = os.path.join(person_folder, filename)

            try:
                # Carga la imagen en array NumPy
                image = face_recognition.load_image_file(image_path)

                # Detecta rostros en la imagen usando el modelo "hog" (más liviano)
                face_locations = face_recognition.face_locations(image, model="hog")

                # Extrae embeddings faciales basados en las ubicaciones detectadas
                face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)

                if face_encodings:
                    person_encodings.append(face_encodings[0])  # Guarda solo el primer rostro detectado
                    print(f"✅ Embedding generado para {filename}")
                else:
                    print(f"⚠️ No se detectó rostro en {filename}. Se omite.")

            except Exception as e:
                print(f"❌ Error procesando {filename}: {e}")  # Captura errores por imagen corrupta, formato inválido, etc.

        # Serializa y guarda el archivo .pkl si se generaron embeddings correctamente
        if person_encodings:
            with open(person_embeddings_path, "wb") as f:
                pickle.dump({"encodings": person_encodings, "name": person_name}, f)
            print(f"\n✅ Embeddings guardados en {person_embeddings_path}")

    print("\n🚀 Procesamiento completado.")

# Punto de entrada si se ejecuta como script principal
if __name__ == "__main__":
    generar_embeddings()

