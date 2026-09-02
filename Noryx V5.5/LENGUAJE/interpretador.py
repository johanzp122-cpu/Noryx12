import json
import os
import re
from difflib import SequenceMatcher

from .aprendizaje import obtener_aprendizaje


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
    return SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()


def buscar_palabra_parecida(palabra, candidatos, minimo=0.55):
    palabra = palabra.lower().strip()

    mejor_candidato = None
    mejor_puntuacion = 0

    for candidato in candidatos:

        puntuacion = similitud(
            palabra,
            candidato
        )

        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_candidato = candidato

    if mejor_puntuacion >= minimo:
        return mejor_candidato, mejor_puntuacion

    return None, 0


def aplicar_aprendizaje(texto):
    """
    Aplica las correcciones y expresiones
    que Noryx ha aprendido.
    """

    aprendizaje = obtener_aprendizaje()

    correcciones = aprendizaje.get(
        "correcciones",
        {}
    )

    expresiones = aprendizaje.get(
        "expresiones",
        {}
    )

    # Correcciones aprendidas.
    for original, correcto in correcciones.items():

        patron = rf"\b{re.escape(original)}\b"

        texto = re.sub(
            patron,
            correcto,
            texto,
            flags=re.IGNORECASE
        )

    # Expresiones aprendidas.
    for expresion, significado in expresiones.items():

        patron = rf"\b{re.escape(expresion)}\b"

        texto = re.sub(
            patron,
            significado,
            texto,
            flags=re.IGNORECASE
        )

    return texto


def interpretar_comando(texto):

    if not texto:
        return {
            "texto": "",
            "cambio": False,
            "original": "",
            "corregido": "",
            "confianza": 0
        }

    # ==========================================
    # 1. APLICAR APRENDIZAJE
    # ==========================================

    texto_aprendido = aplicar_aprendizaje(texto)

    if texto_aprendido != texto:

        # Intentamos detectar exactamente qué cambió.
        palabras_originales = texto.split()
        palabras_nuevas = texto_aprendido.split()

        original = ""
        corregido = ""

        for antes, despues in zip(
            palabras_originales,
            palabras_nuevas
        ):
            if antes.lower() != despues.lower():
                original = antes
                corregido = despues
                break

        print(
            f"🧠 Lenguaje aprendido: "
            f"{original} → {corregido}"
        )

        return {
            "texto": texto_aprendido,
            "cambio": True,
            "original": original,
            "corregido": corregido,
            "confianza": 1.0
        }

    # ==========================================
    # 2. PROGRAMAS CONOCIDOS
    # ==========================================

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
        "cs2"
    ])

    # ==========================================
    # 3. BUSCAR ERRORES PARECIDOS
    # ==========================================

    palabras = re.findall(
        r"\b[\wáéíóúüñ]+\b",
        texto.lower(),
        flags=re.UNICODE
    )

    mejor_cambio = None

    for palabra in palabras:

        if len(palabra) < 3:
            continue

        candidato, confianza = buscar_palabra_parecida(
            palabra,
            candidatos,
            minimo=0.55
        )

        if not candidato:
            continue

        if palabra == candidato:
            continue

        # Evitar correcciones demasiado dudosas.
        if confianza < 0.65:
            continue

        mejor_cambio = (
            palabra,
            candidato,
            confianza
        )

        break

    if not mejor_cambio:

        return {
            "texto": texto,
            "cambio": False,
            "original": "",
            "corregido": "",
            "confianza": 0
        }

    original, corregido, confianza = mejor_cambio

    texto_corregido = re.sub(
        rf"\b{re.escape(original)}\b",
        corregido,
        texto,
        count=1,
        flags=re.IGNORECASE
    )

    return {
        "texto": texto_corregido,
        "cambio": True,
        "original": original,
        "corregido": corregido,
        "confianza": confianza
    }