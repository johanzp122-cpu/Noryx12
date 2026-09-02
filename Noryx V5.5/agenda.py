import os.path
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


# ============================================================
# ZONA HORARIA DE PERÚ
# ============================================================

ZONA_PERU = datetime.timezone(
    datetime.timedelta(hours=-5)
)


# ============================================================
# CONECTAR CON GOOGLE CALENDAR
# ============================================================

def obtener_servicio_calendar():

    creds = None

    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            if not os.path.exists("credentials.json"):

                print(
                    "❌ Falta el archivo "
                    "'credentials.json' de Google Cloud."
                )

                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open(
            "token.json",
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )

    try:

        service = build(
            "calendar",
            "v3",
            credentials=creds
        )

        return service

    except Exception as e:

        print(
            f"❌ Error al conectar con Google Calendar: {e}"
        )

        return None


# ============================================================
# EVENTOS DE HOY
# ============================================================

def obtener_eventos_hoy():

    service = obtener_servicio_calendar()

    if not service:

        return (
            "No pude conectar con tu "
            "Google Calendar."
        )

    # ========================================================
    # HORA ACTUAL EN PERÚ
    # ========================================================

    ahora = datetime.datetime.now(
        ZONA_PERU
    )

    # ========================================================
    # INICIO DEL DÍA EN PERÚ
    # ========================================================

    inicio_dia = ahora.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    # ========================================================
    # FINAL DEL DÍA EN PERÚ
    # ========================================================

    fin_dia = ahora.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999
    )

    print(
        "📅 Consultando Google Calendar:"
    )

    print(
        f"   Desde: {inicio_dia.isoformat()}"
    )

    print(
        f"   Hasta: {fin_dia.isoformat()}"
    )

    try:

        events_result = service.events().list(

            calendarId="primary",

            timeMin=inicio_dia.isoformat(),

            timeMax=fin_dia.isoformat(),

            singleEvents=True,

            orderBy="startTime"

        ).execute()

    except Exception as e:

        print(
            f"❌ Error leyendo Google Calendar: {e}"
        )

        return (
            "No pude consultar tu "
            "Google Calendar."
        )

    eventos = events_result.get(
        "items",
        []
    )

    if not eventos:

        return (
            "No tienes eventos ni citas "
            "programadas para hoy."
        )

    lista_eventos = []

    for event in eventos:

        inicio = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        titulo = event.get(
            "summary",
            "Evento sin título"
        )

        if "T" in inicio:

            hora = inicio.split("T")[1][:5]

            try:

                hora_numero = int(
                    hora[:2]
                )

                minutos = hora[3:]

                if hora_numero == 0:

                    hora_12 = 12
                    periodo = "a. m."

                elif hora_numero < 12:

                    hora_12 = hora_numero
                    periodo = "a. m."

                elif hora_numero == 12:

                    hora_12 = 12
                    periodo = "p. m."

                else:

                    hora_12 = hora_numero - 12
                    periodo = "p. m."

                hora_formateada = (
                    f"{hora_12}:"
                    f"{minutos} "
                    f"{periodo}"
                )

            except Exception:

                hora_formateada = hora

            lista_eventos.append(
                f"{titulo} a las "
                f"{hora_formateada}"
            )

        else:

            lista_eventos.append(
                f"{titulo} todo el día"
            )

    return (
        "Tus eventos para hoy son: "
        + ", ".join(lista_eventos)
        + "."
    )


# ============================================================
# CREAR EVENTO NORMAL
# ============================================================

def crear_evento(
    titulo,
    duracion_minutos=60
):

    service = obtener_servicio_calendar()

    if not service:

        return (
            "No pude conectar con Google Calendar "
            "para guardar la cita."
        )

    # ========================================================
    # HORA ACTUAL EN PERÚ
    # ========================================================

    ahora = datetime.datetime.now(
        ZONA_PERU
    )

    inicio = (
        ahora
        + datetime.timedelta(hours=1)
    )

    fin = (
        inicio
        + datetime.timedelta(
            minutes=duracion_minutos
        )
    )

    evento = {

        "summary": titulo,

        "start": {

            "dateTime": inicio.isoformat(),

            "timeZone": "America/Lima"

        },

        "end": {

            "dateTime": fin.isoformat(),

            "timeZone": "America/Lima"

        }

    }

    try:

        service.events().insert(

            calendarId="primary",

            body=evento

        ).execute()

        return (
            f"Cita '{titulo}' "
            "agendada con éxito "
            "en tu Google Calendar."
        )

    except Exception as e:

        print(
            f"❌ Error al crear evento: {e}"
        )

        return (
            "Ocurrió un error al "
            "agendar la cita."
        )


# ============================================================
# CREAR EVENTO DE UTP
# ============================================================

def crear_evento_utp(
    titulo,
    fecha_vencimiento,
    curso=""
):

    service = obtener_servicio_calendar()

    if not service:

        return (
            "No pude conectar con "
            "Google Calendar."
        )

    try:

        # ----------------------------------------------------
        # Convertir fecha de UTP
        # ----------------------------------------------------

        fecha = datetime.datetime.strptime(
            fecha_vencimiento,
            "%Y-%m-%d %H:%M:%S.%f"
        )

        # UTP entrega la hora de Perú.
        # Le asignamos la zona horaria de Perú.
        fecha = fecha.replace(
            tzinfo=ZONA_PERU
        )

        # ----------------------------------------------------
        # Duración del evento
        # ----------------------------------------------------

        inicio = fecha - datetime.timedelta(
            minutes=30
        )

        fin = fecha

        # ----------------------------------------------------
        # Título
        # ----------------------------------------------------

        if curso:

            titulo_evento = (
                f"[UTP] {titulo} - {curso}"
            )

        else:

            titulo_evento = (
                f"[UTP] {titulo}"
            )

        # ----------------------------------------------------
        # Crear evento
        # ----------------------------------------------------

        evento = {

            "summary": titulo_evento,

            "description": (
                "Actividad de UTP+ Class\n"
                f"Curso: {curso}\n"
                f"Fecha límite: "
                f"{fecha.strftime('%d/%m/%Y %I:%M %p')}"
            ),

            "start": {

                "dateTime": inicio.isoformat(),

                "timeZone": "America/Lima"

            },

            "end": {

                "dateTime": fin.isoformat(),

                "timeZone": "America/Lima"

            }

        }

        service.events().insert(

            calendarId="primary",

            body=evento

        ).execute()

        print(
            f"📅 Evento creado: {titulo_evento}"
        )

        print(
            f"   Inicio: {inicio.isoformat()}"
        )

        print(
            f"   Fin: {fin.isoformat()}"
        )

        return (
            f"'{titulo}' fue agregado "
            "a tu Google Calendar."
        )

    except ValueError:

        return (
            "La fecha de vencimiento "
            "de la actividad no tiene "
            "un formato válido."
        )

    except Exception as e:

        print(
            f"❌ Error creando evento UTP: {e}"
        )

        return (
            "Ocurrió un error al "
            "agregar la actividad a "
            "Google Calendar."
        )