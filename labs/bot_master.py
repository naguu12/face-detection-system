# ========================== IMPORTS Y SETUP ==========================
import cv2                     # OpenCV: captura y manipulación de imágenes/video, dibuja sobre frames

import os                      # Manejo de rutas, nombres de archivo y operaciones sobre el sistema de archivos

import time                    # Medición de tiempo y delays, útil para timestamps y control de flujo

import pickle                  # Serialización y deserialización de objetos Python (embeddings, configuración, etc.)

import threading               # Ejecución paralela mediante hilos (ideal para tareas concurrentes como video + Telegram)

import shutil                  # Copia, movimiento y limpieza de archivos/directorios (gestión de estado del sistema)

import requests                # Cliente HTTP para hacer llamadas a APIs REST (enviar datos, recibir respuestas)

import face_recognition        # Detección y comparación de rostros; basado en dlib + modelos preentrenados

import nest_asyncio            # Parchea el loop async para permitir reentrancia en entornos como Jupyter o Telegram bot

from datetime import datetime, timedelta  # Utilidades para manejo de fechas, tiempos y deltas temporales

from telegram import Update    # Objeto que representa el mensaje recibido por el bot (texto, imagen, etc.)

from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters  
#  Componentes del framework de Telegram:
# - Application: clase principal del bot (loop + configuración)
# - CommandHandler: responde a comandos como /start, /foto
# - MessageHandler: gestiona mensajes genéricos (texto, foto, etc.)
# - ContextTypes: proporciona contexto adicional a handlers
# - filters: permite filtrar tipos de mensajes (texto, imagen, comando, etc.)


# ========================== CONFIGURACIÓN ==========================
TELEGRAM_TOKEN = "TU_TELEGRAM_TOKEN_AQUI"                        # Reemplazar con token real o cargar desde archivo .env
CHAT_ID = "TU_CHAT_ID_AQUI"                                      # ID del chat al que enviar mensajes
CAMARA_RTSP = "rtsp://USUARIO:CLAVE@IP:PUERTO/STREAM"            # URL RTSP genérica, parametrizable
DELAY_NOTIFICACION_MIN = 5                                       # Tiempo de espera para detectar a la misma persona

dataset_dir = 'dataset'
embeddings_dir = 'embeddings'
temp_dir = 'temp_unknown'
os.makedirs(dataset_dir, exist_ok=True)
os.makedirs(embeddings_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)

known_face_encodings = []
known_face_names = []

def cargar_embeddings():
    known_face_encodings.clear()
    known_face_names.clear()
    for archivo in os.listdir(embeddings_dir):
        if archivo.endswith(".pkl"):
            with open(os.path.join(embeddings_dir, archivo), "rb") as f:
                data = pickle.load(f)
                known_face_encodings.extend(data["encodings"])
                known_face_names.extend([data["name"]] * len(data["encodings"]))

cargar_embeddings()

# ========================== ESTADOS ==========================
esperando_nombre = False
procesando_desconocido = None
cola_desconocidos = []
contador_desconocidos = 1
deteccion_activa = True
ultima_notificacion = {}

# ========================== FUNCIONES ==========================
def capturar_imagen(ruta):
    cap = cv2.VideoCapture(CAMARA_RTSP)
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite(ruta, frame)
        return frame
    return None

def enviar_desconocido_telegram(desconocido):
    primera_img = desconocido["imagenes"][0]
    mensaje = f"🕵️ Se detectó una persona desconocida ({desconocido['id']}) el {desconocido['hora'].strftime('%d/%m/%Y %H:%M:%S')}"
    pregunta = "❓ ¿Conocés a esta persona? (Sí / No)"

    with open(primera_img, "rb") as img:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                      data={"chat_id": CHAT_ID, "caption": mensaje},
                      files={"photo": img})

    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": pregunta})

def deteccion():
    global contador_desconocidos, procesando_desconocido

    while True:
        if not deteccion_activa:
            time.sleep(1)
            continue

        ahora = datetime.now()
        path_img = os.path.join(temp_dir, "frame.jpg")
        frame = capturar_imagen(path_img)
        if frame is None:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locs = face_recognition.face_locations(rgb)
        encs = face_recognition.face_encodings(rgb, locs)

        nombres = []
        nuevos_desconocidos = []

        for enc in encs:
            matches = face_recognition.compare_faces(known_face_encodings, enc, tolerance=0.4)
            name = "Desconocido"
            if True in matches:
                idx = matches.index(True)
                name = known_face_names[idx]
            else:
                nuevos_desconocidos.append(enc)
            if name not in nombres:
                nombres.append(name)    

        for name in nombres:
            ultima = ultima_notificacion.get(name)
            if not ultima or (ahora - ultima > timedelta(minutes=DELAY_NOTIFICACION_MIN)):
                if name == "Desconocido":
                    desconocido_id = f"desconocido_{contador_desconocidos}"
                    carpeta = os.path.join(temp_dir, desconocido_id)
                    os.makedirs(carpeta, exist_ok=True)

                    fotos = []
                    for i in range(20):
                        img_path = os.path.join(carpeta, f"{desconocido_id}_{i+1}.jpg")
                        capturar_imagen(img_path)
                        fotos.append(img_path)
                        time.sleep(2)

                    cola_desconocidos.append({
                        "id": desconocido_id,
                        "encodings": nuevos_desconocidos,
                        "imagenes": fotos,
                        "hora": ahora
                    })

                    if procesando_desconocido is None:
                        procesando_desconocido = cola_desconocidos.pop(0)
                        enviar_desconocido_telegram(procesando_desconocido)

                    contador_desconocidos += 1

                else:
                    mensaje = f"✅ {name} fue detectado el {ahora.strftime('%d/%m/%Y %H:%M:%S')}"
                    with open(path_img, "rb") as img:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                                      data={"chat_id": CHAT_ID, "caption": mensaje},
                                      files={"photo": img})
                ultima_notificacion[name] = ahora

        time.sleep(1)

async def recibir_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global esperando_nombre, procesando_desconocido

    mensaje = update.message.text.lower().strip()

    if esperando_nombre and procesando_desconocido:
        nombre = mensaje.capitalize()
        carpeta_vieja = os.path.join(temp_dir, procesando_desconocido["id"])
        carpeta_nueva = os.path.join(dataset_dir, nombre)
        os.makedirs(carpeta_nueva, exist_ok=True)

        for i, path in enumerate(procesando_desconocido["imagenes"]):
            nueva_path = os.path.join(carpeta_nueva, f"{nombre}_{i+1}.jpg")
            shutil.move(path, nueva_path)
                
        # ✅ Eliminar la carpeta vacía en temp_unknown
        if os.path.exists(carpeta_vieja):
            os.rmdir(carpeta_vieja)

        embeddings = []
        for filename in os.listdir(carpeta_nueva):
            image = face_recognition.load_image_file(os.path.join(carpeta_nueva, filename))
            locs = face_recognition.face_locations(image)
            encs = face_recognition.face_encodings(image, locs)
            if encs:
                embeddings.append(encs[0])

        with open(os.path.join(embeddings_dir, f"{nombre}.pkl"), "wb") as f:
            pickle.dump({"encodings": embeddings, "name": nombre}, f)

        cargar_embeddings()
        await update.message.reply_text(f"✅ {nombre} agregado correctamente.")

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot listo. Detectando personas...")

async def iniciar_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mensaje))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

# ========================== EJECUCIÓN FINAL ==========================
if __name__ == "__main__":
    threading.Thread(target=deteccion, daemon=True).start()

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mensaje))

    app.run_polling()


