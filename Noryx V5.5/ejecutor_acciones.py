import time
import pyautogui
from acciones import abrir_programa, cerrar_programa

# =========================================================
# EJECUTOR DE ACCIONES UNIVERSALES
# =========================================================


# =========================================================
# ESPERAR
# =========================================================

def esperar(segundos):

    time.sleep(segundos)


# =========================================================
# ESCRIBIR
# =========================================================

def escribir(texto):

    pyautogui.write(
        texto,
        interval=0.01
    )


# =========================================================
# PRESIONAR TECLA
# =========================================================

def presionar_tecla(tecla):

    pyautogui.press(tecla)


# =========================================================
# ATAJO DE TECLADO
# =========================================================

def atajo(*teclas):

    pyautogui.hotkey(
        *teclas
    )


# =========================================================
# GUARDAR
# =========================================================

def guardar():

    pyautogui.hotkey(
        "ctrl",
        "s"
    )


# =========================================================
# COPIAR
# =========================================================

def copiar():

    pyautogui.hotkey(
        "ctrl",
        "c"
    )


# =========================================================
# PEGAR
# =========================================================

def pegar():

    pyautogui.hotkey(
        "ctrl",
        "v"
    )


# =========================================================
# DESHACER
# =========================================================

def deshacer():

    pyautogui.hotkey(
        "ctrl",
        "z"
    )


# =========================================================
# MOVER MOUSE
# =========================================================

def mover_mouse(x, y):

    pyautogui.moveTo(
        x,
        y,
        duration=0.2
    )


# =========================================================
# CLIC
# =========================================================

def clic():

    pyautogui.click()


# =========================================================
# DOBLE CLIC
# =========================================================

def doble_clic():

    pyautogui.doubleClick()


# =========================================================
# CLIC DERECHO
# =========================================================

def clic_derecho():

    pyautogui.rightClick()


# =========================================================
# EJECUTAR UNA ACCIÓN
# =========================================================

def ejecutar_accion(accion):

    tipo = accion.get(
        "accion",
        ""
    ).lower()

    # -----------------------------------------------------
    # ABRIR PROGRAMA
    # -----------------------------------------------------

    if tipo == "abrir":

        programa = accion.get(
            "programa",
            ""
        )

        if programa:

            resultado = abrir_programa(
                programa
            )

            print(
                resultado
            )

            return (
                resultado !=
                "No encontré ese programa"
            )

        return False


    # -----------------------------------------------------
    # CERRAR PROGRAMA
    # -----------------------------------------------------

    if tipo == "cerrar":

        programa = accion.get(
            "programa",
            ""
        )

        if programa:

            resultado = cerrar_programa(
                programa
            )

            print(
                resultado
            )

            return (
                resultado !=
                "No encontré ese programa"
            )

        return False

    # -----------------------------------------------------
    # ESPERAR
    # -----------------------------------------------------

    if tipo == "esperar":

        segundos = accion.get(
            "segundos",
            1
        )

        esperar(segundos)

        return True


    # -----------------------------------------------------
    # ESCRIBIR
    # -----------------------------------------------------

    if tipo == "escribir":

        texto = accion.get(
            "texto",
            ""
        )

        escribir(texto)

        return True


    # -----------------------------------------------------
    # TECLA
    # -----------------------------------------------------

    if tipo == "tecla":

        tecla = accion.get(
            "tecla"
        )

        if tecla:

            presionar_tecla(
                tecla
            )

            return True

        return False


    # -----------------------------------------------------
    # ATAJO
    # -----------------------------------------------------

    if tipo == "atajo":

        teclas = accion.get(
            "teclas",
            []
        )

        if teclas:

            atajo(
                *teclas
            )

            return True

        return False


    # -----------------------------------------------------
    # GUARDAR
    # -----------------------------------------------------

    if tipo == "guardar":

        guardar()

        return True


    # -----------------------------------------------------
    # COPIAR
    # -----------------------------------------------------

    if tipo == "copiar":

        copiar()

        return True


    # -----------------------------------------------------
    # PEGAR
    # -----------------------------------------------------

    if tipo == "pegar":

        pegar()

        return True


    # -----------------------------------------------------
    # DESHACER
    # -----------------------------------------------------

    if tipo == "deshacer":

        deshacer()

        return True


    # -----------------------------------------------------
    # MOVER MOUSE
    # -----------------------------------------------------

    if tipo == "mover_mouse":

        x = accion.get(
            "x"
        )

        y = accion.get(
            "y"
        )

        if x is not None and y is not None:

            mover_mouse(
                x,
                y
            )

            return True

        return False


    # -----------------------------------------------------
    # CLIC
    # -----------------------------------------------------

    if tipo == "clic":

        clic()

        return True


    # -----------------------------------------------------
    # DOBLE CLIC
    # -----------------------------------------------------

    if tipo == "doble_clic":

        doble_clic()

        return True


    # -----------------------------------------------------
    # CLIC DERECHO
    # -----------------------------------------------------

    if tipo == "clic_derecho":

        clic_derecho()

        return True


    # -----------------------------------------------------
    # ACCIÓN DESCONOCIDA
    # -----------------------------------------------------

    print(
        "Acción desconocida:",
        tipo
    )

    return False


# =========================================================
# EJECUTAR PLAN COMPLETO
# =========================================================

def ejecutar_plan(plan):

    resultados = []

    for accion in plan:

        resultado = ejecutar_accion(
            accion
        )

        resultados.append(
            resultado
        )

    return all(
        resultados
    )


# =========================================================
# PRUEBA
# =========================================================

if __name__ == "__main__":

    print(
        "Tienes 3 segundos para hacer clic "
        "en una ventana..."
    )

    plan = [

        {
            "accion": "esperar",
            "segundos": 3
        },

        {
            "accion": "escribir",
            "texto": "Hola desde Noryx"
        },

        {
            "accion": "tecla",
            "tecla": "enter"
        }

    ]

    ejecutar_plan(
        plan
    )
if __name__ == "__main__":

    plan = [

        {
            "accion": "abrir",
            "programa": "ópera"
        },

        {
            "accion": "esperar",
            "segundos": 2
        },

        {
            "accion": "cerrar",
            "programa": "ópera"
        }

    ]

    ejecutar_plan(plan)