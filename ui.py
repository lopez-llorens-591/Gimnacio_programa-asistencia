import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import backend as bcn
from datetime import datetime
from confi import get_config, set_config



C = {
    "fondo": "#F3F4F6", 
    "blanco": "#FFFFFF",
    "texto": "#1F2937",
    "secundario": "#6B7280",
    "borde": "#D1D5DB",

    "azul": "#2563EB",
    "azul_hover": "#1D4ED8",
    "azul_claro": "#EFF6FF",
    "azul_texto": "#1D4ED8",

    "verde_fondo": "#F0FDF4",
    "verde_texto": "#166534",

    "naranja_fondo": "#FFFBEB",
    "naranja_texto": "#92400E",

    "rojo_fondo": "#FEF2F2",
    "rojo_texto": "#991B1B",
}

FUENTE = "Segoe UI"


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
        admin.geometry("300x80")

        admin.bind("<Escape>", lambda e: admin.destroy())

        tk.Button(admin, text="Agregar Cliente",command=lambda:ventana_agregar(False)).pack(fill="x",pady=3)
        tk.Button(admin, text="Clientes", command=ventana_clientes).pack(fill="x",pady=3)
        #tk.Button(admin, text="Configuracion", command=ventana_configuracion).pack(fill="x",padx=3)

    
    def ventana_agregar(editar: bool, id: int | None = None):
        # ---------------- PALETA ----------------

        C = {
            "fondo": "#F3F4F6",
            "blanco": "#FFFFFF",
            "texto": "#1F2937",
            "secundario": "#6B7280",
            "borde": "#D1D5DB",

            "azul": "#2563EB",
            "azul_hover": "#1D4ED8",
            "azul_claro": "#DBEAFE",
            "azul_texto": "#1D4ED8",

            "verde": "#15803D",
            "verde_fondo": "#F0FDF4",

            "rojo": "#DC2626",
            "rojo_hover": "#B91C1C",

            "gris_boton": "#F9FAFB",
            "gris_hover": "#E5E7EB",
        }

        FUENTE = "Segoe UI"

        # ---------------- DATOS INICIALES ----------------

        cli_var = bcn.get_cliente_id(id) if editar else None

        dias_semana_nombres = [
            "Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"
        ]

        id_var = id if editar else bcn.get_ultimo_id() + 1

        dias_previos = cli_var[7] if editar else []

        estado_dias = {
            dia: dia in dias_previos
            for dia in dias_semana_nombres
        }

        # Conservamos los días restantes existentes al editar.
        var_dias_restantes = tk.IntVar(
            value=cli_var[3] if editar else 0
        )

        texto_contador = tk.StringVar()

        # ---------------- VENTANA ----------------

        agregar_clientes_ventana = tk.Toplevel(admin)
        agregar_clientes_ventana.title(
            "Editar cliente" if editar else "Agregar cliente"
        )
        agregar_clientes_ventana.geometry("650x500")
        agregar_clientes_ventana.minsize(580, 450)
        agregar_clientes_ventana.configure(bg=C["fondo"])
        agregar_clientes_ventana.bind(
            "<Escape>",
            lambda e: agregar_clientes_ventana.destroy()
        )

        # ---------------- FUNCIONES VISUALES ----------------

        def crear_boton(
            parent, texto, comando,
            principal=False, peligro=False, **kwargs
        ):
            if principal:
                fondo = C["azul"]
                hover = C["azul_hover"]
                texto_color = C["blanco"]
            elif peligro:
                fondo = C["blanco"]
                hover = "#FEE2E2"
                texto_color = C["rojo"]
            else:
                fondo = C["blanco"]
                hover = C["gris_hover"]
                texto_color = C["texto"]

            boton = tk.Button(
                parent,
                text=texto,
                command=comando,
                bg=fondo,
                fg=texto_color,
                activebackground=hover,
                activeforeground=texto_color,
                relief="flat",
                bd=0,
                padx=12,
                pady=7,
                cursor="hand2",
                font=(FUENTE, 10),
                **kwargs
            )

            boton.bind(
                "<Enter>",
                lambda e: boton.configure(bg=hover)
                if str(boton["state"]) != "disabled" else None
            )
            boton.bind(
                "<Leave>",
                lambda e: boton.configure(bg=fondo)
                if str(boton["state"]) != "disabled" else None
            )

            return boton

        def crear_titulo(parent, texto):
            tk.Label(
                parent,
                text=texto,
                bg=C["blanco"],
                fg=C["texto"],
                font=(FUENTE, 11, "bold"),
                anchor="w"
            ).pack(
                fill="x",
                pady=(0, 10)
            )

        # ---------------- DÍAS DE ASISTENCIA ----------------

        botones_dias = {}

        def actualizar_dias_restantes(delta=0, reiniciar=False):
            if reiniciar:
                cantidad = sum(estado_dias.values())
                var_dias_restantes.set(
                    bcn.get_diasrR_diasS(cantidad)
                )
            else:
                var_dias_restantes.set(
                    var_dias_restantes.get() + delta
                )

        def actualizador_contador(reiniciar=False):
            cantidad = sum(estado_dias.values())

            texto_contador.set(
                f"Asistencia: {cantidad} "
                f"{'día' if cantidad == 1 else 'días'} por semana"
            )

            if reiniciar:
                actualizar_dias_restantes(reiniciar=True)

        def actualizar_apariencia_dia(dia):
            seleccionado = estado_dias[dia]
            boton = botones_dias[dia]

            if seleccionado:
                boton.configure(
                    bg=C["azul"],
                    fg=C["blanco"],
                    activebackground=C["azul_hover"],
                    activeforeground=C["blanco"],
                    relief="flat"
                )
            else:
                boton.configure(
                    bg=C["gris_boton"],
                    fg=C["secundario"],
                    activebackground=C["gris_hover"],
                    activeforeground=C["texto"],
                    relief="solid"
                )

        def toggle_dia(dia):
            estado_dias[dia] = not estado_dias[dia]

            actualizar_apariencia_dia(dia)

            # Al cambiar la frecuencia semanal, recalculamos
            # los días restantes usando tu función existente.
            actualizador_contador(reiniciar=True)

        # ---------------- GUARDAR ----------------

        def agregar():
            nombre = nombre_entry.get().strip()
            dni_texto = dni_entry.get().strip()

            cantidad_xdia = sum(estado_dias.values())

            dias_seleccionados = [
                dia for dia, activo in estado_dias.items()
                if activo
            ]

            if not nombre:
                messagebox.showerror(
                    "Error",
                    "Debe ingresar el nombre del cliente.",
                    parent=agregar_clientes_ventana
                )
                nombre_entry.focus_set()
                return

            if not dni_texto.isdigit():
                messagebox.showerror(
                    "Error",
                    "Ingrese un DNI válido, usando solamente números.",
                    parent=agregar_clientes_ventana
                )
                dni_entry.focus_set()
                return

            if not dias_seleccionados:
                messagebox.showerror(
                    "Error",
                    "Debe seleccionar al menos un día.",
                    parent=agregar_clientes_ventana
                )
                return

            resultado = bcn.guardar_cliente(
                id_var,
                nombre,
                int(dni_texto),
                cantidad_xdia,
                dias_seleccionados,
                var_dias_restantes.get()
            )

            mensaje_error(
                resultado[0],
                "Guardado de cliente",
                resultado[1],
                agregar_clientes_ventana
            )

        # ---------------- CABECERA ----------------

        cabecera = tk.Frame(
            agregar_clientes_ventana,
            bg=C["blanco"]
        )
        cabecera.pack(fill="x")

        tk.Label(
            cabecera,
            text="Editar cliente" if editar else "Nuevo cliente",
            bg=C["blanco"],
            fg=C["texto"],
            font=(FUENTE, 17, "bold")
        ).pack(
            side="left",
            padx=20,
            pady=15
        )

        tk.Label(
            cabecera,
            text=f"ID #{id_var}",
            bg=C["azul_claro"],
            fg=C["azul_texto"],
            font=(FUENTE, 10, "bold"),
            padx=10,
            pady=5
        ).pack(
            side="right",
            padx=20
        )

        ttk.Separator(
            agregar_clientes_ventana,
            orient="horizontal"
        ).pack(fill="x")

        # ---------------- CONTENIDO ----------------

        contenido = tk.Frame(
            agregar_clientes_ventana,
            bg=C["fondo"]
        )
        contenido.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=12
        )

        # Tarjeta de datos personales
        tarjeta_datos = tk.Frame(
            contenido,
            bg=C["blanco"],
            highlightbackground=C["borde"],
            highlightthickness=1
        )
        tarjeta_datos.pack(fill="x", pady=(0, 10))

        interior_datos = tk.Frame(
            tarjeta_datos,
            bg=C["blanco"]
        )
        interior_datos.pack(
            fill="x",
            padx=14,
            pady=12
        )

        crear_titulo(
            interior_datos,
            "Datos personales"
        )

        fila_campos = tk.Frame(
            interior_datos,
            bg=C["blanco"]
        )
        fila_campos.pack(fill="x")

        columna_nombre = tk.Frame(
            fila_campos,
            bg=C["blanco"]
        )
        columna_nombre.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        tk.Label(
            columna_nombre,
            text="Nombre completo",
            bg=C["blanco"],
            fg=C["secundario"],
            font=(FUENTE, 9)
        ).pack(anchor="w", pady=(0, 4))

        nombre_entry = tk.Entry(
            columna_nombre,
            font=(FUENTE, 11),
            bg=C["blanco"],
            fg=C["texto"],
            insertbackground=C["texto"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=C["borde"],
            highlightcolor=C["azul"]
        )
        nombre_entry.pack(fill="x", ipady=5)

        columna_dni = tk.Frame(
            fila_campos,
            bg=C["blanco"],
            width=150
        )
        columna_dni.pack(
            side="left",
            fill="x"
        )
        columna_dni.pack_propagate(True)

        tk.Label(
            columna_dni,
            text="DNI",
            bg=C["blanco"],
            fg=C["secundario"],
            font=(FUENTE, 9)
        ).pack(anchor="w", pady=(0, 4))

        dni_entry = tk.Entry(
            columna_dni,
            font=(FUENTE, 11),
            bg=C["blanco"],
            fg=C["texto"],
            insertbackground=C["texto"],
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=C["borde"],
            highlightcolor=C["azul"]
        )
        dni_entry.pack(fill="x", ipady=5)

        if editar:
            nombre_entry.insert(0, cli_var[1])
            dni_entry.insert(0, cli_var[2])

        # Tarjeta de asistencia
        tarjeta_dias = tk.Frame(
            contenido,
            bg=C["blanco"],
            highlightbackground=C["borde"],
            highlightthickness=1
        )
        tarjeta_dias.pack(fill="x", pady=(0, 10))

        interior_dias = tk.Frame(
            tarjeta_dias,
            bg=C["blanco"]
        )
        interior_dias.pack(
            fill="x",
            padx=14,
            pady=12
        )

        crear_titulo(
            interior_dias,
            "Días de asistencia"
        )

        barra_botones = tk.Frame(
            interior_dias,
            bg=C["blanco"]
        )
        barra_botones.pack(fill="x")

        for dia in dias_semana_nombres:
            boton = tk.Button(
                barra_botones,
                text=dia[:3],
                font=(FUENTE, 9, "bold"),
                padx=5,
                pady=7,
                cursor="hand2",
                relief="flat",
                bd=0,
                command=lambda d=dia: toggle_dia(d)
            )

            boton.pack(
                side="left",
                fill="x",
                expand=True,
                padx=2
            )

            botones_dias[dia] = boton
            actualizar_apariencia_dia(dia)

        # Leyenda de días
        tk.Label(
            interior_dias,
            text="Seleccioná los días en los que asistirá el cliente.",
            bg=C["blanco"],
            fg=C["secundario"],
            font=(FUENTE, 9)
        ).pack(anchor="w", pady=(8, 0))

        # Contador de asistencia
        tk.Label(
            interior_dias,
            textvariable=texto_contador,
            bg=C["blanco"],
            fg=C["azul_texto"],
            font=(FUENTE, 10, "bold")
        ).pack(anchor="w", pady=(8, 0))

        # Tarjeta de días restantes
        tarjeta_restantes = tk.Frame(
            contenido,
            bg=C["blanco"],
            highlightbackground=C["borde"],
            highlightthickness=1
        )
        tarjeta_restantes.pack(fill="x")

        interior_restantes = tk.Frame(
            tarjeta_restantes,
            bg=C["blanco"]
        )
        interior_restantes.pack(
            fill="x",
            padx=14,
            pady=10
        )

        tk.Label(
            interior_restantes,
            text="Días restantes",
            bg=C["blanco"],
            fg=C["texto"],
            font=(FUENTE, 10, "bold")
        ).pack(side="left")

        controles_restantes = tk.Frame(
            interior_restantes,
            bg=C["blanco"]
        )
        controles_restantes.pack(side="right")

        crear_boton(
            controles_restantes,
            "−",
            comando=lambda: actualizar_dias_restantes(-1)
        ).pack(side="left", padx=4)

        tk.Label(
            controles_restantes,
            textvariable=var_dias_restantes,
            bg=C["blanco"],
            fg=C["azul_texto"],
            font=(FUENTE, 13, "bold"),
            width=4
        ).pack(side="left", padx=4)

        crear_boton(
            controles_restantes,
            "+",
            comando=lambda: actualizar_dias_restantes(1),
            principal=True
        ).pack(side="left", padx=4)

        # ---------------- PIE DE VENTANA ----------------

        ttk.Separator(
            agregar_clientes_ventana,
            orient="horizontal"
        ).pack(fill="x")

        pie = tk.Frame(
            agregar_clientes_ventana,
            bg=C["blanco"]
        )
        pie.pack(fill="x", side="bottom")

        crear_boton(
            pie,
            "Cancelar",
            comando=agregar_clientes_ventana.destroy
        ).pack(side="right", padx=(4, 16), pady=10)

        crear_boton(
            pie,
            "Guardar cambios" if editar else "Guardar cliente",
            comando=agregar,
            principal=True
        ).pack(side="right", padx=4, pady=10)

        # Inicializamos el contador sin sobrescribir
        # los días restantes de un cliente existente.
        actualizador_contador()

        nombre_entry.focus_set()



    def ventana_clientes():
        clientes_toplevel = tk.Toplevel(admin)
        clientes_toplevel.title("Clientes")
        clientes_toplevel.geometry("850x500")
        clientes_toplevel.minsize(750, 400)
        clientes_toplevel.configure(bg="#F3F4F6")

        clientes_toplevel.bind(
            "<Escape>", lambda e: clientes_toplevel.destroy()
        )

        # ---------------- VARIABLES ----------------

        text_nombre = tk.StringVar(value="Nombre: --")
        text_dni = tk.StringVar(value="DNI: --")
        text_dias_servicio = tk.StringVar(value="Días x semana: --")
        text_dias_faltantes = tk.StringVar(value="Días Restantes: --")
        text_ultima_fecha = tk.StringVar(value="Última fecha: --")
        text_id = tk.StringVar(value="ID: --")
        text_proximo_dia = tk.StringVar(value="Próximo día: --")
        text_dias_x_semana = tk.StringVar(value="Días de ingreso: --")
        text_fecha_inicio = tk.StringVar(value="Inicio de cuota: --")
        text_fecha_final = tk.StringVar(value="Fin de cuota: --")

        # ---------------- BÚSQUEDA ----------------

        def buscar_cliente() -> list:
            cli = bcn.get_cliente(entry_name.get())

            if not cli:
                return

            label_nada.pack_forget()
            contenedor.pack(
                fill="both",
                expand=True,
                padx=12,
                pady=12
            )

            text_id.set(f"ID: {cli[0]}")
            text_nombre.set(f"{cli[1]}")
            text_dni.set(f"DNI: {cli[2]}")

            text_dias_servicio.set(
                f"Días por semana: {cli[5]}"
            )
            text_dias_faltantes.set(
                f"Días Restantes: {cli[3]}"
            )

            text_ultima_fecha.set(
                f"Ultimo ingreso: {bcn.get_dias_de_semana(cli[4])} "
                f"{cli[4]} {bcn.advervios_fecha(cli[4])}"
            )

            text_proximo_dia.set(
                f"Proximo dia: {bcn.get_dias_de_semana(cli[6])} "
                f"{cli[6]} {bcn.advervios_fecha(cli[6])}"
            )

            text_dias_x_semana.set(
                f"Días de ingreso: {cli[7]}"
            )

            text_fecha_inicio.set(
                f"Inicio: {bcn.get_dias_de_semana(cli[8])} "
                f"{cli[8]} {bcn.advervios_fecha(cli[8])}"
            )

            text_fecha_final.set(
                f"Final: {bcn.get_dias_de_semana(cli[9])} "
                f"{cli[9]} {bcn.advervios_fecha(cli[9])}"
            )

            editar_cliente_boton.config(state="normal")
            eleminar_cliente_boton.config(state="normal")
            agregar_dias_boton.config(state="normal")

            return cli

        def eleminar_cliente():
            if bcn.eliminar_cliente(
                bcn.traduccion_nombre_dni(entry_name.get())
            ):
                messagebox.showinfo(
                    "Eliminado",
                    "Se ha eliminado el cliente",
                    parent=clientes_toplevel
                )
                buscar_cliente()
                contenedor.pack_forget()
                label_nada.pack(
                    anchor="center",
                    expand=True
                )

                text_nombre.set("Nombre: --")
                text_dni.set("DNI: --")
                text_id.set("ID: --")

                editar_cliente_boton.config(state="disabled")
                eleminar_cliente_boton.config(state="disabled")
                agregar_dias_boton.config(state="disabled")

            else:
                messagebox.showerror(
                    "Error",
                    "Ha ocurrido un error al eliminar",
                    parent=clientes_toplevel
                )

        def agregar_dias():
            if bcn.agregar_dias(
                bcn.traduccion_nombre_dni(entry_name.get())
            ):
                mensaje_error(
                    False,
                    "Completado",
                    "Se han agregado los días satisfactoriamente",
                    admin
                )
                buscar_cliente()
            else:
                mensaje_error(
                    True,
                    "Error",
                    "Ha ocurrido un error",
                    admin
                )

        cli_encon = buscar_cliente

        # ---------------- PANEL IZQUIERDO ----------------

        frame_a = tk.Frame(
            clientes_toplevel,
            bg=C["blanco"],
            width=220
        )
        frame_a.pack(
            side=tk.LEFT,
            fill="y"
        )
        frame_a.pack_propagate(False)

        tk.Label(
            frame_a,
            text="CLIENTES",
            bg=C["blanco"],
            fg=C["texto"],
            font=(FUENTE, 14, "bold"),
            anchor="w"
        ).pack(fill="x", padx=18, pady=(22, 4))

        tk.Label(
            frame_a,
            text="Buscá un cliente por nombre",
            bg=C["blanco"],
            fg=C["secundario"],
            font=(FUENTE, 9),
            anchor="w"
        ).pack(fill="x", padx=18, pady=(0, 12))

        entry_name = entry_autocompletado(frame_a)

        boton_buscar = crear_boton(frame_a,"Buscar cliente",comando=cli_encon,principal=True)
        boton_buscar.pack(fill="x", padx=18, pady=12)

        # Separador entre paneles
        ttk.Separator(
            clientes_toplevel,
            orient="vertical"
        ).pack(side="left", fill="y")

        # ---------------- PANEL DERECHO ----------------

        frame_b = tk.Frame(
            clientes_toplevel,
            bg=C["fondo"]
        )
        frame_b.pack(
            side=tk.LEFT,
            fill="both",
            expand=True
        )

        # Zona de información
        frame_b_a = tk.Frame(
            frame_b,
            bg=C["fondo"]
        )
        frame_b_a.pack(
            fill="both",
            expand=True
        )

        label_nada = tk.Label(
            frame_b_a,
            text="Seleccioná un cliente para ver sus datos",
            bg=C["fondo"],
            fg=C["secundario"],
            font=(FUENTE, 11)
        )
        label_nada.pack(
            anchor="center",
            expand=True
        )

        # Tarjeta principal: inicialmente oculta
        contenedor = tk.Frame(
            frame_b_a,
            bg=C["blanco"],
            highlightbackground=C["borde"],
            highlightthickness=1
        )

        # Cabecera de la tarjeta
        cabecera = tk.Frame(
            contenedor,
            bg=C["blanco"]
        )
        cabecera.pack(fill="x", padx=12, pady=(10, 4))

        crear_dato(
            cabecera,
            text_nombre,
            destacado=True
        ).pack(side="left", fill="x", expand=True)

        crear_dato(
            cabecera,
            text_id
        ).pack(side="right")

        crear_dato(
            contenedor,
            text_dni
        ).pack(fill="x", padx=12)

        ttk.Separator(
            contenedor,
            orient="horizontal"
        ).pack(fill="x", padx=12, pady=6)

        # Datos de asistencia
        crear_seccion(
            contenedor,
            "ASISTENCIA"
        )

        fila_asistencia = tk.Frame(
            contenedor,
            bg=C["blanco"]
        )
        fila_asistencia.pack(fill="x", padx=12)

        crear_dato(
            fila_asistencia,
            text_dias_servicio
        ).pack(side="left", fill="x", expand=True)

        crear_dato(
            fila_asistencia,
            text_dias_faltantes,
            destacado=True
        ).pack(side="left", fill="x", expand=True)

        crear_dato(
            contenedor,
            text_ultima_fecha
        ).pack(fill="x", padx=12)

        if get_config("general","restar_dias",tipo=bool):
            crear_dato(
                contenedor,
                text_proximo_dia
            ).pack(fill="x", padx=12)

        crear_dato(
            contenedor,
            text_dias_x_semana
        ).pack(fill="x", padx=12)

        ttk.Separator(
            contenedor,
            orient="horizontal"
        ).pack(fill="x", padx=12, pady=6)

        # Datos de la cuota
        crear_seccion(
            contenedor,
            "CUOTA"
        )

        crear_dato(
            contenedor,
            text_fecha_inicio
        ).pack(fill="x", padx=12)

        crear_dato(
            contenedor,
            text_fecha_final
        ).pack(fill="x", padx=12, pady=(0, 8))

        # ---------------- BOTONES INFERIORES ----------------

        ttk.Separator(
            frame_b,
            orient="horizontal"
        ).pack(side="bottom", fill="x")

        frame_b_b = tk.Frame(
            frame_b,
            bg=C["blanco"]
        )
        frame_b_b.pack(
            side="bottom",
            fill="x",
            padx=8,
            pady=8
        )

        agregar_dias_boton = crear_boton(
            frame_b_b,
            "Agregar días",
            comando=lambda: mensaje_confirmacion(
                "Agregar días",
                "¿Desea actualizar el mes al cliente?",
                clientes_toplevel,
                agregar_dias
            ),
            principal=True,
            state="disabled"
        )
        agregar_dias_boton.pack(
            side="left",
            padx=4
        )

        eleminar_cliente_boton = crear_boton(
            frame_b_b,
            "Eliminar cliente",
            comando=lambda: mensaje_confirmacion(
                "Eliminar cliente",
                "¿Desea eliminar a este cliente?",
                clientes_toplevel,
                eleminar_cliente
            ),
            peligro=True,
            state="disabled"
        )
        eleminar_cliente_boton.pack(
            side="left",
            padx=4
        )

        editar_cliente_boton = crear_boton(
            frame_b_b,
            "Editar cliente",
            comando=lambda: ventana_agregar(
                True,
                cli_encon()[0]
            ),
            state="disabled"
        )
        editar_cliente_boton.pack(
            side="left",
            padx=4
        )

        
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
    C = {
        "blanco": "#FFFFFF",
        "fondo": "#F3F4F6",
        "texto": "#1F2937",
        "secundario": "#6B7280",
        "borde": "#D1D5DB",
        "azul": "#2563EB",
        "azul_claro": "#DBEAFE",
        "azul_texto": "#1D4ED8",
    }

    FUENTE = "Segoe UI"

    frame = tk.Frame(
        jefe,
        bg=C["blanco"]
    )
    frame.pack(
        fill="x",
        padx=12,
        pady=8
    )

    # Etiqueta del campo
    tk.Label(
        frame,
        text="Nombre del cliente",
        bg=C["blanco"],
        fg=C["texto"],
        font=(FUENTE, 10, "bold"),
        anchor="w"
    ).pack(
        fill="x",
        pady=(0, 6)
    )

    # Campo de búsqueda
    entry_nombre = tk.Entry(
        frame,
        justify="left",
        bg=C["blanco"],
        fg=C["texto"],
        insertbackground=C["texto"],
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightbackground=C["borde"],
        highlightcolor=C["azul"],
        font=(FUENTE, 10)
    )
    entry_nombre.pack(
        fill="x",
        ipady=6,
        pady=(0, 8)
    )

    # Lista de sugerencias
    frame_lista = tk.Frame(
        frame,
        bg=C["blanco"],
        highlightbackground=C["borde"],
        highlightthickness=1
    )
    frame_lista.pack(
        fill="both",
        expand=True
    )

    menu_autocompletado = tk.Listbox(
        frame_lista,
        activestyle="none",
        bg=C["blanco"],
        fg=C["texto"],
        selectbackground=C["azul_claro"],
        selectforeground=C["azul_texto"],
        relief="flat",
        bd=0,
        highlightthickness=0,
        font=(FUENTE, 10),
        height=7,
        exportselection=False
    )
    menu_autocompletado.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar = tk.Scrollbar(
        frame_lista,
        orient=tk.VERTICAL,
        command=menu_autocompletado.yview
    )
    scrollbar.pack(
        side="right",
        fill="y"
    )

    menu_autocompletado.config(
        yscrollcommand=scrollbar.set
    )

    # Obtener clientes una sola vez al inicializar.
    # Se actualiza en cada búsqueda de sugerencias.
    clientes = bcn.get_todos_clientes_nombre()

    def actualizar_sugerencias(event=None):
        texto = entry_nombre.get().strip().casefold()

        menu_autocompletado.delete(0, tk.END)

        if not texto:
            coincidencias = clientes
        else:
            coincidencias = [
                c for c in clientes
                if texto in c.casefold()
            ]

        for cliente in coincidencias:
            menu_autocompletado.insert(
                tk.END,
                cliente
            )

    def seleccionar(event=None):
        seleccion = menu_autocompletado.curselection()

        if not seleccion:
            return

        cliente = menu_autocompletado.get(seleccion[0])

        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, cliente)

    # Eventos
    entry_nombre.bind(
        "<KeyRelease>",
        actualizar_sugerencias
    )

    menu_autocompletado.bind(
        "<<ListboxSelect>>",
        seleccionar
    )

    # Carga inicial
    actualizar_sugerencias()

    return entry_nombre


def mensaje_confirmacion(titulo: str, mensaje: str, jefe: tk.Toplevel,funcion):

    if messagebox.askyesno(title=titulo,message=mensaje,parent=jefe,icon="question"):
        funcion()
    else:
        return

def mensaje_error(error:bool,titulo:str,mensaje:str,padre: tk.Toplevel):
    messagebox.showinfo(title=titulo,message=mensaje,parent=padre) if error else messagebox.showerror(title=titulo,message=mensaje,parent=padre) 


#==========================FUNCIONES AUXILIARES===============================

def crear_boton(
    parent, texto, comando,
    principal=False, peligro=False, **kwargs
):
    if principal:
        bg = C["azul"]
        fg = C["blanco"]
        hover = C["azul_hover"]
    elif peligro:
        bg = C["blanco"]
        fg = C["rojo_texto"]
        hover = C["rojo_fondo"]
    else:
        bg = C["blanco"]
        fg = C["texto"]
        hover = "#E5E7EB"

    boton = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=12,
        pady=7,
        cursor="hand2",
        font=(FUENTE, 9),
        **kwargs
    )

    boton.bind(
        "<Enter>",
        lambda e: boton.configure(bg=hover)
        if str(boton["state"]) != "disabled" else None
    )
    boton.bind(
        "<Leave>",
        lambda e: boton.configure(bg=bg)
        if str(boton["state"]) != "disabled" else None
    )

    return boton

def crear_dato(parent, variable, destacado=False):
    return tk.Label(
        parent,
        textvariable=variable,
        bg=C["blanco"],
        fg=C["texto"],
        font=(FUENTE, 11, "bold" if destacado else "normal"),
        anchor="w",
        justify="left",
        padx=10,
        pady=5
    )

def crear_seccion(parent, titulo):
    tk.Label(
        parent,
        text=titulo,
        bg=C["blanco"],
        fg=C["secundario"],
        font=(FUENTE, 9, "bold"),
        anchor="w"
    ).pack(fill="x", padx=12, pady=(10, 3))   
