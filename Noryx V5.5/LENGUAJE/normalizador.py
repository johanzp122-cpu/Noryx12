import re

from .aprendizaje import obtener_aprendizaje


# Correcciones conocidas por Noryx
CORRECCIONES = {
    "mjjor": "mejor",
    "aver": "a ver",
    "ola": "hola",
    "q": "que",
    "xq": "porque",
    "pq": "porque",
    "tmb": "también",
    "tb": "también",
    "asqi": "así que",
    "x": "por",
}


# Expresiones conocidas por Noryx
EXPRESIONES = {
    "yap": "ya",
    "yep": "sí",
    "demole": "démosle",
}


def aplicar_aprendizaje(texto):
    """
    Aplica primero las expresiones que Noryx
    ha aprendido anteriormente.
    """

    aprendizaje = obtener_aprendizaje()

    expresiones = aprendizaje.get("expresiones", {})
    correcciones = aprendizaje.get("correcciones", {})

    # Las expresiones pueden contener varias palabras.
    for expresion, significado in sorted(
        expresiones.items(),
        key=lambda elemento: len(elemento[0]),
        reverse=True
    ):
        patron = r"(?<!\w)" + re.escape(expresion) + r"(?!\w)"

        texto = re.sub(
            patron,
            significado,
            texto
        )

    # Correcciones aprendidas.
    for original, correcto in correcciones.items():
        patron = r"(?<!\w)" + re.escape(original) + r"(?!\w)"

        texto = re.sub(
            patron,
            correcto,
            texto
        )

    return texto


def normalizar_texto(texto):

    if not texto:
        return ""

    texto = texto.lower().strip()

    # Primero aplicamos lo que Noryx ha aprendido.
    texto = aplicar_aprendizaje(texto)

    palabras = re.findall(
        r"\b[\wáéíóúüñ]+\b|[^\w\s]",
        texto,
        flags=re.UNICODE
    )

    resultado = []

    for palabra in palabras:

        # Mantener signos de puntuación.
        if not re.match(
            r"^[\wáéíóúüñ]+$",
            palabra,
            flags=re.IGNORECASE
        ):
            resultado.append(palabra)
            continue

        palabra_normalizada = CORRECCIONES.get(
            palabra,
            palabra
        )

        palabra_normalizada = EXPRESIONES.get(
            palabra_normalizada,
            palabra_normalizada
        )

        resultado.append(palabra_normalizada)

    texto_normalizado = ""

    for elemento in resultado:

        if elemento in ".,!?;:":
            texto_normalizado += elemento

        elif not texto_normalizado:
            texto_normalizado = elemento

        else:
            texto_normalizado += " " + elemento

    return texto_normalizado.strip()