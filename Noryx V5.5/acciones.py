import os
import json
import tkinter as tk
import pyautogui
import webbrowser
import urllib.parse
import time
import re

from tkinter import filedialog
from difflib import get_close_matches

from windows import (
    minimizar_ventana,
    maximizar_ventana,
    restaurar_ventana,
    cerrar_ventana,
    cambiar_a_ventana,
    mover_a_monitor,
    mover_a_posicion
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

CARPETA_NORYX = os.path.dirname(
    os.path.abspath(__file__)
)

ARCHIVO_PROGRAMAS = os.path.join(
    CARPETA_NORYX,
    "programas.json"
)

CARPETA_DOCUMENTOS = os.path.join(
    CARPETA_NORYX,
    "documentos"
)

os.makedirs(
    CARPETA_DOCUMENTOS,
    exist_ok=True
)


# =========================================================
# PROGRAMAS
# =========================================================

def cargar_programas():

    if not os.path.exists(ARCHIVO_PROGRAMAS):
        return {}

    try:

        with open(
            ARCHIVO_PROGRAMAS,
            "r",
            encoding="utf-8"
        ) as archivo:

            datos = json.load(archivo)

            if isinstance(datos, dict):
                return datos

            return {}

    except (json.JSONDecodeError, OSError):

        return {}


def guardar_programas(programas):

    try:

        with open(
            ARCHIVO_PROGRAMAS,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                programas,
                archivo,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError as error:

        print(
            "Error guardando programas.json:",
            error
        )

        return False


PROGRAMAS = cargar_programas()

# =========================================================
# ÚLTIMA CORRECCIÓN DETECTADA
# =========================================================

ULTIMA_CORRECCION = {
    "original": "",
    "corregido": ""
}


def obtener_ultima_correccion():
    return {
        "original": ULTIMA_CORRECCION["original"],
        "corregido": ULTIMA_CORRECCION["corregido"]
    }


def limpiar_ultima_correccion():
    ULTIMA_CORRECCION["original"] = ""
    ULTIMA_CORRECCION["corregido"] = ""

# =========================================================
# BUSCAR DISCORD DINÁMICAMENTE
# =========================================================

def buscar_discord():

    carpeta_discord = os.path.join(
        os.environ.get(
            "LOCALAPPDATA",
            ""
        ),
        "Discord"
    )

    if not os.path.isdir(
        carpeta_discord
    ):

        print(
            "❌ No encontré la carpeta de Discord:",
            carpeta_discord
        )

        return None

    versiones = []

    for nombre in os.listdir(
        carpeta_discord
    ):

        ruta = os.path.join(
            carpeta_discord,
            nombre
        )

        if not os.path.isdir(
            ruta
        ):
            continue

        coincidencia = re.match(
            r"app-(\d+(?:\.\d+)+)$",
            nombre,
            re.IGNORECASE
        )

        if not coincidencia:
            continue

        version = tuple(
            int(numero)
            for numero in coincidencia.group(1).split(".")
        )

        discord_exe = os.path.join(
            ruta,
            "Discord.exe"
        )

        if os.path.isfile(
            discord_exe
        ):

            versiones.append(
                (
                    version,
                    discord_exe
                )
            )

    if not versiones:

        print(
            "❌ No encontré Discord.exe en ninguna versión."
        )

        return None

    versiones.sort(
        key=lambda elemento: elemento[0],
        reverse=True
    )

    version, ruta = versiones[0]

    print(
        "Discord encontrado dinámicamente:",
        ruta
    )

    return ruta


# =========================================================
# PROCESOS
# =========================================================

PROCESOS = {

    "bloc de notas": "notepad.exe",
    "calculadora": "calc.exe",
    "ópera": "opera.exe",
    "opera": "opera.exe",
    "spotify": "spotify.exe",
    "counter strike": "cs2.exe",
    "steam": "steam.exe",
    "curseforge": "CurseForge.exe",
    "explorador de archivos": "explorer.exe",
    "discord": "discord.exe"

}


# =========================================================
# ALIAS
# =========================================================

ALIAS = {

    "notas": "bloc de notas",
    "bloc": "bloc de notas",

    "navegador": "ópera",
    "google": "ópera",
    "opera": "ópera",

    "counter": "counter strike",
    "cs": "counter strike",

    "curse": "curseforge",

    "explorador": "explorador de archivos",

    "zte": "steam",
    "sting": "steam",

    "disco": "discord",
    "discor": "discord",
    "discordo": "discord"

}


# =========================================================
# CORREGIR PROGRAMA
# =========================================================

def corregir_programa(nombre):

    coincidencias = get_close_matches(
        nombre,
        PROGRAMAS.keys(),
        n=1,
        cutoff=0.45
    )

    if coincidencias:
        return coincidencias[0]

    return nombre


# =========================================================
# NORMALIZAR PROGRAMA
# =========================================================

def normalizar_programa(nombre):
    global PROGRAMAS
    global ULTIMA_CORRECCION

    nombre_original = str(
        nombre
    ).lower().strip()

    nombre = nombre_original

    ULTIMA_CORRECCION["original"] = ""
    ULTIMA_CORRECCION["corregido"] = ""

    palabras_extra = [
        "el ",
        "la ",
        "los ",
        "las ",
        "un ",
        "una "
    ]

    for palabra in palabras_extra:
        if nombre.startswith(palabra):
            nombre = nombre[
                len(palabra):
            ].strip()
            break

    # =====================================================
    # ALIAS
    # =====================================================

    if nombre in ALIAS:
        return ALIAS[nombre]

    # =====================================================
    # NOMBRE EXACTO
    # =====================================================

    if nombre in PROGRAMAS:
        return nombre

    # =====================================================
    # CORRECCIÓN AUTOMÁTICA
    # =====================================================

    corregido = corregir_programa(
        nombre
    )

    if corregido != nombre_original:

        ULTIMA_CORRECCION["original"] = (
            nombre_original
        )

        ULTIMA_CORRECCION["corregido"] = (
            corregido
        )

    return corregido


# =========================================================
# NORMALIZAR NOMBRE DE VENTANA
# =========================================================

def normalizar_nombre_ventana(nombre):

    nombre = str(
        nombre
    ).lower().strip()

    reemplazos = {

        "ópera": "opera",
        "óperá": "opera",
        "opera": "opera",

        "el bloc de notas": "bloc de notas",
        "la calculadora": "calculadora",

        "discordo": "discord",
        "discor": "discord",
        "disco": "discord",

        "counter": "counter strike",
        "cs": "counter strike",

        "explorador": "explorador de archivos"

    }

    if nombre in reemplazos:

        return reemplazos[nombre]

    return nombre


# =========================================================
# ABRIR PROGRAMA
# =========================================================

def abrir_programa(nombre):

    global PROGRAMAS

    PROGRAMAS = cargar_programas()

    nombre_original = str(
        nombre
    ).lower().strip()

    nombre = normalizar_programa(
        nombre
    )

    print(
        "Programa solicitado:",
        nombre_original
    )

    print(
        "Programa normalizado:",
        nombre
    )

    if nombre not in PROGRAMAS:

        print(
            "No existe en programas.json"
        )

        return "No encontré ese programa"

    ruta = PROGRAMAS[nombre]

    # =====================================================
    # DISCORD DINÁMICO
    # =====================================================

    if nombre == "discord":

        ruta_discord = buscar_discord()

        if ruta_discord:

            ruta = ruta_discord

            # Actualizar automáticamente
            # programas.json
            PROGRAMAS["discord"] = ruta

            guardar_programas(
                PROGRAMAS
            )

        else:

            print(
                "❌ No pude encontrar Discord dinámicamente."
            )

            return (
                "No encuentro Discord instalado"
            )

    print(
        "Ruta encontrada:",
        ruta
    )

    if not os.path.exists(
        ruta
    ):

        print(
            "La ruta no existe:",
            ruta
        )

        return (
            f"No encuentro el archivo de {nombre}"
        )

    try:

        os.startfile(
            ruta
        )

        return (
            f"Abriendo {nombre}"
        )

    except Exception as error:

        print(
            "Error al abrir:",
            error
        )

        return (
            f"No pude abrir {nombre}"
        )


# =========================================================
# CERRAR PROGRAMA
# =========================================================

def cerrar_programa(nombre):

    nombre = normalizar_programa(
        nombre
    )

    if nombre not in PROCESOS:

        return "No encontré ese programa"

    proceso = PROCESOS[nombre]

    try:

        os.system(
            f'taskkill /im "{proceso}"'
        )

        return (
            f"Cerrando {nombre}"
        )

    except Exception as error:

        print(
            "Error al cerrar:",
            error
        )

        return (
            f"No pude cerrar {nombre}"
        )


# =========================================================
# AGREGAR PROGRAMA
# =========================================================

def agregar_programa(nombre, ruta):

    global PROGRAMAS

    PROGRAMAS = cargar_programas()

    nombre = str(
        nombre
    ).lower().strip()

    PROGRAMAS[nombre] = ruta

    if guardar_programas(
        PROGRAMAS
    ):

        print(
            f"Programa agregado: {nombre}"
        )

        print(
            f"Ruta guardada: {ruta}"
        )

        return True

    return False


# =========================================================
# ELIMINAR PROGRAMA
# =========================================================

def eliminar_programa(nombre):

    global PROGRAMAS

    PROGRAMAS = cargar_programas()

    nombre = str(
        nombre
    ).lower().strip()

    if nombre in PROGRAMAS:

        del PROGRAMAS[nombre]

        guardar_programas(
            PROGRAMAS
        )

        print(
            f"Programa eliminado: {nombre}"
        )

        return True

    return False


# =========================================================
# SELECCIONAR PROGRAMA
# =========================================================

def seleccionar_programa():

    root = tk.Tk()

    root.withdraw()

    ruta = filedialog.askopenfilename(

        title="Selecciona el programa",

        filetypes=[
            ("Programas", "*.exe"),
            ("Todos los archivos", "*.*")
        ]

    )

    root.destroy()

    return ruta


# =========================================================
# BUSCAR EN INTERNET
# =========================================================

def buscar_en_internet(programa):

    texto = str(
        programa
    ).lower().strip()

    palabras_busqueda = [

        "busca",
        "buscame",
        "búscame",
        "buscar",
        "quiero buscar",
        "quiero ver"

    ]

    es_busqueda = False

    for palabra in palabras_busqueda:

        if texto.startswith(
            palabra + " "
        ):

            es_busqueda = True
            break

    if not es_busqueda:

        return None

    es_youtube = (
        "youtube" in texto
    )

    busqueda = texto

    palabras_quitar = [

        "busca",
        "buscame",
        "búscame",
        "buscar",
        "quiero buscar",
        "quiero ver",

        "en youtube",
        "youtube",

        "en google",
        "google"

    ]

    for palabra in palabras_quitar:

        busqueda = busqueda.replace(
            palabra,
            ""
        )

    busqueda = " ".join(
        busqueda.split()
    ).strip()

    if not busqueda:

        return None

    if es_youtube:

        url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote(
                busqueda
            )
        )

        webbrowser.open(
            url
        )

        return (
            f"Buscando {busqueda} en YouTube"
        )

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(
            busqueda
        )
    )

    webbrowser.open(
        url
    )

    return (
        f"Buscando {busqueda} en Google"
    )


# =========================================================
# SEPARAR MÚLTIPLES ACCIONES
# =========================================================

def separar_acciones(comando):

    comando = str(
        comando
    ).lower().strip()

    separadores = [

        " y luego ",
        " y después ",
        " y despues ",
        " después ",
        " despues "

    ]

    partes = [
        comando
    ]

    for separador in separadores:

        nuevas_partes = []

        for parte in partes:

            nuevas_partes.extend(
                parte.split(
                    separador
                )
            )

        partes = nuevas_partes

    palabras_accion = [

        "minimiza ",
        "minimizar ",

        "maximiza ",
        "maximizar ",

        "restaura ",
        "restaurar ",

        "cambia a ",
        "cambiar a ",

        "mueve ",
        "mover ",

        "pon ",

        "abre ",
        "abrir ",

        "cierra ",
        "cerrar ",

        "escribe ",
        "escribir ",
        "escribeme ",
        "escríbeme ",

        "busca ",
        "buscar ",
        "buscame ",
        "búscame ",

        "guarda como ",
        "guardar como ",
        "guardalo como ",
        "guárdalo como ",

        "sube ",
        "baja ",

        "silencia ",

        "captura "

    ]

    resultado = []

    for parte in partes:

        texto = parte.strip()

        encontrado = False

        for accion in palabras_accion:

            marcador = " " + accion

            if marcador in texto:

                antes, despues = texto.split(
                    marcador,
                    1
                )

                if antes.strip():

                    resultado.append(
                        antes.strip()
                    )

                    resultado.append(
                        accion + despues
                    )

                    encontrado = True

                    break

        if not encontrado:

            resultado.append(
                texto
            )

    return [

        parte.strip()

        for parte in resultado

        if parte.strip()

    ]


# =========================================================
# ESCRIBIR TEXTO
# =========================================================

def escribir_texto(texto):

    try:

        time.sleep(1)

        pyautogui.write(
            texto,
            interval=0.02
        )

        return (
            f"Escribiendo: {texto}"
        )

    except Exception as error:

        print(
            "Error al escribir:",
            error
        )

        return (
            "No pude escribir el texto"
        )


# =========================================================
# GUARDAR ARCHIVO
# =========================================================

def guardar_archivo(nombre):

    try:

        nombre = str(
            nombre
        ).strip()

        if not nombre:

            return (
                "No especificaste un nombre"
            )

        nombre = os.path.basename(
            nombre
        )

        if not os.path.splitext(
            nombre
        )[1]:

            nombre += ".txt"

        ruta = os.path.join(
            CARPETA_DOCUMENTOS,
            nombre
        )

        time.sleep(0.5)

        pyautogui.hotkey(
            "ctrl",
            "shift",
            "s"
        )

        time.sleep(1)

        pyautogui.hotkey(
            "ctrl",
            "a"
        )

        pyautogui.write(
            ruta,
            interval=0.02
        )

        time.sleep(0.3)

        pyautogui.press(
            "enter"
        )

        time.sleep(1)

        return (
            f"Guardado como {nombre}"
        )

    except Exception as error:

        print(
            "Error al guardar:",
            error
        )

        return (
            "No pude guardar el archivo"
        )


# =========================================================
# NORMALIZAR PANTALLA
# =========================================================

def normalizar_pantalla(pantalla):

    pantalla = str(
        pantalla
    ).lower().strip()

    equivalencias = {

        "principal": "principal",
        "primaria": "principal",

        "primera": "1",
        "primero": "1",

        "uno": "1",
        "una": "1",
        "1": "1",

        "secundaria": "secundaria",
        "secundario": "secundaria",

        "segunda": "2",
        "segundo": "2",

        "dos": "2",
        "2": "2"

    }

    return equivalencias.get(
        pantalla,
        pantalla
    )


# =========================================================
# MOVER ENTRE MONITORES
# =========================================================

def procesar_mover_monitor(programa):

    formas = [

        "mueve ",
        "mover ",
        "pon "

    ]

    for forma in formas:

        if not programa.startswith(
            forma
        ):

            continue

        comando_mover = programa.replace(
            forma,
            "",
            1
        ).strip()

        marcadores = [

            " a la pantalla ",
            " en la pantalla ",
            " a pantalla ",
            " en pantalla "

        ]

        marcador_encontrado = None

        for marcador in marcadores:

            if marcador in comando_mover:

                marcador_encontrado = marcador
                break

        if marcador_encontrado:

            nombre, pantalla = (
                comando_mover.split(
                    marcador_encontrado,
                    1
                )
            )

            nombre = nombre.strip()

            pantalla = normalizar_pantalla(
                pantalla
            )

            print(
                "Pantalla solicitada:",
                pantalla
            )

            pantallas_validas = (
                "1",
                "2",
                "principal",
                "secundaria"
            )

            if pantalla not in pantallas_validas:

                return (
                    f"No pude mover {nombre} "
                    f"a la pantalla {pantalla}"
                )

            nombre = normalizar_nombre_ventana(
                nombre
            )

            print(
                "Ventana normalizada:",
                nombre
            )

            resultado = mover_a_monitor(
                nombre,
                pantalla
            )

            if resultado:

                return (
                    f"Moviendo {nombre} "
                    f"a la pantalla {pantalla}"
                )

            return (
                f"No pude mover {nombre} "
                f"a la pantalla {pantalla}"
            )

        marcador = " al monitor "

        if marcador in comando_mover:

            nombre, pantalla = (
                comando_mover.split(
                    marcador,
                    1
                )
            )

            nombre = nombre.strip()

            pantalla = normalizar_pantalla(
                pantalla
            )

            print(
                "Monitor solicitado:",
                pantalla
            )

            pantallas_validas = (
                "1",
                "2",
                "principal",
                "secundaria"
            )

            if pantalla not in pantallas_validas:

                return (
                    f"No pude mover {nombre} "
                    f"al monitor {pantalla}"
                )

            nombre = normalizar_nombre_ventana(
                nombre
            )

            resultado = mover_a_monitor(
                nombre,
                pantalla
            )

            if resultado:

                return (
                    f"Moviendo {nombre} "
                    f"al monitor {pantalla}"
                )

            return (
                f"No pude mover {nombre} "
                f"al monitor {pantalla}"
            )

    return None


# =========================================================
# MOVER DENTRO DEL MONITOR
# =========================================================

def procesar_mover_posicion(programa):

    formas = [

        "mueve ",
        "mover ",
        "pon "

    ]

    posiciones = [

        "izquierda",
        "derecha",
        "arriba",
        "abajo"

    ]

    for forma in formas:

        if not programa.startswith(
            forma
        ):

            continue

        comando_mover = programa.replace(
            forma,
            "",
            1
        ).strip()

        for posicion in posiciones:

            final = (
                " a la " + posicion
            )

            if comando_mover.endswith(
                final
            ):

                nombre = comando_mover[
                    :-len(final)
                ].strip()

                if nombre:

                    nombre = normalizar_nombre_ventana(
                        nombre
                    )

                    resultado = mover_a_posicion(
                        nombre,
                        posicion
                    )

                    if resultado:

                        return (
                            f"Moviendo {nombre} "
                            f"a la {posicion}"
                        )

                    return (
                        f"No pude mover {nombre} "
                        f"a la {posicion}"
                    )

            final = (
                " a " + posicion
            )

            if comando_mover.endswith(
                final
            ):

                nombre = comando_mover[
                    :-len(final)
                ].strip()

                if nombre:

                    nombre = normalizar_nombre_ventana(
                        nombre
                    )

                    resultado = mover_a_posicion(
                        nombre,
                        posicion
                    )

                    if resultado:

                        return (
                            f"Moviendo {nombre} "
                            f"a la {posicion}"
                        )

                    return (
                        f"No pude mover {nombre} "
                        f"a la {posicion}"
                    )

            final = (
                " " + posicion
            )

            if comando_mover.endswith(
                final
            ):

                nombre = comando_mover[
                    :-len(final)
                ].strip()

                if nombre:

                    nombre = normalizar_nombre_ventana(
                        nombre
                    )

                    resultado = mover_a_posicion(
                        nombre,
                        posicion
                    )

                    if resultado:

                        return (
                            f"Moviendo {nombre} "
                            f"a la {posicion}"
                        )

                    return (
                        f"No pude mover {nombre} "
                        f"a la {posicion}"
                    )

    return None


# =========================================================
# EJECUTAR COMANDO
# =========================================================

def ejecutar_comando(programa):

    programa = str(
        programa
    ).lower().strip()

    if not programa:

        return "No entendí el comando"

    # =====================================================
    # MÚLTIPLES ACCIONES
    # =====================================================

    acciones = separar_acciones(
        programa
    )

    if len(acciones) > 1:

        resultados = []

        for accion in acciones:

            accion = accion.strip()

            print(
                f"Ejecutando acción: {accion}"
            )

            resultado = ejecutar_comando(
                accion
            )

            if resultado is not None:

                resultados.append(
                    str(resultado)
                )

        if resultados:

            return ". ".join(
                resultados
            )

        return "No entendí el comando"


    # =====================================================
    # AGREGAR PROGRAMAS
    # =====================================================

    comandos_agregar = [

        "agrega un programa",
        "agregar un programa",
        "añade un programa",
        "añadir un programa",
        "agrega programa",
        "agregar programa",
        "añade programa",
        "añadir programa"

    ]

    if programa in comandos_agregar:

        return (
            "ACCION_AGREGAR_PROGRAMA"
        )


    # =====================================================
    # ELIMINAR PROGRAMAS
    # =====================================================

    comandos_eliminar = [

        "elimina ",
        "eliminar ",
        "borra ",
        "borrar ",
        "quita ",
        "quitar "

    ]

    for palabra in comandos_eliminar:

        if programa.startswith(
            palabra
        ):

            nombre = programa.replace(
                palabra,
                "",
                1
            ).strip()

            if nombre:

                return (
                    f"CONFIRMAR_ELIMINAR:{nombre}"
                )


    # =====================================================
    # INTERNET
    # =====================================================

    resultado = buscar_en_internet(
        programa
    )

    if resultado:

        return str(resultado)


    # =====================================================
    # CERRAR
    # =====================================================

    if programa.startswith(
        "cierra "
    ):

        nombre = programa.replace(
            "cierra ",
            "",
            1
        ).strip()

        nombre_ventana = (
            normalizar_nombre_ventana(
                nombre
            )
        )

        resultado = cerrar_ventana(
            nombre_ventana
        )

        if resultado:

            return (
                f"Cerrando {nombre}"
            )

        return cerrar_programa(
            nombre
        )


    if programa.startswith(
        "cerrar "
    ):

        nombre = programa.replace(
            "cerrar ",
            "",
            1
        ).strip()

        nombre_ventana = (
            normalizar_nombre_ventana(
                nombre
            )
        )

        resultado = cerrar_ventana(
            nombre_ventana
        )

        if resultado:

            return (
                f"Cerrando {nombre}"
            )

        return cerrar_programa(
            nombre
        )


    # =====================================================
    # MOVER ENTRE MONITORES
    # =====================================================

    resultado_monitor = (
        procesar_mover_monitor(
            programa
        )
    )

    if resultado_monitor is not None:

        return str(
            resultado_monitor
        )


    # =====================================================
    # MOVER DERECHA / IZQUIERDA / ARRIBA / ABAJO
    # =====================================================

    resultado_posicion = (
        procesar_mover_posicion(
            programa
        )
    )

    if resultado_posicion is not None:

        return str(
            resultado_posicion
        )


    # =====================================================
    # MINIMIZAR
    # =====================================================

    if programa.startswith(
        "minimiza "
    ):

        nombre = programa.replace(
            "minimiza ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = minimizar_ventana(
            nombre
        )

        if resultado:

            return (
                f"Minimizando {nombre}"
            )

        return (
            f"No pude minimizar {nombre}"
        )


    if programa.startswith(
        "minimizar "
    ):

        nombre = programa.replace(
            "minimizar ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = minimizar_ventana(
            nombre
        )

        if resultado:

            return (
                f"Minimizando {nombre}"
            )

        return (
            f"No pude minimizar {nombre}"
        )


    # =====================================================
    # MAXIMIZAR
    # =====================================================

    if programa.startswith(
        "maximiza "
    ):

        nombre = programa.replace(
            "maximiza ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = maximizar_ventana(
            nombre
        )

        if resultado:

            return (
                f"Maximizando {nombre}"
            )

        return (
            f"No pude maximizar {nombre}"
        )


    if programa.startswith(
        "maximizar "
    ):

        nombre = programa.replace(
            "maximizar ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = maximizar_ventana(
            nombre
        )

        if resultado:

            return (
                f"Maximizando {nombre}"
            )

        return (
            f"No pude maximizar {nombre}"
        )


    # =====================================================
    # RESTAURAR
    # =====================================================

    if programa.startswith(
        "restaura "
    ):

        nombre = programa.replace(
            "restaura ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = restaurar_ventana(
            nombre
        )

        if resultado:

            return (
                f"Restaurando {nombre}"
            )

        return (
            f"No pude restaurar {nombre}"
        )


    if programa.startswith(
        "restaurar "
    ):

        nombre = programa.replace(
            "restaurar ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = restaurar_ventana(
            nombre
        )

        if resultado:

            return (
                f"Restaurando {nombre}"
            )

        return (
            f"No pude restaurar {nombre}"
        )


    # =====================================================
    # CAMBIAR A VENTANA
    # =====================================================

    if programa.startswith(
        "cambia a "
    ):

        nombre = programa.replace(
            "cambia a ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = cambiar_a_ventana(
            nombre
        )

        if resultado:

            return (
                f"Cambiando a {nombre}"
            )

        return (
            f"No pude cambiar a {nombre}"
        )


    if programa.startswith(
        "cambiar a "
    ):

        nombre = programa.replace(
            "cambiar a ",
            "",
            1
        ).strip()

        nombre = normalizar_nombre_ventana(
            nombre
        )

        resultado = cambiar_a_ventana(
            nombre
        )

        if resultado:

            return (
                f"Cambiando a {nombre}"
            )

        return (
            f"No pude cambiar a {nombre}"
        )


    # =====================================================
    # ESCRIBIR
    # =====================================================

    formas_escribir = [

        "escribe ",
        "escribir ",
        "escribeme ",
        "escríbeme "

    ]

    for forma in formas_escribir:

        if programa.startswith(
            forma
        ):

            texto = programa.replace(
                forma,
                "",
                1
            ).strip()

            if texto:

                return escribir_texto(
                    texto
                )

            return (
                "No especificaste qué escribir"
            )


    # =====================================================
    # GUARDAR COMO
    # =====================================================

    formas_guardar = [

        "guarda como ",
        "guardar como ",
        "guardalo como ",
        "guárdalo como "

    ]

    for forma in formas_guardar:

        if programa.startswith(
            forma
        ):

            nombre = programa.replace(
                forma,
                "",
                1
            ).strip()

            if nombre:

                return guardar_archivo(
                    nombre
                )

            return (
                "No especificaste un nombre "
                "para guardar"
            )


    # =====================================================
    # ABRIR
    # =====================================================

    if programa.startswith(
        "abre "
    ):

        nombre = programa.replace(
            "abre ",
            "",
            1
        ).strip()

        return abrir_programa(
            nombre
        )


    if programa.startswith(
        "abrir "
    ):

        nombre = programa.replace(
            "abrir ",
            "",
            1
        ).strip()

        return abrir_programa(
            nombre
        )


    # =====================================================
    # VOLUMEN
    # =====================================================

    if (
        "sube" in programa
        and "volumen" in programa
    ):

        pyautogui.press(
            "volumeup"
        )

        pyautogui.press(
            "volumeup"
        )

        return "Subiendo volumen"


    if (
        "baja" in programa
        and "volumen" in programa
    ):

        pyautogui.press(
            "volumedown"
        )

        pyautogui.press(
            "volumedown"
        )

        return "Bajando volumen"


    if (
        "silencio" in programa
        or "silencia" in programa
    ):

        pyautogui.press(
            "volumemute"
        )

        return "Silenciando volumen"


    # =====================================================
    # MULTIMEDIA
    # =====================================================

    if (
        "siguiente" in programa
        and "canción" in programa
    ):

        pyautogui.press(
            "nexttrack"
        )

        return "Siguiente canción"


    if (
        "canción" in programa
        and "anterior" in programa
    ):

        pyautogui.press(
            "prevtrack"
        )

        return "Canción anterior"


    if (
        "pausar" in programa
        and "música" in programa
    ):

        pyautogui.press(
            "playpause"
        )

        return "Pausando música"


    if (
        "reproducir" in programa
        and "música" in programa
    ):

        pyautogui.press(
            "playpause"
        )

        return "Reproduciendo música"


    # =====================================================
    # CAPTURA
    # =====================================================

    if (
        "captura" in programa
        and "pantalla" in programa
    ):

        pyautogui.hotkey(
            "win",
            "shift",
            "s"
        )

        return "Capturando pantalla"


    # =====================================================
    # NO ENTENDIDO
    # =====================================================

    return "No entendí el comando"