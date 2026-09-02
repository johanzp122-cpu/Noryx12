import re
import requests


# =========================================================
# CONFIGURACIÓN
# =========================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

MODELO_IA = "llama3.2:3b"


INSTRUCCIONES_NORYX = """
Eres Noryx, un asistente de voz para computadora.

Responde en español de forma breve, directa y natural.

Tus respuestas serán leídas en voz alta por un motor TTS.

REGLAS OBLIGATORIAS:

- Máximo 2 o 3 oraciones cortas.
- No uses formato Markdown.
- No repitas la pregunta del usuario.
- Entrega directamente la respuesta final.
- Jamás expliques tu proceso de pensamiento o razonamiento.
"""


# =========================================================
# FILTRO DE LIMPIEZA PARA VOZ
# =========================================================

def limpiar_texto_voz(texto):

    if not texto:
        return ""

    # Eliminar etiquetas <think>...</think>
    texto = re.sub(
        r"<think>.*?</think>",
        "",
        texto,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Eliminar <think> sin cerrar
    texto = re.sub(
        r"<think>.*$",
        "",
        texto,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Eliminar bloques Markdown
    texto = re.sub(
        r"```.*?```",
        "",
        texto,
        flags=re.DOTALL
    )

    texto = texto.replace("**", "")
    texto = texto.replace("__", "")
    texto = texto.replace("*", "")
    texto = texto.replace("`", "")

    # Eliminar encabezados
    texto = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        texto,
        flags=re.MULTILINE
    )

    # Eliminar viñetas
    texto = re.sub(
        r"^\s*[-•]\s+",
        "",
        texto,
        flags=re.MULTILINE
    )

    # Limpiar espacios
    texto = re.sub(
        r"[ \t]+",
        " ",
        texto
    )

    texto = re.sub(
        r"\n+",
        " ",
        texto
    )

    return texto.strip()


# =========================================================
# CONSULTA A OLLAMA
# =========================================================

def preguntar_ia(pregunta):

    payload = {

        "model": MODELO_IA,

        "messages": [

            {
                "role": "system",
                "content": INSTRUCCIONES_NORYX
            },

            {
                "role": "user",
                "content": pregunta
            }

        ],

        "stream": False,

        "options": {

            "temperature": 0.3,

            "num_predict": 120,

            "top_k": 20,

            "top_p": 0.8,

            "repeat_penalty": 1.1
        }
    }

    try:

        respuesta = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )

        if respuesta.status_code != 200:

            print(
                f"❌ Error HTTP {respuesta.status_code} "
                "de Ollama."
            )

            return (
                "No pude conectar con "
                "la inteligencia local."
            )

        datos = respuesta.json()

        mensaje = datos.get(
            "message",
            {}
        )

        contenido = mensaje.get(
            "content",
            ""
        ).strip()

        thinking = mensaje.get(
            "thinking",
            ""
        ).strip()

        # Algunos modelos pueden devolver
        # el contenido dentro de thinking.
        if not contenido and thinking:

            bloques = [

                bloque.strip()

                for bloque in thinking.split("\n")

                if bloque.strip()
            ]

            if bloques:

                contenido = bloques[-1]

        texto_limpio = limpiar_texto_voz(
            contenido
        )

        if texto_limpio:

            return texto_limpio

        return (
            "No pude generar una "
            "respuesta clara."
        )

    except requests.exceptions.ConnectionError:

        print(
            "❌ Error: Ollama no está ejecutándose "
            "en http://127.0.0.1:11434"
        )

        return (
            "La inteligencia local no está "
            "disponible en este momento."
        )

    except requests.exceptions.Timeout:

        print(
            "❌ Error: Tiempo de espera agotado "
            "con Ollama."
        )

        return (
            "La inteligencia local tardó "
            "demasiado en responder."
        )

    except Exception as error:

        print(
            f"❌ Error inesperado en IA: {error}"
        )

        return (
            "Ocurrió un error al procesar "
            "la respuesta."
        )