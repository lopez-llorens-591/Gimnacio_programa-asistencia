import sys
import os
import configparser

def _ruta_recurso(relativa):
    base = getattr(sys, "_MEIPASS",os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base,relativa)

def _ruta_datos(relativa):
    if getattr(sys,"frozen",False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relativa)

NOMBRE_CARPETA = "datos"
CARPETA_DATOS =_ruta_datos(NOMBRE_CARPETA)
RUTA_CLIENTES = os.path.join(CARPETA_DATOS,"clientes.xlsx")
RUTA_CONFIGURACION = os.path.join(CARPETA_DATOS,"confi.ini")

#=====================================configuracion============================================================

CONFIGURACION_POR_DEFECTO = {
    "general":{
        "version": "1",
        "fin_semana": "True",
    },
}

def _leer():
    confi = configparser.ConfigParser()
    confi.read(RUTA_CONFIGURACION, encoding="utf-8")
    return confi

def _guerdar(config):
    os.makedirs(CARPETA_DATOS,exist_ok=True)
    with open (RUTA_CONFIGURACION,"w",encoding="utf-8") as f:
        config.write(f)

def crear_configuracion_por_defecto():
    confi = configparser.ConfigParser()
    confi.read_dict(CONFIGURACION_POR_DEFECTO)
    _guerdar(confi)


def get_config(seccion, clave, deefcto=None, tipo=str):
    if deefcto is None:
        deefcto = CONFIGURACION_POR_DEFECTO.get(seccion, {}).get(clave)
        if deefcto is not None and tipo is not bool:
            deefcto = tipo(deefcto)

    config = _leer()
    if not config.has_option(seccion,clave):
        return deefcto
    try:
        if tipo is bool:
            return config.getboolean(seccion,clave)
        return tipo(config.get(seccion,clave))
    except ValueError:
        return deefcto


def set_config(seccion, clave, valor):
    config = _leer()
    if not config.has_option(seccion):
        config.add_section(seccion)
    config.set(seccion,clave, str(valor))
    _guerdar(config)