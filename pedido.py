import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import calendar
import os
import subprocess
import sys
import time
from contextlib import closing

from almacenamiento import obtener_conexion, obtener_datos_planilla, registrar_actividad



COLOR_CHROME = "#F3F3F1"       
COLOR_CHROME_LINE = "#D7D7D3"  
COLOR_NAVY = "#0B1F6B"         
COLOR_NAVY_DEEP = "#071540"    
COLOR_ACCENT = "#3B5FC7"       
COLOR_ACCENT_BG = "#E8EDFB"   
COLOR_INK = "#1B1D1F"          
COLOR_GRAY = "#68696A"         
COLOR_WHITE = "#FFFFFF"


COLOR_FONDO = COLOR_CHROME
COLOR_BOTON = COLOR_NAVY

FUENTE_BOTON = ("Segoe UI", 12, "bold")
FUENTE_TITULO = ("Segoe UI", 22, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_ETIQUETA = ("Segoe UI", 11, "bold")
FUENTE_ETIQUETA_SUAVE = ("Segoe UI", 10)


DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def fecha_en_espanol(fecha):
    dia_semana = DIAS_ES[fecha.weekday()]
    mes = MESES_ES[fecha.month - 1]
    return f"{dia_semana} , {fecha.day} de {mes} de {fecha.year}"


def fecha_actual_en_espanol():
    return fecha_en_espanol(date.today())


DIAS_CORTOS_ES = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"]


class SelectorFecha(ttk.Combobox):
    """
    fecha de windows amm calendario
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, state="readonly", **kwargs)
        self._popup = None
        self._cuerpo = None
        self._cerrado_en = 0.0
        self._fecha = date.today()
        self._mes_visible = date(self._fecha.year, self._fecha.month, 1)
        self.set(fecha_en_espanol(self._fecha))
        self.bind("<Button-1>", self._alternar_calendario)


    def obtener_fecha(self):
        """Devuelve la fecha elegida como datetime.date."""
        return self._fecha

    def establecer_fecha(self, fecha):
        self._fecha = fecha
        self.set(fecha_en_espanol(fecha))


    def _alternar_calendario(self, event=None):

        if time.time() - self._cerrado_en < 0.25:
            return "break"
        if self._popup is not None and self._popup.winfo_exists():
            self._cerrar()
        else:
            self._abrir()
        return "break"  

    def _abrir(self):
        self._mes_visible = date(self._fecha.year, self._fecha.month, 1)
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg=COLOR_ACCENT)
        self._popup = popup
        self._cuerpo = tk.Frame(popup, bg=COLOR_WHITE)
        self._cuerpo.pack(padx=1, pady=1)
        self._dibujar()

        popup.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        popup.geometry(f"+{x}+{y}")
        popup.bind("<Escape>", lambda e: self._cerrar())
        popup.bind("<FocusOut>", lambda e: self.after(80, self._cerrar_si_sin_foco))
        popup.focus_force()

    def _cerrar(self):
        if self._popup is not None:
            try:
                self._popup.destroy()
            except tk.TclError:
                pass
        self._popup = None
        self._cuerpo = None
        self._cerrado_en = time.time()

    def _cerrar_si_sin_foco(self):
        if self._popup is None:
            return
        try:
            foco = self.focus_get()
        except KeyError:
            foco = None
        if foco is None or not str(foco).startswith(str(self._popup)):
            self._cerrar()

    def _cambiar_mes(self, delta):
        m = self._mes_visible.month - 1 + delta
        self._mes_visible = date(self._mes_visible.year + m // 12, m % 12 + 1, 1)
        self._dibujar()

    def _elegir(self, fecha):
        self.establecer_fecha(fecha)
        self._cerrar()

    def _dibujar(self):
        for hijo in self._cuerpo.winfo_children():
            hijo.destroy()

        hoy = date.today()
        fuente = ("Segoe UI", 10)

        cab = tk.Frame(self._cuerpo, bg=COLOR_WHITE)
        cab.pack(fill="x", padx=6, pady=(6, 2))
        flecha_izq = tk.Label(cab, text="◄", font=fuente, fg=COLOR_INK, bg=COLOR_WHITE, cursor="hand2")
        flecha_izq.pack(side="left", padx=4)
        flecha_izq.bind("<Button-1>", lambda e: self._cambiar_mes(-1))
        flecha_der = tk.Label(cab, text="►", font=fuente, fg=COLOR_INK, bg=COLOR_WHITE, cursor="hand2")
        flecha_der.pack(side="right", padx=4)
        flecha_der.bind("<Button-1>", lambda e: self._cambiar_mes(1))
        tk.Label(
            cab,
            text=f"{MESES_ES[self._mes_visible.month - 1]} de {self._mes_visible.year}",
            font=fuente, fg=COLOR_ACCENT, bg=COLOR_WHITE,
        ).pack(expand=True)



        rejilla = tk.Frame(self._cuerpo, bg=COLOR_WHITE)
        rejilla.pack(padx=6, pady=2)
        for col, nombre in enumerate(DIAS_CORTOS_ES):
            tk.Label(
                rejilla, text=nombre, width=4, font=("Segoe UI", 10, "bold"),
                fg=COLOR_INK, bg=COLOR_WHITE,
            ).grid(row=0, column=col)

        semanas = calendar.Calendar(firstweekday=6).monthdatescalendar(
            self._mes_visible.year, self._mes_visible.month
        )
        for fila, semana in enumerate(semanas, start=1):
            for col, dia in enumerate(semana):
                del_mes = dia.month == self._mes_visible.month
                etiqueta = tk.Label(
                    rejilla, text=str(dia.day), width=4, font=fuente,
                    fg=COLOR_INK if del_mes else "#AAAAAA",
                    bg=COLOR_ACCENT_BG if dia == self._fecha else COLOR_WHITE,
                    cursor="hand2",
                    highlightthickness=1,
                    highlightbackground=COLOR_ACCENT if dia == hoy else (
                        COLOR_ACCENT_BG if dia == self._fecha else COLOR_WHITE
                    ),
                )
                etiqueta.grid(row=fila, column=col, padx=1, pady=1)
                etiqueta.bind("<Button-1>", lambda e, d=dia: self._elegir(d))


        pie = tk.Label(
            self._cuerpo, text=f"Hoy: {hoy.strftime('%d/%m/%Y')}", font=fuente,
            fg=COLOR_INK, bg=COLOR_WHITE, cursor="hand2",
        )
        pie.pack(pady=(2, 6))
        pie.bind("<Button-1>", lambda e: self._elegir(hoy))



class VentanaAgregarPedido(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Agregar Pedido — MACS COL")

        # ----------------------------------------------------------------
        # Tamaño de ventana
        # ----------------------------------------------------------------
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        ancho_ventana = min(1200, max(320, ancho_pantalla - 40))
        alto_ventana = min(700, max(240, alto_pantalla - 80))
        pos_x = max((ancho_pantalla - ancho_ventana) // 2, 0)
        pos_y = max((alto_pantalla - alto_ventana) // 2, 0)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")
        self.minsize(min(700, ancho_ventana), min(500, alto_ventana))
        self.resizable(True, True)
        self._escala_tk_base = float(self.tk.call("tk", "scaling"))
        self.configure(bg=COLOR_CHROME)


        self.numero_planilla = 1


        self.items_pedido_actual = []
        self.peso_total_actual = 0
        self.clientes = {}
        self.productos = {}
        self.vehiculos = {}
        self.destinos = {}
        self.conductores = {}

        self._configurar_estilo_tablas()
        self._crear_titulo()
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()
        self._crear_fila_listar()
        self._crear_tablas()
        self._crear_pie_formulario()
        self.cargar_datos_formulario()
        self.cargar_pedidos()

    # ------------------------------------------------------------------
    # TABLAS
    # ------------------------------------------------------------------
    def _configurar_estilo_tablas(self):

        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(
            "Excel.Treeview",
            background="white",
            fieldbackground="white",
            rowheight=24,
            bordercolor="#999999",
            borderwidth=1,
            relief="solid",
        )
        estilo.configure(
            "Excel.Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#F0F0F0",
            relief="solid",
            borderwidth=1,
        )

        estilo.map(
            "Excel.Treeview",
            background=[("selected", "#CCE8FF")],
            foreground=[("selected", "black")],
        )

    def _aplicar_filas_alternas(self, tabla):
        """Colorea las filas pares/impares como en Excel (blanco / gris claro)."""
        tabla.tag_configure("par", background="#F5F5F5")
        tabla.tag_configure("impar", background="white")














    def _configurar_busqueda_combobox(self, combo, obtener_valores):
        """
        obtener_valores: función sin argumentos que retorna la lista
        COMPLETA de valores disponibles en ese momento (por ejemplo
        list(self.clientes)). Se llama cada vez que el usuario escribe,
        así siempre refleja los datos más recientes cargados de la BD.
        """
        combo.configure(state="normal")

        def filtrar(event=None):
            
            if event is not None and event.keysym in (
                "Up", "Down", "Left", "Right", "Return", "Escape", "Tab"
            ):
                return

            texto = combo.get().lower().strip()
            todos = obtener_valores()
            coincidencias = todos if texto == "" else [
                valor for valor in todos if texto in valor.lower()
            ]
            combo["values"] = coincidencias

            if coincidencias:
                try:
                    combo.event_generate("<Down>")
                except tk.TclError:
                    pass

        def restaurar_lista_completa(event=None):

            combo["values"] = obtener_valores()

        combo.bind("<KeyRelease>", filtrar)
        combo.bind("<<ComboboxSelected>>", restaurar_lista_completa)
        combo.bind("<FocusIn>", restaurar_lista_completa)

    # ------------------------------------------------------------------
    # TÍTULO + PLANILLA
    # ------------------------------------------------------------------
    def _crear_titulo(self):
        frame_titulo = tk.Frame(self, bg=COLOR_CHROME)
        frame_titulo.pack(fill="x", padx=25, pady=(18, 0))

        tk.Label(
            frame_titulo,
            text="AGREGAR PEDIDO",
            font=FUENTE_TITULO,
            fg=COLOR_NAVY_DEEP,
            bg=COLOR_CHROME,
        ).pack(side="left")

        badge = tk.Frame(frame_titulo, bg=COLOR_ACCENT_BG)
        badge.pack(side="left", padx=(16, 0))
        self.label_planilla = tk.Label(
            badge,
            text=f"Planilla No {self.numero_planilla}",
            font=FUENTE_SUBTITULO,
            fg=COLOR_NAVY,
            bg=COLOR_ACCENT_BG,
            padx=12,
            pady=4,
        )
        self.label_planilla.pack()

        tk.Label(
            frame_titulo,
            text="Principal › Pedidos › Agregar",
            font=FUENTE_ETIQUETA_SUAVE,
            fg=COLOR_GRAY,
            bg=COLOR_CHROME,
        ).pack(side="right")

        # Línea separadora, como el borde inferior de una barra de
        # herramientas / encabezado en el HTML de referencia.
        separador = tk.Frame(self, bg=COLOR_CHROME_LINE, height=1)
        separador.pack(fill="x", padx=0, pady=(14, 0))
        self.bind("<Configure>", self._ajustar_diseno_responsivo)
        self.after_idle(self._ajustar_diseno_responsivo)


    def _ajustar_diseno_responsivo(self, event=None):
        """Escala la distribuci?n absoluta del formulario al ?rea visible."""
        if event is not None and event.widget is not self:
            return
        if not hasattr(self, "_geometrias_base"):
            self._geometrias_base = {}
            pendientes = list(self.winfo_children())
            while pendientes:
                widget = pendientes.pop()
                pendientes.extend(widget.winfo_children())
                if widget.winfo_manager() == "place":
                    info = widget.place_info()
                    self._geometrias_base[widget] = {
                        clave: info.get(clave, "0")
                        for clave in ("x", "y", "width", "height")
                    }
        ancho = max(self.winfo_width(), 1)
        alto = max(self.winfo_height(), 1)
        escala = min(ancho / 1200, alto / 700, 1.0)
        self.tk.call("tk", "scaling", self._escala_tk_base * escala)
        desplazamiento_x = max((ancho - 1200 * escala) // 2, 0)
        for widget, base in self._geometrias_base.items():
            try:
                x = round(int(base["x"]) * escala)
                y = round(int(base["y"]) * escala)
                if widget.master is self:
                    x += desplazamiento_x
                widget.place_configure(
                    x=x, y=y,
                    width=max(1, round(int(base["width"]) * escala)),
                    height=max(1, round(int(base["height"]) * escala)),
                )
            except (tk.TclError, ValueError):
                continue

    # ------------------------------------------------------------------
    # PANEL IZQUIERDO: Cliente / Producto / Cantidad
    # ------------------------------------------------------------------
    def _crear_panel_izquierdo(self):
        self.frame_izquierdo = tk.Frame(
            self,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_CHROME_LINE,
            highlightthickness=1,
            bd=0,
        )
        self.frame_izquierdo.place(x=30, y=80, width=520, height=190)

        tk.Label(
            self.frame_izquierdo, text="Cliente", font=FUENTE_ETIQUETA, fg=COLOR_INK, bg=COLOR_WHITE
        ).place(x=25, y=22)
        self.combo_cliente = ttk.Combobox(self.frame_izquierdo, state="readonly", width=28)
        self.combo_cliente.place(x=150, y=19)
        self._configurar_busqueda_combobox(self.combo_cliente, lambda: list(self.clientes))

        tk.Label(
            self.frame_izquierdo, text="Producto", font=FUENTE_ETIQUETA, fg=COLOR_INK, bg=COLOR_WHITE
        ).place(x=25, y=72)
        self.combo_producto = ttk.Combobox(
            self.frame_izquierdo,
            state="readonly",
            width=28,
        )
        self.combo_producto.place(x=150, y=69)
        self._configurar_busqueda_combobox(self.combo_producto, lambda: list(self.productos))

        tk.Label(
            self.frame_izquierdo, text="Cantidad", font=FUENTE_ETIQUETA, fg=COLOR_INK, bg=COLOR_WHITE
        ).place(x=25, y=122)
        self.entrada_cantidad = tk.Entry(
            self.frame_izquierdo, width=30, relief="solid", bd=1,
            highlightbackground=COLOR_CHROME_LINE, highlightthickness=1,
        )
        self.entrada_cantidad.place(x=150, y=120)

    # ------------------------------------------------------------------
    # PANEL DERECHO: Vehiculo / Origen / Destino / Fecha / Conductor
    # ------------------------------------------------------------------
    def _crear_panel_derecho(self):
        self.frame_derecho = tk.Frame(
            self,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_CHROME_LINE,
            highlightthickness=1,
            bd=0,
        )
        self.frame_derecho.place(x=610, y=80, width=560, height=190)

        frame = tk.Frame(self.frame_derecho, bg=COLOR_WHITE)
        frame.place(x=25, y=6, width=510, height=178)

        etiquetas = ["Vehiculo", "Origen", "Destino", "Fecha", "Conductor"]
        self.combos_derecha = {}

        for i, texto in enumerate(etiquetas):
            tk.Label(
                frame, text=texto, font=FUENTE_ETIQUETA, fg=COLOR_INK, bg=COLOR_WHITE
            ).grid(row=i, column=0, sticky="w", pady=3, padx=(0, 15))






            if texto == "Fecha":

                # el calendario.
                combo = SelectorFecha(frame, width=30)
            else:
                combo = ttk.Combobox(frame, state="readonly", width=30)

            combo.grid(row=i, column=1, sticky="w", pady=3)
            self.combos_derecha[texto] = combo

        self._configurar_busqueda_combobox(
            self.combos_derecha["Vehiculo"], lambda: list(self.vehiculos)
        )
        self._configurar_busqueda_combobox(
            self.combos_derecha["Origen"], lambda: list(self.destinos)
        )
        self._configurar_busqueda_combobox(
            self.combos_derecha["Destino"], lambda: list(self.destinos)
        )
        self._configurar_busqueda_combobox(
            self.combos_derecha["Conductor"], lambda: list(self.conductores)
        )

    # ------------------------------------------------------------------
    # FILA: botón Listar + Peso + Observaciones
    # ------------------------------------------------------------------
    def cargar_datos_formulario(self):
        """Carga los catálogos disponibles en los controles del pedido."""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            clientes = cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre, id").fetchall()
            productos = cursor.execute("""
                SELECT id, nombre, peso_canastilla
                FROM productos
                ORDER BY nombre, id
            """).fetchall()
            vehiculos = cursor.execute("SELECT id, placa FROM vehiculos ORDER BY placa").fetchall()
            destinos = cursor.execute("SELECT id, nombre FROM destinos ORDER BY nombre, id").fetchall()
            conductores = cursor.execute("""
                SELECT cedula, nombre FROM conductores ORDER BY nombre, cedula
            """).fetchall()
            conexion.close()

            self.clientes = {f"{id_cliente} - {nombre}": id_cliente for id_cliente, nombre in clientes}
            self.productos = {
                f"{id_producto} - {nombre}": (id_producto, nombre, peso or 0)
                for id_producto, nombre, peso in productos
            }
            self.vehiculos = {placa: id_vehiculo for id_vehiculo, placa in vehiculos}
            self.destinos = {f"{id_destino} - {nombre}": id_destino for id_destino, nombre in destinos}
            self.conductores = {f"{cedula} - {nombre}": cedula for cedula, nombre in conductores}

            self.combo_cliente["values"] = list(self.clientes)
            self.combo_producto["values"] = list(self.productos)
            self.combos_derecha["Vehiculo"]["values"] = list(self.vehiculos)
            self.combos_derecha["Origen"]["values"] = list(self.destinos)
            self.combos_derecha["Destino"]["values"] = list(self.destinos)
            self.combos_derecha["Conductor"]["values"] = list(self.conductores)

        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron cargar los datos del pedido:\n\n{error}")

    def cargar_pedidos(self):
        """
        Actualiza el numero de la planilla actual (siguiente Id libre en la BD).
        Las tablas del formulario ya NO se llenan con planillas guardadas:
        solo muestran la planilla que se esta armando.

        
        """
        try:
            with closing(obtener_conexion()) as conexion:
                proximo_id = conexion.execute(
                    "SELECT COALESCE(MAX(id), 0) + 1 FROM pedidos"
                ).fetchone()[0]

            self.numero_planilla = proximo_id
            self.siguiente_id_pedido = proximo_id
            self.label_planilla.config(text=f"Planilla No {self.numero_planilla}")

        except Exception as error:
            messagebox.showerror("Error", f"No se pudo leer el numero de planilla:\n\n{error}")

    def _crear_fila_listar(self):
        frame = tk.Frame(self, bg=COLOR_FONDO)
        frame.place(x=30, y=280, width=1150, height=100)

        tk.Button(
            frame,
            text="Listar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.listar_item,
        ).place(x=0, y=15)

        self.label_peso = tk.Label(
            frame,
            text=f"Peso {self.peso_total_actual}",
            font=("Segoe UI", 18, "bold"),
            fg="navy",
            bg=COLOR_FONDO,
        )
        self.label_peso.place(x=290, y=18)

        tk.Label(
            frame, text="Kg", font=("Segoe UI", 14, "bold"), bg=COLOR_FONDO
        ).place(x=440, y=22)

        tk.Label(
            frame, text="Observaciones", font=FUENTE_ETIQUETA, bg=COLOR_FONDO
        ).place(x=520, y=20)

        self.texto_observaciones = tk.Text(frame, width=36, height=3)
        self.texto_observaciones.place(x=520, y=50)

    
    def _crear_tablas(self):
        frame = tk.Frame(self, bg=COLOR_FONDO)
        frame.place(x=30, y=390, width=1150, height=180)

      # tabla
        columnas_1 = ("Cliente", "Producto", "Cantidad", "Peso (Kg)")
        self.tabla_pedidos = ttk.Treeview(
            frame,
            columns=columnas_1,
            show="headings",
            height=9,
            style="Excel.Treeview",
        )
        anchos_1 = (200, 200, 100, 100)
        for col, ancho in zip(columnas_1, anchos_1):
            self.tabla_pedidos.heading(col, text=col)
            self.tabla_pedidos.column(col, width=ancho, anchor="center")

        self.tabla_pedidos.place(x=0, y=0, width=630, height=170)
        self._aplicar_filas_alternas(self.tabla_pedidos)

        # ---------- Tabla derecha ----------
        columnas_2 = ("Producto", "Cantidad")
        self.tabla_items = ttk.Treeview(
            frame,
            columns=columnas_2,
            show="headings",
            height=9,
            style="Excel.Treeview",
        )
        anchos_2 = (220, 130)
        for col, ancho in zip(columnas_2, anchos_2):
            self.tabla_items.heading(col, text=col)
            self.tabla_items.column(col, width=ancho, anchor="center")

        self.tabla_items.place(x=660, y=0, width=490, height=170)
        self._aplicar_filas_alternas(self.tabla_items)

    # ------------------------------------------------------------------
    # BOTONES
    # ------------------------------------------------------------------
    def _crear_pie_formulario(self):
        frame = tk.Frame(self, bg=COLOR_FONDO)
        frame.place(x=30, y=585, width=1150, height=100)

        tk.Button(
            frame,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.eliminar_pedido,
        ).place(x=0, y=5)

        tk.Label(
            frame, text="ID pedido", font=FUENTE_ETIQUETA, bg=COLOR_FONDO
        ).place(x=145, y=5)
        self.entrada_id_eliminar = tk.Entry(frame, width=25)
        self.entrada_id_eliminar.place(x=145, y=32)

        tk.Button(
            frame,
            text="Actualizar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.actualizar,
        ).place(x=0, y=55)

        tk.Label(
            frame, text="Número de ruta", font=FUENTE_ETIQUETA, bg=COLOR_FONDO
        ).place(x=145, y=55)
        self.entrada_numero_ruta = tk.Entry(frame, width=25)
        self.entrada_numero_ruta.place(x=145, y=78)

        tk.Button(
            frame,
            text="Guardar",
            bg=COLOR_BOTON,
            fg="white",
            font=("Segoe UI", 16, "bold"),
            width=14,
            command=self.guardar_pedido,
        ).place(x=880, y=0)

        tk.Button(
            frame,
            text="Generar Planilla (ruta)",
            bg=COLOR_ACCENT,
            fg="white",
            font=FUENTE_BOTON,
            width=18,
            command=self.generar_planilla_ruta,
        ).place(x=880, y=55)

    # ------------------------------------------------------------------
    # ACCIONES
    # ------------------------------------------------------------------
    def _refrescar_totales_producto(self):
        """Rellena la tabla derecha sumando la cantidad de cada producto repetido."""
        totales = {}
        for item in self.items_pedido_actual:
            clave = item["producto_id"]
            if clave not in totales:
                totales[clave] = [f"{item['producto_id']} - {item['producto']}", 0]
            totales[clave][1] += item["cantidad"]

        for fila in self.tabla_items.get_children():
            self.tabla_items.delete(fila)
        for i, (nombre, cantidad) in enumerate(totales.values()):
            tag = "par" if i % 2 == 0 else "impar"
            self.tabla_items.insert("", "end", values=(nombre, cantidad), tags=(tag,))

    def listar_item(self):


        producto = self.combo_producto.get()
        cantidad_texto = self.entrada_cantidad.get().strip()

        cliente = self.combo_cliente.get()

        if not cliente:
            messagebox.showwarning("Pedido", "Selecciona un cliente.")
            return

        if not producto:
            messagebox.showwarning("Pedido", "Selecciona un producto.")
            return

        if not cantidad_texto.isdigit():
            messagebox.showwarning("Pedido", "La cantidad debe ser un número.")
            return

        cantidad = int(cantidad_texto)
        producto_id, nombre_producto, peso_unitario = self.productos[producto]
        peso_item = int(round(cantidad * peso_unitario))  # sin decimales

        # Se agrega a la lista en memoria del pedido actual
        self.items_pedido_actual.append(
            {"producto_id": producto_id, "producto": nombre_producto,
             "cantidad": cantidad, "peso": peso_item}
        )

        # Tabla izquierda: una fila por cada pedido (cliente + producto)
        tag = "par" if len(self.tabla_pedidos.get_children()) % 2 == 0 else "impar"
        self.tabla_pedidos.insert(
            "", "end", values=(cliente, producto, cantidad, peso_item), tags=(tag,)
        )
        # Tabla derecha: total sumado por producto
        self._refrescar_totales_producto()

        self.peso_total_actual += peso_item
        self.label_peso.config(text=f"Peso {int(self.peso_total_actual)}")

        # Limpia los campos para el siguiente producto
        self.combo_producto.set("")
        self.entrada_cantidad.delete(0, "end")

    def guardar_pedido(self):

    
        cliente = self.combo_cliente.get()

        if not cliente:
            messagebox.showwarning("Pedido", "Selecciona un cliente.")
            return

        if not self.items_pedido_actual:
            messagebox.showwarning(
                "Pedido", "Agrega al menos un producto con 'Listar' antes de guardar."
            )
            return

        cliente_id = self.clientes[cliente]
        vehiculo = self.combos_derecha["Vehiculo"].get()
        origen = self.combos_derecha["Origen"].get()
        destino = self.combos_derecha["Destino"].get()
        conductor = self.combos_derecha["Conductor"].get()
        observaciones = self.texto_observaciones.get("1.0", "end").strip()
        fecha = self.combos_derecha["Fecha"].obtener_fecha().isoformat()

        try:
            with closing(obtener_conexion()) as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO pedidos
                        (cliente_id, vehiculo_id, destino_id, conductor_cedula,
                         numero_ruta, observaciones, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    cliente_id,
                    self.vehiculos.get(vehiculo),
                    self.destinos.get(destino),
                    self.conductores.get(conductor),
                    None,  # la ruta se asigna despues con "Actualizar"
                    observaciones,
                    fecha,
                ))
                id_pedido = cursor.lastrowid
                cursor.executemany("""
                    INSERT INTO detalle_pedido
                        (pedido_id, producto_id, cantidad, peso_total)
                    VALUES (?, ?, ?, ?)
                """, [
                    (id_pedido, item["producto_id"], item["cantidad"], item["peso"])
                    for item in self.items_pedido_actual
                ])
                conexion.commit()
        except Exception as error:
            messagebox.showerror("Pedido", f"No se pudo guardar el pedido:\n\n{error}")
            return

        registrar_actividad(
            f"Pedido No {id_pedido} guardado: {cliente.split(' - ', 1)[-1]} "
            f"({int(self.peso_total_actual)} kg)"
        )
        self.cargar_pedidos()

        planilla_creada = False
        try:
            from generar_planilla import generar_planilla_despacho

            carpeta_proyecto = os.path.dirname(os.path.abspath(__file__))
            carpeta_planillas = os.path.join(carpeta_proyecto, "planillas")
            os.makedirs(carpeta_planillas, exist_ok=True)
            filas_planilla = [
                {
                    "cliente": cliente.split(" - ", 1)[-1],
                    "producto": item["producto"],
                    "cantidad": item["cantidad"],
                    "no_envio": "",
                }
                for item in self.items_pedido_actual
            ]
            encabezado_planilla = {
                "vehiculo": vehiculo,
                "origen": origen.split(" - ", 1)[-1] if origen else "",
                "destino": destino.split(" - ", 1)[-1] if destino else "",
                "conductor": conductor.split(" - ", 1)[-1] if conductor else "",
                "fecha": fecha,
                "numero_ruta": "",
                "numero_planilla": id_pedido,
                "observaciones": observaciones,
            }
            plantilla = os.path.join(carpeta_proyecto, "17092026EYZ9456262F PASTO.docx")
            archivo_planilla = os.path.join(carpeta_planillas, f"planilla_{id_pedido}.docx")
            generar_planilla_despacho(filas_planilla, plantilla, archivo_planilla, encabezado_planilla)
            planilla_creada = True
        except Exception as error:
            messagebox.showwarning(
                "Pedido guardado",
                f"El pedido {id_pedido} quedó guardado en la base de datos, "
                f"pero no se pudo crear el archivo de la planilla:\n\n{error}",
            )

        # Prepara el formulario para el siguiente pedido
        self.items_pedido_actual = []
        self.peso_total_actual = 0
        self.label_peso.config(text=f"Peso {self.peso_total_actual}")

        for tabla in (self.tabla_items, self.tabla_pedidos):
            for fila in tabla.get_children():
                tabla.delete(fila)

        self.combo_cliente.set("")
        self.texto_observaciones.delete("1.0", "end")
        if planilla_creada:
            messagebox.showinfo(
                "Pedido",
                f"Pedido No {id_pedido} guardado. Planilla creada en:\n{archivo_planilla}",
            )

    def eliminar_pedido(self):
        """Elimina de la tabla izquierda TODAS las filas que tengan el Id escrito."""
        id_buscado = self.entrada_id_eliminar.get().strip()

        if not id_buscado:
            messagebox.showwarning("Pedido", "Debe escribir un Id de pedido.")
            return

        try:
            with closing(obtener_conexion()) as conexion:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM pedidos WHERE id = ?", (id_buscado,))
                filas_eliminadas = cursor.rowcount
                conexion.commit()
        except Exception as error:
            messagebox.showerror("Pedido", f"No se pudo eliminar el pedido:\n\n{error}")
            return

        self.cargar_pedidos()

        if filas_eliminadas == 0:
            messagebox.showwarning(
                "Pedido", f"No se encontró ningún pedido con el Id '{id_buscado}'."
            )
        else:
            registrar_actividad(f"Pedido No {id_buscado} eliminado")
            messagebox.showinfo(
                "Pedido", f"Se eliminó el pedido No {id_buscado} de la base de datos."
            )
        self.entrada_id_eliminar.delete(0, "end")

    def generar_planilla_ruta(self):


        numero_ruta = self.entrada_numero_ruta.get().strip()
        if not numero_ruta:
            messagebox.showwarning(
                "Planilla", "Escribe el Número de ruta de la planilla que quieres generar."
            )
            return

        try:
            encabezado, filas = obtener_datos_planilla(numero_ruta)
        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron leer los pedidos de la ruta:\n\n{error}")
            return

        if not filas:
            messagebox.showwarning(
                "Planilla", f"No hay pedidos guardados para la ruta '{numero_ruta}'."
            )
            return

        encabezado["numero_planilla"] = numero_ruta

        from generar_planilla import generar_planilla_despacho

        carpeta_proyecto = os.path.dirname(os.path.abspath(__file__))
        carpeta_planillas = os.path.join(carpeta_proyecto, "planillas")
        os.makedirs(carpeta_planillas, exist_ok=True)
        plantilla = os.path.join(carpeta_proyecto, "17092026EYZ9456262F PASTO.docx")
        archivo_planilla = os.path.join(carpeta_planillas, f"planilla_ruta_{numero_ruta}.docx")

        try:
            generar_planilla_despacho(filas, plantilla, archivo_planilla, encabezado)
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo generar la planilla:\n\n{error}")
            return

        messagebox.showinfo(
            "Planilla", f"Planilla de la ruta '{numero_ruta}' generada en:\n{archivo_planilla}"
        )
        registrar_actividad(f"Planilla generada para la ruta {numero_ruta}")
        self._abrir_archivo(archivo_planilla)

    @staticmethod
    def _abrir_archivo(ruta):
        """Abre el .docx generado con la aplicacion asociada del sistema."""
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", ruta], check=False)
            else:
                subprocess.run(["xdg-open", ruta], check=False)
        except Exception:
            pass  # si no se puede abrir solo, el archivo ya quedo guardado

    def actualizar(self):
        id_pedido = self.entrada_id_eliminar.get().strip()
        numero_ruta = self.entrada_numero_ruta.get().strip()
        if not id_pedido:
            messagebox.showwarning("Pedido", "Escribe el ID del pedido al que quieres asignar la ruta.")
            return
        if not numero_ruta:
            messagebox.showwarning("Pedido", "Escribe el número de ruta.")
            return

        try:
            with closing(obtener_conexion()) as conexion:
                cursor = conexion.cursor()
                cursor.execute("UPDATE pedidos SET numero_ruta = ? WHERE id = ?",
                               (numero_ruta, id_pedido))
                actualizado = cursor.rowcount
                conexion.commit()
        except Exception as error:
            messagebox.showerror("Pedido", f"No se pudo actualizar la ruta:\n\n{error}")
            return
        self.cargar_pedidos()
        self.entrada_numero_ruta.delete(0, "end")
        self.entrada_id_eliminar.delete(0, "end")
        if actualizado:
            registrar_actividad(f"Ruta {numero_ruta} asignada al pedido No {id_pedido}")
            messagebox.showinfo("Pedido", f"Ruta del pedido {id_pedido} actualizada.")
        else:
            messagebox.showwarning("Pedido", f"No se encontró ningún pedido con el Id '{id_pedido}'.")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    VentanaAgregarPedido(root)

    root.mainloop()
