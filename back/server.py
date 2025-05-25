from fastapi import FastAPI, WebSocket
import face_recognition
import numpy as np
import base64
import cv2
from io import BytesIO
from datetime import datetime
from PIL import Image
import os

from back.service.reconocimiento import identificar_persona, identificar_gesto
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
            data = await websocket.receive_json()
            id_empleado = data.get("id_empleado")
            registrar = data.get("registrar", False)  # Modo registro

            if registrar and id_empleado:  # 📌 Modo registro
                contador = 1
                vectores_persona = []

                for tipo in ["normal", "sonrisa", "giro"]:
                    image_data = base64.b64decode(data[f"imagen_{tipo}"])
                    image = np.array(Image.open(BytesIO(image_data)))

                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    face_encodings = face_recognition.face_encodings(rgb_image)

                    if face_encodings:
                        vector_actual = face_encodings[0]
                        vectores_persona.append(vector_actual)
                        guardar_vector(id_empleado, f"{tipo}_{contador}", vector_actual)

                if vectores_persona:
                    await websocket.send_text(f"✅ Persona '{id_empleado}' registrada con gestos")
                    print(f"✅ Persona '{id_empleado}' registrada")
                else:
                    await websocket.send_text("🚫 No se detectó un rostro válido en todas las imágenes")
                    print("🚫 Registro fallido")

            else:  # 📌 Modo detección normal
                image_data = base64.b64decode(data["imagen"])
                image = np.array(Image.open(BytesIO(image_data)))

                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_image)

                if not face_encodings:
                    await websocket.send_text("🚫 No se detectó un rostro válido")
                    continue

                vector_actual = face_encodings[0]

                nombre_detectado, distancia = identificar_persona(vector_actual)
                if nombre_detectado:
                    await websocket.send_text("🔄 Por favor, envía una segunda imagen con un gesto (sonrisa o giro)")

                    # 🔄 Recibir segunda imagen para verificación de liveness
                    nueva_data = await websocket.receive_json()
                    image_data_gesto = base64.b64decode(nueva_data["imagen"])
                    image_gesto = np.array(Image.open(BytesIO(image_data_gesto)))

                    rgb_image_gesto = cv2.cvtColor(image_gesto, cv2.COLOR_BGR2RGB)
                    face_encodings_gesto = face_recognition.face_encodings(rgb_image_gesto)

                    if face_encodings_gesto:
                        vector_gesto = face_encodings_gesto[0]

                        # 📌 Validar que la imagen sea diferente de la inicial y coincida con un gesto registrado
                        if identificar_gesto(vector_gesto, vector_actual, nombre_detectado):
                            fichajes[nombre_detectado] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            await websocket.send_text(f"✅ {nombre_detectado} fichado con verificación de liveness a las {fichajes[nombre_detectado]}")
                            print(f"✅ {nombre_detectado} fichado correctamente")
                        else:
                            await websocket.send_text("🚫 Verificación fallida, gesto no reconocido o imagen muy similar")
                            print("🚫 Gesto no válido, fichaje bloqueado")
                    else:
                        await websocket.send_text("🚫 No se detectó un rostro válido en la verificación de liveness")
                        print("🚫 Error en liveness")
                else:
                    await websocket.send_text("❌ Rostro NO reconocido")
                    print("❌ Rostro NO reconocido")

        except Exception as e:
            print("Error en el procesamiento:", e)
            break



@app.get("/fichadas")
async def obtener_fichajes():
    return fichajes