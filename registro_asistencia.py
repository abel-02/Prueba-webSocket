import datetime

# Registro temporal en memoria
fichajes = []  # cada ítem será un dict con nombre, fecha, hora

# Esto lo podemos implementar guardando el id del empleado en lugar del nombre
def registrar_fichaje(nombre: str):
    ahora = datetime.datetime.now()
    fichaje = {
        "nombre": nombre,
        "fecha": ahora.strftime("%Y-%m-%d"),
        "hora": ahora.strftime("%H:%M:%S"),
    }
    fichajes.append(fichaje)
    print(f"📌 Fichaje registrado: {fichaje}")
    return fichaje

def obtener_fichajes():
    return fichajes
