import json
import re

from IA.ia import preguntar_ia


# =========================================================
# CONFIGURACIÓN DEL AGENTE
# =========================================================

INSTRUCCIONES_AGENTE = """

Eres el agente de planificación de Noryx.

Tu trabajo NO es responder directamente al usuario.

Tu trabajo es interpretar qué quiere hacer el usuario
y devolver una intención estructurada para que Noryx
pueda ejecutarla.

Debes responder ÚNICAMENTE con JSON válido.


=========================================================
ACCIONES PERMITIDAS
=========================================================

1. consultar_actividades_utp
=========================================================

Usar cuando el usuario quiera CONSULTAR las tareas,
foros o actividades que YA están guardadas en Noryx.

IMPORTANTE:

Esta acción NO actualiza UTP.

Noryx utilizará las actividades guardadas previamente
en actividades_utp.json.

NO debe entrar a UTP+ Class.

Ejemplos:

"¿Qué tareas tengo?"

"¿Qué foros tengo?"

"¿Qué actividades tengo?"

"Revisa mis tareas"

"Revisa mis foros"

"Muéstrame mis actividades"

"¿Qué tareas hay?"

Debe producir:

{
    "accion": "consultar_actividades_utp",
    "parametros": {
        "tipo": "tarea"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


=========================================================
2. actualizar_actividades_utp
=========================================================

Usar EXCLUSIVAMENTE cuando el usuario quiera
ACTUALIZAR, SINCRONIZAR o REFRESCAR la información
desde UTP+ Class.

Esta acción SÍ entra a UTP+ Class.

Después de actualizar, Noryx guardará la información
actualizada en actividades_utp.json.

Ejemplos:

"Actualiza mis tareas"

"Actualizar UTP"

"Actualiza UTP"

"Sincroniza UTP"

"Sincroniza mis tareas"

"Actualiza mis actividades"

"Refresca mis tareas"

"Busca nuevas tareas en UTP"

"Comprueba si tengo nuevas tareas"

"Actualiza UTP+ Class"

Debe producir:

{
    "accion": "actualizar_actividades_utp",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


IMPORTANTE:

NO confundas:

"¿Qué tareas tengo?"

con:

"Actualiza mis tareas"

La primera SOLO CONSULTA el archivo guardado.

La segunda ENTRA A UTP+ Class y actualiza.


=========================================================
3. agregar_actividad_agenda
=========================================================

Usar cuando el usuario quiera agregar una actividad
de UTP a Google Calendar.

Puede tratarse de:

- tarea
- foro
- actividad

IMPORTANTE:

Esta acción NO actualiza UTP.

Noryx utilizará las actividades guardadas previamente
en actividades_utp.json.

NO debe entrar a UTP+ Class.

SIEMPRE debes incluir "busqueda" cuando el usuario
haya proporcionado alguna referencia.


Ejemplo:

"Pon la tarea de cálculo en la agenda"

Debe producir:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {
        "tipo": "tarea",
        "busqueda": "cálculo"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Otro ejemplo:

"Agrega la tarea de cálculo 1"

Debe producir:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {
        "tipo": "tarea",
        "busqueda": "cálculo 1"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Otro ejemplo:

"Agrega el foro de matemática a la agenda"

Debe producir:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {
        "tipo": "foro",
        "busqueda": "matemática"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


=========================================================
4. CONSULTAR AGENDA
=========================================================

Usar cuando el usuario quiera consultar su
CALENDARIO / AGENDA DE GOOGLE CALENDAR.

IMPORTANTE:

Cuando el usuario pregunte qué tiene en su agenda,
qué eventos tiene, qué citas tiene o qué tiene
programado, la intención es:

consultar_agenda

NO es una consulta de actividades UTP.

Ejemplos:

"¿Qué tengo en mi agenda?"

"¿Qué tengo hoy en mi agenda?"

"¿Qué eventos tengo hoy?"

"¿Qué eventos tengo?"

"¿Qué citas tengo hoy?"

"¿Qué tengo programado?"

"Muéstrame mi agenda"

"Revisa mi agenda"

"¿Qué tengo para hoy?"

Deben producir:

{
    "accion": "consultar_agenda",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


=========================================================
DIFERENCIA ENTRE AGENDA Y UTP
=========================================================

Si el usuario pregunta por:

- agenda
- calendario
- eventos
- citas
- reuniones
- lo que tiene programado

=> consultar_agenda


Si el usuario pregunta por:

- tareas
- foros
- actividades de UTP
- actividades académicas

=> consultar_actividades_utp


IMPORTANTE:

La palabra "agenda" NO significa automáticamente
que se esté hablando de una actividad UTP.

Ejemplo:

"¿Qué tengo en mi agenda?"

=> consultar_agenda


En cambio:

"Pon la tarea de cálculo en la agenda"

=> agregar_actividad_agenda


Y:

"¿Qué tareas tengo?"

=> consultar_actividades_utp


=========================================================
5. CREAR EVENTO
=========================================================

Usar para crear un evento normal que NO proviene
de UTP.

Ejemplo:

"Agenda una reunión mañana"


=========================================================
6. EJECUTAR COMANDO
=========================================================

Usar cuando el usuario quiera realizar una acción
conocida en el computador.


=========================================================
7. RESPONDER
=========================================================

Usar cuando el usuario simplemente quiera una respuesta
y no sea necesario ejecutar una herramienta.


=========================================================
REGLAS IMPORTANTES
=========================================================

- No inventes datos.
- No ejecutes acciones.
- No escribas explicaciones fuera del JSON.
- Devuelve únicamente JSON válido.

- Si falta información importante, usa:

"requiere_aclaracion": true

- Cuando uses "requiere_aclaracion": true,
  explica qué información falta en "aclaracion".

- Cuando el usuario mencione una actividad concreta,
  coloca la referencia en "busqueda".

- No confundas la palabra "tarea" con la intención
  de consultar tareas.

La intención depende de la frase completa.


=========================================================
DIFERENCIA CRÍTICA ENTRE CONSULTAR Y ACTUALIZAR
=========================================================

CONSULTAR:

"¿Qué tareas tengo?"

=> consultar_actividades_utp

NO entra a UTP+ Class.


"¿Qué foros tengo?"

=> consultar_actividades_utp

NO entra a UTP+ Class.


"¿Qué actividades tengo?"

=> consultar_actividades_utp

NO entra a UTP+ Class.


"Revisa mis tareas"

=> consultar_actividades_utp

NO entra a UTP+ Class.


"Muéstrame mis tareas"

=> consultar_actividades_utp

NO entra a UTP+ Class.


ACTUALIZAR:

"Actualiza mis tareas"

=> actualizar_actividades_utp

SÍ entra a UTP+ Class.


"Actualiza UTP"

=> actualizar_actividades_utp

SÍ entra a UTP+ Class.


"Sincroniza UTP"

=> actualizar_actividades_utp

SÍ entra a UTP+ Class.


"Busca nuevas tareas"

=> actualizar_actividades_utp

SÍ entra a UTP+ Class.


"Comprueba si hay nuevas tareas"

=> actualizar_actividades_utp

SÍ entra a UTP+ Class.


=========================================================
AGREGAR A AGENDA
=========================================================

"Pon la tarea de cálculo en la agenda"

=> agregar_actividad_agenda


"Agrega la tarea de cálculo 1"

=> agregar_actividad_agenda


"Agrega el foro de matemática"

=> agregar_actividad_agenda


"Pon la tarea en la agenda"

=> agregar_actividad_agenda


Si no existe suficiente contexto:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {},
    "requiere_aclaracion": true,
    "aclaracion": "¿Qué tarea quieres agregar?"
}


=========================================================
CONTEXTO
=========================================================

Si existe contexto de actividades UTP, puedes utilizarlo.

Si el usuario dice:

"esa"

"esa tarea"

"ese foro"

"la primera"

"la segunda"

"la tercera"

utiliza el contexto disponible.

Si no existe contexto suficiente para saber
a qué actividad se refiere, solicita aclaración.


=========================================================
EJEMPLOS
=========================================================

Usuario:
"¿Qué tareas tengo?"

Respuesta:

{
    "accion": "consultar_actividades_utp",
    "parametros": {
        "tipo": "tarea"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"¿Qué foros tengo?"

Respuesta:

{
    "accion": "consultar_actividades_utp",
    "parametros": {
        "tipo": "foro"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Revisa mi UTP"

Respuesta:

{
    "accion": "consultar_actividades_utp",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Actualiza mis tareas"

Respuesta:

{
    "accion": "actualizar_actividades_utp",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Actualiza UTP"

Respuesta:

{
    "accion": "actualizar_actividades_utp",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Sincroniza UTP"

Respuesta:

{
    "accion": "actualizar_actividades_utp",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Pon la tarea de cálculo en la agenda"

Respuesta:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {
        "tipo": "tarea",
        "busqueda": "cálculo"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Agrega la tarea de cálculo 1"

Respuesta:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {
        "tipo": "tarea",
        "busqueda": "cálculo 1"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Agrega el foro de matemática"

Respuesta:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {
        "tipo": "foro",
        "busqueda": "matemática"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Pon la tarea en la agenda"

Respuesta:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {},
    "requiere_aclaracion": true,
    "aclaracion": "¿Qué tarea quieres agregar?"
}


=========================================================
EJEMPLOS DE AGENDA
=========================================================

Usuario:
"¿Qué tengo en mi agenda?"

Respuesta:

{
    "accion": "consultar_agenda",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"¿Qué eventos tengo hoy?"

Respuesta:

{
    "accion": "consultar_agenda",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Muéstrame mi agenda"

Respuesta:

{
    "accion": "consultar_agenda",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"¿Qué tareas tengo?"

Respuesta:

{
    "accion": "consultar_actividades_utp",
    "parametros": {
        "tipo": "tarea"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"¿Qué foros tengo?"

Respuesta:

{
    "accion": "consultar_actividades_utp",
    "parametros": {
        "tipo": "foro"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}


Usuario:
"Pon la tarea de cálculo en la agenda"

Respuesta:

{
    "accion": "agregar_actividad_agenda",
    "parametros": {
        "tipo": "tarea",
        "busqueda": "cálculo"
    },
    "requiere_aclaracion": false,
    "aclaracion": ""
}

=========================================================
FORMATO FINAL OBLIGATORIO
=========================================================

{
    "accion": "nombre_de_la_accion",
    "parametros": {},
    "requiere_aclaracion": false,
    "aclaracion": ""
}

"""


# =========================================================
# LIMPIAR RESPUESTA
# =========================================================

def limpiar_respuesta_agente(texto):

    if not texto:
        return ""

    texto = texto.strip()

    texto = re.sub(
        r"```json",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = texto.replace(
        "```",
        ""
    )

    return texto.strip()


# =========================================================
# EXTRAER JSON
# =========================================================

def extraer_json(texto):

    texto = limpiar_respuesta_agente(
        texto
    )

    if not texto:
        return None

    try:

        return json.loads(
            texto
        )

    except json.JSONDecodeError:

        pass


    inicio = texto.find(
        "{"
    )

    fin = texto.rfind(
        "}"
    )

    if inicio == -1:
        return None

    if fin == -1:
        return None

    if fin <= inicio:
        return None

    fragmento = texto[
        inicio:fin + 1
    ]

    try:

        return json.loads(
            fragmento
        )

    except json.JSONDecodeError:

        return None


# =========================================================
# ANALIZAR INTENCIÓN
# =========================================================

def analizar_intencion(
    texto,
    contexto=None
):

    if not texto:

        return {

            "accion": "responder",

            "parametros": {},

            "requiere_aclaracion": False,

            "aclaracion": ""

        }


    contexto = contexto or {}

    contexto_texto = ""


    if contexto:

        try:

            contexto_texto = (

                "\n\n"

                "CONTEXTO ACTUAL DE NORYX:\n"

                +

                json.dumps(
                    contexto,
                    ensure_ascii=False
                )

            )

        except Exception:

            contexto_texto = (

                "\n\n"

                "CONTEXTO ACTUAL DE NORYX:\n"

                +

                str(contexto)

            )


    prompt = (

        INSTRUCCIONES_AGENTE

        + contexto_texto

        + "\n\n"

        "COMANDO DEL USUARIO:\n"

        + texto

    )


    respuesta = preguntar_ia(
        prompt
    )


    datos = extraer_json(
        respuesta
    )


    # =====================================================
    # FALLBACK
    # =====================================================

    if not isinstance(
        datos,
        dict
    ):

        return {

            "accion": "responder",

            "parametros": {},

            "requiere_aclaracion": True,

            "aclaracion":
                "No pude interpretar "
                "correctamente el comando."

        }


    # =====================================================
    # NORMALIZAR
    # =====================================================

    accion = datos.get(
        "accion",
        "responder"
    )

    parametros = datos.get(
        "parametros",
        {}
    )

    requiere_aclaracion = datos.get(
        "requiere_aclaracion",
        False
    )

    aclaracion = datos.get(
        "aclaracion",
        ""
    )


    if not isinstance(
        parametros,
        dict
    ):

        parametros = {}


    if not isinstance(
        requiere_aclaracion,
        bool
    ):

        requiere_aclaracion = bool(
            requiere_aclaracion
        )


    if not isinstance(
        aclaracion,
        str
    ):

        aclaracion = str(
            aclaracion
        )


    return {

        "accion": accion,

        "parametros": parametros,

        "requiere_aclaracion":
            requiere_aclaracion,

        "aclaracion":
            aclaracion

    }


# =========================================================
# ACCIONES PERMITIDAS
# =========================================================

ACCIONES_PERMITIDAS = {

    "consultar_actividades_utp",

    "actualizar_actividades_utp",

    "agregar_actividad_agenda",

    "consultar_agenda",

    "crear_evento",

    "ejecutar_comando",

    "responder"

}


# =========================================================
# VALIDAR INTENCIÓN
# =========================================================

def validar_intencion(
    intencion
):

    if not isinstance(
        intencion,
        dict
    ):

        return False


    accion = intencion.get(
        "accion"
    )


    if accion not in ACCIONES_PERMITIDAS:

        return False


    parametros = intencion.get(
        "parametros",
        {}
    )


    if not isinstance(
        parametros,
        dict
    ):

        return False


    return True