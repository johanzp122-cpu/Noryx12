import json
import os


ARCHIVO_CONFIG = "configuracion.json"


CONFIGURACION_POR_DEFECTO = {
    "microfono": 1,
    "energy_threshold":300,
    "pause_threshold": 0.4
}


def cargar_configuracion():

    if not os.path.exists(ARCHIVO_CONFIG):

        with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as archivo:
            json.dump(
                CONFIGURACION_POR_DEFECTO,
                archivo,
                indent=4
            )

        return CONFIGURACION_POR_DEFECTO

    try:

        with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except (json.JSONDecodeError, OSError):

        return CONFIGURACION_POR_DEFECTO


CONFIG = cargar_configuracion()


NOMBRE = "Noryx"

PALABRAS_ACTIVACION = [
    "noryx",
    "nori",
    "norix",
    "noriz"
]

TIEMPO_ESPERA_ORDEN = 5

ENERGY_THRESHOLD = CONFIG["energy_threshold"]

PAUSE_THRESHOLD = CONFIG["pause_threshold"]

MICROFONO = CONFIG["microfono"]