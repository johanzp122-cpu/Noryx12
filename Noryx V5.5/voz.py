import pyttsx3
import threading


# =========================================================
# ESTADO DE VOZ
# =========================================================

hablando = threading.Event()
detener_voz = threading.Event()

# Motor actual
motor_actual = None

# Evita que dos hilos manipulen el motor al mismo tiempo
bloqueo = threading.Lock()


# =========================================================
# HABLAR
# =========================================================

def hablar(texto):

    global motor_actual

    if not texto:
        return


    # -----------------------------------------------------
    # Si Noryx ya estaba hablando, detenerlo
    # -----------------------------------------------------

    detener_voz.clear()


    def reproducir():

        global motor_actual

        try:

            hablando.set()

            # -------------------------------------------------
            # CREAR MOTOR NUEVO
            # -------------------------------------------------

            with bloqueo:

                motor_actual = pyttsx3.init()

                motor_actual.setProperty(
                    "rate",
                    180
                )

                motor_actual.setProperty(
                    "volume",
                    1.0
                )


            # -------------------------------------------------
            # COMPROBAR SI FUE INTERRUMPIDO
            # -------------------------------------------------

            if detener_voz.is_set():

                return


            motor_actual.say(texto)

            motor_actual.runAndWait()


        except Exception as error:

            print(
                "Error de voz:",
                error
            )


        finally:

            # -------------------------------------------------
            # DETENER MOTOR
            # -------------------------------------------------

            try:

                if motor_actual:

                    motor_actual.stop()

            except Exception:

                pass


            # -------------------------------------------------
            # DESTRUIR MOTOR
            # -------------------------------------------------

            motor_actual = None

            hablando.clear()


    hilo = threading.Thread(
        target=reproducir,
        daemon=True
    )

    hilo.start()


# =========================================================
# SABER SI NORYX ESTÁ HABLANDO
# =========================================================

def esta_hablando():

    return hablando.is_set()


# =========================================================
# DETENER HABLA
# =========================================================

def detener_hablar():

    global motor_actual


    print(
        "Deteniendo voz..."
    )


    # -----------------------------------------------------
    # MARCAR INTERRUPCIÓN
    # -----------------------------------------------------

    detener_voz.set()


    # -----------------------------------------------------
    # DETENER MOTOR ACTUAL
    # -----------------------------------------------------

    try:

        with bloqueo:

            if motor_actual:

                motor_actual.stop()

    except Exception as error:

        print(
            "Error al detener voz:",
            error
        )


    # -----------------------------------------------------
    # LIMPIAR REFERENCIA
    # -----------------------------------------------------

    motor_actual = None

    hablando.clear()