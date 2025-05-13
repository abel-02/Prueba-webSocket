import numpy as np
from utilsVectores import cargar_vectores, UMBRAL

def identificar_persona(vector_actual):
    """
    Identifica si el rostro pertenece a una persona registrada, comparando con los vectores guardados.
    Recibe directamente el `face_encoding` en lugar de la imagen completa.
    """

    if vector_actual is None or not isinstance(vector_actual, np.ndarray):
        print("❌ Error: Datos inválidos en identificación facial")
        return None, None

    # Cargar los vectores faciales de personas registradas
    datos_vectores = cargar_vectores()

    # Comparar el vector del rostro detectado con los almacenados
    for persona_id, vectores_guardados in datos_vectores.items():
        for vector_guardado in vectores_guardados:
            distancia = np.linalg.norm(vector_actual - vector_guardado)
            if distancia < UMBRAL:
                return persona_id, distancia  # ✅ Persona reconocida

    return None, None  # 🚫 No se encontró coincidencia