import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERFIL_FILE = os.path.join(BASE_DIR, "perfil_lenguaje.json")


def cargar_perfil():
    if not os.path.exists(PERFIL_FILE):
        perfil = {
            "correcciones": {},
            "expresiones": {}
        }

        guardar_perfil(perfil)
        return perfil

    try:
        with open(PERFIL_FILE, "r", encoding="utf-8") as archivo:
            perfil = json.load(archivo)

    except Exception as error:
        print(f"⚠️ No pude leer el perfil de lenguaje: {error}")

        perfil = {
            "correcciones": {},
            "expresiones": {}
        }

    perfil.setdefault("correcciones", {})
    perfil.setdefault("expresiones", {})

    return perfil


def guardar_perfil(perfil):
    try:
        with open(PERFIL_FILE, "w", encoding="utf-8") as archivo:
            json.dump(
                perfil,
                archivo,
                ensure_ascii=False,
                indent=4
            )

        return True

    except Exception as error:
        print(f"⚠️ No pude guardar el perfil de lenguaje: {error}")
        return False


def obtener_aprendizaje():
    perfil = cargar_perfil()

    return {
        "correcciones": perfil.get("correcciones", {}),
        "expresiones": perfil.get("expresiones", {})
    }


def registrar_correccion(original, correcto):
    original = str(original).lower().strip()
    correcto = str(correcto).lower().strip()

    if not original or not correcto:
        return False

    perfil = cargar_perfil()

    perfil["correcciones"][original] = correcto

    return guardar_perfil(perfil)


def registrar_expresion(expresion, significado):
    expresion = str(expresion).lower().strip()
    significado = str(significado).lower().strip()

    if not expresion or not significado:
        return False

    perfil = cargar_perfil()

    perfil["expresiones"][expresion] = significado

    return guardar_perfil(perfil)


def eliminar_aprendizaje(texto):
    texto = str(texto).lower().strip()

    perfil = cargar_perfil()

    eliminado = False

    if texto in perfil["correcciones"]:
        del perfil["correcciones"][texto]
        eliminado = True

    if texto in perfil["expresiones"]:
        del perfil["expresiones"][texto]
        eliminado = True

    if eliminado:
        guardar_perfil(perfil)

    return eliminado