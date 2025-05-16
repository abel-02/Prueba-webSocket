import os

import cv2
import face_recognition
import numpy as np

# Configuración
UMBRAL = 0.5
CARPETA_VECTORES = "vectores"
os.makedirs(CARPETA_VECTORES, exist_ok=True)


def cargar_vectores():
    """
    Carga todos los vectores .npy y los agrupa por persona (ej: Pedro_1.npy → Pedro → [v1, v2...]).
    """
    vectores = {}
    for archivo in os.listdir(CARPETA_VECTORES):
        if archivo.endswith(".npy"):
            nombre_base = archivo.split("_")[0]
            vector = np.load(os.path.join(CARPETA_VECTORES, archivo))
            vectores.setdefault(nombre_base, []).append(vector)
    return vectores


def guardar_vector(nombre, contador, vector):
    """
    Guarda un vector facial con formato {nombre}_{contador}.npy
    """
    nombre_archivo = f"{nombre}_{contador}.npy"
    ruta = os.path.join(CARPETA_VECTORES, nombre_archivo)
    np.save(ruta, vector)

def extraer_vector(imagen_bytes: bytes):
    np_arr = np.frombuffer(imagen_bytes, np.uint8)
    imagen_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    vectores = face_recognition.face_encodings(imagen_np)
    if vectores:
        return vectores[0]
    return None
