import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import backend as bcn
from datetime import datetime
from confi import get_config, set_config


def iniciar_ui():
    
    global ventana, entry_dni

    # ===== FUNCION RESULTADO =====
    def mostrar_resultado(texto, tipo="ok"):
        popup = tk.Toplevel(ventana)
        popup.overrideredirect(True)

        ancho = ventana.winfo_screenwidth()
        alto = int(ventana.winfo_screenheight() * 3 / 5)

        x = 0
        y = int((ventana.winfo_screenheight() - alto) / 2)

        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Colores
        if tipo == "ok":
            color = "#2ecc71"   # verde
        elif tipo == "error":
            color = "#e74c3c"   # rojo
        else:
            color = "#f1c40f"   # amarillo

        frame = tk.Frame(popup, bg=color)
        frame.pack(fill="both", expand=True)

        label = tk.Label(
            frame,
            text=texto,
            bg=color,
            fg="white",
            font=("Arial", 30, "bold"),
            justify="center"
        )
        label.pack(expand=True)

        # cerrar solo
        popup.after(3000, popup.destroy)

    # ===== FUNCION DNI =====
    def verificar_dni(event=None):
        try:
            dni = int(entry_dni.get())
        except:
            mostrar_resultado("DNI inválido", "error")
            entry_dni.delete(0, tk.END)
            entry_dni.focus_set()
            return

        resultado = bcn.verificar_cliente(dni)

        if "error" in resultado:
            mostrar_resultado(resultado["error"], "error")

        elif resultado["estado"] == "ok":
            mostrar_resultado(
                f"Bienvenido {resultado['nombres']}\nDías restantes: {resultado['dias']}",
                "ok"
            )

        elif resultado["estado"] == "sin_dias":
            mostrar_resultado(
                f"{resultado['nombres']} sin días disponibles",
                "error"
            )
        elif resultado["estado"] == "ya_vino":
            mostrar_resultado(
                f"{resultado['nombres']} ya ingresó hoy",
                "warning"
    )


        entry_dni.delete(0, tk.END)
        entry_dni.focus_set()

    admin = None

    bcn.actualizar_dias_clientes()

    def abrir_admin():
        admin = tk.Toplevel(ventana)
        admin.title("Admin")
        admin.geometry("350x100")

        admin.bind("<Escape>", lambda e: admin.destroy())

        tk.Button(admin, text="Agregar Cliente",command=lambda:ventana_agregar(False)).pack(fill="x",pady=3)
        tk.Button(admin, text="Clientes", command=ventana_clientes).pack(fill="x",pady=3)
        tk.Button(admin, text="Configuracion", command=ventana_configuracion).pack(fill="x",padx=3)

    def ventana_agregar(editar: bool, id: int | None = None):
        cli_var = bcn.get_cliente_id(id) if editar else None

        print("Interfaz: ",cli_var)

        dias_semana_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        COLOR_ACTIVO = "#2ecc71"    # verde, cuando está seleccionado
        COLOR_INACTIVO = "#d9d9d9"  # gris, color por defecto de un botón

        def toggle_dia(dia):
            estado_dias[dia] = not estado_dias[dia]
            color = COLOR_ACTIVO if estado_dias[dia] else COLOR_INACTIVO
            botones_dias[dia].config(bg=color)
            actualizador_contador()

        def actualizador_contador():
            cantidad = sum(1 for activo in estado_dias.values() if activo)
            texto_contador.set(f"Ira {cantidad} dias por semana")
            actualizar_dias(var=bcn.get_diasrR_diasS(cantidad))

        def actualizar_dias(sube = None, var: int = 0):
            if sube == True:
                var += 1
            elif sube == False:
                var -= 1
            var_dias_restantes.set(var)
            

        def agregar():
            cantidad_xdia = sum(1 for activo in estado_dias.values() if activo)
            dias_seleccionados = [dia for dia, activo in estado_dias.items() if activo]

            if not dias_seleccionados:
                messagebox.showerror("Error", "Debe seleccionar al menos un día")
                return

            resultado = bcn.guardar_cliente(id_var, nombre_entry.get(), int(dni_entry.get()),cantidad_xdia,dias_seleccionados,var_dias_restantes.get())
            mensaje_error(resultado[0], "Guardado cliente", resultado[1], agregar_clientes_ventana)
            return

        agregar_clientes_ventana = tk.Toplevel(admin)
        agregar_clientes_ventana.title("Editar cliente" if editar else "Agregar cliente")
        agregar_clientes_ventana.geometry("600x350")

        id_var = id if editar else bcn.get_ultimo_id() + 1

        var_dias_restantes = tk.IntVar(value=cli_var[3] if editar else 0)

        label_id = tk.Label(agregar_clientes_ventana, text=(f"Id: {str(id_var)}"), font=("Arial", 14))
        label_id.pack(side="top")

        nombre_label = tk.Label(agregar_clientes_ventana, text="Nombre del cliente", font=("Arial", 16))
        nombre_label.pack(side="top")
        nombre_entry = tk.Entry(agregar_clientes_ventana, font=("Arial", 13), justify="center")
        nombre_entry.pack(side="top")
        if editar:
            nombre_entry.insert(0, cli_var[1])

        dni_label = tk.Label(agregar_clientes_ventana, text="DNI del cliente", font=("Arial", 16))
        dni_label.pack()
        dni_entry = tk.Entry(agregar_clientes_ventana, font=("Arial", 13), justify="center")
        dni_entry.pack()
        if editar:
            dni_entry.insert(0, cli_var[2])

        servicio_label = tk.Label(agregar_clientes_ventana, text="Días que asiste", font=("Arial", 16))
        servicio_label.pack()

        dias_previos = cli_var[7] if editar else []

        # estado_dias guarda True/False por cada día; botones_dias guarda la referencia al widget
        estado_dias = {dia: (dia in dias_previos) for dia in dias_semana_nombres}
        botones_dias = {}

        barra_botones = tk.Frame(agregar_clientes_ventana)
        barra_botones.pack(fill="x",anchor="center")

        for dia in dias_semana_nombres:
            color_inicial = COLOR_ACTIVO if estado_dias[dia] else COLOR_INACTIVO
            btn = tk.Button(
                barra_botones,
                text=dia,
                bg=color_inicial,
                font=("Arial", 12),
                command=lambda d=dia: toggle_dia(d)
            )
            btn.pack(anchor="center", fill="x", padx=5, pady=2,side="left")
            botones_dias[dia] = btn

        texto_contador = tk.StringVar()
        label_contador = tk.Label(agregar_clientes_ventana,textvariable=texto_contador,font=("Arial",12,"bold"))
        label_contador.pack(padx=5)
        actualizador_contador()

        frame_dias = tk.Frame(agregar_clientes_ventana,relief="solid",bg="")
        frame_dias.pack(padx=5)

        tk.Label(frame_dias,text="Modificar los dias restantes").pack(side="top",padx=5,pady=5)

        tk.Button(frame_dias,text="-",command=lambda: actualizar_dias(False,var_dias_restantes.get())).pack(side="left",padx=5,anchor="center",expand=True)
        label_dias_restantes = tk.Label(frame_dias,textvariable=var_dias_restantes,font=("Arial",12,"bold")).pack(side="left",padx=5,anchor="center")
        tk.Button(frame_dias,text="+",command=lambda: actualizar_dias(True, var_dias_restantes.get())).pack(side="left",padx=5,anchor="center",expand=True)

        boton_ok = tk.Button(agregar_clientes_ventana, text="Guardar Cliente", command=agregar)
        boton_ok.pack(anchor="center", pady=10)

    def ventana_clientes():
        clientes_toplevel = tk.Toplevel(admin)
        clientes_toplevel.title("Clientes")
        clientes_toplevel.geometry("650x350")

        clientes_toplevel.bind("<Escape>", lambda e: clientes_toplevel.destroy())

        text_nombre = tk.StringVar(value="Nombre: ")
        text_dni = tk.StringVar(value="DNI: ")
        text_dias_servicio = tk.StringVar(value="Dias x Semana: ")
        text_dias_faltantes = tk.StringVar(value="Dias faltantes: ")
        text_ultima_fecha = tk.StringVar(value="Ultima Fecha: ")
        text_id = tk.StringVar(value="ID: ")
        text_proximo_dia = tk.StringVar(value="Proximo dia: ")

        
        def buscar_cliente() -> list:
            cli = bcn.get_cliente(entry_name.get())
            if not cli:
                return

            label_nada.pack_forget()
            contenedor.pack(expand=True)  # muestra el bloque completo si estaba oculto

            es_hoy: str = "" if not bcn.get_es_hoy(cli[4]) else " (Hoy)"
            es_hoy2: str = "" if not bcn.get_es_hoy(cli[6]) else " (Hoy)"

            text_id.set(f"ID:  {cli[0]}")
            text_nombre.set(f"Nombre: {cli[1]}")
            text_dni.set(f"D.N.I: {cli[2]}")
            text_dias_servicio.set(f"Dias X Semana: {cli[5]}")
            text_dias_faltantes.set(f"Dias faltantes: {cli[3]}")
            text_ultima_fecha.set(f"Ultima Fecha: {cli[4]} {es_hoy}")
            text_proximo_dia.set(f"Proximo dia: {cli[6]} {es_hoy2}")

            editar_cliente_boton.config(state="normal")
            eleminar_cliente_boton.config(state="normal")
            agregar_dias_boton.config(state="normal")

            return cli
        
        def eleminar_cliente():
            if bcn.eliminar_cliente(bcn.traduccion_nombre_dni(entry_name.get())):
                messagebox.showinfo("Eleminado","Ha eleminado el cliente")
            else:
                messagebox.showerror("Error", "Ha ocurrido un error al eleminar")

        def agregar_dias():
            if bcn.agregar_dias(bcn.traduccion_nombre_dni(entry_name.get())):
                mensaje_error(False,"Completado","Se ha agredado los dias satifactoriamente",admin)
            else:
                mensaje_error(True,"Error","Ha ocurrido un error",admin)

        cli_encon = buscar_cliente
        
        frame_a = tk.Frame(clientes_toplevel, bg="lightgreen", relief="solid")
        frame_a.pack(side=tk.LEFT, expand=True, fill="both",anchor="center")

        entry_name = entry_autocompletado(frame_a)

        tk.Button(frame_a, text="Buscar Cliente", command=cli_encon).pack(pady=10)

        ttk.Separator(clientes_toplevel, orient="vertical").pack(anchor="center", side="left", fill="y")

        frame_b = tk.Frame(clientes_toplevel, bg="lightgreen", relief="solid")
        frame_b.pack(side=tk.LEFT, expand=True, fill="both")

        frame_b_a = tk.Frame(frame_b, bg="navy")
        frame_b_a.pack(expand=True, anchor="center", fill="both")

        label_nada = tk.Label(frame_b_a, text="No se ha buscado a ningun cliente")
        label_nada.pack(anchor="center", expand=True)

        # Contenedor que agrupa las dos filas, oculto hasta la primera búsqueda
        contenedor = tk.Frame(frame_b_a, bg="navy")

        fila1 = tk.Frame(contenedor, bg="grey")
        fila1.pack(pady=5)

        tk.Label(fila1, textvariable=text_id, bg="gray", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Label(fila1, textvariable=text_nombre, bg="gray", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Label(fila1, textvariable=text_dni, bg="gray", font=("Arial", 12)).pack(side="left", padx=5)

        fila2 = tk.Frame(contenedor, bg="grey")
        fila2.pack(pady=5)

        tk.Label(fila2, textvariable=text_dias_servicio, bg="gray", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Label(fila2, textvariable=text_dias_faltantes, bg="gray", font=("Arial", 12)).pack(side="left", padx=5)
  
        fila3 = tk.Frame(contenedor, bg="grey")
        fila3.pack(pady=5)

        tk.Label(fila3, textvariable=text_ultima_fecha, bg="grey", font=("Arial", 12)).pack(side="left", padx=5)

        fila4 = tk.Frame(contenedor, bg="blue")
        fila4.pack(pady=5)

        tk.Label(fila4,textvariable=text_proximo_dia,bg="grey", font=("Arial",12)).pack(side="left",padx=5)

        frame_b_b = tk.Frame(frame_b)
        frame_b_b.pack(side="bottom", fill="y",padx=5,pady=5)

        agregar_dias_boton = tk.Button(frame_b_b, text="Agregar Dias", command=lambda: mensaje_confirmacion("Agregar dias", "¿Desea actualizar el mas al cliente?",clientes_toplevel,agregar_dias), state="disabled")
        agregar_dias_boton.pack(side="left",padx=5)
        eleminar_cliente_boton = tk.Button(frame_b_b, text="Eleminar Cliente", command=lambda: mensaje_confirmacion("Eleminar cliente", "¿Desea eleminar a este cliente?",clientes_toplevel,eleminar_cliente), state="disabled")
        eleminar_cliente_boton.pack(side="left",padx=5)
        editar_cliente_boton = tk.Button(frame_b_b, text="Editar Cliente", command=lambda:ventana_agregar(True,cli_encon()[0]), state="disabled")
        editar_cliente_boton.pack(side="left",padx=5)
        
    def ventana_configuracion():
        ventana_emergente = tk.Toplevel(admin)
        tabcontrol = ttk.Notebook(ventana_emergente)
        ventana_emergente.geometry("200x200")
        tabcontrol.pack(expand=1,fill="both")
        tab1 = tk.Frame(tabcontrol)
        tab2 = tk.Frame(tabcontrol)
        tabcontrol.add(tab1,text='Tab 1')
        tabcontrol.add(tab2,text='Tab 2')

    # ===== VENTANA =====
    ventana = tk.Tk()
    ventana.title("Control Gimnasio")

    ventana.attributes("-fullscreen", True)
    ventana.overrideredirect(False)

    # salir con ESC
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # ===== FONDO =====
    fondo = tk.Frame(ventana, bg="#1e1e2f")
    fondo.pack(fill="both", expand=True)

    # ===== PANEL CENTRAL =====
    panel = tk.Frame(fondo, bg="#2c2c3e", width=1000, height=500)
    panel.place(relx=0.5, rely=0.5, anchor="center")

    label_reloj = tk.Label(panel, fg="white", bg="#1e1e2f", font=("Arial", 16))
    label_reloj.pack(expand=True, pady=5)

    titulo = tk.Label(
        panel,
        text="Bienvenido, por favor ingrese su DNI",
        fg="white",
        bg="#2c2c3e",
        font=("Arial", 16)
    )
    titulo.pack(pady=15)

    entry_dni = tk.Entry(
        panel,
        font=("Arial", 14),
        justify="center"
    )
    entry_dni.pack(pady=10, ipadx=10, ipady=5)

    entry_dni.focus_set()

    def actualizar_reloj():
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        label_reloj.config(text=ahora)
        ventana.after(1000, actualizar_reloj)

    actualizar_reloj()

    # Enter = validar
    ventana.bind("<Return>", verificar_dni)
    ventana.bind("<F1>", lambda e: abrir_admin())


    ventana.mainloop()

def entry_autocompletado(jefe: tk.Toplevel):
    frame = tk.Frame(jefe, bg="lightblue")
    frame.pack(padx=10, pady=10)


    def seleccionar(cliente):
        entry_nombre.delete(0,tk.END)
        entry_nombre.insert(0, cliente)

    def al_escribir(event):
        texto = entry_nombre.get().lower()

        menu_autocopletado.delete(0,tk.END)

        if texto == "":
            return
        cosidencias = [c for c in bcn.get_todos_clientes_nombre() if texto in c.lower()]

        if cosidencias:
            for c in cosidencias:
                menu_autocopletado.insert(tk.END, c)
   
    def seleccionar(event):
        selecion = menu_autocopletado.curselection()
        if selecion:
            entry_nombre.delete(0,tk.END)
            entry_nombre.insert(0, menu_autocopletado.get(selecion[0]))
            return entry_nombre.get().lower()


    tk.Label(frame,text="Nombre del Cliente").pack()
    entry_nombre= tk.Entry(frame,justify="center")
    entry_nombre.pack(fill="x",pady=10)
    entry_nombre.bind("<KeyRelease>", al_escribir)

    menu_autocopletado = tk.Listbox(frame,activestyle="dotbox")
    menu_autocopletado.bind("<<ListboxSelect>>", seleccionar)
    menu_autocopletado.pack(fill="x",side="left")

    scrollbar = tk.Scrollbar(frame,orient=tk.VERTICAL,command=menu_autocopletado.yview)
    scrollbar.pack(side="right", expand=True,fill="y")

    menu_autocopletado.config(yscrollcommand=scrollbar.set)


    for c in bcn.get_todos_clientes_nombre():
        menu_autocopletado.insert(tk.END, c)

    return entry_nombre

def mensaje_confirmacion(titulo: str, mensaje: str, jefe: tk.Toplevel,funcion):

    if messagebox.askyesno(title=titulo,message=mensaje,parent=jefe,icon="question"):
        funcion()
    else:
        return

def mensaje_error(error:bool,titulo:str,mensaje:str,padre: tk.Toplevel):
    messagebox.showinfo(title=titulo,message=mensaje,parent=padre) if error else messagebox.showerror(title=titulo,message=mensaje,parent=padre) 
    
