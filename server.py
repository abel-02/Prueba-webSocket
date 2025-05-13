from fastapi import FastAPI, WebSocket
import face_recognition
import numpy as np
import base64
import cv2
from io import BytesIO
from datetime import datetime
from PIL import Image

from reconocimiento import identificar_persona

app = FastAPI()

# Base de datos en memoria para fichajes
fichajes = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket abierto, esperando imágenes...")

    while True:
        try:
            data = await websocket.receive_text()
            image_data = base64.b64decode(data.split(',')[1])
            image = Image.open(BytesIO(image_data))  # ✅ Convertir correctamente los bytes en imagen
            image = np.array(image)

            # Convertir imagen a formato compatible con Face Recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

            print(f"Rostros detectados: {len(face_locations)}")

            # Comprobar si el rostro es reconocido
            for face_encoding in face_encodings:
                nombre, distancia = identificar_persona(face_encoding)
                if nombre:
                    # Guardar fichaje con fecha y hora
                    fichajes[nombre] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await websocket.send_text(f"✅ {nombre} fichado a las {fichajes[nombre]}")
                    print(f"✅ {nombre} fichado")
                else:
                    await websocket.send_text("❌ Rostro NO reconocido")
                    print("❌ Rostro NO reconocido")

        except Exception as e:
            print("Error en el procesamiento:", e)
            break

@app.get("/fichadas")
async def obtener_fichajes():
    return fichajes