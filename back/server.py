from fastapi import FastAPI, WebSocket
import face_recognition
import numpy as np
import base64
import cv2
from io import BytesIO
from datetime import datetime
from PIL import Image
import random

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
            registrar = data.get("registrar", False)  # 📌 Modo registro

            if registrar and id_empleado:  # 📌 Modo registro
                await registrar_empleado(websocket, data, id_empleado)
            else:  # 📌 Modo verificación de identidad
                await verificar_identidad(websocket, data)

        except Exception as e:
            print("❌ Error en el procesamiento:", e)
            break

async def registrar_empleado(websocket, data, id_empleado):
    """Registra un empleado con sus gestos en la base de datos, validando que se hagan correctamente."""
    vectores_persona = []
    errores_gestos = []

    for tipo in ["normal", "sonrisa", "giro"]:
        try:
            image_data = base64.b64decode(data[f"imagen_{tipo}"])
            image = np.array(Image.open(BytesIO(image_data)))
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_image)

            if not face_encodings:
                errores_gestos.append(f"❌ No se detectó rostro en imagen '{tipo}'")
                continue

            vector_actual = face_encodings[0]

            # Si es un gesto, validarlo
            if tipo in ["sonrisa", "giro"]:
                if not identificar_gesto(rgb_image, tipo):
                    errores_gestos.append(f"🚫 El gesto '{tipo}' no fue detectado correctamente")
                    continue

            # Guardar vector si todo está bien
            vectores_persona.append(vector_actual)
            guardar_vector(id_empleado, tipo, vector_actual)

        except Exception as e:
            errores_gestos.append(f"⚠️ Error procesando imagen '{tipo}': {e}")

    if len(vectores_persona) >= 2:  # Al menos 2 vectores válidos
        await websocket.send_text(f"✅ Persona '{id_empleado}' registrada con gestos")
        print(f"✅ Persona '{id_empleado}' registrada")
    else:
        await websocket.send_text("❌ Registro fallido:\n" + "\n".join(errores_gestos))
        print("❌ Registro fallido:", errores_gestos)

async def verificar_identidad(websocket, data):
    """Verifica la identidad de un usuario a través de reconocimiento facial y gestos"""
    image_data = base64.b64decode(data["imagen"])
    image = np.array(Image.open(BytesIO(image_data)))
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_image)

    if not face_encodings:
        await websocket.send_text("🚫 No se detectó un rostro válido")
        return

    vector_actual = face_encodings[0]
    nombre_detectado, distancia = identificar_persona(vector_actual)

    if nombre_detectado:
        gesto_requerido = random.choice(["sonrisa", "giro", "cejas"])
        await websocket.send_text(f"🔄 Por favor, realiza el gesto: {gesto_requerido}")

        nueva_data = await websocket.receive_json()
        image_data_gesto = base64.b64decode(nueva_data["imagen"])
        image_gesto = np.array(Image.open(BytesIO(image_data_gesto)))
        rgb_image_gesto = cv2.cvtColor(image_gesto, cv2.COLOR_BGR2RGB)
        face_encodings_gesto = face_recognition.face_encodings(rgb_image_gesto)

        if face_encodings_gesto:
            vector_gesto = face_encodings_gesto[0]

            if identificar_gesto(rgb_image_gesto, gesto_requerido):
                fichajes[nombre_detectado] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                await websocket.send_text(f"✅ {nombre_detectado} fichado con verificación de liveness a las {fichajes[nombre_detectado]}")
                print(f"✅ {nombre_detectado} fichado correctamente")
            else:
                await websocket.send_text("🚫 Verificación fallida, gesto no reconocido o imagen muy similar")
                print("🚫 Gesto no válido, fichaje bloqueado")



@app.get("/fichadas")
async def obtener_fichajes():
    return fichajes