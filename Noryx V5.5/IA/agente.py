import json
import re
import unicodedata

from IA.ia import preguntar_ia


ACCIONES_VALIDAS = {
    "consultar_actividades_utp",
    "actualizar_actividades_utp",
    "agregar_actividad_agenda",
    "consultar_agenda",
    "crear_evento",
    "ejecutar_comando",
    "responder",
}


INSTRUCCIONES_AGENTE = """
Eres el agente de planificación de Noryx.
NO respondas directamente al usuario. Devuelve ÚNICAMENTE JSON válido.

ACCIONES PERMITIDAS:
consultar_actividades_utp, actualizar_actividades_utp,
agregar_actividad_agenda, consultar_agenda, crear_evento,
ejecutar_comando, responder.

REGLAS:
- "¿Qué tareas tengo?" => consultar_actividades_utp.
- "Actualiza mis tareas" => actualizar_actividades_utp.
- "¿Qué tengo en mi agenda?" => consultar_agenda.
- "Pon la tarea X en la agenda" => agregar_actividad_agenda.
- "¿Qué puedes hacer?" => responder.
- Las preguntas sobre capacidades de Noryx SIEMPRE son responder.
- No uses consultar_actividades_utp solo porque exista contexto UTP.
- El contexto solo sirve para referencias como "esa", "ese", "la primera", etc.
- Si una actividad se agrega a la agenda y hay referencia, incluye "busqueda".
- Si falta información necesaria, usa requiere_aclaracion=true.

FORMATO:
{
  "accion": "...",
  "parametros": {},
  "requiere_aclaracion": false,
  "aclaracion": ""
}
"""


def _normalizar_simple(texto):
    """Normalización mínima. No aplica aprendizaje ni corrección difusa."""
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto)


def detectar_intencion_directa(texto):
    """Resuelve comandos inequívocos sin depender del modelo."""
    n = _normalizar_simple(texto)
    if not n:
        return None

    capacidades = {
        "que puedes hacer",
        "que puedes hacer por mi",
        "que sabes hacer",
        "que cosas puedes hacer",
        "que funciones tienes",
        "cuales son tus funciones",
        "para que sirves",
    }
    if n in capacidades:
        return {
            "accion": "responder",
            "parametros": {},
            "requiere_aclaracion": False,
            "aclaracion": "",
            "respuesta_directa": (
                "Puedo ayudarte con comandos del computador, "
                "tus actividades de UTP y tu agenda."
            ),
        }

    if n in {
        "actualiza utp", "actualizar utp", "sincroniza utp", "refresca utp"
    } or any(n.startswith(x) for x in (
        "actualiza mis tareas",
        "actualizar mis tareas",
        "sincroniza mis tareas",
        "refresca mis tareas",
        "actualiza mis actividades",
        "busca nuevas tareas",
        "comprueba si tengo nuevas tareas",
    )):
        return {
            "accion": "actualizar_actividades_utp",
            "parametros": {},
            "requiere_aclaracion": False,
            "aclaracion": "",
        }

    if n in {"que tareas tengo", "que tareas tengo hoy", "revisa mis tareas", "muestrame mis tareas"}:
        return {
            "accion": "consultar_actividades_utp",
            "parametros": {"tipo": "tarea"},
            "requiere_aclaracion": False,
            "aclaracion": "",
        }

    if n in {"que foros tengo", "que foros tengo hoy", "revisa mis foros", "muestrame mis foros"}:
        return {
            "accion": "consultar_actividades_utp",
            "parametros": {"tipo": "foro"},
            "requiere_aclaracion": False,
            "aclaracion": "",
        }

    if n in {"que actividades tengo", "que actividades tengo hoy", "revisa mi utp", "muestrame mis actividades"}:
        return {
            "accion": "consultar_actividades_utp",
            "parametros": {},
            "requiere_aclaracion": False,
            "aclaracion": "",
        }

    if n in {
        "que tengo en mi agenda",
        "que tengo hoy en mi agenda",
        "que hay en mi agenda",
        "que eventos tengo",
        "que eventos tengo hoy",
        "que citas tengo hoy",
        "que tengo programado",
        "muestrame mi agenda",
        "revisa mi agenda",
        "que tengo para hoy",
    }:
        return {
            "accion": "consultar_agenda",
            "parametros": {},
            "requiere_aclaracion": False,
            "aclaracion": "",
        }

    patron = re.match(
        r"^(?:pon|agrega|agregar|añade|anade)\s+(?:la\s+)?"
        r"(tarea|foro|actividad)\s+(.+?)\s+(?:en|a)\s+la\s+agenda$",
        texto.strip().lower(),
    )
    if patron:
        tipo, busqueda = patron.groups()
        return {
            "accion": "agregar_actividad_agenda",
            "parametros": {"tipo": tipo, "busqueda": busqueda.strip()},
            "requiere_aclaracion": False,
            "aclaracion": "",
        }

    return None


def comando_necesita_contexto(texto):
    """El contexto UTP solo se entrega cuando hay una referencia explícita."""
    n = _normalizar_simple(texto)
    referencias = (
        "esa tarea", "ese foro", "esa actividad", "esa",
        "ese", "esta tarea", "este foro", "esta actividad", "este",
        "la primera", "la segunda", "la tercera", "la cuarta",
        "la quinta", "la sexta",
    )
    return any(r in n for r in referencias)


def validar_intencion(intencion):
    if not isinstance(intencion, dict):
        return False
    accion = intencion.get("accion")
    parametros = intencion.get("parametros", {})
    if accion not in ACCIONES_VALIDAS or not isinstance(parametros, dict):
        return False
    if not isinstance(intencion.get("requiere_aclaracion", False), bool):
        return False
    if accion == "agregar_actividad_agenda" and not intencion.get("requiere_aclaracion", False):
        if not parametros.get("busqueda"):
            return False
    return True


def _extraer_json(respuesta):
    if isinstance(respuesta, dict):
        return respuesta
    if not respuesta:
        return None
    texto = str(respuesta).strip()
    texto = re.sub(r"^```(?:json)?\s*", "", texto, flags=re.I)
    texto = re.sub(r"\s*```$", "", texto)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        inicio = texto.find("{")
        fin = texto.rfind("}")
        if inicio >= 0 and fin > inicio:
            try:
                return json.loads(texto[inicio:fin + 1])
            except json.JSONDecodeError:
                pass
    return None


def analizar_intencion(texto, contexto=None):
    """Intenta primero reglas deterministas y usa IA solo cuando hace falta."""
    directa = detectar_intencion_directa(texto)
    if directa:
        return directa

    prompt = INSTRUCCIONES_AGENTE + "\n\nUSUARIO:\n" + str(texto).strip()

    # No contaminamos preguntas nuevas con actividades UTP anteriores.
    if contexto and comando_necesita_contexto(texto):
        relevante = {}
        if "ultimas_actividades_utp" in contexto:
            relevante["ultimas_actividades_utp"] = contexto["ultimas_actividades_utp"]
        if relevante:
            prompt += "\n\nCONTEXTO RELEVANTE:\n" + json.dumps(relevante, ensure_ascii=False)

    respuesta = preguntar_ia(prompt)
    intencion = _extraer_json(respuesta)

    if not validar_intencion(intencion):
        return {
            "accion": "responder",
            "parametros": {},
            "requiere_aclaracion": False,
            "aclaracion": "",
            "respuesta_directa": "No pude interpretar con seguridad ese comando.",
        }

    intencion.setdefault("parametros", {})
    intencion.setdefault("requiere_aclaracion", False)
    intencion.setdefault("aclaracion", "")
    return intencion
