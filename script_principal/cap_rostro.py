# === IMPORTS ===
import cv2                                                # Captura y procesamiento de video en tiempo real
import os                                                 # Manejo de directorios y archivos
import time                                               # Control de tiempo y delays
import pickle                                             # Serialización y deserialización de datos (embeddings, etc.)
import threading                                          # Ejecución concurrente (notificación, procesamiento paralelo)
import shutil                                             # Operaciones de archivo (mover, copiar, eliminar)
import requests                                           # Envío de datos HTTP (notificaciones externas, si aplica)
import face_recognition                                   # Detección y reconocimiento facial basado en deep learning
import sys                                                # Acceso a parámetros del sistema y manipulación de flujo de ejecución
import subprocess                                         # Usado para lanzar comandos externos, ej: actualización de embeddings vía script con argumentos (--generar nombre)
from datetime import datetime, timedelta                  # Timestamps y control de ventanas temporales

# Telegram Bot (para notificar rostro detectado)
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === CONFIGURACIÓN DEL SISTEMA ===
TELEGRAM_TOKEN = "<TOKEN>"                               # Token privado del bot de Telegram
CHAT_ID = "<ID_DEL_CHAT>"                                # ID del chat donde se enviarán las alertas
CAMARA_RTSP = "<URL_RTSP>"                               # Dirección RTSP de la cámara IP
DELAY_NOTIFICACION_MIN = 5                               # Delay mínimo entre notificaciones (en minutos) para un mismo rostro

# === ESTRUCTURA DE DIRECTORIOS (se crean si no existen) ===
dataset_dir = 'dataset'                                  # Almacén de imágenes etiquetadas
embeddings_dir = 'embeddings'                            # Directorio donde se guardan los vectores de rostro
temp_dir = 'temp_unknown'                                # Imágenes temporales de rostros no reconocidos

# Crear directorios si no existen
os.makedirs(dataset_dir, exist_ok=True)
os.makedirs(embeddings_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)

# === VARIABLES DE REFERENCIA ===
known_face_encodings = []                                # Lista de vectores de rostros conocidos
known_face_names = []                                    # Nombres asociados a cada rostro


def cargar_embeddings():
    """
    Carga los vectores faciales (embeddings) previamente almacenados en archivos .pkl.
    Actualiza las listas globales de 'known_face_encodings' y 'known_face_names'.
    """
    known_face_encodings.clear()
    known_face_names.clear()
    
    for archivo in os.listdir(embeddings_dir):
        if archivo.endswith(".pkl"):
            with open(os.path.join(embeddings_dir, archivo), "rb") as f:
                data = pickle.load(f)
                known_face_encodings.extend(data["encodings"])
                known_face_names.extend([data["name"]] * len(data["encodings"]))

# Inicializa la base de rostros conocidos desde el disco
cargar_embeddings()


# === ESTADOS DEL SISTEMA ===
esperando_nombre = False                     # Flag cuando se espera un nombre por parte del usuario
procesando_desconocido = None                # Rostro no reconocido en procesamiento activo
cola_desconocidos = []                       # Cola de rostros desconocidos para verificar posteriormente
contador_desconocidos = 1                    # ID incremental para etiquetar rostros desconocidos
deteccion_activa = True                      # Flag para habilitar o pausar la detección
ultima_notificacion = {}                     # Mapeo de última notificación por rostro
encodings_desconocidos_vivos = []            # Lista de vectores faciales recientes sin reconocimiento
fecha_contador = datetime.now().date()       # Fecha actual para reiniciar contador diario

# ========================== FUNCIONES ==========================
def capturar_imagen(ruta):
    """
    Captura un frame desde la cámara RTSP, detecta rostro y lo guarda opcionalmente.
    Retorna el rostro recortado en formato imagen o None si no hay detección.
    """
    cap = cv2.VideoCapture(CAMARA_RTSP)                          # Inicializa la captura de la cámara IP
    ret, frame = cap.read()                                      # Lee un frame
    cap.release()                                                # Libera el recurso de video

    if not ret or frame is None:
        return None                                              # Falla en la captura, se retorna vacío

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)                 # Conversión a RGB (requerido por face_recognition)
    locs = face_recognition.face_locations(rgb, model="hog")     # Detecta rostro usando modelo HOG (rápido y CPU-friendly)

    if not locs:
        print("[⚠️] No se detectó rostro, se omite el frame.")
        return None                                              # Sin detección facial, se ignora

    top, right, bottom, left = locs[0]                           # Extrae coordenadas del primer rostro
    rostro = frame[top:bottom, left:right]                       # Recorta el rostro del frame original

    if ruta:
        cv2.imwrite(ruta, rostro)                                # Guarda el rostro en disco si se indica ruta

    return rostro                                                # Devuelve el rostro recortado

def enviar_desconocido_telegram(desconocido):
    """
    Envía la primera imagen del rostro desconocido detectado vía Telegram.
    Incluye fecha/hora de detección y consulta al usuario si lo reconoce.
    """
    primera_img = desconocido["imagenes"][0]                      # Imagen del rostro desconocido
    mensaje = f"🕵️ Se detectó una persona desconocida ({desconocido['id']}) el {desconocido['hora'].strftime('%d/%m/%Y %H:%M:%S')}"
    pregunta = "❓ ¿Conocés a esta persona? (Sí / No)"

    with open(primera_img, "rb") as img:
        # Envía la foto con un mensaje informativo
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                      data={"chat_id": CHAT_ID, "caption": mensaje},
                      files={"photo": img})

    # Envía la pregunta como mensaje separado
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": pregunta})


def generar_embeddings_para(nombre):
    """
    Genera vectores faciales (embeddings) a partir de imágenes de un nombre dado.
    Guarda los vectores en un archivo .pkl y actualiza la base.
    """
    carpeta = os.path.join(dataset_dir, nombre)
    encodings = []

    for filename in sorted(os.listdir(carpeta)):
        path = os.path.join(carpeta, filename)
        try:
            image = face_recognition.load_image_file(path)
            if image is None or image.size == 0:
                print(f"[⛔] Imagen vacía o corrupta: {filename}")
                continue

            locs = face_recognition.face_locations(image, model="hog")
            encs = face_recognition.face_encodings(image, locs)

            if encs:
                encodings.append(encs[0])
                print(f"[✅] Embedding generado para {filename}")
            else:
                print(f"[⚠️] No se detectó rostro en {filename}, se omite.")
        except Exception as e:
            print(f"[❌] Error en {filename}: {e}")

    if not encodings:
        print(f"[⛔] No se generaron embeddings para {nombre}.")
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": f"⚠️ No se pudieron generar embeddings para {nombre}."}
        )
        return

    try:
        path_pkl = os.path.join(embeddings_dir, f"{nombre}.pkl")
        with open(path_pkl, "wb") as f:
            pickle.dump({"encodings": encodings, "name": nombre}, f)

        cargar_embeddings()  # Recarga la base con el nuevo rostro
        print(f"[📦] Embeddings guardados en {path_pkl}")
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": f"✅ {nombre} agregado correctamente."}
        )
    except Exception as e:
        print(f"[💥] Error al guardar .pkl: {e}")
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": f"❌ No se pudo guardar el archivo para {nombre}."}
        )

def deteccion():
    """
    Loop principal de vigilancia. Captura frames, detecta rostros,
    compara con base de conocidos y gestiona desconocidos (almacenamiento + notificación).
    """
    global contador_desconocidos, procesando_desconocido, encodings_desconocidos_vivos, fecha_contador

    ultima_carga = time.time()                           # Marca de última recarga de embeddings

    while True:
        if not deteccion_activa:
            time.sleep(1)                                # Pausa si el sistema está desactivado
            continue

        # Recarga periódica de base de rostros (embeddings)
        if time.time() - ultima_carga > 10:
            cargar_embeddings()
            print("[🔁] Embeddings actualizados en hilo de detección")
            ultima_carga = time.time()

        ahora = datetime.now()
        hoy = datetime.now().date()

        # Reinicio diario del contador de desconocidos
        if hoy != fecha_contador:
            contador_desconocidos = 1
            fecha_contador = hoy

        # Captura imagen y guarda frame temporal
        path_img = os.path.join(temp_dir, "frame.jpg")
        frame = capturar_imagen(path_img)
        if frame is None:
            continue

        # Detección y extracción de características del rostro
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        encs = face_recognition.face_encodings(rgb, locs)

        for i, enc in enumerate(encs):
            # Comparación contra rostros conocidos
            matches = face_recognition.compare_faces(known_face_encodings, enc, tolerance=0.4)
            if True in matches:
                idx = matches.index(True)
                name = known_face_names[idx]
                ultima = ultima_notificacion.get(name)

                # Notifica si no fue detectado recientemente
                if not ultima or (ahora - ultima > timedelta(minutes=DELAY_NOTIFICACION_MIN)):
                    mensaje = f"✅ {name} fue detectado el {ahora.strftime('%d/%m/%Y %H:%M:%S')}"
                    with open(path_img, "rb") as img:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                                      data={"chat_id": CHAT_ID, "caption": mensaje},
                                      files={"photo": img})
                    ultima_notificacion[name] = ahora

            else:
                # Verifica si el rostro ya fue detectado como desconocido recientemente
                es_repetido = False
                for enc_vivo in encodings_desconocidos_vivos:
                    distancia = face_recognition.face_distance([enc_vivo], enc)[0]
                    if distancia < 0.4:
                        es_repetido = True
                        break
                if es_repetido:
                    continue

                # Inicializa carpeta para nuevo rostro desconocido
                desconocido_id = f"desconocido_{contador_desconocidos}"
                carpeta = os.path.join(temp_dir, desconocido_id)
                os.makedirs(carpeta, exist_ok=True)
                fotos = []
                encoding_objetivo = enc  # 🧠 Para seguimiento por identidad

                # Captura 20 imágenes espaciadas para ese rostro
                for j in range(20):
                    frame_captura = capturar_imagen(None)
                    if frame_captura is None:
                        continue

                    rgb_j = cv2.cvtColor(frame_captura, cv2.COLOR_BGR2RGB)
                    locs_j = face_recognition.face_locations(rgb_j)
                    encs_j = face_recognition.face_encodings(rgb_j, locs_j)

                    rostro_encontrado = False
                    for loc_j, enc_j in zip(locs_j, encs_j):
                        distancia = face_recognition.face_distance([encoding_objetivo], enc_j)[0]
                        if distancia < 0.4:
                            top, right, bottom, left = loc_j
                            rostro = frame_captura[top:bottom, left:right]
                            img_path = os.path.join(carpeta, f"{desconocido_id}_{j+1}.jpg")
                            cv2.imwrite(img_path, rostro)
                            fotos.append(img_path)
                            rostro_encontrado = True
                            break

                    if not rostro_encontrado:
                        print(f"[⚠️] No se encontró rostro objetivo en frame {j+1}")
                    time.sleep(2)

                # Validación de cantidad mínima de imágenes antes de continuar
                if len(fotos) < 3:
                    print(f"[🗑️] Carpeta {desconocido_id} descartada por baja cantidad de imágenes ({len(fotos)} capturas)")
                    shutil.rmtree(carpeta, ignore_errors=True)
                    continue

                # Registra rostro desconocido y encola para procesar
                encodings_desconocidos_vivos.append(encoding_objetivo)
                cola_desconocidos.append({
                    "id": desconocido_id,
                    "encodings": [encoding_objetivo],
                    "imagenes": fotos,
                    "hora": ahora
                })

                # Inicia proceso de notificación si no hay otro activo
                if procesando_desconocido is None:
                    procesando_desconocido = cola_desconocidos.pop(0)
                    enviar_desconocido_telegram(procesando_desconocido)

                contador_desconocidos += 1

        time.sleep(1)                       # Espera breve antes de procesar el siguiente frame 

async def recibir_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Gestiona la interacción Telegram tras la detección de rostro desconocido.
    - Si el usuario responde "Sí", se activa espera de nombre.
    - Si el usuario responde con un nombre, las imágenes se etiquetan y se actualizan embeddings.
    - Si el usuario responde "No", se descartan las imágenes y se limpia el estado.
    """

    global esperando_nombre, procesando_desconocido, encodings_desconocidos_vivos

    mensaje = update.message.text.lower().strip()

    if esperando_nombre and procesando_desconocido:
        nombre = mensaje.capitalize()
        carpeta_nueva = os.path.join(dataset_dir, nombre)
        os.makedirs(carpeta_nueva, exist_ok=True)

        existentes = set(os.listdir(carpeta_nueva))
        contador = len([f for f in existentes if f.endswith(".jpg") and f.startswith(nombre)])

        for i, path in enumerate(procesando_desconocido["imagenes"]):
            nueva_path = os.path.join(carpeta_nueva, f"{nombre}_{contador + i + 1}.jpg")
            shutil.move(path, nueva_path)

        carpeta_vieja = os.path.join(temp_dir, procesando_desconocido["id"])
        if os.path.exists(carpeta_vieja):
            shutil.rmtree(carpeta_vieja)

        await update.message.reply_text(f"📂 Nuevas imágenes añadidas para {nombre}. Actualizando embeddings...")

        subprocess.Popen(["python", __file__, "--generar", nombre])

        for _ in range(20):
            path_pkl = os.path.join(embeddings_dir, f"{nombre}.pkl")
            if os.path.exists(path_pkl):
                cargar_embeddings()
                print(f"[🔁] Embeddings actualizados en memoria para {nombre}")
                break
            time.sleep(0.5)

        # Limpiar buffer de encodings vivos
        encodings_desconocidos_vivos = [
            e for e in encodings_desconocidos_vivos
            if all(face_recognition.face_distance([e], enc)[0] > 0.4
                   for enc in procesando_desconocido["encodings"])
        ]

        procesando_desconocido = None
        esperando_nombre = False

        if cola_desconocidos:
            procesando_desconocido = cola_desconocidos.pop(0)
            enviar_desconocido_telegram(procesando_desconocido)

    elif mensaje == "no" and procesando_desconocido:
        carpeta = os.path.join(temp_dir, procesando_desconocido["id"])
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
        await update.message.reply_text("🗑️ Imágenes descartadas.")
        
        # Limpiar buffer de encodings vivos
        encodings_desconocidos_vivos = [
            e for e in encodings_desconocidos_vivos
            if all(face_recognition.face_distance([e], enc)[0] > 0.4
                   for enc in procesando_desconocido["encodings"])
        ]

        procesando_desconocido = None
        esperando_nombre = False

        if cola_desconocidos:
            procesando_desconocido = cola_desconocidos.pop(0)
            enviar_desconocido_telegram(procesando_desconocido)

    elif mensaje in ["sí", "si"]:
        if procesando_desconocido:
            esperando_nombre = True
            await update.message.reply_text("✏️ Ingresá el nombre de la persona:")
    else:
        await update.message.reply_text("🤖 Respondé con 'Sí', 'No' o el nombre para continuar.")

# Comando /start del bot: envía mensaje de bienvenida
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot listo. Detectando personas...")

# Modo CLI: permite generar embeddings manualmente (ej: python script.py --generar Lionel), solo si se requiere uso manual
if len(sys.argv) == 3 and sys.argv[1] == "--generar":
    generar_embeddings_para(sys.argv[2])
    sys.exit(0)

# Arranque del sistema: detección + bot Telegram
if __name__ == "__main__":
    threading.Thread(target=deteccion, daemon=True).start()   # Hilo para vigilancia facial

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))           # Handler para /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mensaje))  # Mensajes normales
    app.run_polling()                                         # Inicia escucha de mensajes Telegram        