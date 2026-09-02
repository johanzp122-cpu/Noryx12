from acciones import (
    ejecutar_comando,
    obtener_ultima_correccion,
    limpiar_ultima_correccion
)

from IA.ia import preguntar_ia
from IA.agente import analizar_intencion, validar_intencion

from memoria import agregar_recuerdo

from LENGUAJE.normalizador import normalizar_texto
from LENGUAJE.interpretador import interpretar_comando

from LENGUAJE.aprendizaje import (
    registrar_correccion,
    registrar_expresion,
    eliminar_aprendizaje
)

from agenda import (
    obtener_eventos_hoy,
    crear_evento,
    crear_evento_utp
)

from UTP.utp import (
    obtener_actividades,
    actualizar_utp,
    obtener_estado_utp
)

import re
from datetime import datetime


class CerebroNoryx:

    def __init__(self):
        self.ultimo_programa = None
        self.ultima_ventana = None
        self.ventanas_recientes = []
        self.ultima_accion = None
        self.ultimo_comando = None
        self.contexto = {}

    def limpiar_estado(self):
        self.ultimo_programa = None
        self.ultima_ventana = None
        self.ultima_accion = None
        self.ultimo_comando = None
        self.ventanas_recientes = []

    # =========================================================
    # PROCESAR COMANDO PRINCIPAL
    # =========================================================

    def procesar(self, texto):

        texto_original = texto

        # =====================================================
        # NORMALIZACIÓN
        # =====================================================

        texto = normalizar_texto(texto)

        print(f"🧹 Comando normalizado: {texto}")

        # =====================================================
        # INTERPRETADOR
        # =====================================================

        resultado_lenguaje = interpretar_comando(texto)

        # Seguridad:
        # interpretar_comando debe devolver un diccionario.
        # Si por alguna razón devuelve True/False, no rompemos Noryx.
        if not isinstance(resultado_lenguaje, dict):
            resultado_lenguaje = {
                "texto": texto,
                "cambio": False,
                "original": "",
                "corregido": "",
                "confianza": 0
            }

        texto_interpretado = resultado_lenguaje.get(
            "texto",
            texto
        )

        if resultado_lenguaje.get("cambio"):

            print(
                f"🧠 Corrección aprendida: "
                f"{texto} → {texto_interpretado}"
            )

            texto = texto_interpretado

        # =====================================================
        # APRENDER EXPLÍCITAMENTE
        # =====================================================

        texto_lower = texto.lower().strip()

        # -----------------------------------------------------
        # Aprende que X significa Y
        # -----------------------------------------------------

        coincidencia = re.match(
            r"^aprende que (.+?) significa (.+)$",
            texto_lower
        )

        if coincidencia:

            expresion = coincidencia.group(1).strip()
            significado = coincidencia.group(2).strip()

            if registrar_expresion(
                expresion,
                significado
            ):

                return {
                    "tipo": "respuesta",
                    "texto": (
                        f"Entendido. Cuando digas "
                        f"{expresion}, entenderé "
                        f"{significado}."
                    )
                }

            return {
                "tipo": "respuesta",
                "texto": "No pude guardar ese aprendizaje."
            }

        # -----------------------------------------------------
        # Aprende que X se escribe Y
        # -----------------------------------------------------

        coincidencia = re.match(
            r"^aprende que (.+?) se escribe (.+)$",
            texto_lower
        )

        if coincidencia:

            original = coincidencia.group(1).strip()
            correcto = coincidencia.group(2).strip()

            if registrar_correccion(
                original,
                correcto
            ):

                return {
                    "tipo": "respuesta",
                    "texto": (
                        f"Entendido. Si dices "
                        f"{original}, entenderé "
                        f"{correcto}."
                    )
                }

            return {
                "tipo": "respuesta",
                "texto": "No pude guardar esa corrección."
            }

        # -----------------------------------------------------
        # Olvida X
        # -----------------------------------------------------

        coincidencia = re.match(
            r"^olvida (.+)$",
            texto_lower
        )

        if coincidencia:

            expresion = coincidencia.group(1).strip()

            if eliminar_aprendizaje(expresion):

                return {
                    "tipo": "respuesta",
                    "texto": (
                        f"Listo. Olvidé lo relacionado "
                        f"con {expresion}."
                    )
                }

            return {
                "tipo": "respuesta",
                "texto": (
                    f"No tenía ningún aprendizaje "
                    f"guardado para {expresion}."
                )
            }

        # =====================================================
        # ATAJOS DIRECTOS DE AGENDA
        # =====================================================

        if (
            "qué tengo en mi agenda" in texto_lower
            or "que tengo en mi agenda" in texto_lower
            or "qué hay en mi agenda" in texto_lower
            or "que hay en mi agenda" in texto_lower
            or "muéstrame mi agenda" in texto_lower
            or "muestrame mi agenda" in texto_lower
            or "qué eventos tengo hoy" in texto_lower
            or "que eventos tengo hoy" in texto_lower
        ):

            return {
                "tipo": "respuesta",
                "texto": obtener_eventos_hoy()
            }

        # =====================================================
        # SELECCIÓN DE ACTIVIDAD PENDIENTE
        # =====================================================

        seleccion = self.procesar_seleccion_agenda(texto)

        if seleccion:
            return seleccion

        # =====================================================
        # AGENTE IA
        # =====================================================

        try:

            intencion = analizar_intencion(
                texto,
                contexto=self.contexto
            )

            # Seguridad:
            # validar_intencion puede devolver False.
            # Solo usamos .get() más abajo si realmente tenemos dict.
            validada = validar_intencion(intencion)

            if isinstance(validada, dict):
                intencion = validada
            elif isinstance(intencion, dict):
                # Si validar_intencion solo devuelve True/False
                # para indicar si es válida, conservamos el dict original.
                if validada is False:
                    intencion = None
            else:
                intencion = None

        except Exception as error:

            print(
                f"⚠️ Error analizando intención: {error}"
            )

            intencion = None

        # =====================================================
        # EJECUTAR INTENCIÓN DEL AGENTE
        # =====================================================

        if isinstance(intencion, dict):

            accion = intencion.get(
                "accion"
            )

            parametros = intencion.get(
                "parametros",
                {}
            )

            if accion in (
                "consultar_actividades_utp",
                "actualizar_actividades_utp",
                "agregar_actividad_agenda",
                "consultar_agenda",
                "crear_evento"
            ):

                return self.ejecutar_intencion(
                    accion,
                    parametros
                )

        # =====================================================
        # CREAR EVENTO NORMAL
        # =====================================================

        if texto_lower.startswith(
            (
                "crea un evento",
                "crear un evento",
                "agrega un evento",
                "agregar un evento"
            )
        ):

            return self.procesar_crear_evento(
                texto
            )

        # =====================================================
        # EJECUTAR COMANDO LOCAL
        # =====================================================

        resultado = ejecutar_comando(
            texto
        )

        # =====================================================
        # APRENDIZAJE AUTOMÁTICO DE CORRECCIONES
        # =====================================================

        correccion = obtener_ultima_correccion()

        if isinstance(correccion, dict):

            original = correccion.get(
                "original",
                ""
            )

            corregido = correccion.get(
                "corregido",
                ""
            )

            if original and corregido:

                print(
                    f"🧠 Aprendizaje automático: "
                    f"{original} → {corregido}"
                )

                registrar_correccion(
                    original,
                    corregido
                )

                limpiar_ultima_correccion()

        # =====================================================
        # GUARDAR CONTEXTO
        # =====================================================

        self.contexto["ultimo_comando"] = texto_original
        self.contexto["ultimo_resultado"] = resultado

        # =====================================================
        # SI EL COMANDO LOCAL FUNCIONÓ
        # =====================================================

        if resultado:

            if isinstance(resultado, dict):

                if resultado.get("tipo"):
                    return resultado

            return {
                "tipo": "respuesta",
                "texto": str(resultado)
            }

        # =====================================================
        # VENTANAS / MONITORES
        # =====================================================

        if any(
            palabra in texto_lower
            for palabra in (
                "ventana",
                "monitor",
                "pantalla"
            )
        ):

            resultado_ventana = ejecutar_comando(
                texto
            )

            if resultado_ventana:

                return {
                    "tipo": "respuesta",
                    "texto": str(
                        resultado_ventana
                    )
                }

        # =====================================================
        # IA COMO ÚLTIMO RECURSO
        # =====================================================

        try:

            respuesta_ia = preguntar_ia(
                texto
            )

            if respuesta_ia:

                return {
                    "tipo": "respuesta",
                    "texto": respuesta_ia
                }

        except Exception as error:

            print(
                f"⚠️ Error usando IA: {error}"
            )

        # =====================================================
        # NO ENTENDIDO
        # =====================================================

        return {
            "tipo": "respuesta",
            "texto": "No entendí el comando."
        }

    # =========================================================
    # EJECUTAR INTENCIÓN
    # =========================================================

    def ejecutar_intencion(
        self,
        accion,
        parametros
    ):

        if accion == "consultar_actividades_utp":

            return self.consultar_actividades_utp(
                parametros
            )

        if accion == "actualizar_actividades_utp":

            return self.actualizar_actividades_utp()

        if accion == "agregar_actividad_agenda":

            return self.agregar_actividad_agenda(
                parametros
            )

        if accion == "consultar_agenda":

            return {
                "tipo": "respuesta",
                "texto": obtener_eventos_hoy()
            }

        if accion == "crear_evento":

            return self.procesar_crear_evento(
                parametros
            )

        return {
            "tipo": "respuesta",
            "texto": "No pude ejecutar esa acción."
        }

    # =========================================================
    # CONSULTAR ACTIVIDADES UTP
    # =========================================================

    def consultar_actividades_utp(
        self,
        parametros=None
    ):

        parametros = parametros or {}

        tipo = parametros.get(
            "tipo"
        )

        try:

            actividades = obtener_actividades(
                force=False
            )

        except Exception as error:

            print(
                f"❌ Error consultando UTP: {error}"
            )

            return {
                "tipo": "respuesta",
                "texto": (
                    "No pude consultar las "
                    "actividades de UTP."
                )
            }

        if not actividades:

            return {
                "tipo": "respuesta",
                "texto": (
                    "No tienes actividades "
                    "guardadas de UTP."
                )
            }

        # =====================================================
        # FILTRAR POR TIPO
        # =====================================================

        if tipo:

            tipo = str(tipo).lower()

            if tipo in (
                "tarea",
                "tareas",
                "homework"
            ):

                actividades = [
                    actividad
                    for actividad in actividades
                    if str(
                        actividad.get(
                            "type",
                            ""
                        )
                    ).upper() == "HOMEWORK"
                ]

            elif tipo in (
                "foro",
                "foros",
                "forum"
            ):

                actividades = [
                    actividad
                    for actividad in actividades
                    if str(
                        actividad.get(
                            "type",
                            ""
                        )
                    ).upper() == "FORUM"
                ]

        if not actividades:

            if tipo:

                return {
                    "tipo": "respuesta",
                    "texto": (
                        f"No tienes {tipo}s "
                        "pendientes."
                    )
                }

            return {
                "tipo": "respuesta",
                "texto": (
                    "No tienes actividades "
                    "pendientes."
                )
            }

        # =====================================================
        # FORMATEAR RESPUESTA
        # =====================================================

        partes = []

        for actividad in actividades:

            titulo = self.limpiar_titulo(
                actividad.get(
                    "activityTitle",
                    "Actividad sin nombre"
                )
            )

            curso = actividad.get(
                "courseName",
                "Curso desconocido"
            )

            fecha = actividad.get(
                "finishAt",
                ""
            )

            estado = self.formatear_estado(
                actividad.get(
                    "activityStatusFinal",
                    ""
                )
            )

            fecha_formateada = self.formatear_fecha(
                fecha
            )

            partes.append(
                f"{titulo} de {curso}, "
                f"vence {fecha_formateada}, "
                f"está {estado}"
            )

        texto_respuesta = (
            f"Tienes {len(partes)} actividades. "
            + ". ".join(partes)
            + "."
        )

        self.contexto[
            "ultimas_actividades_utp"
        ] = actividades

        return {
            "tipo": "respuesta",
            "texto": texto_respuesta
        }

    # =========================================================
    # ACTUALIZAR UTP
    # =========================================================

    def actualizar_actividades_utp(self):

        try:

            actividades = actualizar_utp()

        except Exception as error:

            print(
                f"❌ Error actualizando UTP: {error}"
            )

            return {
                "tipo": "respuesta",
                "texto": (
                    "No pude actualizar las "
                    "actividades de UTP."
                )
            }

        if not actividades:

            return {
                "tipo": "respuesta",
                "texto": (
                    "Actualicé UTP, pero no "
                    "encontré actividades."
                )
            }

        self.contexto[
            "ultimas_actividades_utp"
        ] = actividades

        return {
            "tipo": "respuesta",
            "texto": (
                f"Listo. Actualicé UTP y "
                f"encontré {len(actividades)} "
                f"actividades."
            )
        }

    # =========================================================
    # AGREGAR ACTIVIDAD A AGENDA
    # =========================================================

    def agregar_actividad_agenda(
        self,
        parametros
    ):

        parametros = parametros or {}

        tipo = parametros.get(
            "tipo"
        )

        busqueda = parametros.get(
            "busqueda",
            ""
        )

        actividades = obtener_actividades(
            force=False
        )

        # =====================================================
        # FILTRAR TIPO
        # =====================================================

        if tipo:

            tipo_lower = str(
                tipo
            ).lower()

            if tipo_lower in (
                "tarea",
                "tareas",
                "homework"
            ):

                actividades = [
                    actividad
                    for actividad in actividades
                    if str(
                        actividad.get(
                            "type",
                            ""
                        )
                    ).upper() == "HOMEWORK"
                ]

            elif tipo_lower in (
                "foro",
                "foros",
                "forum"
            ):

                actividades = [
                    actividad
                    for actividad in actividades
                    if str(
                        actividad.get(
                            "type",
                            ""
                        )
                    ).upper() == "FORUM"
                ]

        # =====================================================
        # BUSCAR PALABRAS
        # =====================================================

        if busqueda:

            palabras = [
                palabra.lower()
                for palabra in str(
                    busqueda
                ).split()
                if len(palabra) > 2
            ]

            coincidencias = []

            for actividad in actividades:

                titulo = str(
                    actividad.get(
                        "activityTitle",
                        ""
                    )
                ).lower()

                curso = str(
                    actividad.get(
                        "courseName",
                        ""
                    )
                ).lower()

                texto_busqueda = (
                    titulo + " " + curso
                )

                if all(
                    palabra in texto_busqueda
                    for palabra in palabras
                ):

                    coincidencias.append(
                        actividad
                    )

            actividades = coincidencias

        # =====================================================
        # NO ENCONTRADO
        # =====================================================

        if not actividades:

            return {
                "tipo": "respuesta",
                "texto": (
                    "No encontré esa actividad "
                    "en UTP."
                )
            }

        # =====================================================
        # VARIAS COINCIDENCIAS
        # =====================================================

        if len(actividades) > 1:

            self.contexto[
                "selecciones_agenda"
            ] = actividades

            opciones = []

            for indice, actividad in enumerate(
                actividades,
                start=1
            ):

                titulo = self.limpiar_titulo(
                    actividad.get(
                        "activityTitle",
                        ""
                    )
                )

                curso = actividad.get(
                    "courseName",
                    ""
                )

                opciones.append(
                    f"{indice}. {titulo} de {curso}"
                )

            return {
                "tipo": "respuesta",
                "texto": (
                    "Encontré varias actividades: "
                    + "; ".join(opciones)
                    + ". Dime cuál quieres agregar."
                )
            }

        # =====================================================
        # UNA SOLA COINCIDENCIA
        # =====================================================

        return self.crear_evento_desde_utp(
            actividades[0]
        )

    # =========================================================
    # CREAR EVENTO DESDE UTP
    # =========================================================

    def crear_evento_desde_utp(
        self,
        actividad
    ):

        try:

            resultado = crear_evento_utp(
                actividad
            )

        except Exception as error:

            print(
                f"❌ Error creando evento UTP: {error}"
            )

            return {
                "tipo": "respuesta",
                "texto": (
                    "No pude agregar la actividad "
                    "a la agenda."
                )
            }

        titulo = self.limpiar_titulo(
            actividad.get(
                "activityTitle",
                "Actividad UTP"
            )
        )

        return {
            "tipo": "respuesta",
            "texto": (
                f"Listo. Agregué {titulo} "
                "a tu agenda."
            )
        }

    # =========================================================
    # SELECCIÓN DE ACTIVIDAD
    # =========================================================

    def procesar_seleccion_agenda(
        self,
        texto
    ):

        actividades = self.contexto.get(
            "selecciones_agenda"
        )

        if not actividades:
            return None

        texto_lower = texto.lower().strip()

        # -----------------------------------------------------
        # Número
        # -----------------------------------------------------

        coincidencia = re.search(
            r"\b([1-9])\b",
            texto_lower
        )

        if coincidencia:

            indice = int(
                coincidencia.group(1)
            ) - 1

            if 0 <= indice < len(
                actividades
            ):

                actividad = actividades[
                    indice
                ]

                self.contexto.pop(
                    "selecciones_agenda",
                    None
                )

                return self.crear_evento_desde_utp(
                    actividad
                )

        # -----------------------------------------------------
        # Búsqueda por texto
        # -----------------------------------------------------

        for actividad in actividades:

            titulo = str(
                actividad.get(
                    "activityTitle",
                    ""
                )
            ).lower()

            curso = str(
                actividad.get(
                    "courseName",
                    ""
                )
            ).lower()

            if (
                texto_lower in titulo
                or texto_lower in curso
            ):

                self.contexto.pop(
                    "selecciones_agenda",
                    None
                )

                return self.crear_evento_desde_utp(
                    actividad
                )

        return {
            "tipo": "respuesta",
            "texto": (
                "No identifiqué cuál actividad "
                "quieres agregar."
            )
        }

    # =========================================================
    # CREAR EVENTO NORMAL
    # =========================================================

    def procesar_crear_evento(
        self,
        datos
    ):

        try:

            if isinstance(datos, dict):

                titulo = datos.get(
                    "titulo",
                    "Evento"
                )

                fecha = datos.get(
                    "fecha"
                )

                hora = datos.get(
                    "hora"
                )

                resultado = crear_evento(
                    titulo,
                    fecha,
                    hora
                )

                return {
                    "tipo": "respuesta",
                    "texto": str(
                        resultado
                    )
                }

            return {
                "tipo": "respuesta",
                "texto": (
                    "Necesito más información "
                    "para crear el evento."
                )
            }

        except Exception as error:

            print(
                f"❌ Error creando evento: {error}"
            )

            return {
                "tipo": "respuesta",
                "texto": (
                    "No pude crear el evento."
                )
            }

    # =========================================================
    # LIMPIAR TÍTULO UTP
    # =========================================================

    def limpiar_titulo(
        self,
        titulo
    ):

        titulo = str(
            titulo or ""
        ).strip()

        titulo = re.sub(
            r"^S\d{2}\.s\d+\s*-\s*",
            "",
            titulo,
            flags=re.IGNORECASE
        )

        return titulo.strip()

    # =========================================================
    # FORMATEAR FECHA
    # =========================================================

    def formatear_fecha(
        self,
        fecha
    ):

        if not fecha:
            return "sin fecha"

        try:

            fecha_limpia = str(
                fecha
            ).replace(
                "Z",
                ""
            )

            formatos = [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S"
            ]

            fecha_objeto = None

            for formato in formatos:

                try:

                    fecha_objeto = datetime.strptime(
                        fecha_limpia,
                        formato
                    )

                    break

                except ValueError:
                    continue

            if fecha_objeto is None:
                return str(fecha)

            meses = [
                "enero",
                "febrero",
                "marzo",
                "abril",
                "mayo",
                "junio",
                "julio",
                "agosto",
                "septiembre",
                "octubre",
                "noviembre",
                "diciembre"
            ]

            hora = fecha_objeto.hour
            minuto = fecha_objeto.minute

            if hora == 0:

                hora_12 = 12
                periodo = "am"

            elif hora < 12:

                hora_12 = hora
                periodo = "am"

            elif hora == 12:

                hora_12 = 12
                periodo = "pm"

            else:

                hora_12 = hora - 12
                periodo = "pm"

            return (
                f"{fecha_objeto.day} de "
                f"{meses[fecha_objeto.month - 1]} "
                f"a las {hora_12}:"
                f"{minuto:02d} {periodo}"
            )

        except Exception:
            return str(fecha)

    # =========================================================
    # FORMATEAR ESTADO
    # =========================================================

    def formatear_estado(
        self,
        estado
    ):

        estados = {
            "IN_PROCESS":
                "en proceso",

            "TO_START":
                "pendiente",

            "FINISHED":
                "finalizada",

            "COMPLETED":
                "completada",

            "SUBMITTED":
                "enviada",

            "OVERDUE":
                "vencida"
        }

        return estados.get(
            str(
                estado or ""
            ).upper(),
            "pendiente"
        )
    