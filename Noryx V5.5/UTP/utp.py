import json
import os
import time
from datetime import datetime

from playwright.sync_api import sync_playwright


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_URL = "https://class.utp.edu.pe"

CARPETA_UTP = os.path.dirname(os.path.abspath(__file__))

CREDENCIALES_FILE = os.path.join(
    CARPETA_UTP,
    "credenciales.json"
)

ACTIVIDADES_FILE = os.path.join(
    CARPETA_UTP,
    "actividades_utp.json"
)

# Tiempo máximo para cargar/login
TIMEOUT = 60000

# Tiempo máximo buscando actividades después del login
TIEMPO_BUSQUEDA = 25


# ============================================================
# JSON
# ============================================================

def cargar_json(ruta, valor_default=None):
    """
    Carga un archivo JSON.
    Si no existe o está dañado devuelve valor_default.
    """

    if not os.path.exists(ruta):
        return valor_default

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except Exception as e:
        print(f"⚠️ No se pudo leer {ruta}")
        print(f"   {e}")
        return valor_default


def guardar_json(ruta, datos):
    """
    Guarda información en JSON.
    """

    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=4
            )

        return True

    except Exception as e:
        print(f"❌ Error guardando JSON:")
        print(e)
        return False


# ============================================================
# CREDENCIALES
# ============================================================

def cargar_credenciales():
    """
    Obtiene usuario y contraseña desde credenciales.json.
    """

    datos = cargar_json(
        CREDENCIALES_FILE,
        {}
    )

    if not isinstance(datos, dict):
        print("❌ credenciales.json no tiene un formato válido.")
        return None

    usuario = str(
        datos.get("usuario", "")
    ).strip()

    contrasena = str(
        datos.get("contrasena", "")
    )

    if not usuario:
        print("❌ Falta el usuario en credenciales.json.")
        return None

    if not contrasena:
        print("❌ Falta la contraseña en credenciales.json.")
        return None

    return {
        "usuario": usuario,
        "contrasena": contrasena
    }


# ============================================================
# ACTIVIDADES LOCALES
# ============================================================

def cargar_actividades():
    """
    Devuelve las actividades guardadas localmente.

    IMPORTANTE:
    Esta función NO abre UTP+Class.
    """

    datos = cargar_json(
        ACTIVIDADES_FILE,
        {
            "ultima_actualizacion": None,
            "actividades": []
        }
    )

    if not isinstance(datos, dict):
        return {
            "ultima_actualizacion": None,
            "actividades": []
        }

    actividades = datos.get("actividades", [])

    if not isinstance(actividades, list):
        actividades = []

    return {
        "ultima_actualizacion": datos.get(
            "ultima_actualizacion"
        ),
        "actividades": actividades
    }


def guardar_actividades(actividades):
    """
    Guarda las actividades obtenidas desde UTP+Class.
    """

    datos = {
        "ultima_actualizacion": datetime.now().isoformat(
            timespec="seconds"
        ),
        "actividades": actividades
    }

    return guardar_json(
        ACTIVIDADES_FILE,
        datos
    )


def obtener_actividades_guardadas():
    """
    Función para Cerebro/Agenda.

    NO entra a UTP.
    """

    datos = cargar_actividades()

    return datos["actividades"]


# ============================================================
# DETECCIÓN DE LOGIN
# ============================================================

def parece_pagina_login(page):
    """
    Intenta determinar si estamos viendo el formulario
    de inicio de sesión.
    """

    try:
        url = page.url.lower()

        if "login" in url:
            return True

        if "signin" in url:
            return True

        if "auth" in url:
            return True

        texto = page.locator("body").inner_text(
            timeout=5000
        ).lower()

        palabras = [
            "iniciar sesión",
            "iniciar sesion",
            "usuario",
            "contraseña",
            "contrasena",
            "password"
        ]

        coincidencias = 0

        for palabra in palabras:
            if palabra in texto:
                coincidencias += 1

        return coincidencias >= 2

    except Exception:
        return False


# ============================================================
# RELLENAR LOGIN
# ============================================================

def buscar_campo_usuario(page):
    """
    Busca el campo real de usuario en la página y sus iframes.
    """

    selectores = [
        'input[type="email"]',
        'input[type="text"]',
        'input[name="username"]',
        'input[name="user"]',
        'input[name="usuario"]',
        'input[id="username"]',
        'input[id="user"]',
        'input[id="usuario"]',
        'input[placeholder*="usuario" i]',
        'input[placeholder*="correo" i]',
        'input[placeholder*="email" i]',
    ]

    # Página principal
    for selector in selectores:
        try:
            elementos = page.locator(selector)

            for i in range(elementos.count()):
                campo = elementos.nth(i)

                if campo.is_visible():
                    print(
                        f"🔎 Usuario encontrado: "
                        f"{selector}"
                    )
                    return campo

        except Exception:
            pass

    # Iframes
    for frame in page.frames:

        if frame == page.main_frame:
            continue

        for selector in selectores:
            try:
                elementos = frame.locator(selector)

                for i in range(elementos.count()):
                    campo = elementos.nth(i)

                    if campo.is_visible():
                        print(
                            f"🔎 Usuario encontrado "
                            f"en iframe: {selector}"
                        )
                        return campo

            except Exception:
                pass

    return None


def buscar_campo_password(page):
    """
    Busca el campo real de contraseña en la página
    y sus iframes.
    """

    selectores = [
        'input[type="password"]',
        'input[name="password"]',
        'input[name="contrasena"]',
        'input[name="contraseña"]',
        'input[id="password"]',
        'input[id="contrasena"]',
        'input[id="contraseña"]',
    ]

    # Página principal
    for selector in selectores:
        try:
            elementos = page.locator(selector)

            for i in range(elementos.count()):
                campo = elementos.nth(i)

                if campo.is_visible():
                    print(
                        f"🔎 Contraseña encontrada: "
                        f"{selector}"
                    )
                    return campo

        except Exception:
            pass

    # Iframes
    for frame in page.frames:

        if frame == page.main_frame:
            continue

        for selector in selectores:
            try:
                elementos = frame.locator(selector)

                for i in range(elementos.count()):
                    campo = elementos.nth(i)

                    if campo.is_visible():
                        print(
                            f"🔎 Contraseña encontrada "
                            f"en iframe: {selector}"
                        )
                        return campo

            except Exception:
                pass

    return None


def buscar_boton_login(page):
    """
    Busca el botón real de inicio de sesión.
    """

    selectores = [
        'button[type="submit"]',
        'input[type="submit"]',

        'button:has-text("Iniciar sesión")',
        'button:has-text("Iniciar sesion")',
        'button:has-text("Ingresar")',
        'button:has-text("Acceder")',
        'button:has-text("Continuar")',
        'button:has-text("Login")',

        '[role="button"]:has-text("Ingresar")',
        '[role="button"]:has-text("Acceder")',
        '[role="button"]:has-text("Iniciar sesión")',
        '[role="button"]:has-text("Iniciar sesion")',
    ]

    # Página principal
    for selector in selectores:
        try:
            elementos = page.locator(selector)

            for i in range(elementos.count()):
                boton = elementos.nth(i)

                if boton.is_visible():
                    print(
                        f"🔎 Botón login encontrado: "
                        f"{selector}"
                    )
                    return boton

        except Exception:
            pass

    # Iframes
    for frame in page.frames:

        if frame == page.main_frame:
            continue

        for selector in selectores:
            try:
                elementos = frame.locator(selector)

                for i in range(elementos.count()):
                    boton = elementos.nth(i)

                    if boton.is_visible():
                        print(
                            f"🔎 Botón login encontrado "
                            f"en iframe: {selector}"
                        )
                        return boton

            except Exception:
                pass

    return None


def iniciar_sesion(page, credenciales):
    """
    Inicia sesión con credenciales.json.
    """

    print()
    print("🔐 Comprobando inicio de sesión...")

    # Esperamos a que aparezca realmente el formulario
    page.wait_for_timeout(3000)

    print(f"📍 URL actual: {page.url}")

    usuario = buscar_campo_usuario(page)
    password = buscar_campo_password(page)

    if usuario is None:
        print("❌ NO encontré el campo de usuario.")

        # Diagnóstico
        print()
        print("🔍 INPUTS QUE VE PLAYWRIGHT:")

        try:
            inputs = page.locator("input")
            cantidad = inputs.count()

            print(f"Cantidad de inputs: {cantidad}")

            for i in range(cantidad):

                elemento = inputs.nth(i)

                try:
                    print(
                        f"  [{i}] "
                        f"type={elemento.get_attribute('type')} "
                        f"name={elemento.get_attribute('name')} "
                        f"id={elemento.get_attribute('id')} "
                        f"placeholder={elemento.get_attribute('placeholder')}"
                    )
                except Exception:
                    pass

        except Exception as e:
            print(e)

        return False

    if password is None:
        print("❌ NO encontré el campo de contraseña.")
        return False

    try:

        print("✍️ Escribiendo usuario...")

        usuario.click()
        usuario.fill(
            credenciales["usuario"]
        )

        print("✅ Usuario escrito.")

        print("✍️ Escribiendo contraseña...")

        password.click()
        password.fill(
            credenciales["contrasena"]
        )

        print("✅ Contraseña escrita.")

    except Exception as e:

        print("❌ Error escribiendo las credenciales:")
        print(e)

        return False

    boton = buscar_boton_login(page)

    if boton is None:
        print("❌ NO encontré el botón de login.")
        return False

    try:

        print("🚀 Pulsando iniciar sesión...")

        boton.click()

        page.wait_for_timeout(5000)

        print()
        print("📍 URL después del login:")
        print(page.url)

        return True

    except Exception as e:

        print("❌ Error pulsando login:")
        print(e)

        return False


# ============================================================
# CAPTURA DE RESPUESTAS
# ============================================================

def instalar_capturador(page):
    """
    Captura respuestas JSON de UTP+Class.

    No asumimos todavía un endpoint concreto.
    Guardamos respuestas que parezcan contener actividades.
    """

    capturas = []

    def manejar_response(response):

        try:

            content_type = response.headers.get(
                "content-type",
                ""
            ).lower()

            if "json" not in content_type:
                return

            texto = response.text()

            if not texto:
                return

            datos = json.loads(texto)

            if not isinstance(datos, (dict, list)):
                return

            url = response.url.lower()

            # Palabras que nos ayudan a localizar
            # respuestas relacionadas con actividades.
            palabras = [
                "activity",
                "activities",
                "actividad",
                "actividades",
                "task",
                "tasks",
                "tarea",
                "tareas",
                "assignment",
                "assignments",
                "course",
                "courses"
            ]

            parece_relacionado = any(
                palabra in url
                for palabra in palabras
            )

            # También examinamos las claves principales.
            if isinstance(datos, dict):

                claves = " ".join(
                    str(k).lower()
                    for k in datos.keys()
                )

                if any(
                    palabra in claves
                    for palabra in palabras
                ):
                    parece_relacionado = True

            if not parece_relacionado:
                return

            captura = {
                "url": response.url,
                "datos": datos
            }

            capturas.append(captura)

            print()
            print("📡 Respuesta UTP detectada:")
            print(response.url)

        except Exception:
            pass

    page.on(
        "response",
        manejar_response
    )

    return capturas


# ============================================================
# EXTRAER ACTIVIDADES
# ============================================================

def buscar_listas(datos):
    """
    Busca recursivamente listas dentro de una respuesta JSON.
    """

    listas = []

    if isinstance(datos, list):

        listas.append(datos)

        for elemento in datos:
            listas.extend(
                buscar_listas(elemento)
            )

    elif isinstance(datos, dict):

        for valor in datos.values():
            listas.extend(
                buscar_listas(valor)
            )

    return listas


def parece_actividad(elemento):
    """
    Determina si un objeto parece representar
    una actividad/tarea.

    Esta función es deliberadamente flexible porque
    todavía estamos descubriendo la estructura real.
    """

    if not isinstance(elemento, dict):
        return False

    claves = {
        str(k).lower()
        for k in elemento.keys()
    }

    indicadores = [
        "activityid",
        "assignmentid",
        "taskid",
        "activityname",
        "assignmentname",
        "taskname",
        "activitytitle",
        "assignmenttitle",
        "tasktitle",
        "duedate",
        "deliverydate",
        "fechaentrega",
        "fechalimite"
    ]

    coincidencias = 0

    for indicador in indicadores:

        if indicador in claves:
            coincidencias += 1

    return coincidencias >= 1


def extraer_actividades(capturas):
    """
    Intenta encontrar actividades dentro de las
    respuestas capturadas.
    """

    encontradas = []

    for captura in capturas:

        datos = captura["datos"]

        listas = buscar_listas(datos)

        for lista in listas:

            for elemento in lista:

                if not parece_actividad(elemento):
                    continue

                actividad = dict(elemento)

                # Guardamos también de dónde salió.
                actividad["_origen_url"] = captura["url"]

                encontradas.append(
                    actividad
                )

    return encontradas


# ============================================================
# NAVEGACIÓN
# ============================================================

def navegar_para_cargar_actividades(page):
    """
    Después del login intenta localizar las páginas
    relacionadas con cursos/actividades.

    Primero deja que la aplicación cargue normalmente.
    """

    print()
    print("📚 Cargando contenido de UTP+Class...")

    try:
        page.wait_for_load_state(
            "networkidle",
            timeout=15000
        )
    except Exception:
        pass

    page.wait_for_timeout(3000)

    # Por ahora NO hacemos clic a botones arbitrariamente.
    #
    # Primero queremos observar las peticiones que hace
    # la aplicación al entrar.
    #
    # Esto evita volver a romper el login como ocurrió
    # anteriormente.

    print("🔎 Observando las peticiones de UTP+Class...")


# ============================================================
# ACTUALIZAR UTP
# ============================================================

def actualizar_actividades():
    """
    FUNCIÓN PRINCIPAL DE ACTUALIZACIÓN.

    Esta es la función que debe utilizar Noryx cuando
    el usuario diga:

        "actualiza mis tareas"

    o

        "busca si tengo nuevas tareas"

    Esta función SÍ entra a UTP+Class.
    """

    print()
    print("=" * 60)
    print("       ACTUALIZANDO ACTIVIDADES UTP")
    print("=" * 60)

    credenciales = cargar_credenciales()

    if credenciales is None:
        print()
        print("❌ No puedo actualizar UTP.")
        print("   Revisa UTP/credenciales.json")
        return False

    print("🔐 Credenciales encontradas.")

    with sync_playwright() as p:

        browser = None

        try:

            print()
            print("🌐 Abriendo UTP+Class...")

            browser = p.chromium.launch(
                headless=True
            )

            context = browser.new_context()

            page = context.new_page()

            capturas = instalar_capturador(page)

            print(f"📍 Abriendo: {BASE_URL}")

            page.goto(
                BASE_URL,
                wait_until="domcontentloaded",
                timeout=TIMEOUT
            )

            print(f"📍 URL inicial: {page.url}")

            # ------------------------------------------------
            # LOGIN
            # ------------------------------------------------

            if not iniciar_sesion(
                page,
                credenciales
            ):
                print()
                print("❌ No se pudo iniciar sesión.")
                return False

            # ------------------------------------------------
            # CARGAR ACTIVIDADES
            # ------------------------------------------------

            navegar_para_cargar_actividades(
                page
            )

            # ------------------------------------------------
            # ESPERAR RESPUESTAS
            # ------------------------------------------------

            print()
            print(
                f"⏳ Esperando datos "
                f"({TIEMPO_BUSQUEDA}s)..."
            )

            limite = (
                time.time()
                + TIEMPO_BUSQUEDA
            )

            actividades = []

            while time.time() < limite:

                actividades = extraer_actividades(
                    capturas
                )

                if actividades:
                    break

                page.wait_for_timeout(500)

            # ------------------------------------------------
            # RESULTADO
            # ------------------------------------------------

            if not actividades:

                print()
                print("⚠️ No encontré actividades todavía.")
                print()
                print(
                    f"📡 Respuestas JSON capturadas: "
                    f"{len(capturas)}"
                )

                # No borramos actividades anteriores.
                print(
                    "📦 Las actividades anteriores "
                    "se conservarán."
                )

                return False

            # ------------------------------------------------
            # GUARDAR
            # ------------------------------------------------

            print()
            print(
                f"✅ Actividades encontradas: "
                f"{len(actividades)}"
            )

            if not guardar_actividades(
                actividades
            ):
                return False

            print()
            print("💾 actividades_utp.json actualizado.")
            print("=" * 60)

            return actividades

        except Exception as e:

            print()
            print("❌ Error conectando con UTP+Class:")
            print(e)

            return False

        finally:

            if browser is not None:

                try:
                    browser.close()

                except Exception:
                    pass


# ============================================================
# FUNCIONES PARA CEREBRO / AGENDA
# ============================================================

def hay_actividades():
    """
    Comprueba si existen actividades guardadas.

    NO entra a UTP.
    """

    actividades = obtener_actividades_guardadas()

    return len(actividades) > 0


def ultima_actualizacion():
    """
    Devuelve la fecha de la última actualización.

    NO entra a UTP.
    """

    datos = cargar_actividades()

    return datos.get(
        "ultima_actualizacion"
    )


def obtener_resumen_actividades():
    """
    Devuelve información básica de las actividades guardadas.

    NO entra a UTP.
    """

    actividades = obtener_actividades_guardadas()

    return {
        "cantidad": len(actividades),
        "ultima_actualizacion": ultima_actualizacion(),
        "actividades": actividades
    }

# ============================================================
# COMPATIBILIDAD CON CEREBRO / AGENDA
# ============================================================

def obtener_actividades(force=False):
    """
    Devuelve las actividades guardadas localmente.

    NO entra a UTP+Class.

    force se mantiene por compatibilidad con Cerebro.
    Actualmente no provoca una actualización automática.
    """
    return obtener_actividades_guardadas()


def actualizar_utp():
    """
    Actualiza las actividades entrando a UTP+Class.

    SÍ entra a UTP+Class.
    """
    return actualizar_actividades()


def obtener_estado_utp():
    """
    Devuelve el estado de las actividades guardadas.

    NO entra a UTP+Class.
    """
    datos = cargar_actividades()

    actividades = datos.get(
        "actividades",
        []
    )

    return {
        "disponible": len(actividades) > 0,
        "cantidad": len(actividades),
        "ultima_actualizacion": datos.get(
            "ultima_actualizacion"
        )
    }

# ============================================================
# PRUEBA DIRECTA
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("           PRUEBA DEL MÓDULO UTP")
    print("=" * 60)

    print()
    print("¿Qué quieres probar?")
    print()
    print("1. Ver actividades guardadas")
    print("2. Actualizar desde UTP+Class")
    print("3. Verificar credenciales")
    print()

    opcion = input(
        "Selecciona una opción: "
    ).strip()

    # --------------------------------------------------------
    # ACTIVIDADES LOCALES
    # --------------------------------------------------------

    if opcion == "1":

        datos = cargar_actividades()

        print()
        print("📦 ACTIVIDADES GUARDADAS")
        print("-" * 60)

        print(
            "Última actualización:",
            datos["ultima_actualizacion"]
        )

        print(
            "Cantidad:",
            len(datos["actividades"])
        )

        for actividad in datos["actividades"]:

            print()
            print(
                json.dumps(
                    actividad,
                    ensure_ascii=False,
                    indent=2
                )
            )

    # --------------------------------------------------------
    # ACTUALIZAR UTP
    # --------------------------------------------------------

    elif opcion == "2":

        actualizar_actividades()

    # --------------------------------------------------------
    # CREDENCIALES
    # --------------------------------------------------------

    elif opcion == "3":

        credenciales = cargar_credenciales()

        print()

        if credenciales:

            print("✅ credenciales.json está configurado.")
            print(
                "👤 Usuario:",
                credenciales["usuario"]
            )
            print("🔒 Contraseña: configurada")

        else:

            print(
                "❌ credenciales.json necesita "
                "ser configurado."
            )

    else:

        print("❌ Opción no válida.")

    print()
    print("=" * 60)
    print("FIN DE LA PRUEBA")
    print("=" * 60)

