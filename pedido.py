#esta seccion tiene que estar conectada a el principal por medio del boton de pedido
# (esta ventana en particular es el formulario "Agregar Pedido")

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from almacenamiento import obtener_conexion

# ------------------------------------------------------------------
# Paleta de colores (tomada del HTML de referencia
# "macscol_app_menu_escritorio.html") para que la app de escritorio
# se vea consistente con el diseño aprobado.
# ------------------------------------------------------------------
COLOR_CHROME = "#F3F3F1"       # fondo general de la ventana
COLOR_CHROME_LINE = "#D7D7D3"  # bordes / separadores
COLOR_NAVY = "#0B1F6B"         # color principal (botones, acentos fuertes)
COLOR_NAVY_DEEP = "#071540"    # títulos / barra oscura
COLOR_ACCENT = "#3B5FC7"       # resaltados / foco
COLOR_ACCENT_BG = "#E8EDFB"    # fondo de resaltado suave
COLOR_INK = "#1B1D1F"          # texto principal
COLOR_GRAY = "#68696A"         # texto secundario
COLOR_WHITE = "#FFFFFF"

# Alias para no romper referencias anteriores del archivo
COLOR_FONDO = COLOR_CHROME
COLOR_BOTON = COLOR_NAVY

FUENTE_BOTON = ("Segoe UI", 12, "bold")
FUENTE_TITULO = ("Segoe UI", 22, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_ETIQUETA = ("Segoe UI", 11, "bold")
FUENTE_ETIQUETA_SUAVE = ("Segoe UI", 10)

# ------------------------------------------------------------------
# Nombres de días y meses en español (no dependemos del "locale" del
# sistema operativo, porque en Windows/Linux no siempre está instalado
# el idioma español; así el formato de fecha nunca falla).
# ------------------------------------------------------------------
DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


def fecha_actual_en_espanol():
    """Devuelve la fecha de hoy con el formato: 'viernes , 24 de julio de 2026'"""
    hoy = date.today()
    dia_semana = DIAS_ES[hoy.weekday()]
    mes = MESES_ES[hoy.month - 1]
    return f"{dia_semana} , {hoy.day} de {mes} de {hoy.year}"


# ------------------------------------------------------------------
# NOTA sobre el peso por producto:
# Todavía no hay una base de datos conectada entre módulos, así que
# aquí se usa un diccionario de ejemplo (producto -> peso por unidad
# en KG) solo para poder calcular el "Peso" mientras se arma el
# pedido. Cuando conectemos Producto con una base de datos real, este
# diccionario se reemplaza por una consulta al peso real registrado
# en el módulo Producto ("Peso Canastilla (KG)").
# ------------------------------------------------------------------
PESO_UNITARIO_DEMO = {
    "Producto A": 10,
    "Producto B": 15,
    "Producto C": 8,
}


class VentanaAgregarPedido(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Agregar Pedido — MACS COL")

        # ----------------------------------------------------------------
        # Tamaño de ventana: se redujo de 1200x950 a 1200x860 y se centra
        # en la pantalla, para que quepa cómodamente en pantallas de
        # portátil (1366x768) sin quedar cortada por la barra de tareas.
        # ----------------------------------------------------------------
        ancho_ventana, alto_ventana = 1200, 860
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        pos_x = (ancho_pantalla - ancho_ventana) // 2
        pos_y = max((alto_pantalla - alto_ventana) // 2 - 20, 0)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")
        self.resizable(False, False)
        self.configure(bg=COLOR_CHROME)

        # Número de planilla (se incrementa cada vez que se guarda un pedido)
        self.numero_planilla = 1

        # ID incremental para cada pedido guardado en la tabla de la izquierda
        # Items que se van agregando con "Listar" antes de guardar el pedido
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
    # ESTILO "TIPO EXCEL" PARA LAS TABLAS (Treeview)
    # ------------------------------------------------------------------
    def _configurar_estilo_tablas(self):
        """
        ttk.Treeview no dibuja líneas de cuadrícula verticales/horizontales
        de forma nativa como una hoja de Excel, así que nos acercamos lo
        más posible usando:
          - tema "clam" (permite personalizar bordes y colores)
          - bordes delgados en encabezados y celdas
          - franjas de color alternas en las filas (como Excel)
        """
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
        # Quita el resaltado azul feo de selección y lo deja gris claro,
        # más parecido a Excel.
        estilo.map(
            "Excel.Treeview",
            background=[("selected", "#CCE8FF")],
            foreground=[("selected", "black")],
        )

    def _aplicar_filas_alternas(self, tabla):
        """Colorea las filas pares/impares como en Excel (blanco / gris claro)."""
        tabla.tag_configure("par", background="#F5F5F5")
        tabla.tag_configure("impar", background="white")

    # ------------------------------------------------------------------
    # BUSCADOR EN LOS COMBOBOX (Cliente, Producto, Vehiculo, Destino,
    # Conductor). Convierte el Combobox de "solo selección" a uno donde
    # se puede escribir texto y la lista desplegable se filtra en vivo
    # mostrando solo las coincidencias.
    # ------------------------------------------------------------------
    def _configurar_busqueda_combobox(self, combo, obtener_valores):
        """
        obtener_valores: función sin argumentos que retorna la lista
        COMPLETA de valores disponibles en ese momento (por ejemplo
        list(self.clientes)). Se llama cada vez que el usuario escribe,
        así siempre refleja los datos más recientes cargados de la BD.
        """
        combo.configure(state="normal")

        def filtrar(event=None):
            # Las teclas de navegación/selección no deben re-filtrar
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

            # Despliega automáticamente la lista filtrada mientras se escribe
            if coincidencias:
                try:
                    combo.event_generate("<Down>")
                except tk.TclError:
                    pass

        def restaurar_lista_completa(event=None):
            # Al seleccionar un valor o al volver a hacer clic en el
            # campo, se restaura la lista completa (por si se quiere
            # buscar algo distinto).
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

    # ------------------------------------------------------------------
    # PANEL IZQUIERDO: Cliente / Producto / Cantidad (dentro de un recuadro)
    # ------------------------------------------------------------------
    def _crear_panel_izquierdo(self):
        self.frame_izquierdo = tk.Frame(
            self,
            bg=COLOR_WHITE,
            highlightbackground=COLOR_CHROME_LINE,
            highlightthickness=1,
            bd=0,
        )
        self.frame_izquierdo.place(x=30, y=90, width=520, height=230)

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
        self.frame_derecho.place(x=610, y=90, width=560, height=230)

        frame = tk.Frame(self.frame_derecho, bg=COLOR_WHITE)
        frame.place(x=25, y=15, width=510, height=200)

        etiquetas = ["Vehiculo", "Origen", "Destino", "Fecha", "Conductor"]
        self.combos_derecha = {}

        for i, texto in enumerate(etiquetas):
            tk.Label(
                frame, text=texto, font=FUENTE_ETIQUETA, fg=COLOR_INK, bg=COLOR_WHITE
            ).grid(row=i, column=0, sticky="w", pady=9, padx=(0, 15))

            if texto == "Fecha":
                # Campo de solo lectura con la fecha de hoy en español.
                combo = ttk.Combobox(
                    frame,
                    state="readonly",
                    width=30,
                    values=[fecha_actual_en_espanol()],
                )
                combo.set(fecha_actual_en_espanol())
            else:
                combo = ttk.Combobox(frame, state="readonly", width=30)

            combo.grid(row=i, column=1, sticky="w", pady=9)
            self.combos_derecha[texto] = combo

        self._configurar_busqueda_combobox(
            self.combos_derecha["Vehiculo"], lambda: list(self.vehiculos)
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
            self.combos_derecha["Destino"]["values"] = list(self.destinos)
            self.combos_derecha["Conductor"]["values"] = list(self.conductores)

        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron cargar los datos del pedido:\n\n{error}")

    def cargar_pedidos(self):
        """Carga el historial de pedidos y sus detalles desde SQLite."""
        for fila in self.tabla_pedidos.get_children():
            self.tabla_pedidos.delete(fila)

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT pedidos.id, clientes.nombre, productos.nombre,
                       detalle_pedido.cantidad, detalle_pedido.peso_total
                FROM pedidos
                JOIN clientes ON clientes.id = pedidos.cliente_id
                JOIN detalle_pedido ON detalle_pedido.pedido_id = pedidos.id
                JOIN productos ON productos.id = detalle_pedido.producto_id
                ORDER BY pedidos.id, detalle_pedido.id
            """)
            pedidos = cursor.fetchall()
            proximo_id = cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM pedidos").fetchone()[0]
            conexion.close()

            for id_pedido, cliente, producto, cantidad, peso in pedidos:
                tag = "par" if len(self.tabla_pedidos.get_children()) % 2 == 0 else "impar"
                self.tabla_pedidos.insert(
                    "", "end", values=(id_pedido, cliente, producto, cantidad, peso), tags=(tag,)
                )

            self.numero_planilla = proximo_id
            self.label_planilla.config(text=f"Planilla No {self.numero_planilla}")

        except Exception as error:
            messagebox.showerror("Error", f"No se pudieron cargar los pedidos:\n\n{error}")

    def _crear_fila_listar(self):
        frame = tk.Frame(self, bg=COLOR_FONDO)
        frame.place(x=30, y=390, width=1150, height=160)

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

        self.texto_observaciones = tk.Text(frame, width=36, height=8)
        self.texto_observaciones.place(x=520, y=50)

    # ------------------------------------------------------------------
    # TABLAS (estilo Excel)
    # ------------------------------------------------------------------
    def _crear_tablas(self):
        frame = tk.Frame(self, bg=COLOR_FONDO)
        frame.place(x=30, y=560, width=1150, height=250)

        # ---------- Tabla izquierda: pedidos guardados ----------
        columnas_1 = ("Id", "Cliente", "Producto", "Cantidad", "Peso Total")
        self.tabla_pedidos = ttk.Treeview(
            frame,
            columns=columnas_1,
            show="headings",
            height=9,
            style="Excel.Treeview",
        )
        anchos_1 = (50, 180, 180, 100, 110)
        for col, ancho in zip(columnas_1, anchos_1):
            self.tabla_pedidos.heading(col, text=col)
            self.tabla_pedidos.column(col, width=ancho, anchor="center")

        self.tabla_pedidos.place(x=0, y=0, width=630, height=230)
        self._aplicar_filas_alternas(self.tabla_pedidos)

        # ---------- Tabla derecha: items del pedido actual ----------
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

        self.tabla_items.place(x=660, y=0, width=490, height=230)
        self._aplicar_filas_alternas(self.tabla_items)

    # ------------------------------------------------------------------
    # PIE DEL FORMULARIO: Eliminar / Actualizar / Guardar
    # ------------------------------------------------------------------
    def _crear_pie_formulario(self):
        frame = tk.Frame(self, bg=COLOR_FONDO)
        frame.place(x=30, y=830, width=1150, height=110)

        tk.Button(
            frame,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.eliminar_pedido,
        ).place(x=0, y=0)

        tk.Label(
            frame, text="Id Pedido a eliminar", font=FUENTE_ETIQUETA, bg=COLOR_FONDO
        ).place(x=320, y=0)
        self.entrada_id_eliminar = tk.Entry(frame, width=25)
        self.entrada_id_eliminar.place(x=320, y=28)

        tk.Button(
            frame,
            text="Actualizar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.actualizar,
        ).place(x=0, y=65)

        tk.Label(
            frame, text="Numero de Ruta", font=FUENTE_ETIQUETA, bg=COLOR_FONDO
        ).place(x=320, y=65)
        self.entrada_numero_ruta = tk.Entry(frame, width=25)
        self.entrada_numero_ruta.place(x=320, y=93)

        tk.Button(
            frame,
            text="Guardar",
            bg=COLOR_BOTON,
            fg="white",
            font=("Segoe UI", 16, "bold"),
            width=14,
            command=self.guardar_pedido,
        ).place(x=880, y=25)

    # ------------------------------------------------------------------
    # ACCIONES
    # ------------------------------------------------------------------
    def listar_item(self):
        """
        Agrega el Producto + Cantidad actuales a la tabla derecha
        (items del pedido que se está armando) y suma su peso al
        total mostrado junto al botón "Listar".
        """
        producto = self.combo_producto.get()
        cantidad_texto = self.entrada_cantidad.get().strip()

        if not producto:
            messagebox.showwarning("Pedido", "Selecciona un producto.")
            return

        if not cantidad_texto.isdigit():
            messagebox.showwarning("Pedido", "La cantidad debe ser un número.")
            return

        cantidad = int(cantidad_texto)
        peso_unitario = PESO_UNITARIO_DEMO.get(producto, 0)
        peso_item = cantidad * peso_unitario

        # Se agrega a la lista en memoria del pedido actual
        self.items_pedido_actual.append(
            {"producto": producto, "cantidad": cantidad, "peso": peso_item}
        )

        tag = "par" if len(self.tabla_items.get_children()) % 2 == 0 else "impar"
        self.tabla_items.insert("", "end", values=(producto, cantidad), tags=(tag,))

        self.peso_total_actual += peso_item
        self.label_peso.config(text=f"Peso {self.peso_total_actual}")

        # Limpia los campos para el siguiente producto
        self.combo_producto.set("")
        self.entrada_cantidad.delete(0, "end")

    def guardar_pedido(self):
        """
        Guarda el pedido actual: pasa cada item de la tabla derecha
        (items_pedido_actual) a la tabla izquierda (historial de
        pedidos), todos con el mismo Id de pedido, y luego limpia
        el formulario para uno nuevo.
        """
        cliente = self.combo_cliente.get()

        if not cliente:
            messagebox.showwarning("Pedido", "Selecciona un cliente.")
            return

        if not self.items_pedido_actual:
            messagebox.showwarning(
                "Pedido", "Agrega al menos un producto con 'Listar' antes de guardar."
            )
            return

        id_pedido = self.siguiente_id_pedido

        for item in self.items_pedido_actual:
            tag = "par" if len(self.tabla_pedidos.get_children()) % 2 == 0 else "impar"
            self.tabla_pedidos.insert(
                "",
                "end",
                values=(id_pedido, cliente, item["producto"], item["cantidad"], item["peso"]),
                tags=(tag,),
            )

        # Prepara el formulario para el siguiente pedido
        self.siguiente_id_pedido += 1
        self.numero_planilla += 1
        self.label_planilla.config(text=f"Planilla No {self.numero_planilla}")

        self.items_pedido_actual = []
        self.peso_total_actual = 0
        self.label_peso.config(text=f"Peso {self.peso_total_actual}")

        for fila in self.tabla_items.get_children():
            self.tabla_items.delete(fila)

        self.combo_cliente.set("")
        self.texto_observaciones.delete("1.0", "end")
        self.entrada_numero_ruta.delete(0, "end")

        messagebox.showinfo("Pedido", f"Pedido No {id_pedido} guardado correctamente.")

    def eliminar_pedido(self):
        """Elimina de la tabla izquierda TODAS las filas que tengan el Id escrito."""
        id_buscado = self.entrada_id_eliminar.get().strip()

        if not id_buscado:
            messagebox.showwarning("Pedido", "Debe escribir un Id de pedido.")
            return

        filas_eliminadas = 0
        for fila in self.tabla_pedidos.get_children():
            valores = self.tabla_pedidos.item(fila, "values")
            if valores and str(valores[0]) == id_buscado:
                self.tabla_pedidos.delete(fila)
                filas_eliminadas += 1

        if filas_eliminadas == 0:
            messagebox.showwarning(
                "Pedido", f"No se encontró ningún pedido con el Id '{id_buscado}'."
            )
        else:
            messagebox.showinfo(
                "Pedido", f"Se eliminó el pedido No {id_buscado} ({filas_eliminadas} producto(s))."
            )
        self.entrada_id_eliminar.delete(0, "end")

    def actualizar(self):
        messagebox.showinfo("Pedido", "Datos actualizados.")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    VentanaAgregarPedido(root)

    root.mainloop()