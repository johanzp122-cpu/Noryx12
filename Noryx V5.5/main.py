import time
import threading
import UTP.utp

from escuchar import (
    escuchar,
    escuchar_interrupcion,
    iniciar_escucha_continua,
    calibrar_microfono
)

from voz import (
    hablar,
    detener_hablar,
    esta_hablando
)
  
from config import PALABRAS_ACTIVACION

from cerebro import CerebroNoryx

from memoria import (
    recordar,
    obtener_recuerdo,
    olvidar,
    mostrar_memoria
)

from acciones import (
    agregar_programa,
    seleccionar_programa,
    eliminar_programa
)


# =========================================================
# CONFIGURACIÓN DE NORYX
# =========================================================

TIEMPO_REPOSO = 10


# =========================================================
# ESTADO
# =========================================================

noryx_activo = True

ultima_interaccion = time.time()

bloqueo_estado = threading.Lock()


# =========================================================
# CEREBRO
# =========================================================

cerebro = CerebroNoryx()


# =========================================================
# CALIBRAR MICRÓFONO
# =========================================================

calibrar_microfono()


# =========================================================
# LIMPIAR COMANDO
# =========================================================

def limpiar_comando(texto):

    texto = texto.lower().strip()

    palabras_activacion = [
        "noryx",
        "norix",
        "noriz",
        "nori",
        "noris",
        "nodrix"
    ]

    palabras = texto.split()

    if palabras and palabras[0] in palabras_activacion:

        palabras.pop(0)

    texto = " ".join(palabras)

    frases = [
        "por favor ",
        "puedes ",
        "puede ",
        "podrias ",
        "podrías ",
        "quiero que ",
        "quiero ",
        "me puedes ",
        "me podrías "
    ]

    cambio = True

    while cambio:

        cambio = False

        for frase in frases:

            if texto.startswith(frase):

                texto = texto[
                    len(frase):
                ].strip()

                cambio = True

                break

    return " ".join(
        texto.split()
    )


# =========================================================
# ACTIVACIÓN
# =========================================================

def es_activacion(texto):

    texto = texto.lower().strip()

    return any(
        palabra in texto
        for palabra in PALABRAS_ACTIVACION
    )


# =========================================================
# REGISTRAR INTERACCIÓN
# =========================================================

def registrar_interaccion():

    global ultima_interaccion

    with bloqueo_estado:

        ultima_interaccion = time.time()


# =========================================================
# ACTIVAR NORYX
# =========================================================

def activar_noryx():

    global noryx_activo
    global ultima_interaccion

    with bloqueo_estado:

        noryx_activo = True

        ultima_interaccion = time.time()

    print(
        "\n🟢 Noryx activo."
    )


# =========================================================
# ENTRAR EN REPOSO
# =========================================================

def entrar_reposo():

    global noryx_activo

    with bloqueo_estado:

        noryx_activo = False

    print(
        "\n😴 Noryx entrando en reposo "
        "por inactividad."
    )

    print(
        "🎙️ El oído continúa activo."
    )


# =========================================================
# COMPROBAR REPOSO
# =========================================================

def comprobar_reposo():

    with bloqueo_estado:

        if not noryx_activo:

            return False

        tiempo_inactivo = (
            time.time()
            - ultima_interaccion
        )

    if tiempo_inactivo >= TIEMPO_REPOSO:

        entrar_reposo()

        return True

    return False


# =========================================================
# RESPONDER
# =========================================================

def responder(texto):

    if not texto:

        return

    registrar_interaccion()

    print(
        "Noryx:",
        texto
    )

    hablar(texto)


# =========================================================
# ESPERAR INTERRUPCIÓN
# =========================================================

def esperar_interrupcion():

    while esta_hablando():

        interrupcion = escuchar_interrupcion()

        if not interrupcion:

            continue

        interrupcion = (
            interrupcion
            .lower()
            .strip()
        )

        print(
            "Interrupción escuchada:",
            interrupcion
        )

        if es_activacion(interrupcion):

            print(
                "¡Palabra de activación detectada!"
            )

            registrar_interaccion()

            detener_hablar()

            return True

    return False


# =========================================================
# HABLAR CON INTERRUPCIÓN
# =========================================================

def hablar_con_interrupcion(texto):

    if not texto:

        return False

    responder(texto)

    interrumpido = esperar_interrupcion()

    if interrumpido:

        print(
            "¡Interrupción de Noryx detectada!"
        )

        return True

    return False


# =========================================================
# MEMORIA
# =========================================================

def procesar_memoria(comando):

    comando = comando.lower().strip()


    # =====================================================
    # RECORDAR QUE
    # =====================================================

    if comando.startswith("recuerda que "):

        contenido = comando[
            len("recuerda que "):
        ].strip()

        if " es " in contenido:

            clave, valor = contenido.split(
                " es ",
                1
            )

            clave = clave.strip()
            valor = valor.strip()

            if clave and valor:

                recordar(
                    clave,
                    valor
                )

                hablar_con_interrupcion(
                    f"Listo. Recordaré que "
                    f"{clave} es {valor}."
                )

                return True

        responder(
            "Dime qué quieres que recuerde."
        )

        return True


    # =====================================================
    # RECORDAR
    # =====================================================

    if comando.startswith("recuerda "):

        contenido = comando[
            len("recuerda "):
        ].strip()

        if " es " in contenido:

            clave, valor = contenido.split(
                " es ",
                1
            )

            clave = clave.strip()
            valor = valor.strip()

            if clave and valor:

                recordar(
                    clave,
                    valor
                )

                hablar_con_interrupcion(
                    f"Listo. Recordaré que "
                    f"{clave} es {valor}."
                )

                return True

        responder(
            "Dime qué quieres que recuerde."
        )

        return True


    # =====================================================
    # OLVIDAR
    # =====================================================

    if comando.startswith("olvida "):

        clave = comando[
            len("olvida "):
        ].strip()

        if olvidar(clave):

            hablar_con_interrupcion(
                f"He olvidado {clave}."
            )

        else:

            hablar_con_interrupcion(
                f"No tenía ningún recuerdo "
                f"sobre {clave}."
            )

        return True


    # =====================================================
    # BUSCAR RECUERDO
    # =====================================================

    frases_busqueda = [

        "qué recuerdas de ",
        "que recuerdas de ",
        "qué sabes de ",
        "que sabes de ",
        "recuerdas mi ",
        "recuerdas el ",
        "recuerdas la "

    ]

    for frase in frases_busqueda:

        if comando.startswith(frase):

            clave = comando[
                len(frase):
            ].strip()

            recuerdo = obtener_recuerdo(
                clave
            )

            if recuerdo:

                hablar_con_interrupcion(
                    f"Recuerdo que "
                    f"{clave} es {recuerdo}."
                )

            else:

                hablar_con_interrupcion(
                    f"No tengo ningún recuerdo "
                    f"sobre {clave}."
                )

            return True


    # =====================================================
    # MOSTRAR MEMORIA
    # =====================================================

    if comando in [

        "qué recuerdas",
        "que recuerdas",
        "muéstrame lo que recuerdas",
        "muestrame lo que recuerdas",
        "muestra tu memoria"

    ]:

        memoria = mostrar_memoria()

        if not memoria:

            hablar_con_interrupcion(
                "Todavía no tengo recuerdos guardados."
            )

            return True

        recuerdos = []

        for clave, valor in memoria.items():

            recuerdos.append(
                f"{clave} es {valor}"
            )

        hablar_con_interrupcion(
            "Recuerdo: "
            + ", ".join(recuerdos)
        )

        return True


    return False


# =========================================================
# PROCESAR COMANDO
# =========================================================

def procesar_comando(comando):

    if not comando:

        return

    registrar_interaccion()


    # =====================================================
    # MEMORIA
    # =====================================================

    if procesar_memoria(comando):

        return


    # =====================================================
    # CEREBRO
    # =====================================================

    print(
        "Procesando comando:",
        comando
    )

    resultado = cerebro.procesar(
        comando
    )

    print(
        "Cerebro:",
        resultado
    )

    tipo = resultado.get(
        "tipo"
    )


    # =====================================================
    # AGREGAR PROGRAMA
    # =====================================================

    if tipo == "agregar_programa":

        hablar_con_interrupcion(
            "¿Cómo quieres llamar al programa?"
        )

        nombre = escuchar(
            timeout=15
        )

        if not nombre:

            hablar_con_interrupcion(
                "No escuché el nombre del programa."
            )

            return

        registrar_interaccion()

        nombre = limpiar_comando(
            nombre
        )

        hablar_con_interrupcion(
            "Selecciona el archivo del programa."
        )

        ruta = seleccionar_programa()

        if not ruta:

            hablar_con_interrupcion(
                "No seleccionaste ningún programa."
            )

            return

        agregar_programa(
            nombre,
            ruta
        )

        hablar_con_interrupcion(
            f"{nombre} fue agregado correctamente."
        )

        cerebro.limpiar_estado()

        return


    # =====================================================
    # CONFIRMAR ELIMINACIÓN
    # =====================================================

    if tipo == "confirmacion_eliminar":

        nombre = resultado[
            "programa"
        ]

        hablar_con_interrupcion(
            f"¿Seguro que quieres eliminar {nombre}?"
        )

        confirmacion = escuchar(
            timeout=10
        )

        if not confirmacion:

            hablar_con_interrupcion(
                "No escuché tu respuesta."
            )

            cerebro.limpiar_estado()

            return

        registrar_interaccion()

        confirmacion = limpiar_comando(
            confirmacion
        )

        print(
            "Confirmación:",
            confirmacion
        )

        respuestas_si = [

            "si",
            "sí",
            "correcto",
            "afirmativo",
            "hazlo",
            "adelante"

        ]

        respuestas_no = [

            "no",
            "cancelar",
            "cancela",
            "déjalo",
            "dejalo"

        ]

        if confirmacion in respuestas_si:

            eliminado = eliminar_programa(
                nombre
            )

            if eliminado:

                hablar_con_interrupcion(
                    f"{nombre} fue eliminado correctamente."
                )

            else:

                hablar_con_interrupcion(
                    f"No encontré {nombre} "
                    f"en mis programas."
                )

        elif confirmacion in respuestas_no:

            hablar_con_interrupcion(
                "Cancelando."
            )

        else:

            hablar_con_interrupcion(
                "No entendí la confirmación."
            )

        cerebro.limpiar_estado()

        return


    # =====================================================
    # RESPUESTA NORMAL
    # =====================================================

    if tipo == "respuesta":

        respuesta = resultado.get(
            "texto",
            ""
        )

        print(
            "Respuesta:",
            respuesta
        )

        interrumpido = hablar_con_interrupcion(
            respuesta
        )

        if interrumpido:

            print(
                "Noryx fue interrumpido."
            )

        cerebro.limpiar_estado()

        return


    # =====================================================
    # NINGÚN COMANDO
    # =====================================================

    hablar_con_interrupcion(
        "No entendí el comando."
    )

    cerebro.limpiar_estado()


# =========================================================
# INICIO
# =========================================================

print(
    "\n================================"
)

print(
    "       NORYX INICIADO"
)

print(
    "================================\n"
)


# =========================================================
# INICIAR OÍDO CONTINUO
# =========================================================

if not iniciar_escucha_continua():

    print(
        "❌ No se pudo iniciar el oído de Noryx."
    )

    raise SystemExit


print(
    "🟢 Noryx está listo."
)

print(
    "🎙️ Oído continuo activo."
)


# =========================================================
# BUCLE PRINCIPAL
# =========================================================

while True:

    try:

        # -------------------------------------------------
        # COMPROBAR REPOSO
        # -------------------------------------------------

        comprobar_reposo()


        # -------------------------------------------------
        # ESCUCHAR
        # -------------------------------------------------

        texto = escuchar(
            timeout=1
        )

        if not texto:

            continue


        texto = (
            texto
            .lower()
            .strip()
        )


        if not texto:

            continue


        print(
            "🎙️ Escuchado:",
            texto
        )


        # -------------------------------------------------
        # SI NORYX ESTÁ EN REPOSO
        # -------------------------------------------------

        if not noryx_activo:

            if not es_activacion(texto):

                continue

            print(
                "🟢 Activación detectada desde reposo."
            )

            activar_noryx()


        # -------------------------------------------------
        # LIMPIAR ACTIVACIÓN
        # -------------------------------------------------

        comando = limpiar_comando(
            texto
        )


        # -------------------------------------------------
        # SOLO DIJERON NORYX
        # -------------------------------------------------

        if not comando:

            activar_noryx()

            print(
                "👂 Noryx está atento."
            )

            continue


        # -------------------------------------------------
        # COMANDOS DE REPOSO
        # -------------------------------------------------

        comandos_reposo = {

            "descansa",
            "entra en reposo",
            "modo reposo",
            "ponte en reposo",
            "duerme"

        }

        if comando in comandos_reposo:

            registrar_interaccion()

            entrar_reposo()

            continue


        # -------------------------------------------------
        # PROCESAR COMANDO
        # -------------------------------------------------

        procesar_comando(
            comando
        )


    except KeyboardInterrupt:

        print(
            "\n🔴 Noryx detenido."
        )

        break


    except Exception as error:

        print(
            f"❌ Error en Noryx: {error}"
        )

        time.sleep(0.1)