import numpy as np
from back.utils.utilsVectores import cargar_vectores, UMBRAL
import random

UMBRAL_GESTO = 0.35  # 🔧 Ajusta según pruebas


def identificar_persona(vector_actual):
    """Compara el rostro detectado con los registrados para identificar a la persona."""

    if vector_actual is None or not isinstance(vector_actual, np.ndarray):
        print("❌ Error: Datos inválidos en identificación facial")
        return None, None

    datos_vectores = cargar_vectores()

    for persona_id, vectores_guardados in datos_vectores.items():
        for vector_guardado in vectores_guardados:
            distancia = np.linalg.norm(vector_actual - vector_guardado)
            if distancia < UMBRAL:
                return persona_id, distancia  # ✅ Persona reconocida

    return None, None  # 🚫 No se encontró coincidencia


def identificar_gesto(vector_gesto, vector_inicial, nombre_detectado):
    datos_vectores = cargar_vectores()

    if nombre_detectado in datos_vectores:
        vectores_guardados = datos_vectores[nombre_detectado]

        # 📌 Excluir la imagen neutra y tomar solo los gestos
        gestos_validos = vectores_guardados[1:] if len(vectores_guardados) > 1 else []

        if not gestos_validos:
            print("🚫 No hay gestos registrados para esta persona.")
            return False

        print(f"Vectores registrados para {nombre_detectado}: {gestos_validos}")

        # 📌 Elegir un gesto aleatorio en cada intento
        gesto_requerido = random.choice(["sonrisa", "giro"])
        print(f"🔄 Se requiere el gesto: {gesto_requerido}")

        distancia_inicial = np.linalg.norm(vector_inicial - vector_gesto)
        print(f"⚠️ Comparación inicial vs gesto, distancia calculada: {distancia_inicial}")

        if distancia_inicial < 0.2:
            print("🚫 La segunda imagen es demasiado similar a la primera, gesto no realizado")
            return False

        print("✅ Se detectó un cambio en el rostro, verificando si coincide con el gesto requerido...")

        # 📌 Comparar la imagen con los gestos registrados
        for vector_guardado in gestos_validos:
            distancia_gesto = np.linalg.norm(vector_gesto - vector_guardado)
            print(f"Comparando con gesto registrado, distancia: {distancia_gesto}")

            if distancia_gesto < UMBRAL_GESTO:
                print("✅ Gesto válido, verificación aprobada")
                return True  # ✅ Gesto válido

    print("🚫 Gesto no reconocido, verificación fallida")
    return False  # ❌ Gesto no reconocido
