# 👁️‍🗨️ face_detection_system

Sistema de reconocimiento facial en tiempo real conectado con Telegram. Permite la detección de personas conocidas y desconocidas, con captura automática de rostros, generación de embeddings y aprendizaje asistido desde el chat.

---

## 📌 Descripción

Este sistema utiliza una cámara IP para capturar imágenes en tiempo real, detecta rostros usando `face_recognition`, y compara con una base de datos local. Si detecta una persona desconocida, toma múltiples imágenes, las envía a un chat de Telegram y permite decidir si se trata de alguien conocido. En ese caso, se actualiza el modelo sin reiniciar el sistema.

---

## 🗂️ Estructura del Proyecto

face_detection_system/
├── embeddings/              # Archivos .pkl con embeddings de cada persona
├── dataset/                 # Imágenes recortadas (solo rostros) por persona
├── temp_unknown/            # Imágenes temporales de personas desconocidas
├── cap_rostro.py            # Script principal del sistema
├── README.md                # Este archivo
└── requirements.txt         # Dependencias del proyecto

---

## 🧠 Componentes Principales

### 🔹 Captura y Procesamiento
- Captura de imágenes desde cámara IP (RTSP)
- Recorte automático al rostro
- Carga de embeddings previamente guardados

### 🔹 Detección y Reconocimiento
- Reconocimiento facial con `face_recognition`
- Notificación por Telegram cuando se detecta una persona (conocida o desconocida)

### 🔹 Aprendizaje Asistido
- Al detectar desconocidos:
  - Captura 20 imágenes del rostro
  - Envía la primera por Telegram
  - El usuario responde si lo conoce
  - Si se confirma, las imágenes se mueven al dataset, se generan embeddings y se actualiza el sistema automáticamente
  - Caso contrario se eliminan las imágenes
---

## ⚙️ Requisitos

### 🐍 Python
- Python 3.8 o superior recomendado

### 📦 Dependencias
Estas son algunas librerías esenciales:
- `opencv-python`
- `face_recognition`
- `numpy`
- `python-telegram-bot`
- `requests`
- `pickle`

**Instalación completa más abajo.**

---

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/naguu12/face_detection_system.git
cd face_detection_system
```

### 2. Crear y activar entorno virtual

🔸 En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

🔸 En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar versión de Python
```bash
python --version
 ✅ Asegurate de estar usando Python 3.8 o superior
```
---

## 🔐 Configurar token de Telegram y cámara
Modificá las siguientes variables en el archivo cap_rostro.py:

TELEGRAM_TOKEN = "tu_token_de_telegram"
CHAT_ID = "tu_chat_id"
CAMARA_RTSP = "rtsp://usuario:contraseña@IP:puerto/stream"

---

## 🧪 Ejecución

### ▶️ Para iniciar el sistema:

python cap_rostro.py

---

## ✍️ Autor
Creado por Nahuel – geofísico, científico de datos y entusiasta del machine learning e IA en general.

---

## 📘 Para documentación técnica extendida y casos de uso, ver el repositorio: [face_detection_docs](https://github.com/naguu12/face_detection_docs)

---

## 🛡️ Licencia
Este proyecto se publica bajo la Licencia MIT.
