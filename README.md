# 👁️‍🗨️ Smart Face Detection System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Face Recognition](https://img.shields.io/badge/face--recognition-Enabled-success)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema inteligente de reconocimiento facial en tiempo real, conectado con Telegram. Permite identificar personas conocidas, detectar desconocidos y aprender automáticamente desde el chat, sin necesidad de reiniciar el sistema.

---

## 📌 Descripción

Este sistema utiliza una cámara IP (RTSP) para capturar imágenes en vivo. Detecta rostros con `face_recognition` y los compara con una base de datos local. Si encuentra un rostro no registrado, captura automáticamente múltiples imágenes y envía la primera por Telegram al usuario, quien puede decidir si se trata de alguien conocido.

El sistema aprende automáticamente a partir de la respuesta del usuario: si es alguien conocido, las imágenes se renombran, se mueven al dataset y se regeneran los embeddings para mejorar el reconocimiento en el futuro.

---

## 🧠 ¿Cómo funciona?

1. 📷 Captura de imagen desde cámara IP
2. 🧠 Detección de rostro y comparación con base de datos local
3. 🟢 Si es conocido:
   - Se notifica con nombre y hora exacta vía Telegram
4. 🔴 Si es desconocido:
   - Se capturan 20 imágenes de su rostro
   - Se envía la primera por Telegram al usuario
   - El usuario responde “Sí” o “No”
5. ✏️ Si el usuario lo identifica:
   - Se renombra la carpeta
   - Se generan los embeddings del nuevo individuo
   - El sistema se actualiza automáticamente en tiempo real
6. 🗑️ Si el usuario responde “No”:
   - Las imágenes temporales se eliminan
7. 🔁 Si hay múltiples desconocidos:
   - Se encolan en orden de aparición
   - Se procesan uno por uno
8. 🧠 Si una persona ya conocida es identificada como desconocido:
   - El usuario puede actualizar su dataset con más imágenes
   - Esto aumenta la robustez del sistema en detecciones futuras

---

## 🖼️ Estructura del Proyecto

```plaintext
face-detection-system/
├── labs/                # Scripts funcionales
│   ├── cam_test.py                # Testeo de cámara local (Tapo C-210)
│   ├── img_capture.py             # Captura de dataset por rostro
│   ├── generate_embeddings.py     # Embedding facial y persistencia
│   ├── live_compare.py            # Imagen en vivo vs embeddings
│   └── bot_master.py              # Módulo Telegram + cam + Auto-entrenamiento
│
├── notebooks/           # Notebooks de desarrollo
│   ├── cam_test.ipynb
│   ├── img_capture.ipynb
│   ├── generate_embeddings.ipynb
│   ├── live_compare.ipynb
│   └── bot_master.ipynb
│
├── script_principal/    # Script principal del sistema
│   └── cap_rostro.py
│
├── docs/                # Documentación técnica extendida
│   └── README_TECNICO.md
│
├── requirements.txt     # Dependencias del proyecto
├── .gitignore
├── LICENSE
├── README.md
```

---

## ⚙️ Requisitos

### 🐍 Python
- Python 3.8 o superior recomendado

### 📦 Dependencias
Instaladas con requirements.txt, pero algunas esenciales son:
- `opencv-python`
- `face_recognition`
- `numpy`
- `python-telegram-bot`
- `requests`
- `pickle`

---

## 🚀 Instalación

### 1. Clonar el repositorio
```
git clone https://github.com/naguu12/face_detection_system.git
cd face_detection_system
```

### 2. Crear y activar entorno virtual

🔸 En Windows:
```
python -m venv venv
venv\Scripts\activate
```

🔸 En Linux / macOS:
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```
pip install -r requirements.txt
```

### 4. Verificar versión de Python
```
python --version
 ✅ Asegurate de estar usando Python 3.8 o superior
```
---

## 🔐 Configurar token de Telegram y cámara IP

Editá el archivo cap_rostro.py y completá las siguientes variables:

```
TELEGRAM_TOKEN = "tu_token_de_telegram"
CHAT_ID = "tu_chat_id"
CAMARA_RTSP = "rtsp://usuario:contraseña@IP:puerto/stream"
```
Obtené tu token creando un bot con BotFather en Telegram usando /newbot.
---

## ▶️ Ejecución del sistema:

```
python script_principal/cap_rostro.py
```
---
## 📘 Para documentación técnica extendida y casos de uso, ver: [docs/README_TECNICO.md](docs/README_TECNICO.md)
---

## ✍️ Autor

Creado por **Nahuel Aguirre**  
📍 Geofísico | Científico de Datos | Entusiasta de Machine Learning e IA en general  
🔗 [LinkedIn](https://www.linkedin.com/in/nahuel-aguirre-3876a3325)  
📩 [nahuuaguirre@outlook.es](mailto:nahuuaguirre@outlook.es)

---

## 🛡️ Licencia
Este proyecto se publica bajo la Licencia MIT.
