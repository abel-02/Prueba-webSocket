from fastapi import FastAPI, WebSocket
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

# Cargar imagen de referencia (persona autorizada)
known_image = face_recognition.load_image_file("authorized_person1.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

import cv2  # Necesario para convertir la imagen correctamente

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket abierto, esperando imágenes...")

    while True:
        try:
            data = await websocket.receive_text()
            image_data = base64.b64decode(data.split(',')[1])
            image = Image.open(BytesIO(image_data))
            image = np.array(image)

            # Convertir imagen a formato compatible con Face Recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

            print(f"👀 Rostros detectados: {len(face_locations)}")

            # Comprobar si alguno de los rostros coincide con el autorizado
            for face_encoding in face_encodings:
                match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
                if match[0]:
                    await websocket.send_text("✅ Rostro autorizado")
                    print("✅ Rostro autorizado")
                else:
                    await websocket.send_text("❌ Rostro NO autorizado")
                    print("❌ Rostro NO autorizado")

        except Exception as e:
            print("🚨 Error en el procesamiento:", e)
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)