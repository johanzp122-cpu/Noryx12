import speech_recognition as sr
import threading
import queue

from config import (
    ENERGY_THRESHOLD,
    MICROFONO,
    PAUSE_THRESHOLD
)


# =========================================================
# RECONOCEDOR
# =========================================================

r = sr.Recognizer()


# =========================================================
# CONFIGURACIÓN
# =========================================================

r.energy_threshold = ENERGY_THRESHOLD

r.dynamic_energy_threshold = False

r.dynamic_energy_adjustment_damping = 0.15
r.dynamic_energy_ratio = 1.5

r.pause_threshold = PAUSE_THRESHOLD
r.phrase_threshold = 0.15
r.non_speaking_duration = 0.3


# =========================================================
# ESTADO DEL OÍDO
# =========================================================

microfono_activo = False

fuente_microfono = None
escucha_fondo = None

bloqueo_microfono = threading.Lock()


# =========================================================
# COLA DE FRASES
# =========================================================
#
# El micrófono escucha continuamente.
#
# Cuando reconoce una frase:
#
# MICRÓFONO
#     ↓
# reconocimiento
#     ↓
# cola
#     ↓
# main.py
#
# main.py ya NO tiene que abrir y cerrar el micrófono
# para cada escucha.
# =========================================================

cola_frases = queue.Queue()


# =========================================================
# CALIBRAR MICRÓFONO
# =========================================================

def calibrar_microfono():

    print("\n🎙️ Calibrando micrófono...")
    print("Mantente en silencio durante 1 segundo.")

    try:

        with sr.Microphone(
            device_index=MICROFONO
        ) as source:

            r.adjust_for_ambient_noise(
                source,
                duration=1
            )

        print("Micrófono calibrado.")

        print(
            f"Nivel de ruido detectado: "
            f"{r.energy_threshold:.0f}"
        )

        print("Noryx listo.\n")

        return True

    except Exception as error:

        print(
            "Error calibrando micrófono:",
            error
        )

        r.energy_threshold = ENERGY_THRESHOLD

        print(
            f"Usando ENERGY_THRESHOLD = "
            f"{ENERGY_THRESHOLD}"
        )

        return False


# =========================================================
# MOSTRAR MICRÓFONOS
# =========================================================

def mostrar_microfonos():

    microfonos = sr.Microphone.list_microphone_names()

    print("\n--- MICRÓFONOS DISPONIBLES ---")

    for indice, nombre in enumerate(microfonos):

        print(
            f"{indice}: {nombre}"
        )

    print("------------------------------\n")


# =========================================================
# RECIBIR AUDIO EN SEGUNDO PLANO
# =========================================================

def _procesar_audio(
    recognizer,
    audio
):

    if not microfono_activo:
        return

    try:

        texto = recognizer.recognize_google(
            audio,
            language="es-ES"
        )

        texto = texto.lower().strip()

        if texto:

            print(
                "Dijiste:",
                texto
            )

            cola_frases.put(
                texto
            )

    except sr.UnknownValueError:

        pass

    except sr.RequestError:

        print(
            "No se pudo conectar "
            "al reconocimiento de voz."
        )

    except Exception as error:

        print(
            "Error reconociendo audio:",
            error
        )


# =========================================================
# INICIAR OÍDO CONTINUO
# =========================================================

def iniciar_escucha_continua():

    global microfono_activo
    global fuente_microfono
    global escucha_fondo

    if microfono_activo:
        return True

    try:

        with bloqueo_microfono:

            fuente_microfono = sr.Microphone(
                device_index=MICROFONO
            )
            

            microfono_activo = True


            escucha_fondo = r.listen_in_background(
                fuente_microfono,
                _procesar_audio,
                phrase_time_limit=8
            )

        print(
            "🎙️ Oído continuo de Noryx activado."
        )

        return True

    except Exception as error:

        microfono_activo = False

        print(
            "Error iniciando oído continuo:",
            error
        )

        return False


# =========================================================
# DETENER OÍDO CONTINUO
# =========================================================

def detener_escucha_continua():

    global microfono_activo
    global fuente_microfono
    global escucha_fondo

    microfono_activo = False

    try:

        if escucha_fondo:

            escucha_fondo(
                wait_for_stop=False
            )

    except Exception:
        pass

    escucha_fondo = None

    try:

        if fuente_microfono:

            fuente_microfono.__exit__(
                None,
                None,
                None
            )

    except Exception:
        pass

    fuente_microfono = None


# =========================================================
# OBTENER SIGUIENTE FRASE
# =========================================================

def escuchar(
    timeout=5,
    phrase_time_limit=15
):

    if not microfono_activo:
        return ""

    try:

        texto = cola_frases.get(
            timeout=timeout
        )

        if texto:

            return texto.lower().strip()

    except queue.Empty:

        return ""

    return ""


# =========================================================
# ESCUCHAR INTERRUPCIÓN
# =========================================================

def escuchar_interrupcion():

    if not microfono_activo:
        return ""

    try:

        texto = cola_frases.get(
            timeout=0.5
        )

        if texto:

            return texto.lower().strip()

    except queue.Empty:

        return ""

    return ""


# =========================================================
# ESCUCHAR ACTIVACIÓN
# =========================================================

def escuchar_activacion(timeout=1):

    if not microfono_activo:
        return ""

    try:

        texto = cola_frases.get(
            timeout=timeout
        )

        if texto:

            return texto.lower().strip()

    except queue.Empty:

        return ""

    return ""

# =========================================================
# LIMPIAR FRASES PENDIENTES
# =========================================================

def limpiar_cola():

    while True:

        try:

            cola_frases.get_nowait()

        except queue.Empty:

            break