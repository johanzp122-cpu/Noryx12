import json
import os

ARCHIVO_MEMORIA = "memoria.json"

def cargar_memoria():
    if not os.path.exists(ARCHIVO_MEMORIA):
        return {}
    try:
        with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def guardar_memoria(datos):
    with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def recordar(clave, valor):
    datos = cargar_memoria()
    datos[clave.lower().strip()] = valor.strip()
    guardar_memoria(datos)

def obtener_recuerdo(clave):
    datos = cargar_memoria()
    return datos.get(clave.lower().strip(), None)

def olvidar(clave):
    datos = cargar_memoria()
    clave_limpia = clave.lower().strip()
    if clave_limpia in datos:
        del datos[clave_limpia]
        guardar_memoria(datos)
        return True
    return False

def mostrar_memoria():
    return cargar_memoria()

def obtener_contexto_memoria():
    datos = cargar_memoria()
    if not datos:
        return ""
    
    lineas = [f"- {clave}: {valor}" for clave, valor in datos.items()]
    return "Memoria del usuario:\n" + "\n".join(lineas)

def agregar_recuerdo(texto):
    if " es " in texto:
        clave, valor = texto.split(" es ", 1)
        recordar(clave, valor)
    else:
        recordar(texto, "")