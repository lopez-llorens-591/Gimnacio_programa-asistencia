import os
from openpyxl import Workbook
from confi import CARPETA_DATOS, RUTA_CLIENTES, RUTA_CONFIGURACION, crear_configuracion_por_defecto

encabezado_inicial = ["id","nombres","dni","dias restantes","ultimo_ingreso","dias x semana","proximo dia","dias semanal"]



async def inicializador():
    os.makedirs(CARPETA_DATOS,exist_ok=True)

    if not os.path.exists(RUTA_CLIENTES):
        crear_archivo_xlsx()
    print("Iniciador: Ya esta creado el excel")
    if not os.path.exists(RUTA_CONFIGURACION):
        crear_configuracion_por_defecto()
    print("Iniciador: Ya esta creado la configuracion")


def crear_archivo_xlsx():
    wb = Workbook()
    hoja = wb.active
    hoja.title = "Clientes"
    hoja.append(encabezado_inicial)
    wb.save(RUTA_CLIENTES)
    print(f"Iniciador: Archivo xlsx completado y guardado en: {RUTA_CLIENTES}")

