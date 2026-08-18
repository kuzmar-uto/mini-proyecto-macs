"""
================================================================================
 INTERFAZ PRINCIPAL - MACS COL
================================================================================
Recreación en Python/Tkinter de la ventana "Principal", con el nuevo diseño
tipo "software de escritorio" (mockup: macscol_app_menu_escritorio.html):

    - Barra de menú superior (Archivo / Ver / Herramientas / Ayuda)
    - Barra de herramientas con accesos directos y un buscador
    - Panel de navegación a la izquierda (árbol con secciones y contadores)
    - Panel central de "Accesos rápidos" con tarjetas (tiles)
    - Panel de "Actividad reciente" a la derecha
    - Barra de estadzo inferior

Los colores y fuentes viven en el archivo estilo.py, para que esta ventana
y todas las ventanas secundarias (Vehiculo, Destino, Cliente, Producto,
Conductor, Pedido) se vean como una sola aplicación.
================================================================================
"""

import os
import tkinter as tk
from tkinter import messagebox

from estilo import (
    CHROME, CHROME_LINE, NAVY, NAVY_DEEP, ACCENT, ACCENT_BG, INK, GRAY,
    WHITE, fecha_corta_en_espanol, linea_separadora,
)

from producto import VentanaProducto
from conductor import VentanaConductor
from destino import VentanaDestino
from vehiculo import VentanaVehiculo
from clientes import VentanaCliente
from pedido import VentanaAgregarPedido
from almacenamiento import crear_base_datos

RUTA_LOGO = os.path.join(os.path.dirname(__file__), "logo_macscol.png")

# ------------------------------------------------------------------
# Datos del panel de navegación / tarjetas.
# clave -> (título, ícono, descripción para la tarjeta, contador demo)
# ------------------------------------------------------------------
MODULOS = {
    "Vehiculo":  ("Vehículos",   "🚚", "Placa y capacidad de la flota.",              "18 registrados"),
    "Destino":   ("Destinos",    "📍", "Ciudades y puntos de entrega.",               "32 registrados"),
    "Cliente":   ("Clientes",    "👤", "Nombre e identificación.",                    "156 registrados"),
    "Producto":  ("Productos",   "📦", "Embalaje, peso y descripción.",               "64 registrados"),
    "Conductor": ("Conductores", "🧑", "Cédula, nombre y teléfono.",                  "27 registrados"),
    "Pedido":    ("Pedidos",     "📋", "Selecciona cliente, productos, vehículo y ruta para despachar.", "312 planillas este mes"),
}

ACTIVIDAD_RECIENTE = [

# funcion que se le puede añadir despues esto es un place holder #


    ("09:41", "Planilla N.° 312 guardada."),
    ("09:22", "Vehículo agregado a la flota."),
    ("08:57", "Conductor registrado."),
    ("08:30", "Destino agregado."),
    ("Ayer", "Producto actualizado."),
]


class InterfazPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---------------- Ventana principal ----------------
        self.title("Principal — MACS COL")
        self.geometry("1150x700")
        self.configure(bg=CHROME)
        self.minsize(980, 600)

        self.items_nav = {}   # clave del módulo -> widgets de su fila en el nav
        self.item_activo = "Inicio"

        self._crear_menu()
        self._crear_toolbar()

        cuerpo = tk.Frame(self, bg=CHROME)
        cuerpo.pack(side="top", fill="both", expand=True)

        self._crear_nav(cuerpo)
        self._crear_area_principal(cuerpo)

        self._crear_statusbar()

    # ------------------------------------------------------------------
    # MENÚ SUPERIOR: Archivo / Ver / Herramientas / Ayuda
    # ------------------------------------------------------------------
    def _crear_menu(self):
        menubar = tk.Menu(self)

        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Nuevo pedido", command=lambda: self._abrir_modulo("Pedido"))
        menu_archivo.add_command(label="Abrir")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self._salir)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ver = tk.Menu(menubar, tearoff=0)
        menu_ver.add_command(label="Actualizar", command=self._actualizar)
        menu_ver.add_command(label="Actividad reciente")
        menubar.add_cascade(label="Ver", menu=menu_ver)

        menu_herramientas = tk.Menu(menubar, tearoff=0)
        menu_herramientas.add_command(label="Reportes", command=self._reportes)
        menu_herramientas.add_command(label="Planillas", command=lambda: self._abrir_modulo("Pedido"))
        menubar.add_cascade(label="Herramientas", menu=menu_herramientas)

        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self._acerca_de)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.config(menu=menubar)

    # ------------------------------------------------------------------
    # BARRA DE HERRAMIENTAS
    # ------------------------------------------------------------------
    def _crear_toolbar(self):
        toolbar = tk.Frame(self, bg=WHITE, height=58)
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)

        contenido = tk.Frame(toolbar, bg=WHITE)
        contenido.pack(side="left", fill="y", padx=12)

        self._boton_toolbar(contenido, "➕  Nuevo pedido", lambda: self._abrir_modulo("Pedido"),
                             destacado=True).pack(side="left", padx=(0, 12), pady=8)

        tk.Frame(contenido, bg=CHROME_LINE, width=1).pack(side="left", fill="y", pady=10, padx=6)

        self._boton_toolbar(contenido, "🔄  Actualizar", self._actualizar).pack(side="left", padx=6, pady=8)
        self._boton_toolbar(contenido, "🧾  Planillas", lambda: self._abrir_modulo("Pedido")).pack(side="left", padx=6, pady=8)
        self._boton_toolbar(contenido, "📊  Reportes", self._reportes).pack(side="left", padx=6, pady=8)

        # ---- Buscador a la derecha ----
        buscador = tk.Frame(toolbar, bg=CHROME, highlightbackground=CHROME_LINE,
                             highlightthickness=1)
        buscador.pack(side="right", padx=16, pady=13)

        tk.Label(buscador, text="🔍", bg=CHROME, fg=GRAY).pack(side="left", padx=(8, 2))
        entrada_busqueda = tk.Entry(buscador, bg=CHROME, fg=GRAY, relief="flat",
                                     width=26, insertbackground=INK)
        entrada_busqueda.insert(0, "Buscar cliente, placa...")
        entrada_busqueda.bind("<FocusIn>", lambda e: self._limpiar_placeholder(entrada_busqueda))
        entrada_busqueda.pack(side="left", ipady=4, padx=(0, 8))

        linea_separadora(self)

    def _boton_toolbar(self, parent, texto, comando, destacado=False):
        boton = tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10),
            bg=ACCENT_BG if destacado else WHITE,
            fg=NAVY if destacado else INK,
            padx=10,
            pady=6,
            cursor="hand2",
        )
        boton.bind("<Button-1>", lambda e: comando())
        boton.bind("<Enter>", lambda e: boton.config(bg=ACCENT_BG))
        boton.bind("<Leave>", lambda e: boton.config(bg=ACCENT_BG if destacado else WHITE))
        return boton

    def _limpiar_placeholder(self, entrada):
        if entrada.get() == "Buscar cliente, placa...":
            entrada.delete(0, "end")
            entrada.config(fg=INK)

    # ------------------------------------------------------------------
    # PANEL DE NAVEGACIÓN (IZQUIERDA)
    # ------------------------------------------------------------------
    def _crear_nav(self, parent):
        nav = tk.Frame(parent, bg=WHITE, width=210)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        tk.Frame(nav, bg=CHROME_LINE, width=1).place(relx=1.0, rely=0, relheight=1, anchor="ne")

        self._titulo_grupo_nav(nav, "General")
        self._fila_nav(nav, "Inicio", "🏠", "Inicio", None)

        self._titulo_grupo_nav(nav, "Gestión")
        for clave in ("Vehiculo", "Destino", "Cliente", "Producto", "Conductor"):
            titulo, icono, _, contador = MODULOS[clave]
            self._fila_nav(nav, clave, icono, titulo, contador)

        self._titulo_grupo_nav(nav, "Operación")
        titulo, icono, _, contador = MODULOS["Pedido"]
        self._fila_nav(nav, "Pedido", icono, titulo, contador)

        self._resaltar_item_activo()

    def _titulo_grupo_nav(self, parent, texto):
        tk.Label(
            parent,
            text=texto.upper(),
            font=("Segoe UI", 8, "bold"),
            fg=GRAY,
            bg=WHITE,
        ).pack(anchor="w", padx=16, pady=(14, 4))

    def _fila_nav(self, parent, clave, icono, texto, contador):
        fila = tk.Frame(parent, bg=WHITE)
        fila.pack(fill="x")

        barra_activa = tk.Frame(fila, bg=WHITE, width=3)
        barra_activa.pack(side="left", fill="y")

        contenido = tk.Frame(fila, bg=WHITE, cursor="hand2")
        contenido.pack(side="left", fill="x", expand=True, padx=(6, 10), pady=6)

        etiquetas = []
        etiquetas.append(tk.Label(contenido, text=icono, bg=WHITE, font=("Segoe UI", 11)))
        etiquetas[-1].pack(side="left")

        etiquetas.append(tk.Label(contenido, text=texto, bg=WHITE, fg=INK,
                                   font=("Segoe UI", 10)))
        etiquetas[-1].pack(side="left", padx=(8, 0))

        if contador:
            etiqueta_contador = tk.Label(contenido, text=contador.split()[0], bg=WHITE,
                                          fg=GRAY, font=("Segoe UI", 8))
            etiqueta_contador.pack(side="right")
            etiquetas.append(etiqueta_contador)

        widgets = [fila, contenido] + etiquetas

        def al_hacer_clic(event=None, clave=clave):
            self.item_activo = clave
            self._resaltar_item_activo()
            if clave != "Inicio":
                self._abrir_modulo(clave)

        for w in widgets:
            w.bind("<Button-1>", al_hacer_clic)

        self.items_nav[clave] = {"barra": barra_activa, "fondo": [fila, contenido] + etiquetas}

    def _resaltar_item_activo(self):
        for clave, partes in self.items_nav.items():
            activo = clave == self.item_activo
            color_fondo = ACCENT_BG if activo else WHITE
            partes["barra"].config(bg=ACCENT if activo else WHITE)
            for w in partes["fondo"]:
                w.config(bg=color_fondo)

    # ------------------------------------------------------------------
    # ÁREA PRINCIPAL: tarjetas (tiles) + actividad reciente
    # ------------------------------------------------------------------
    def _crear_area_principal(self, parent):
        area = tk.Frame(parent, bg=CHROME)
        area.pack(side="left", fill="both", expand=True)

        panel = tk.Frame(area, bg=CHROME)
        panel.pack(side="left", fill="both", expand=True, padx=24, pady=20)

        encabezado = tk.Frame(panel, bg=CHROME)
        encabezado.pack(fill="x", pady=(0, 14))

        tk.Label(encabezado, text="Accesos rápidos", font=("Segoe UI", 15, "bold"),
                 fg=INK, bg=CHROME).pack(side="left")
        tk.Label(encabezado, text="Principal › Inicio", font=("Segoe UI", 9),
                 fg=GRAY, bg=CHROME).pack(side="right")

        tiles = tk.Frame(panel, bg=CHROME)
        tiles.pack(fill="both", expand=True)
        for c in range(3):
            tiles.grid_columnconfigure(c, weight=1, uniform="tile")

        claves_normales = ["Vehiculo", "Destino", "Cliente", "Producto", "Conductor"]
        fila = col = 0
        for clave in claves_normales:
            titulo, icono, descripcion, contador = MODULOS[clave]
            self._crear_tile(tiles, clave, titulo, icono, descripcion, contador).grid(
                row=fila, column=col, padx=6, pady=6, sticky="nsew"
            )
            col += 1
            if col == 3:
                col = 0
                fila += 1

        # Tarjeta "Reportes" (informativa, junto a las demás)
        self._crear_tile(tiles, None, "Reportes", "📊", "Resumen de despachos por mes.",
                          "Julio 2026", comando=self._reportes).grid(
            row=fila, column=col, padx=6, pady=6, sticky="nsew"
        )
        col += 1
        if col == 3:
            col = 0
            fila += 1

        # Tarjeta ancha: Pedidos
        titulo, icono, descripcion, contador = MODULOS["Pedido"]
        self._crear_tile(tiles, "Pedido", f"{titulo} — armar nueva planilla", icono,
                          descripcion, contador, ancha=True).grid(
            row=fila + 1, column=0, columnspan=3, padx=6, pady=(10, 6), sticky="nsew"
        )

        # ---- Panel de actividad reciente ----
        actividad = tk.Frame(area, bg=WHITE, width=230, highlightbackground=CHROME_LINE,
                              highlightthickness=1)
        actividad.pack(side="left", fill="y")
        actividad.pack_propagate(False)

        tk.Label(actividad, text="ACTIVIDAD RECIENTE", font=("Segoe UI", 8, "bold"),
                 fg=GRAY, bg=WHITE).pack(anchor="w", padx=16, pady=(18, 10))

        for hora, descripcion in ACTIVIDAD_RECIENTE:
            entrada = tk.Frame(actividad, bg=WHITE)
            entrada.pack(fill="x", padx=16, pady=6)
            tk.Label(entrada, text=hora, font=("Consolas", 8), fg=GRAY, bg=WHITE).pack(anchor="w")
            tk.Label(entrada, text=descripcion, font=("Segoe UI", 9), fg=INK, bg=WHITE,
                     wraplength=190, justify="left").pack(anchor="w")
            linea_separadora(entrada, pady=(8, 0))

    def _crear_tile(self, parent, clave, titulo, icono, descripcion, contador,
                     ancha=False, comando=None):
        oscura = ancha
        fondo = NAVY_DEEP if oscura else WHITE
        fg_titulo = WHITE if oscura else INK
        fg_desc = "#9FADD6" if oscura else GRAY
        fg_contador = "#E8C77B" if oscura else NAVY

        tile = tk.Frame(parent, bg=fondo, highlightbackground=CHROME_LINE,
                         highlightthickness=0 if oscura else 1, cursor="hand2")

        contenedor = tk.Frame(tile, bg=fondo)
        contenedor.pack(fill="both", expand=True, padx=16, pady=14)

        icono_bg = "#12245C" if oscura else CHROME
        tk.Label(contenedor, text=icono, font=("Segoe UI", 16), bg=icono_bg,
                 width=2, height=1).grid(row=0, column=0, rowspan=3, sticky="n", padx=(0, 12))

        tk.Label(contenedor, text=titulo, font=("Segoe UI", 11, "bold"), fg=fg_titulo,
                 bg=fondo, anchor="w", justify="left").grid(row=0, column=1, sticky="w")
        tk.Label(contenedor, text=descripcion, font=("Segoe UI", 9), fg=fg_desc, bg=fondo,
                 anchor="w", justify="left", wraplength=260 if ancha else 150).grid(
            row=1, column=1, sticky="w", pady=(2, 4)
        )
        tk.Label(contenedor, text=contador, font=("Segoe UI", 9, "bold"), fg=fg_contador,
                 bg=fondo, anchor="w").grid(row=2, column=1, sticky="w")

        contenedor.grid_columnconfigure(1, weight=1)

        accion = comando if comando else (lambda c=clave: self._abrir_modulo(c))
        widgets = [tile, contenedor] + contenedor.winfo_children()
        for w in widgets:
            w.bind("<Button-1>", lambda e, a=accion: a())
            if not oscura:
                w.bind("<Enter>", lambda e, t=tile: self._hover_tile(t, True))
                w.bind("<Leave>", lambda e, t=tile: self._hover_tile(t, False))

        return tile

    def _hover_tile(self, tile, entrando):
        color = ACCENT_BG if entrando else WHITE

        def pintar(widget):
            try:
                widget.config(bg=color)
            except tk.TclError:
                pass
            for hijo in widget.winfo_children():
                pintar(hijo)

        pintar(tile)

    # ------------------------------------------------------------------
    # BARRA DE ESTADO
    # ------------------------------------------------------------------
    def _crear_statusbar(self):
        barra = tk.Frame(self, bg=NAVY_DEEP, height=26)
        barra.pack(side="bottom", fill="x")
        barra.pack_propagate(False)

        def segmento(texto, lado="left", led=False):
            contenedor = tk.Frame(barra, bg=NAVY_DEEP)
            contenedor.pack(side=lado, padx=12)
            if led:
                tk.Label(contenedor, text="●", font=("Segoe UI", 7), fg="#3FB950",
                         bg=NAVY_DEEP).pack(side="left", padx=(0, 4))
            tk.Label(contenedor, text=texto, font=("Segoe UI", 8), fg="#B9C2DE",
                     bg=NAVY_DEEP).pack(side="left")

        segmento("macscol.db conectada", led=True)
        segmento("297 registros totales")
        segmento("Usuario: admin")
        segmento(fecha_corta_en_espanol(), lado="right")

    # ------------------------------------------------------------------
    # ACCIONES
    # ------------------------------------------------------------------
    def _abrir_modulo(self, nombre):
        if nombre == "Vehiculo":
            VentanaVehiculo(self)
        elif nombre == "Destino":
            VentanaDestino(self)
        elif nombre == "Cliente":
            VentanaCliente(self)
        elif nombre == "Producto":
            VentanaProducto(self)
        elif nombre == "Conductor":
            VentanaConductor(self)
        elif nombre == "Pedido":
            VentanaAgregarPedido(self)
        else:
            messagebox.showinfo("Módulo", f"Aquí se abriría el módulo: {nombre}")

    def _actualizar(self):
        messagebox.showinfo("Actualizar", "Datos actualizados.")

    def _reportes(self):
        messagebox.showinfo("Reportes", "Aquí se mostrará el resumen de despachos por mes.")

    def _acerca_de(self):
        messagebox.showinfo("Acerca de", "Sistema MACS COL\nInterfaz Principal - 10 años")

    def _salir(self):
        if messagebox.askyesno("Salir", "¿Desea salir del programa?"):
            self.destroy()


if __name__ == "__main__":
    crear_base_datos()
    app = InterfazPrincipal()
    app.mainloop()
