import pandas as pd
from datetime import datetime, timedelta
import confi

archivo = "datos/clientes.xlsx"

def verificar_cliente(dni):
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()

    df["ultimo_ingreso"] = df["ultimo_ingreso"].astype(str)

    hoy = datetime.now().strftime("%Y-%m-%d")

    cliente = df[df["dni"] == dni]

    if cliente.empty:
        return {"error": "Cliente no encontrado"}

    index = cliente.index[0]
    nombre = df.at[index, "nombres"]
    dias = df.at[index, "dias restantes"]
    ultimo = str(df.at[index, "ultimo_ingreso"])

    # Ya vino hoy
    if ultimo == hoy:
        return {
            "nombres": nombre,
            "estado": "ya_vino"
        }

    if dias > 0:
        df.at[index, "dias restantes"] = dias - 1
        df.at[index, "ultimo_ingreso"] = hoy
        df.at[index, "proximo dia"] = calcular_proximo_dia(datetime.now().strftime("%Y-%m-%d"),df.at[index, "dias semanal"],datetime.now().strftime("%Y-%m-%d"))
        df.to_excel(archivo, index=False)

        return {
            "nombres": nombre,
            "dias": dias - 1,
            "estado": "ok"
        }
    else:
        return {
            "nombres": nombre,
            "estado": "sin_dias"
        }

def guardar_cliente(id: int, nombre: str, dni: int, diasxsemana:int, dias_semanal:list[str],dias_res:int) -> list[bool,str]:
    try:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip().str.lower()

        
        if "ultimo_ingreso" not in df.columns:
            df["ultimo_ingreso"] = ""
        if "dias semanal" not in df.columns:
            df["dias semanal"] = None

        existe = df["id"] == id
        print("Backend: verifico que si existe el id")

        dias_proximo = calcular_proximo_dia(datetime.now().strftime("%Y-%m-%d"),dias_semanal)

        # Duplicado de DNI: buscamos en TODAS las filas menos la que estamos editando (si existe)
        dni_duplicado = df.loc[~existe, "dni"].eq(dni).any()
        if dni_duplicado:
            return [False, "Un cliente con ese DNI, ya esta registrado"]

        dias_semana_str = str(dias_semanal)

        if existe.any():
            print("Backend: El cliente existe y se esta modificando")
            # ===== EDITAR fila existente =====
            fila = df.index[existe][0]  # índice real de la fila en el DataFrame
            print("backend:",nombre,dni,diasxsemana,dias_res,dias_semanal,dias_proximo)


            df.at[fila, "nombres"] = nombre
            print("Backen: nombre puesto")
            df.at[fila, "dni"] = dni
            print("Backen: dni puesto")
            df.at[fila, "dias restantes"] = dias_res
            print("Backen: dias restantes puesto")
            df.at[fila, "dias x semana"] = diasxsemana
            print("Backen: dias x semana puesto")
            df.at[fila, "proximo dia"] = dias_proximo
            print("Backen: proximo dia puesto")
            df.at[fila,"dias semanal"] = dias_semana_str
            print("Backen: dias semanal puesto")
            # ultimo_ingreso no se toca, se conserva el valor previo

        else:
            print("Backend: el cliente es nuevo, y se esta agregando")
            nuevo = {
                "id": id,
                "nombres": nombre,
                "dni": dni,
                "dias restantes": dias_res,
                "ultimo_ingreso": "",
                "dias x semana": diasxsemana,
                "dias semanal": dias_semana_str,
                "proximo dia": dias_proximo 
            }

            df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
            print("Backend: ",df)

        print("Backend: guardando los cambios")
        df.to_excel(archivo, index=False)
        return [True,"Se a registrado correctamente"]

    except Exception as e:
        print("En Backend Error:", e)
        return [False,"Error al registrar: " + str(e)]


def eliminar_cliente(dni)-> bool:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()

    df = df[df["dni"] != dni]

    df = df.sort_values("id").reset_index(drop=True)
    df["id"] = df.index + 1

    df.to_excel(archivo, index=False)
    return True


def agregar_dias(dni)->bool:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()

    cliente = df[df["dni"] == dni]

    if cliente.empty:
        return False
    index = cliente.index[0]


    dias_extra = get_diasrR_diasS(df.at[index, "dias x semana"])

  
    df.at[index, "dias restantes"] += dias_extra
    df.to_excel(archivo, index=False)

    return True

def actualizar_dias_clientes():
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()

    if "proximo dia" not in df.columns:
        df["proximo dia"] = ""

    df["ultimo_ingreso"] = df["ultimo_ingreso"].astype(str)
    df["proximo dia"] = df["proximo dia"].astype(str)

    ayer = datetime.now() - timedelta(days=1)
    print("Backend: Actualizar dias: dia de ayer",ayer.date())

    id_penalizar = []

    for _, fila in df.iterrows():
        proximo = datetime.strptime(fila["proximo dia"],"%Y-%m-%d")
        ultimo_str = fila["ultimo_ingreso"]
        ultimo_str = str(ultimo_str)
        ultimo = datetime.strptime(ultimo_str,"%Y-%m-%d") if ultimo_str not in ("","nan","Nat","None") else None
        print("--------------------------------------------------")
        print("Backend: actualizar dias: proximo:",proximo,"ultimo:",ultimo)

        print("Backend: actualizar dias: proximo es menor que ayer?:",(proximo.date() < ayer.date()))

        if proximo.date() == ayer.date() or proximo.date() < ayer.date():
            print("Backend: actualizar dias: proximo dia es igual a ayer o proximo es menor a ayer")
            if ultimo != proximo:
                id_penalizar.append(fila["id"])
                print("Backend: actualizar dias: ulimo dia no es igual que proximo, eso significa que no vino")

    df.loc[df["id"].isin(id_penalizar), "dias restantes"] = (df.loc[df["id"].isin(id_penalizar), "dias restantes"] - 1).clip(lower=0)
    print("Backend: actualizar dias: sacandole -1 a dias restante del cliente")

    for id_cliente in id_penalizar:
        fila_idx = df.index[df["id"] == id_cliente][0]
        dias_cliente = df.at[fila_idx, "dias semanal"]
        df.at[fila_idx, "proximo dia"] = calcular_proximo_dia(df.at[fila_idx, "proximo dia"], dias_cliente)
    
    df.to_excel(archivo, index=False)
 
def get_todos_clientes_dni()-> list:
    df = pd.read_excel(archivo)

    return df["dni"].tolist()

def get_todos_clientes_nombre()->list:
    df = pd.read_excel(archivo)
    return df["nombres"].tolist()

def traduccion_nombre_dni(nombre: str) -> int:
    df = pd.read_excel(archivo)
    cliente = df[df["nombres"] == nombre]
    index = cliente.index[0]
    return df.at[index, "dni"]

def calcular_proximo_dia(fecha_str: str, dias_semanal: list, fe: str = None) -> str:
    dias_semana_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    fecha_pivote = (datetime.now() - timedelta(days=1)) if fe is None else datetime.strftime(fe, "%Y-%m-%d")

    while (fecha > fecha_pivote):
        fecha += timedelta(days=1)
        print("Backend: calcular proximo: fecha",fecha)
        nombre_dia = dias_semana_nombres[fecha.weekday()]
        print("Backend: calcular proximo: nombre del dia:",nombre_dia)

        if nombre_dia in dias_semanal:
            print("Backend: calcular proximo: por aca nombre dia en dia semanal",fecha.strftime("%Y-%m-%d"))
            return fecha.strftime("%Y-%m-%d")

    return fecha_str  # fallback: no debería pasar si dias_semanal no está vacía

def get_cliente(nombre:str) -> list:
    df = pd.read_excel(archivo)
    cliente = df[df["nombres"] == nombre]

    if cliente.empty:
        return []

    return cliente.iloc[0][["id","nombres", "dni", "dias restantes", "ultimo_ingreso","dias x semana","proximo dia","dias semanal"]].tolist()

def get_ultimo_id() -> int:
    df = pd.read_excel(archivo)
    e = df["id"].tolist()
    e = len(e)
    return e

def get_es_hoy(fecha:str) -> bool:
    return datetime.now().strftime("%Y-%m-%d") == fecha

def get_diasrR_diasS(dias:int) -> int:
    return dias * 4

def get_cliente_id(id_cliente: int) -> list:
    df = pd.read_excel(archivo)
    cliente = df.loc[df["id"] == id_cliente, ["id", "nombres", "dni", "dias restantes", "ultimo_ingreso", "dias x semana","proximo dia","dias semanal"]]
    
    return cliente.iloc[0].tolist() if not cliente.empty else []

#=================================ARCHIVO DE CONFIGURACION ========================================
