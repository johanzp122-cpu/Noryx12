import ctypes
from ctypes import wintypes
import time


# =========================================================
# WINDOWS API
# =========================================================

user32 = ctypes.windll.user32


SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_RESTORE = 9


# =========================================================
# DETECTAR MONITORES
# =========================================================

def detectar_monitores():

    monitores = []

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        wintypes.LPARAM
    )

    def callback(hmonitor, hdc, rect, lparam):

        r = rect.contents

        izquierda = r.left
        arriba = r.top
        derecha = r.right
        abajo = r.bottom

        ancho = derecha - izquierda
        alto = abajo - arriba

        monitores.append({
            "indice": len(monitores) + 1,
            "x": izquierda,
            "y": arriba,
            "ancho": ancho,
            "alto": alto,
            "principal": (
                izquierda == 0 and arriba == 0
            )
        })

        return True

    callback_func = MONITORENUMPROC(callback)

    user32.EnumDisplayMonitors(
        None,
        None,
        callback_func,
        0
    )

    return monitores


# =========================================================
# MOSTRAR MONITORES
# =========================================================

def mostrar_monitores():

    monitores = detectar_monitores()

    print("\n==============================")
    print("       MONITORES DETECTADOS")
    print("==============================")

    if not monitores:

        print("No se detectaron monitores.")
        return

    for monitor in monitores:

        print(
            f"\nMonitor {monitor['indice']}"
        )

        print(
            f"Resolución: "
            f"{monitor['ancho']} x "
            f"{monitor['alto']}"
        )

        print(
            f"Posición: "
            f"X={monitor['x']} "
            f"Y={monitor['y']}"
        )

        print(
            f"Principal: "
            f"{'SÍ' if monitor['principal'] else 'NO'}"
        )

    print("==============================\n")


# =========================================================
# DETECTAR VENTANAS
# =========================================================

def detectar_ventanas():

    ventanas = []

    EnumWindowsProc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        wintypes.HWND,
        wintypes.LPARAM
    )

    # Ventanas internas del sistema que no queremos mostrar
    ventanas_sistema = {
        "Program Manager",
        "WDADesktopService",
        "Experiencia de entrada de Windows",
        "NVIDIA GeForce Overlay"
    }

    def callback(hwnd, lparam):

        # Ignorar ventanas invisibles
        if not user32.IsWindowVisible(hwnd):
            return True

        # Ignorar ventanas deshabilitadas
        if not user32.IsWindowEnabled(hwnd):
            return True

        # Obtener longitud del título
        longitud = user32.GetWindowTextLengthW(hwnd)

        if longitud == 0:
            return True

        # Obtener título
        titulo = ctypes.create_unicode_buffer(
            longitud + 1
        )

        user32.GetWindowTextW(
            hwnd,
            titulo,
            longitud + 1
        )

        titulo_texto = titulo.value.strip()

        # Ignorar ventanas específicas del sistema
        if titulo_texto in ventanas_sistema:
            return True

        # Obtener posición y tamaño
        rect = wintypes.RECT()

        user32.GetWindowRect(
            hwnd,
            ctypes.byref(rect)
        )

        ventanas.append({
            "hwnd": hwnd,
            "titulo": titulo_texto,
            "x": rect.left,
            "y": rect.top,
            "ancho": rect.right - rect.left,
            "alto": rect.bottom - rect.top
        })

        return True

    callback_func = EnumWindowsProc(callback)

    user32.EnumWindows(
        callback_func,
        0
    )

    return ventanas


# =========================================================
# BUSCAR VENTANA
# =========================================================

def buscar_ventana(nombre):

    import unicodedata

    def normalizar_texto(texto):

        texto = texto.lower().strip()

        texto = unicodedata.normalize(
            "NFD",
            texto
        )

        texto = "".join(
            caracter
            for caracter in texto
            if unicodedata.category(caracter) != "Mn"
        )

        return texto

    nombre = normalizar_texto(nombre)

    ventanas = detectar_ventanas()

    coincidencias = []

    for ventana in ventanas:

        titulo = normalizar_texto(
            ventana["titulo"]
        )

        if nombre in titulo:

            coincidencias.append(
                ventana
            )

    return coincidencias


# =========================================================
# ENCONTRAR MONITOR DE UNA VENTANA
# =========================================================

def obtener_monitor_ventana(ventana):

    monitores = detectar_monitores()

    centro_x = (
        ventana["x"]
        + ventana["ancho"] // 2
    )

    centro_y = (
        ventana["y"]
        + ventana["alto"] // 2
    )

    for monitor in monitores:

        dentro_horizontal = (
            monitor["x"]
            <= centro_x
            <
            monitor["x"] + monitor["ancho"]
        )

        dentro_vertical = (
            monitor["y"]
            <= centro_y
            <
            monitor["y"] + monitor["alto"]
        )

        if dentro_horizontal and dentro_vertical:

            if monitor["principal"]:
                return "principal"

            return "secundaria"

    return None


# =========================================================
# MOSTRAR VENTANAS CON SU PANTALLA
# =========================================================

def mostrar_ventanas():

    ventanas = detectar_ventanas()

    print("\n==============================")
    print("    VENTANAS Y MONITORES")
    print("==============================")

    if not ventanas:

        print("No se encontraron ventanas.")

        print("==============================\n")

        return

    for ventana in ventanas:

        pantalla = obtener_monitor_ventana(
            ventana
        )

        print(
            f"\n{ventana['titulo']}"
        )

        print(
            f"HWND: {ventana['hwnd']}"
        )

        print(
            f"Pantalla: {pantalla}"
        )

        print(
            f"Posición: "
            f"X={ventana['x']} "
            f"Y={ventana['y']}"
        )

        print(
            f"Tamaño: "
            f"{ventana['ancho']} x "
            f"{ventana['alto']}"
        )

    print("==============================\n")


# =========================================================
# SABER EN QUÉ PANTALLA ESTÁ UNA VENTANA
# =========================================================

def pantalla_de_ventana(nombre):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return None

    ventana = coincidencias[0]

    pantalla = obtener_monitor_ventana(
        ventana
    )

    print("\n==============================")
    print("      UBICACIÓN DE VENTANA")
    print("==============================")

    print(
        "Ventana:",
        ventana["titulo"]
    )

    print(
        "Posición:",
        f"X={ventana['x']} "
        f"Y={ventana['y']}"
    )

    print(
        "Pantalla:",
        pantalla
    )

    print("==============================\n")

    return pantalla


# =========================================================
# ENFOCAR VENTANA
# =========================================================

def enfocar_ventana(nombre):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    hwnd = ventana["hwnd"]

    pantalla = obtener_monitor_ventana(
        ventana
    )

    print(
        f"\nEnfocando: "
        f"{ventana['titulo']}"
    )

    print(
        f"Pantalla: {pantalla}"
    )

    try:

        # Restaurar si estaba minimizada
        user32.ShowWindow(
            hwnd,
            SW_RESTORE
        )

        time.sleep(0.1)

        # Llevar al frente
        user32.SetForegroundWindow(
            hwnd
        )

        time.sleep(0.1)

        print(
            "Ventana enfocada correctamente."
        )

        return True

    except Exception as error:

        print(
            "Error enfocando ventana:",
            error
        )

        return False


# =========================================================
# CAMBIAR A UNA VENTANA
# =========================================================

def cambiar_a_ventana(nombre):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    pantalla = obtener_monitor_ventana(
        ventana
    )

    print("\n==============================")
    print("       CAMBIAR A VENTANA")
    print("==============================")

    print(
        "Ventana:",
        ventana["titulo"]
    )

    print(
        "Pantalla:",
        pantalla
    )

    resultado = enfocar_ventana(
        nombre
    )

    print("==============================\n")

    return resultado


# =========================================================
# MINIMIZAR VENTANA
# =========================================================

def minimizar_ventana(nombre):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    hwnd = ventana["hwnd"]

    print(
        "Minimizando:",
        ventana["titulo"]
    )

    user32.ShowWindow(
        hwnd,
        SW_MINIMIZE
    )

    time.sleep(0.2)

    if user32.IsIconic(hwnd):

        print(
            "Ventana minimizada correctamente."
        )

        return True

    print(
        "Windows no confirmó la minimización."
    )

    return False


# =========================================================
# MAXIMIZAR VENTANA
# =========================================================

def maximizar_ventana(nombre):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    hwnd = ventana["hwnd"]

    print(
        "Maximizando:",
        ventana["titulo"]
    )

    user32.ShowWindow(
        hwnd,
        SW_RESTORE
    )

    time.sleep(0.2)

    user32.ShowWindow(
        hwnd,
        SW_MAXIMIZE
    )

    time.sleep(0.3)

    user32.SetForegroundWindow(
        hwnd
    )

    if user32.IsZoomed(hwnd):

        print(
            "Ventana maximizada correctamente."
        )

        return True

    print(
        "Windows no confirmó la maximización."
    )

    return False


# =========================================================
# RESTAURAR VENTANA
# =========================================================

def restaurar_ventana(nombre):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    hwnd = ventana["hwnd"]

    user32.ShowWindow(
        hwnd,
        SW_RESTORE
    )

    time.sleep(0.2)

    user32.SetForegroundWindow(
        hwnd
    )

    print(
        "Ventana restaurada:",
        ventana["titulo"]
    )

    return True


# =========================================================
# CERRAR VENTANA
# =========================================================

def cerrar_ventana(nombre):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    user32.PostMessageW(
        ventana["hwnd"],
        0x0010,
        0,
        0
    )

    return True


# =========================================================
# MOVER VENTANA
# =========================================================

def mover_ventana(nombre, x, y):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    hwnd = ventana["hwnd"]

    user32.MoveWindow(
        hwnd,
        x,
        y,
        ventana["ancho"],
        ventana["alto"],
        True
    )

    return True


# =========================================================
# MOVER VENTANA A UNA PANTALLA Y MAXIMIZAR
# =========================================================

def mover_a_monitor(nombre, pantalla):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    monitores = detectar_monitores()

    monitor_destino = None

    # =====================================================
    # NORMALIZAR PANTALLA
    # =====================================================

    pantalla = str(pantalla).lower().strip()

    # Quitar palabras que puedan venir del comando
    pantalla = pantalla.replace("pantalla", "")
    pantalla = pantalla.replace("monitor", "")
    pantalla = pantalla.strip()

    # =====================================================
    # CONVERTIR NÚMEROS EN TEXTO
    # =====================================================

    numeros = {
        "uno": 1,
        "una": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4
    }

    if pantalla in numeros:

        pantalla_numero = numeros[pantalla]

    elif pantalla.isdigit():

        pantalla_numero = int(pantalla)

    else:

        pantalla_numero = None

    # =====================================================
    # BUSCAR POR NÚMERO
    # =====================================================

    if pantalla_numero is not None:

        for monitor in monitores:

            if monitor["indice"] == pantalla_numero:

                monitor_destino = monitor
                break

    # =====================================================
    # COMPATIBILIDAD CON PRINCIPAL / SECUNDARIA
    # =====================================================

    if monitor_destino is None:

        for monitor in monitores:

            if (
                pantalla == "principal"
                and monitor["principal"]
            ):

                monitor_destino = monitor
                break

            if (
                pantalla == "secundaria"
                and not monitor["principal"]
            ):

                monitor_destino = monitor
                break

    # =====================================================
    # PANTALLA NO ENCONTRADA
    # =====================================================

    if monitor_destino is None:

        print(
            "No encontré la pantalla:",
            pantalla
        )

        print(
            "Pantallas disponibles:",
            len(monitores)
        )

        return False

    hwnd = ventana["hwnd"]

    print(
        f"\nMoviendo '{ventana['titulo']}' "
        f"a la pantalla {monitor_destino['indice']}"
    )

    print(
        f"Destino: "
        f"X={monitor_destino['x']} "
        f"Y={monitor_destino['y']}"
    )

    # =====================================================
    # RESTAURAR ANTES DE MOVER
    # =====================================================

    user32.ShowWindow(
        hwnd,
        SW_RESTORE
    )

    time.sleep(0.2)

    # =====================================================
    # OBTENER TAMAÑO ACTUAL
    # =====================================================

    rect = wintypes.RECT()

    user32.GetWindowRect(
        hwnd,
        ctypes.byref(rect)
    )

    ancho = rect.right - rect.left
    alto = rect.bottom - rect.top

    # =====================================================
    # MOVER
    # =====================================================

    user32.MoveWindow(
        hwnd,

        monitor_destino["x"],
        monitor_destino["y"],

        ancho,
        alto,

        True
    )

    time.sleep(0.3)

    # =====================================================
    # MAXIMIZAR
    # =====================================================

    user32.ShowWindow(
        hwnd,
        SW_MAXIMIZE
    )

    time.sleep(0.4)

    # =====================================================
    # LLEVAR AL FRENTE
    # =====================================================

    user32.SetForegroundWindow(
        hwnd
    )

    if user32.IsZoomed(hwnd):

        print(
            "Ventana movida y "
            "maximizada correctamente."
        )

        return True

    print(
        "La ventana fue movida, "
        "pero Windows no confirmó "
        "la maximización."
    )

    return False

    # =====================================================
    # COMPROBAR
    # =====================================================

    if user32.IsZoomed(hwnd):

        print(
            "Ventana movida y "
            "maximizada correctamente."
        )

        return True

    print(
        "La ventana fue movida, "
        "pero Windows no confirmó "
        "la maximización."
    )

    return False

# =========================================================
# MOVER VENTANA A UNA POSICIÓN DEL MONITOR
# =========================================================

def mover_a_posicion(nombre, posicion):

    coincidencias = buscar_ventana(nombre)

    if not coincidencias:

        print(
            "No encontré la ventana:",
            nombre
        )

        return False

    ventana = coincidencias[0]

    hwnd = ventana["hwnd"]

    # Restaurar antes de mover
    user32.ShowWindow(
        hwnd,
        SW_RESTORE
    )

    time.sleep(0.2)

    # Obtener posición y tamaño actualizados
    rect = wintypes.RECT()

    user32.GetWindowRect(
        hwnd,
        ctypes.byref(rect)
    )

    centro_x = (
        rect.left +
        (rect.right - rect.left) // 2
    )

    centro_y = (
        rect.top +
        (rect.bottom - rect.top) // 2
    )

    # Detectar monitor actual
    monitores = detectar_monitores()

    monitor = None

    for m in monitores:

        if (
            m["x"] <= centro_x < m["x"] + m["ancho"]
            and
            m["y"] <= centro_y < m["y"] + m["alto"]
        ):

            monitor = m
            break

    if monitor is None:

        print(
            "No pude determinar el monitor."
        )

        return False

    posicion = posicion.lower().strip()

    # =====================================================
    # CALCULAR POSICIÓN
    # =====================================================

    if posicion == "izquierda":

        x = monitor["x"]
        y = monitor["y"]

        ancho = monitor["ancho"] // 2
        alto = monitor["alto"]

    elif posicion == "derecha":

        x = (
            monitor["x"] +
            monitor["ancho"] // 2
        )

        y = monitor["y"]

        ancho = (
            monitor["ancho"] -
            monitor["ancho"] // 2
        )

        alto = monitor["alto"]

    elif posicion == "arriba":

        x = monitor["x"]
        y = monitor["y"]

        ancho = monitor["ancho"]
        alto = monitor["alto"] // 2

    elif posicion == "abajo":

        x = monitor["x"]

        y = (
            monitor["y"] +
            monitor["alto"] // 2
        )

        ancho = monitor["ancho"]

        alto = (
            monitor["alto"] -
            monitor["alto"] // 2
        )

    else:

        print(
            "Posición no válida:",
            posicion
        )

        return False

    # =====================================================
    # MOVER
    # =====================================================

    print(
        f"\nMoviendo '{ventana['titulo']}'"
    )

    print(
        f"Monitor: "
        f"{'principal' if monitor['principal'] else 'secundaria'}"
    )

    print(
        f"Posición: {posicion}"
    )

    print(
        f"Destino: X={x} Y={y}"
    )

    print(
        f"Tamaño: {ancho} x {alto}"
    )

    user32.MoveWindow(
        hwnd,
        x,
        y,
        ancho,
        alto,
        True
    )

    time.sleep(0.3)

    user32.SetForegroundWindow(
        hwnd
    )

    print(
        "Ventana colocada correctamente."
    )

    return True

# =========================================================
# PRUEBAS
# =========================================================

if __name__ == "__main__":

    mostrar_monitores()

    mostrar_ventanas()

    print(
        "\nProbando posición izquierda de Opera..."
    )

    resultado = mover_a_posicion(
        "Opera",
        "abajo"
    )

    print(
        "Resultado:",
        resultado
    )

    pantalla_de_ventana("Opera")