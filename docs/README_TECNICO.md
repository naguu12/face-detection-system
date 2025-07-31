# 🧠 Sistema Inteligente de Reconocimiento Facial

## 🧾 Índice

0. [Resumen](#resumen)
1. [Introducción](#introducción)
2. [Acceso al stream RTSP](#acceso-al-stream-rtsp)
3. [Prueba inicial con cámara IP](#prueba-inicial-con-cámara-ip)
4. [Captura de imágenes para dataset](#captura-de-imágenes-para-dataset)
5. [Generación de embeddings faciales](#generación-de-embeddings-faciales)
6. [Reconocimiento facial en vivo](#reconocimiento-facial-en-vivo)
7. [Bot de Telegram: creación y configuración](#bot-de-telegram-creación-y-configuración)
8. [Sistema integral con Bot](#sistema-integral-con-bot)
9. [Sistema Inteligente de Reconocimiento Facial](#sistema-inteligente-de-reconocimiento-facial)
10. [Despliegue en VPS (AWS EC2)](#despliegue-en-vps-aws-ec2)
11. [Lógica del sistema](#lógica-del-sistema)
12. [Trabajos a futuro](#trabajos-a-futuro)

---
## 🧾 Resumen

El proyecto comenzó con la necesidad de desarrollar un sistema de reconocimiento facial en tiempo real, capaz de identificar personas conocidas y detectar personas desconocidas, utilizando una cámara IP y técnicas de visión por computadora. El primer paso fue establecer la conexión con una cámara Tapo C210 vía protocolo RTSP, logrando capturar imágenes desde Python con OpenCV.

A partir de estas imágenes, se implementó una rutina de recorte automático de rostros y se construyó un dataset organizado por persona. Luego, se generaron los **embeddings faciales** utilizando la librería `face_recognition`, y se almacenaron como archivos `.pkl` para su uso posterior.

Con la base de datos armada, se desarrolló un sistema de **detección continua** que analiza cada frame en vivo, reconoce rostros conocidos y notifica su detección mediante un bot de Telegram. Para los rostros no reconocidos, el sistema captura automáticamente múltiples imágenes, envía una al chat y consulta si la persona es conocida. Si el usuario responde afirmativamente, se integran automáticamente al sistema sin necesidad de reiniciar el script.

El flujo se consolidó en un único archivo principal que gestiona captura, reconocimiento, aprendizaje asistido y notificaciones en tiempo real. Finalmente, el sistema fue desplegado en una **instancia EC2 de Amazon Web Services**, lo que permite que el código se ejecute 24/7 de forma ininterrumpida. Así, el proyecto integra componentes de visión artificial, aprendizaje incremental y automatización en la nube, en una solución robusta y extensible.

---
## Introducción

### 🎯 **Objetivo General**

Desarrollar un sistema de reconocimiento facial en tiempo real utilizando una cámara IP, capaz de identificar personas conocidas y desconocidas, con integración a Telegram para permitir interacción directa desde el chat. El sistema debe ser capaz de:

- Capturar rostros en vivo.
- Compararlos con una base de datos local (embeddings).
- Aprender nuevas identidades mediante supervisión humana.
- Ejecutarse 24/7 desde una VPS en la nube (Amazon EC2).

---

### 🛠️ **Fases del Desarrollo**

#### 1. **Prueba de conexión con la cámara IP**

- Se configuró y accedió al stream RTSP de la cámara Tapo C210 desde Python usando OpenCV.
- Se verificó que la conexión era estable y que se podía capturar frames en tiempo real.

#### 2. **Captura y creación del dataset**

- Se desarrolló un script para capturar imágenes desde la cámara, recortar automáticamente los rostros detectados, y almacenarlos en carpetas separadas por persona.
- Se creó la estructura de carpetas `dataset/NombrePersona/Nombre_1.jpg`, etc.

#### 3. **Generación de embeddings**

- Se procesaron las imágenes del dataset utilizando la librería `face_recognition`.
- Para cada rostro se generó un embedding (vector numérico) que se guardó en un archivo `.pkl` por persona.
- Estos archivos se almacenaron en la carpeta `embeddings/`.

#### 4. **Reconocimiento facial en tiempo real**

- Se creó un bucle de detección continua que:
    - Captura un frame desde la cámara.
    - Detecta todos los rostros presentes.
    - Compara cada uno con los embeddings guardados.

#### 5. **Integración con Telegram Bot**

- Se configuró un bot con `python-telegram-bot`.
- Cuando se detecta un rostro **desconocido**:
    - El sistema captura automáticamente 20 imágenes de esa persona.
    - Envía la primera imagen al chat de Telegram.
    - El usuario responde "Sí" o "No".
        - Si responde "Sí", se pide un nombre, se guardan las imágenes y se generan embeddings automáticamente.
        - Si responde "No", las imágenes son descartadas.
- Todo el proceso se realiza sin reiniciar el sistema.

#### 6. **Manejo de múltiples rostros**

- El sistema puede detectar y manejar múltiples personas al mismo tiempo.
- Cada rostro detectado es recortado individualmente y evaluado por separado.
- Las capturas y comparaciones son independientes por rostro.

#### 7. **Diseño del flujo completo**

- Se unificaron todos los scripts en uno solo (`cap_rostro.py`) que ejecuta:
    - Carga de embeddings.
    - Captura de video.
    - Detección facial.
    - Comunicación con Telegram.
    - Aprendizaje supervisado con nuevos usuarios.

#### 8. **Despliegue en la nube (Amazon VPS)**

- Se montó el sistema en una instancia EC2 de Amazon para ejecución continua (24/7).
- El entorno virtual y las dependencias fueron configuradas.
- Se usa `tmux` o `screen` para dejar el script corriendo en segundo plano sin interrupciones.

---

### ⚙️ **Funcionamiento General del Sistema**

1. El script se conecta a la cámara IP y empieza a capturar frames.
2. Se detectan todos los rostros presentes en cada frame.
3. Cada rostro se compara con los embeddings conocidos:
    - Si hay una coincidencia: se notifica por Telegram con la imagen y el nombre.
    - Si no hay coincidencia:
        - Se capturan 20 imágenes de esa persona.
        - Se envía la primera por Telegram.
        - El usuario responde si la conoce.
        - Si la persona es conocida, se genera su dataset y se crean embeddings nuevos automáticamente, caso contrario las imágenes se eliminan.

---

### 🧩 **Componentes del Proyecto**

- `cap_rostro.py`: script principal, integra todas las funcionalidades.
- `dataset/`: imágenes recortadas por persona.
- `embeddings/`: vectores `.pkl` con los embeddings.
- `temp_unknown/`: carpeta temporal para almacenar imágenes de desconocidos antes de clasificar.
- `Telegram bot`: interacción humana para decidir si se conoce o no a la persona.
- `Amazon VPS`: entorno de producción para ejecución constante.

---

### 📌 Notas importantes

- El sistema es **autoaprendizaje supervisado**: mejora a medida que se le indican nuevos rostros.
- Requiere red local estable y cuanto mejor sea la cámara mejor actuará el sistema.

---
## Acceso al stream RTSP

### 🎯 ¿Qué es RTSP?

RTSP (Real Time Streaming Protocol) es un protocolo de red utilizado para transmitir video en tiempo real. La mayoría de las cámaras IP modernas (como TP-Link Tapo, Hikvision, Dahua, etc.) soportan este protocolo, lo que permite capturar video desde Python, VLC o herramientas de vigilancia.

---

### 🧾 Formato general de una URL RTSP

```

rtsp://<usuario>:<contraseña>@<ip>:<puerto>/<ruta>
```

- `<usuario>`: nombre de usuario configurado en la cámara.
- `<contraseña>`: contraseña asociada.
- `<ip>`: dirección IP local de la cámara.
- `<puerto>`: normalmente es `554`, el puerto estándar RTSP.
- `<ruta>`: depende del modelo (puede ser `stream1`, `h264`, `video`, etc.).

---

### 🛠️ Cómo obtener la URL RTSP de tu cámara

#### 📱 Opción 1: Usando la app oficial

Para cámaras Tapo, por ejemplo:

1. Entrá a la app **TP-Link Tapo**.
2. Activá la opción **"Habilitar transmisión RTSP"** (suele estar en "Configuración avanzada" o "Configuración de grabación").
3. Definí un **usuario y contraseña** para el stream.
4. Te mostrará la URL completa (copiala).

#### 🖥️ Opción 2: Usar software como VLC

1. Instalá **VLC Media Player**.
2. En el menú, andá a: `Medio > Abrir ubicación de red`.
3. Pegá una posible URL RTSP con tus credenciales:
    
    ```
    
    rtsp://usuario:contraseña@IP:554/stream1
    ```
    
4. Si se conecta, entonces es válida y podés usarla en Python.

#### 🔍 Opción 3: Consultar documentación oficial del fabricante

Cada marca tiene su propia estructura de URL RTSP. Buscá en Google:

`<modelo de tu cámara> RTSP URL`

---

### ⚠️ Notas

- Asegurate de que la cámara esté **conectada a la misma red local** que tu PC o VPS (salvo que tengas configurado acceso externo).
- Si usás una **VPS como Amazon EC2**, vas a necesitar configurar un túnel o acceso remoto (VPN, reenvío de puertos o DDNS).
- No compartas públicamente tu URL RTSP con usuario y contraseña.

---
## Prueba inicial con cámara IP

### 🎯 Objetivo

Verificar que se puede acceder a la cámara Tapo (u otra IP) desde Python utilizando el protocolo RTSP y capturar correctamente un fotograma para su visualización.

---

### 🧩 Descripción del código

Este script (`cam_test.py`) realiza una conexión básica al stream de la cámara usando OpenCV. Luego intenta capturar un solo frame y mostrarlo como imagen RGB mediante `PIL`.

---

### ✅ Resultados esperados

- Se abre una **ventana emergente** con el fotograma capturado.
- En consola se muestra: `✅ Stream en vivo. Presioná Ctrl+C para frenar.`
- Si hay un error de conexión: `❌ No se pudo conectar al stream.`

---

### 🔍 Observaciones

- Este script **no guarda imágenes**, solo verifica si el acceso al stream funciona correctamente.
- Podés modificar `for _ in range(1)` a un número mayor si querés ver múltiples frames en bucle.
- Este fue el **primer paso del proyecto**, y sirvió como base para construir el pipeline de captura de rostros en tiempo real.

---
## Captura de imágenes para dataset

Una vez verificada la conexión con la cámara IP a través de RTSP, el siguiente paso fue desarrollar un script (`img_capture`) que permitiera **capturar múltiples imágenes de una persona** y guardarlas localmente para luego generar los embeddings faciales.

---

### 🎯 Objetivo

Construir un **dataset personalizado de rostros**, donde cada persona tenga su propia carpeta con varias imágenes capturadas automáticamente desde el stream de la cámara.

---

### ⚙️ Funcionamiento general

El script realiza los siguientes pasos:

1. **Establece conexión con la cámara IP** utilizando la URL RTSP.
2. Solicita o recibe como parámetro el nombre de la persona a capturar.
3. Crea una carpeta específica dentro de `dataset/` con el nombre ingresado (si no existe).
4. **Captura automáticamente múltiples imágenes** (por defecto 20), con una pausa configurable entre cada toma (por defecto 3 segundos).
5. Guarda cada imagen en la carpeta correspondiente con un nombre como `Persona_1.jpg`, `Persona_2.jpg`, etc.

---

### 🧠 ¿Por qué múltiples imágenes?

Capturar varias imágenes en diferentes momentos permite tener **variabilidad en expresiones, ángulos e iluminación**, lo cual es fundamental para mejorar la precisión del reconocimiento facial más adelante.

---

### 🗂️ Estructura generada

Luego de correr el script, la estructura de carpetas queda así:

```

face_detection_system/
└── dataset/
    ├── Juan/
    │   ├── Juan_1.jpg
    │   ├── Juan_2.jpg
    │   └── ...
    └── Ana/
        ├── Ana_1.jpg
        └── ...
```

Cada subcarpeta representa una persona conocida, y contiene imágenes capturadas automáticamente.

---

### 🔧 Parámetros personalizables

En el script se pueden ajustar fácilmente:

- `person_name`: nombre de la persona (se convierte en el nombre de la carpeta).
- `num_images`: cantidad de imágenes a capturar (por defecto 20).
- `interval`: segundos entre cada captura (por defecto 3 segundos).

---

### ✅ Buenas prácticas

- Es recomendable que la persona esté **bien iluminada y centrada** al momento de capturar las imágenes.
- Si se detecta ruido o imágenes borrosas, pueden eliminarse manualmente de la carpeta.
- Podés repetir la captura más adelante si querés mejorar el dataset para esa persona.

---
## Generación de embeddings faciales

Una vez capturadas las imágenes para cada persona, el siguiente paso en el sistema es convertir esas imágenes en **vectores numéricos (embeddings)**, por medio del script `generate_embeddings.py`, que representen matemáticamente los rasgos faciales. Estos vectores permiten comparar rostros entre sí y realizar reconocimiento facial con precisión.

---

### 🎯 Objetivo

Extraer, a partir de las imágenes de cada persona, un conjunto de **embeddings faciales** y almacenarlos como archivos `.pkl`. Estos archivos luego se cargan rápidamente al iniciar el sistema para comparar en tiempo real los rostros detectados con la base conocida.

---

### 🧠 ¿Qué es un embedding facial?

Un *embedding* es un **vector de características** que resume la información clave de un rostro (forma de ojos, nariz, boca, mandíbula, etc.). Este vector tiene normalmente 128 dimensiones y permite comparar rostros mediante **distancias euclidianas**.

---

### ⚙️ Funcionamiento general del script

1. **Carga todas las subcarpetas** de la carpeta `dataset/` (una por persona).
2. Recorre todas las imágenes de cada persona.
3. Para cada imagen:
    - Detecta los rostros presentes.
    - Extrae los embeddings del rostro principal.
    - Si el embedding es válido, lo guarda en una lista.
4. Cuando termina con todas las imágenes de esa persona, **guarda los embeddings en un archivo `.pkl`** dentro de la carpeta `embeddings/`.
5. Si ya existe un `.pkl` para esa persona, se omite para evitar duplicados innecesarios.

---

### 💾 Estructura de salida esperada

Luego de correr este proceso, se obtiene una carpeta con un archivo `.pkl` por persona, por ejemplo:

```

face_detection_system/
└── embeddings/
    ├── Juan.pkl
    ├── Ana.pkl
    └── Pedro.pkl
```

Cada archivo `.pkl` contiene un diccionario con:

- `encodings`: una lista de embeddings (vectores NumPy).
- `name`: nombre de la persona correspondiente.

---

### 🚧 Manejo de errores y validaciones

- Si una imagen no contiene ningún rostro, se omite.
- Si la imagen está corrupta o en un formato no válido, el error se informa pero no detiene el script.
- Se evita procesar personas que ya tengan su archivo `.pkl` generado.

---

### 📌 Consideraciones

- Se utiliza el modelo `"hog"` para la detección de rostros, que es más liviano y rápido que `"cnn"`, aunque menos preciso.
- Sólo se guarda el **primer rostro detectado** en cada imagen para evitar errores por imágenes con múltiples personas.
- Es posible ejecutar este script varias veces sin problema; los embeddings ya generados no se sobrescriben a menos que se borren manualmente.

---
## Reconocimiento facial en vivo

Una vez generados los embeddings faciales, el siguiente paso es realizar **detección en tiempo real** (`live_compare.py`). Este módulo permite capturar un frame desde la cámara IP, detectar los rostros presentes, compararlos con la base conocida y mostrar visualmente el resultado del reconocimiento.

---

### 🎯 Objetivo

Detectar rostros en vivo a partir de un fotograma capturado desde la cámara, compararlos con los embeddings previamente generados, y mostrar por pantalla el nombre de la persona reconocida o marcarla como "Desconocido".

---

### ⚙️ ¿Cómo funciona el proceso?

El pipeline consta de **tres etapas principales**:

### 1. **Carga de embeddings**

- Se leen todos los archivos `.pkl` de la carpeta `embeddings/`.
- Se extraen:
    - Los vectores de características (`encodings`)
    - Los nombres correspondientes a cada vector

### 2. **Captura de frame**

- Se conecta momentáneamente a la cámara IP vía RTSP.
- Se obtiene un único fotograma (`frame`), que será procesado para análisis facial.

### 3. **Reconocimiento facial**

- Se convierte la imagen BGR a RGB (formato esperado por `face_recognition`).
- Se detectan todos los rostros presentes en el frame.
- Por cada rostro detectado:
    - Se genera su embedding.
    - Se compara con todos los embeddings registrados utilizando `compare_faces`.
    - Si se encuentra una coincidencia (dentro de una tolerancia definida), se asigna el nombre correspondiente.
    - Si no hay coincidencia, se marca como **"Desconocido"**.
- Se dibujan cuadros alrededor de los rostros detectados y se etiquetan con el nombre.
- El resultado se muestra con `matplotlib`.

---

### 🧪 ¿Qué devuelve este módulo?

Una imagen renderizada que incluye:

- Cuadro verde sobre cada rostro detectado.
- Nombre de la persona si fue reconocida.
- La etiqueta **"Desconocido"** si no coincide con nadie en la base de datos.

Además, se imprime en el título de la imagen la lista de nombres reconocidos.

---

### 🧩 Consideraciones técnicas

- Se utiliza una tolerancia de `0.4` para el reconocimiento facial. Bajos valores hacen el sistema más estricto (menos falsos positivos), pero pueden generar falsos negativos.
- Sólo se captura un frame por ejecución. Para detección continua o en tiempo real, sería necesario integrarlo en un bucle.
- El reconocimiento se realiza **en memoria** usando los embeddings precargados, lo cual es eficiente.
- Se usa `matplotlib` en lugar de `cv2.imshow()` para mayor compatibilidad y estética al visualizar imágenes.

---

### ✅ Requisitos previos

- Haber generado previamente los archivos `.pkl` con embeddings.
- Tener imágenes bien iluminadas y centradas en el dataset mejora significativamente la precisión del sistema.

---
## Bot de Telegram: creación y configuración

Para que tu sistema de reconocimiento facial pueda **enviarte alertas e interactuar con vos**, necesitás crear un **bot personalizado de Telegram**. Este bot será tu asistente automatizado, capaz de enviarte fotos, hacerte preguntas, y aprender nuevas caras según tus respuestas.

---

### 🧾 PASO A PASO para generar tu bot

#### 1. **Abrí Telegram y buscá a `@BotFather`**

- Este es el **asistente oficial** de Telegram para crear bots.
- Revisá que sea el oficial con el tic de verificación.

#### 2. **Iniciá la conversación**

- Escribí el comando:
    
    ```
    
    /start
    ```
    
    Te va a mostrar una lista de comandos disponibles.
    

#### 3. **Creá un nuevo bot**

- Escribí:
    
    ```
    
    /newbot
    ```
    
- Luego te pedirá:
    1. **Nombre del bot** (puede tener espacios, por ejemplo: `Bot de Seguridad`)
    2. **Nombre de usuario único** para el bot (debe terminar en `bot`, por ejemplo: `SeguridadDeCasaBot`)

> ⚠️ Si el nombre de usuario ya está en uso, te pedirá que elijas otro. No puede haber dos bots con el mismo handle.
> 

#### 4. **Obtené tu token**

- Una vez creado, BotFather te responde con un mensaje como este:
    
    ```
    
    Done! Congratulations on your new bot. You will find it at t.me/SeguridadDeCasaBot.
    Use this token to access the HTTP API:
    123456789:ABCdefGHIjklMNOpqrSTUvwxYZ123456789
    ```
    
- **Guardá este token**, ya que lo vas a necesitar para integrarlo con tu sistema (`TELEGRAM_TOKEN`).

---

### 📥 ¿Cómo obtener tu `chat_id`?

Para que el bot sepa a quién enviar los mensajes (o fotos), necesitás tu `chat_id`. Para obtenerlo:

#### Opción rápida:

1. Enviá cualquier mensaje a tu bot (por ejemplo, escribí “hola”).
2. Abrí este enlace en tu navegador (reemplazá el token por el tuyo):

```

https://api.telegram.org/bot<TELEGRAM_TOKEN>/getUpdates
```

1. Vas a ver una respuesta en formato JSON. Buscá una parte como esta:

```json

"chat": {
  "id": 123456789,
  "first_name": "Nombre",
  ...
}

```

- **Ese número (`123456789`) es tu `CHAT_ID`**.

> Podés usar herramientas como jsonformatter.org si querés que el resultado sea más legible.
> 

---

### ✅ ¿Qué necesitás entonces para que tu sistema funcione?

| Variable | ¿De dónde la sacás? | Ejemplo |
| --- | --- | --- |
| `TELEGRAM_TOKEN` | De BotFather al crear el bot | `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ123456789` |
| `CHAT_ID` | De la respuesta JSON de Telegram | `123456789` |

---

### 📌 Consejos de seguridad

- Nunca publiques tu token ni chat ID en repositorios públicos.
- Guardalos en un archivo `.env` y cargalos desde el código usando librerías como `python-dotenv`.

---
## Sistema integral con Bot

Este módulo es el **núcleo inteligente del sistema** (`bot_master.py`), que integra múltiples componentes para lograr una **detección y gestión automatizada de rostros en vivo**, interactuando con el usuario mediante un **bot de Telegram**. El sistema se ejecuta en tiempo real y está preparado para correr de forma continua en una VPS, permitiendo identificar personas conocidas y gestionar rostros desconocidos desde el celular.

---

### 🧠 Componentes principales del sistema

1. **📡 Streaming en vivo desde la cámara IP (Tapo u otra)**
2. **🧠 Reconocimiento facial asincrónico** basado en embeddings generados previamente
3. **🤖 Interacción vía Telegram bot**, que permite tomar decisiones humanas en tiempo real
4. **📥 Acumulación ordenada de personas desconocidas en espera**
5. **📂 Autoentrenamiento y aprendizaje continuo de nuevos rostros a través del bot**

---

### 🧩 ¿Cómo funciona el sistema completo?

#### 1. **Inicialización y carga de embeddings**

- Se cargan todos los embeddings `.pkl` desde la carpeta `embeddings/`.
- Se generan dos listas:
    - `known_face_encodings`: vectores de características
    - `known_face_names`: etiquetas de cada persona

#### 2. **Captura y reconocimiento facial continuo**

- Se inicia un **hilo paralelo (`threading`)** que ejecuta en bucle:
    - Captura un frame desde la cámara RTSP.
    - Detecta rostros en la imagen.
    - Compara cada rostro con los embeddings conocidos.
    - Si es un rostro reconocido:
        - Envía una foto al usuario por Telegram con su nombre y hora.
        - Aplica un retardo mínimo configurable (`DELAY_NOTIFICACION_MIN`) para evitar spam.
    - Si es un rostro **no reconocido**:
        - Se captura automáticamente una serie de imágenes (por defecto, 20).
        - Se asigna un ID temporal (ej: `desconocido_3`) y se acumula en una **cola de espera**.

#### 3. **Interacción por Telegram con el bot**

- Al detectar un desconocido:
    - Se envía al usuario una primera imagen con una pregunta:
        
        **"¿Conocés a esta persona? (Sí / No)"**
        
- Según la respuesta del usuario:
    - **"No"**: se eliminan las imágenes y se ignora el caso.
    - **"Sí"**: el bot pide que el usuario escriba el nombre.
        - Luego mueve las imágenes a la carpeta del dataset correspondiente.
        - Genera automáticamente los embeddings para esa persona.
        - Los guarda como un nuevo `.pkl` y actualiza la base.
        - El nuevo rostro ya queda disponible para reconocimiento en vivo.

---

### 🔄 Flujo resumido

```

1. Captura frame desde cámara
2. Detecta rostros y compara con base conocida
3. Si conocido → foto + mensaje a Telegram
4. Si desconocido:
   - Captura múltiple de imágenes
   - Envía imagen + pregunta al usuario
   - Espera decisión (Sí/No)
   - Si "Sí" → pide nombre → entrena nuevo rostro
   - Si "No" → descarta imágenes
```

---

### 🧰 Herramientas y librerías usadas

- `face_recognition`: detección y generación de embeddings faciales
- `OpenCV (cv2)`: captura de imágenes desde cámara RTSP
- `Telegram Bot API`: envíos automáticos de imágenes y mensajes
- `asyncio + threading`: ejecución concurrente (detección + interacción sin bloqueos)
- `pickle`: almacenamiento binario de embeddings
- `shutil`: gestión de archivos e imágenes temporales

---

### 💬 Comandos soportados por el bot

- `/start`: inicia el bot y confirma que está escuchando
- Mensajes:
    - `"Sí"`: habilita la carga de nombre para autoentrenamiento
    - `"No"`: descarta a la persona desconocida
    - `"Juan"`, `"Lucía"`, etc.: etiqueta del nuevo rostro a incorporar

---

## Sistema Inteligente de Reconocimiento Facial

### 🎯 Versión Final Documentada

Este sistema (`cap_rostro.py`) permite **detectar rostros en tiempo real** desde una **cámara Tapo vía RTSP**, identificar personas conocidas, **interactuar con un bot de Telegram** en caso de desconocidos, y realizar **autoentrenamiento incremental**, permitiendo que el sistema **aprenda de sus errores y se vuelva más preciso con el tiempo**.

---

### 📦 Funcionalidades incluidas

| Componente | Descripción |
| --- | --- |
| 📡 **Streaming en vivo desde Tapo** | Conexión directa mediante RTSP para capturar imágenes cada pocos segundos. |
| 🧠 **Reconocimiento facial múltiple** | Detecta y reconoce **varias personas en un mismo frame**. |
| 🧩 **Identificación de desconocidos** | Si un rostro no coincide con ningún embedding conocido, lo considera "desconocido". |
| 🤖 **Interacción vía Telegram Bot** | Envía la imagen del desconocido al chat y pregunta si se lo reconoce. |
| 📥 **Acumulación ordenada** | Se almacenan temporalmente 20 capturas distintas por persona desconocida. |
| 🗂️ **Auto-entrenamiento incremental** | Si el usuario indica que el rostro es conocido, las imágenes se suman al dataset existente, y el sistema **actualiza automáticamente los embeddings**. |
| ♻️ **Reutilización de desconocidos** | Si el sistema **detecta que ya había visto al mismo desconocido antes**, **no lo duplica ni vuelve a preguntar**. Esto se hace mediante comparación por distancia facial. |
| 🧠 **Aprendizaje de errores** | Si reconoce erróneamente a alguien conocido como desconocido, ahora se puede **reforzar su dataset** sumando nuevas imágenes desde Telegram. |
| 🧼 **Limpieza automática** | Desconocidos que no tienen suficientes imágenes válidas son descartados automáticamente. |

---

### ⚙️ Módulos y estructuras clave

#### 🔍 `deteccion()`

- Corre en un hilo aparte y se encarga de:
    - Capturar imágenes desde la cámara Tapo.
    - Detectar rostros en el frame.
    - Comparar contra el banco de rostros conocidos (`known_face_encodings`).
    - Evitar duplicados de desconocidos usando `face_distance()` con un umbral (`< 0.4`).
    - Enviar la primera captura al bot y esperar respuesta.

#### 🧠 `recibir_mensaje()`

- Escucha las respuestas del usuario vía Telegram.
- Si se responde “Sí”, solicita un nombre y:
    - Mueve las imágenes al dataset.
    - Genera embeddings nuevos desde cero para esa persona.
    - Actualiza `known_face_encodings` automáticamente.
    - Evita tener que reentrenar todo el sistema desde cero.
- Si se responde “No”, descarta el bloque de imágenes.

#### 📦 `generar_embeddings_para(nombre)`

- Se ejecuta también como **subproceso separado** al actualizar una persona.
- Recorre todas las imágenes en la carpeta de ese nombre y genera sus embeddings (si detecta rostro).

---

#### 🧠 Manejo inteligente de desconocidos

| Caso | ¿Qué hace el sistema? |
| --- | --- |
| Vuelve a aparecer el mismo desconocido | No lo duplica. Compara con `encodings_desconocidos_vivos`. |
| Aparece otro rostro al mismo tiempo | Detecta y maneja múltiples en paralelo. |
| Rostro conocido detectado mal como desconocido | Si el usuario responde "Sí" y le pone el nombre correcto, el sistema suma las imágenes al dataset y mejora la precisión futura. |
| No se detecta rostro en un frame | Lo ignora y no guarda la imagen (previene ruido y falsos positivos). |
| No se llega a capturar al menos 3 fotos válidas | Descarta automáticamente la carpeta de ese desconocido. |

---

### 📁 Estructura de carpetas    

```

📁 dataset/           → Carpetas con imágenes por persona conocida
📁 embeddings/        → Archivos .pkl con embeddings por persona
📁 temp_unknown/      → Carpetas temporales por desconocido detectado
```

---
## Despliegue en VPS (AWS EC2)

---

### 🪜 Paso 1: Crear una cuenta en AWS

1. Ir a https://aws.amazon.com/
2. Crear una cuenta gratuita (te pedirá una tarjeta de crédito, pero hay capa gratuita por 12 meses)
3. Verificá tu identidad, agregá un método de pago y seleccioná el plan **Free Tier**

---

### 🪜 Paso 2: Crear una instancia EC2 (VPS)

1. Ir a la consola de AWS: https://console.aws.amazon.com/
2. En la barra de búsqueda, poné **EC2** y seleccioná el servicio.
3. Click en **“Launch Instance”** (Lanzar nueva instancia).
4. Elegí lo siguiente:
    - **Nombre**: `reconocimiento-facial`
    - **AMI**: Ubuntu Server 22.04 LTS (Free tier elegible)
    - **Tipo de instancia**: `t2.micro` (gratis)
    - **Par de claves (Key pair)**: Crear uno nuevo y **descargar el archivo `.pem`**
    - **Almacenamiento**: 8-10 GB (suficiente)
    - **Firewall**: habilitá el puerto **22 (SSH)**
5. Click en **Launch Instance**

---

### 🪜 Paso 3: Conectarse por SSH a la VPS

1. Asegurate de tener el archivo `.pem` descargado en tu máquina.
2. Abrí una terminal y corré:

```bash

chmod 400 tu_archivo.pem
ssh -i "tu_archivo.pem" ubuntu@<IP_PUBLICA_DE_TU_EC2>

```

📌 *La IP pública la podés copiar desde el panel de AWS (instancias EC2 > tu instancia).*

---

### 🪜 Paso 4: Preparar la VPS (instalar dependencias)

Una vez conectado por SSH:

```bash

sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-opencv python3-dev build-essential cmake git unzip curl -y
pip install --upgrade pip
pip install face_recognition opencv-python-headless telegram python-telegram-bot

```

⚠️ *Si da error por `dlib`, instalá estas libs primero:*

```bash

sudo apt install libdlib-dev libboost-all-dev -y
pip install dlib

```

---

### 🪜 Paso 5: Subir tu proyecto a la VPS

Desde tu computadora local:

```bash

scp -i "tu_archivo.pem" -r ./mi_proyecto ubuntu@<IP_PUBLICA_EC2>:~

```

Reemplazá `mi_proyecto` con la carpeta donde tengas tu script final, datasets y carpetas asociadas.

---

### 🪜 Paso 6: Probar que el sistema funcione

Una vez en la VPS:

```bash

cd mi_proyecto
python3 sistema.py

```

Si todo funciona (y el RTSP de la cámara es accesible desde la red de la VPS), debería empezar a detectar rostros y enviar notificaciones por Telegram.

---

### 🪜 Paso 7: Hacer que corra 24/7 automáticamente (systemd)

Aunque vos uses Windows, **la VPS corre Linux**, y **sí puede usar `systemd`**.

Solo seguí estos pasos **conectado por SSH a la VPS** (desde Windows usás PuTTY o PowerShell):

1. Crear un servicio de Linux que lo mantenga siempre corriendo:

```bash

sudo nano /etc/systemd/system/reconocimiento.service

```

1. Pegá esto dentro:

```

[Unit]
Description=Sistema de reconocimiento facial
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/mi_proyecto
ExecStart=/usr/bin/python3 sistema.py
Restart=always

[Install]
WantedBy=multi-user.target

```

1. Guardar y salir (`Ctrl + O`, Enter, `Ctrl + X`)
2. Activar y arrancar:

```bash

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable reconocimiento.service
sudo systemctl start reconocimiento.service

```

1. Ver logs del sistema (opcional):

```bash

journalctl -u reconocimiento.service -f

```

---

### 🪜 Paso 8: Qué hacer si querés actualizar algo

1. Conectate por SSH a la VPS
2. Navegá a la carpeta del proyecto
3. Hacé los cambios (podés subir archivos vía `scp` de nuevo si querés)
4. Reiniciá el servicio:

```bash

sudo systemctl restart reconocimiento.service

```

---

### 💡 Tips útiles

- 📸 Asegurate que la cámara **Tapo sea accesible desde la red de la VPS**. Si no lo es, deberías instalar la VPS en la misma red local (con Raspberry o similar), o usar una VPN para unir redes.
- 🔐 El `TELEGRAM_TOKEN` y `CHAT_ID` pueden guardarse en un archivo `.env` y usarse vía `os.getenv()` para más seguridad.
- ⛑️ Si querés monitorear el estado del sistema, podés crear un log o canal de Telegram exclusivo para errores y alertas internas.

---

### ✅ Resultado Final

Una vez desplegado, el sistema:

- Estará corriendo **aunque tu computadora esté apagada**.
- Iniciará automáticamente cada vez que la VPS se reinicie.
- Estará listo para reconocer rostros, aprender de errores y enviar mensajes por Telegram de forma autónoma.

---
## Lógica del sistema

Esta sección describe paso a paso la lógica de funcionamiento del sistema de reconocimiento facial en vivo con interacción vía Telegram bot, detección multiusuario y autoaprendizaje incremental.

---

### 1. 📡 Captura y preprocesamiento

- Se conecta a una **cámara IP vía RTSP** para obtener imágenes en tiempo real.
- Por cada frame:
    - Se **detectan todos los rostros** presentes mediante `face_recognition`.
    - Cada rostro se **recorta individualmente** antes de ser procesado, evitando contaminación con otros rostros en la imagen.
    - Se calcula su **encoding facial** (vector que representa el rostro).

---

### 2. 🧠 Comparación con base de datos

- Se cargan desde disco los **embeddings de personas conocidas** previamente entrenadas (`.pkl`).
- Cada nuevo rostro detectado se compara contra la base usando `face_recognition.compare_faces()` con una tolerancia ajustada.

---

### 3. ✅ Detección de persona conocida

- Si el encoding coincide con uno ya existente:
    - Se **verifica si ya fue notificado recientemente** (para evitar spam).
    - En caso contrario, se envía una **notificación automática al Telegram bot** con:
        
        ```
        
        ✅ Nombre fue detectado el DD/MM/AAAA HH:MM:SS
        ```
        
    - La foto del rostro también se adjunta.

---

### 4. 🕵️‍♂️ Detección de desconocido

- Si el encoding no coincide con ninguno en la base:
    - Se verifica que no sea un **desconocido repetido** (mismo encoding dentro de cierta tolerancia). Si ya fue detectado, se ignora.
    - Si es nuevo, se le asigna un ID tipo `desconocido_1`, se crea una carpeta temporal y se **capturan 20 imágenes (como máximo, ya que pueden ser menos de 20 pero más 3) del rostro** con 2 segundos entre cada una.
    - Solo se guardan imágenes donde el rostro detectado coincide con el encoding inicial que disparó la detección, **evitando contaminación por detección múltiple**.
    - En caso de que la carpeta solo tenga 3 o menos fotos (por algún motivo el sistema no logró tomar las fotos necesarias), esta se elimina automáticamente.

---

### 5. 📥 Cola de desconocidos

- Si hay varios desconocidos detectados en momentos cercanos, el sistema **encola los desconocidos** y solo notifica uno a la vez (hasta que el usuario responda por el primer desonocido).
- El bot envía al usuario:
    
    ```
    
    🕵️ Se detectó una persona desconocida (desconocido_1) el DD/MM/AAAA HH:MM:SS
    ❓ ¿Conocés a esta persona? (Sí / No)
    ```
    
- El usuario puede responder:
    - `"No"` → Se eliminan las imágenes capturadas de `desconocido_1`.
    - `"Sí"` → El bot solicita el nombre.

---

### 6. ✏️ Etiquetado y entrenamiento incremental

- Si el usuario responde `"Sí"`:
    - El bot solicita: `"✏️ Ingresá el nombre de la persona:"`
    - Se renombra la carpeta temporal con ese nombre y se **mueve al dataset**.
    - Se generan automáticamente los nuevos **embeddings faciales** (`.pkl`) y se actualiza la base de datos en memoria.
    - Si ya existía una carpeta con ese nombre (por ejemplo, el sistema falló en reconocerlo), las imágenes nuevas se **sumarán a esa carpeta**, robusteciendo el reconocimiento.

---

### 7. 🔄 Autoaprendizaje y mejora continua

- El sistema es **autoentrenable** desde el chat. No requiere comandos manuales.
- Permite corregir falsos negativos: si un rostro ya registrado fue mal clasificado como desconocido, se puede **reasignar con su nombre original** y se regeneran los embeddings, mejorando la precisión futura.
- Las detecciones y los embeddings se recargan periódicamente (cada 10 segundos), asegurando que los nuevos datos estén disponibles sin reiniciar el sistema.

---

### 8. 🔁 Robustez ante múltiples rostros

- En escenarios con varias personas delante de la cámara:
    - Se procesan todos los rostros detectados en cada frame.
    - Para los desconocidos, se mantiene **aislado el seguimiento** de cada individuo:
        - Se guarda sólo el rostro que coincide con el que disparó la detección.
        - Así se evita que fotos de varias personas terminen en la misma carpeta de entrenamiento.

---

### 9. 🔃 Detección continua y ejecución autónoma

- Corre en un hilo paralelo (thread) desde una VPS.
- Puede funcionar indefinidamente sin intervención.
- El bot responde automáticamente ante nuevas detecciones, decisiones del usuario y aprendizaje de nuevos rostros.

---

### ✅ Resultado: Sistema inteligente y autónomo

El sistema:

- Aprende continuamente de sus errores.
- Mejora su precisión con el tiempo.
- Está preparado para funcionar **de manera 100% remota**, sin necesidad de tener la computadora personal encendida.
- Tiene una lógica de decisión limpia, robusta y con prevención de duplicados o errores de clasificación.

---
## Trabajos a futuro

### ✅ Estado actual del sistema

El sistema permite:

- 📡 Captura de video en vivo desde una cámara Tapo vía RTSP.
- 🧠 Reconocimiento facial en tiempo real usando `face_recognition`.
- 🤖 Interacción asincrónica vía Telegram bot (`python-telegram-bot`).
- 🧍‍♂️ Acumulación ordenada de personas desconocidas (sin duplicar).
- ✍️ Posibilidad de asignar nombres a desconocidos y autoincluirlos en el dataset.
- 🔁 Auto-actualización de embeddings en tiempo real.
- 👥 Reconocimiento de múltiples rostros en el mismo frame.
- 🚀 Corre de forma autónoma en una VPS, incluso si la PC personal está apagada.

---

### 🌱 Mejoras futuras (potenciales evoluciones)

#### 1. 🔐 Seguridad y privacidad

- Encriptar el almacenamiento de imágenes sensibles.
- Implementar autenticación para acceder al sistema desde otros canales (web, app).
- Agregar logs de acceso e historial de detecciones.

#### 2. 💡 Inteligencia mejorada

- Implementar una red neuronal más robusta (ej. FaceNet + clasificación SVM o deep metric learning).
- Evaluar modelos alternativos con `torch`, `tensorflow` o `InsightFace` para mayor precisión.
- Agregar tolerancia a ángulos de cámara o baja luz usando aumentación de datos.

#### 3. 📊 Interfaz de monitoreo

- Crear un dashboard web (Flask/FastAPI + Dash/Plotly) con:
    - Historial de detecciones
    - Estadísticas por persona
    - Capturas archivadas
    - Visualización en tiempo real

#### 4. 📁 Gestión avanzada de dataset

- Herramienta gráfica para revisar, renombrar y organizar dataset de imágenes.
- Eliminar automáticamente imágenes borrosas o duplicadas.

#### 5. 📲 Multicanal

- Integrar otros canales: WhatsApp (via Twilio), Discord, WebSockets.
- Crear una Progressive Web App (PWA) para notificaciones push desde el celular.

#### 6. 🧪 Testing & tolerancia a fallos

- Agregar tests automáticos (unitarios/integración) con `pytest`.
- Registrar errores en logs persistentes (archivos `.log`).

#### 7. 🧠 Autoaprendizaje y feedback

- Permitir al sistema reevaluar detecciones pasadas y ajustar la base de datos.
- Sistema de reputación/confianza para embeddings (más imágenes = mayor peso).

#### 8. 🔄 Modo entrenamiento continuo

- Recopilar automáticamente imágenes nuevas de conocidos para mejorar sus embeddings con el tiempo.
- Detectar cuándo un rostro conocido no se reconoce por cambios (barba, gafas, etc.) y permitir "refuerzo".

---

### 🛠️ Posibles tecnologías futuras a evaluar

| Tecnología | Propósito |
| --- | --- |
| **InsightFace** | Reconocimiento facial ultra preciso y veloz |
| **DeepFace** | Framework de alto nivel con varios backends (Facenet, Dlib, etc.) |
| **ONNX Runtime** | Optimización y aceleración en producción |
| **Flask/FastAPI** | API web liviana y escalable |
| **React / Next.js** | Frontend moderno si se crea interfaz web |
| **Docker** | Contenerización para fácil despliegue |
| **Supervisor** | Alternativa a `systemd` para manejo de procesos |

---

### 🗂️ Notas adicionales

- Automatizar backups del dataset a la nube (Google Drive, S3).
- Agregar métricas de rendimiento: detecciones/hora, latencia promedio, etc.

---

### 🧠 Visión a futuro

> “Convertir este sistema en una plataforma extensible para vigilancia inteligente, con capacidad de escalar, aprender con el tiempo y adaptarse a entornos variados (hogares, empresas, instituciones).”
>