from fastapi import FastAPI, WebSocket
import face_recognition
import numpy as np
import base64
import cv2
from io import BytesIO
from datetime import datetime
from PIL import Image
import os

from back.service.reconocimiento import identificar_persona
from back.utils.utilsVectores import guardar_vector

app = FastAPI()

# Base de datos en memoria para fichajes
fichajes = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket abierto, esperando imágenes...")

    while True:
        try:
            # Recibir datos en formato JSON
            data = await websocket.receive_json()
            nombre = data.get("nombre")
            registrar = data.get("registrar", False)  # Modo registro

            image_data = base64.b64decode(data["imagen"])
            image = Image.open(BytesIO(image_data))
            image = np.array(image)

            # Convertir imagen a formato compatible con Face Recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

            print(f"Rostros detectados: {len(face_locations)}")

            if not face_encodings:
                await websocket.send_text("🚫 No se detectó un rostro válido")
                continue

            vector_actual = face_encodings[0]

            if registrar and nombre:  # 📌 Modo registro
                # Determinar siguiente contador disponible
                contador = 1
                while os.path.exists(os.path.join("../vectores", f"{nombre}_{contador}.npy")):
                    contador += 1

                guardar_vector(nombre, contador, vector_actual)
                await websocket.send_text(f"✅ Persona '{nombre}' registrada exitosamente con vector {contador}")
                print(f"✅ Persona '{nombre}' registrada")
            else:  # 📌 Modo detección normal
                nombre_detectado, distancia = identificar_persona(vector_actual)
                if nombre_detectado:
                    fichajes[nombre_detectado] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await websocket.send_text(f"✅ {nombre_detectado} fichado a las {fichajes[nombre_detectado]}")
                    print(f"✅ {nombre_detectado} fichado")
                else:
                    await websocket.send_text("❌ Rostro NO reconocido")
                    print("❌ Rostro NO reconocido")

        except Exception as e:
            print("Error en el procesamiento:", e)
            break

@app.get("/fichadas")
async def obtener_fichajes():
    return fichajes