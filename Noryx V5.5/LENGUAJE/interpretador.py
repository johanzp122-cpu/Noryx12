import json
import os
import re
from difflib import SequenceMatcher


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
PROGRAMAS_FILE = os.path.join(ROOT_DIR, "programas.json")


def cargar_programas():
    if not os.path.exists(PROGRAMAS_FILE):
        return []
    try:
        with open(PROGRAMAS_FILE, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return list(datos.keys())
    except Exception as error:
        print(f"⚠️ No pude leer programas.json: {error}")
        return []


def similitud(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def buscar_palabra_parecida(palabra, candidatos, minimo=0.55):
    palabra = palabra.lower().strip()
    mejor_candidato = None
    mejor_puntuacion = 0

    for candidato in candidatos:
        puntuacion = similitud(palabra, candidato)
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_candidato = candidato

    if mejor_puntuacion >= minimo:
        return mejor_candidato, mejor_puntuacion
    return None, 0


def interpretar_comando(texto):
    """Busca errores tipográficos de programas conocidos.

    El aprendizaje NO se aplica aquí. Se aplica una sola vez en
    normalizador.py para evitar transformaciones encadenadas.
    """
    if not texto:
        return {
            "texto": "",
            "cambio": False,
            "original": "",
            "corregido": "",
            "confianza": 0,
        }

    programas = cargar_programas()
    candidatos = set(programas)
    candidatos.update([
        "discord",
        "spotify",
        "steam",
        "calculadora",
        "curseforge",
        "opera",
        "ópera",
        "bloc de notas",
        "explorador de archivos",
        "counter strike",
        "cs2",
    ])

    palabras = re.findall(
        r"\b[\wáéíóúüñ]+\b",
        texto.lower(),
        flags=re.UNICODE,
    )

    mejor_cambio = None

    for palabra in palabras:
        if len(palabra) < 3:
            continue

        candidato, confianza = buscar_palabra_parecida(
            palabra,
            candidatos,
            minimo=0.65,
        )

        if not candidato or palabra == candidato:
            continue

        # La corrección difusa solo debe actuar con alta confianza.
        # Esto evita convertir palabras normales en comandos ajenos.
        if confianza < 0.78:
            continue

        # No corregir una palabra a otra de forma difusa si ambas son
        # palabras comunes del lenguaje. El objetivo aquí son nombres
        # de programas/comandos conocidos.
        mejor_cambio = (palabra, candidato, confianza)
        break

    if not mejor_cambio:
        return {
            "texto": texto,
            "cambio": False,
            "original": "",
            "corregido": "",
            "confianza": 0,
        }

    original, corregido, confianza = mejor_cambio
    texto_corregido = re.sub(
        rf"\b{re.escape(original)}\b",
        corregido,
        texto,
        count=1,
        flags=re.IGNORECASE,
    )

    return {
        "texto": texto_corregido,
        "cambio": True,
        "original": original,
        "corregido": corregido,
        "confianza": confianza,
    }
