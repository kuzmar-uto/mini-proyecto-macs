

import os
import tkinter as tk
from tkinter import messagebox

from estilo import (
    fecha_corta_en_espanol, linea_separadora,
    ajustar_geometria_ventana,
)

from producto import VentanaProducto
from conductor import VentanaConductor
from destino import VentanaDestino
from vehiculo import VentanaVehiculo
from clientes import VentanaCliente
from pedido import VentanaAgregarPedido
from almacenamiento import crear_base_datos

RUTA_LOGO = os.path.join(os.path.dirname(__file__), "logo_macscol.png")



FONDO = "#F3F5FA"          
SUPERFICIE = "#FFFFFF"     
LINEA = "#E2E7F1"          
TINTA = "#16203A"          
APAGADO = "#6B7794"        
MARCA = "#2F5BEA"          
MARCA_OSCURO = "#2449C4"   
MARCA_SUAVE = "#E8EEFF"    
HOVER_SUAVE = "#F7F9FF"    
DORADO = "#E8C77B"

NAV_FONDO = "#0E1B40"      
NAV_HOVER = "#16285F"
NAV_ACTIVO = "#1F3578"
NAV_TEXTO = "#C5CEE8"
NAV_TENUE = "#7F8DB8"

ESTADO_FONDO = "#0A1330"
ESTADO_TEXTO = "#B9C2DE"

FUENTE = "Segoe UI"
FUENTE_ICONO = "Segoe UI Emoji"


COLOR_ICONO = {
    "Vehiculo":  "#E8EEFF",
    "Destino":   "#FDEBEB",
    "Cliente":   "#E5F6EC",
    "Producto":  "#FFF3D6",
    "Conductor": "#F0E8FF",
    "Reportes":  "#E1F4F8",
    "Pedido":    "#1F3578",
}


MODULOS = {
    "Vehiculo":  ("Vehículos",   "🚚", "Placa y capacidad de la flota.",              ""),
    "Destino":   ("Destinos",    "📍", "Ciudades y puntos de entrega.",               ""),
    "Cliente":   ("Clientes",    "👤", "Nombre e identificación.",                    ""),
    "Producto":  ("Productos",   "📦", "Embalaje, peso y descripción.",               ""),
    "Conductor": ("Conductores", "🧑", "Cédula, nombre y teléfono.",                  ""),
    "Pedido":    ("Pedidos",     "📋", "Selecciona cliente, productos, vehículo y ruta para despachar.", ""),
}

ACTIVIDAD_RECIENTE = []


class InterfazPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---------------- Ventana principal ----------------
        self.title("Principal — MACS COL")
        # Inicia dentro del área visible incluso en pantallas pequeñas.
        ajustar_geometria_ventana(self, 1150, 700, 640, 450)
        self.configure(bg=FONDO)

        self.items_nav = {}
        self.item_activo = "Inicio"
        self._widgets_tile = {}

        self._crear_menu()
        self._crear_toolbar()

        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.pack(side="top", fill="both", expand=True)

        self._crear_nav(cuerpo)
        self._crear_area_principal(cuerpo)

        self._crear_statusbar()
        self.bind("<Configure>", self._adaptar_distribucion)

    # ------------------------------------------------------------------
    # Menú superior
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
    # Barra de herramientas
    # ------------------------------------------------------------------
    def _crear_toolbar(self):
        toolbar = tk.Frame(self, bg=SUPERFICIE, height=60)
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)

        contenido = tk.Frame(toolbar, bg=SUPERFICIE)
        contenido.pack(side="left", fill="y", padx=14)

        self._boton_toolbar(contenido, "＋  Nuevo pedido", lambda: self._abrir_modulo("Pedido"),
                             destacado=True).pack(side="left", padx=(0, 14), pady=11)

        tk.Frame(contenido, bg=LINEA, width=1).pack(side="left", fill="y", pady=14, padx=6)

        self._boton_toolbar(contenido, "↻  Actualizar", self._actualizar).pack(side="left", padx=3, pady=11)
        self._boton_toolbar(contenido, "📄  Planillas", lambda: self._abrir_modulo("Pedido")).pack(side="left", padx=3, pady=11)
        self._boton_toolbar(contenido, "📊  Reportes", self._reportes).pack(side="left", padx=3, pady=11)

        # ---- Buscador a la derecha ----
        buscador = tk.Frame(toolbar, bg=FONDO, highlightbackground=LINEA,
                             highlightcolor=MARCA, highlightthickness=1)
        self._buscador_toolbar = buscador
        buscador.pack(side="right", padx=18, pady=13)

        tk.Label(buscador, text="🔍", bg=FONDO, fg=APAGADO,
                 font=(FUENTE_ICONO, 10)).pack(side="left", padx=(10, 2))
        entrada_busqueda = tk.Entry(buscador, bg=FONDO, fg=APAGADO, relief="flat",
                                     width=28, insertbackground=TINTA,
                                     font=(FUENTE, 10))
        entrada_busqueda.insert(0, "Buscar cliente, placa...")
        entrada_busqueda.bind("<FocusIn>", lambda e: self._limpiar_placeholder(entrada_busqueda))
        entrada_busqueda.pack(side="left", ipady=5, padx=(0, 10))

        tk.Frame(self, bg=LINEA, height=1).pack(side="top", fill="x")

    def _boton_toolbar(self, parent, texto, comando, destacado=False):
        fondo = MARCA if destacado else SUPERFICIE
        fondo_hover = MARCA_OSCURO if destacado else "#EEF2FB"
        boton = tk.Label(
            parent,
            text=texto,
            font=(FUENTE, 10, "bold" if destacado else "normal"),
            bg=fondo,
            fg=SUPERFICIE if destacado else TINTA,
            padx=14,
            pady=7,
            cursor="hand2",
        )
        boton.bind("<Button-1>", lambda e: comando())
        boton.bind("<Enter>", lambda e: boton.config(bg=fondo_hover))
        boton.bind("<Leave>", lambda e: boton.config(bg=fondo))
        return boton

    def _limpiar_placeholder(self, entrada):
        if entrada.get() == "Buscar cliente, placa...":
            entrada.delete(0, "end")
            entrada.config(fg=TINTA)

    # ------------------------------------------------------------------
    # Navegación lateral
    # ------------------------------------------------------------------
    def _crear_nav(self, parent):
        nav = tk.Frame(parent, bg=NAV_FONDO, width=220)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        # ---- Marca ----
        marca = tk.Frame(nav, bg=NAV_FONDO)
        marca.pack(fill="x", padx=18, pady=(18, 10))
        tk.Label(marca, text="MACS COL", font=(FUENTE, 15, "bold"),
                 fg=SUPERFICIE, bg=NAV_FONDO).pack(anchor="w")
        tk.Label(marca, text="Sistema de despachos", font=(FUENTE, 8),
                 fg=NAV_TENUE, bg=NAV_FONDO).pack(anchor="w")
        tk.Frame(nav, bg=NAV_HOVER, height=1).pack(fill="x", padx=14, pady=(8, 0))

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
            font=(FUENTE, 8, "bold"),
            fg=NAV_TENUE,
            bg=NAV_FONDO,
        ).pack(anchor="w", padx=18, pady=(16, 4))

    def _fila_nav(self, parent, clave, icono, texto, contador):
        fila = tk.Frame(parent, bg=NAV_FONDO, cursor="hand2")
        fila.pack(fill="x", padx=8, pady=1)

        barra_activa = tk.Frame(fila, bg=NAV_FONDO, width=3)
        barra_activa.pack(side="left", fill="y", pady=4)

        contenido = tk.Frame(fila, bg=NAV_FONDO, cursor="hand2")
        contenido.pack(side="left", fill="x", expand=True, padx=(8, 10), pady=6)

        textos = []
        textos.append(tk.Label(contenido, text=icono, bg=NAV_FONDO, fg=NAV_TEXTO,
                                font=(FUENTE_ICONO, 11)))
        textos[-1].pack(side="left")

        textos.append(tk.Label(contenido, text=texto, bg=NAV_FONDO, fg=NAV_TEXTO,
                                font=(FUENTE, 10)))
        textos[-1].pack(side="left", padx=(10, 0))

        contadores = []
        if contador:
            etiqueta_contador = tk.Label(contenido, text=contador.split()[0], bg=NAV_FONDO,
                                          fg=NAV_TENUE, font=(FUENTE, 8))
            etiqueta_contador.pack(side="right")
            contadores.append(etiqueta_contador)

        widgets = [fila, contenido] + textos + contadores

        def al_hacer_clic(event=None, clave=clave):
            self.item_activo = clave
            self._resaltar_item_activo()
            if clave != "Inicio":
                self._abrir_modulo(clave)

        for w in widgets:
            w.bind("<Button-1>", al_hacer_clic)
            w.bind("<Enter>", lambda e, c=clave: self._pintar_item(c, hover=True))
            w.bind("<Leave>", lambda e, c=clave: self._pintar_item(c, hover=False))

        self.items_nav[clave] = {
            "barra": barra_activa,
            "fondo": [fila, contenido] + textos + contadores,
            "textos": textos,
            "contadores": contadores,
        }

    def _pintar_item(self, clave, hover=False):
        partes = self.items_nav[clave]
        activo = clave == self.item_activo
        color_fondo = NAV_ACTIVO if activo else (NAV_HOVER if hover else NAV_FONDO)
        partes["barra"].config(bg=MARCA_SUAVE if activo else color_fondo)
        for w in partes["fondo"]:
            w.config(bg=color_fondo)
        for w in partes["textos"]:
            w.config(fg=SUPERFICIE if activo else NAV_TEXTO)
        for w in partes["contadores"]:
            w.config(fg=DORADO if activo else NAV_TENUE)

    def _resaltar_item_activo(self):
        for clave in self.items_nav:
            self._pintar_item(clave)

    # ------------------------------------------------------------------
    # Área principal: tarjetas + actividad reciente
    # ------------------------------------------------------------------
    def _crear_area_principal(self, parent):
        area = tk.Frame(parent, bg=FONDO)
        area.pack(side="left", fill="both", expand=True)

        panel = tk.Frame(area, bg=FONDO)
        panel.pack(side="left", fill="both", expand=True, padx=26, pady=22)

        encabezado = tk.Frame(panel, bg=FONDO)
        encabezado.pack(fill="x", pady=(0, 16))

        titulos = tk.Frame(encabezado, bg=FONDO)
        titulos.pack(side="left")
        tk.Label(titulos, text="Accesos rápidos", font=(FUENTE, 20, "bold"),
                 fg=TINTA, bg=FONDO).pack(anchor="w")
        tk.Label(titulos, text="Elige un módulo para empezar a trabajar.",
                 font=(FUENTE, 10), fg=APAGADO, bg=FONDO).pack(anchor="w")

        tk.Label(encabezado, text="Principal › Inicio", font=(FUENTE, 9),
                 fg=MARCA, bg=MARCA_SUAVE, padx=10, pady=4).pack(side="right", anchor="n")

        tiles = tk.Frame(panel, bg=FONDO)
        tiles.pack(fill="both", expand=True)
        for c in range(3):
            tiles.grid_columnconfigure(c, weight=1, uniform="tile")

        claves_normales = ["Vehiculo", "Destino", "Cliente", "Producto", "Conductor"]
        fila = col = 0
        for clave in claves_normales:
            titulo, icono, descripcion, contador = MODULOS[clave]
            self._crear_tile(tiles, clave, titulo, icono, descripcion, contador).grid(
                row=fila, column=col, padx=7, pady=7, sticky="nsew"
            )
            col += 1
            if col == 3:
                col = 0
                fila += 1

        # Tarjeta "Reportes" (informativa, junto a las demás)
        self._crear_tile(tiles, None, "Reportes", "📊", "Resumen de despachos por mes.",
                          "Septiembre 2026", comando=self._reportes).grid(
            row=fila, column=col, padx=7, pady=7, sticky="nsew"
        )
        col += 1
        if col == 3:
            col = 0
            fila += 1

        # Tarjeta ancha: Pedidos
        titulo, icono, descripcion, contador = MODULOS["Pedido"]
        self._crear_tile(tiles, "Pedido", f"{titulo} — armar nueva planilla", icono,
                          descripcion, contador, ancha=True).grid(
            row=fila + 1, column=0, columnspan=3, padx=7, pady=(12, 7), sticky="nsew"
        )

        # ---- Panel de actividad reciente ----
        actividad = tk.Frame(area, bg=SUPERFICIE, width=240, highlightbackground=LINEA,
                              highlightthickness=1)
        actividad.pack(side="left", fill="y")
        actividad.pack_propagate(False)

        tk.Label(actividad, text="Actividad reciente", font=(FUENTE, 11, "bold"),
                 fg=TINTA, bg=SUPERFICIE).pack(anchor="w", padx=18, pady=(20, 2))
        tk.Label(actividad, text="Lo último que pasó en el sistema",
                 font=(FUENTE, 8), fg=APAGADO, bg=SUPERFICIE).pack(anchor="w", padx=18, pady=(0, 10))
        tk.Frame(actividad, bg=LINEA, height=1).pack(fill="x", padx=18)

        if not ACTIVIDAD_RECIENTE:
            tk.Label(actividad, text="🕑", font=(FUENTE_ICONO, 20), fg=LINEA,
                     bg=SUPERFICIE).pack(pady=(40, 4))
            tk.Label(actividad, text="Sin actividad reciente", font=(FUENTE, 9),
                     fg=APAGADO, bg=SUPERFICIE).pack()

        for hora, descripcion in ACTIVIDAD_RECIENTE:
            entrada = tk.Frame(actividad, bg=SUPERFICIE)
            entrada.pack(fill="x", padx=18, pady=7)
            tk.Label(entrada, text=hora, font=("Consolas", 8), fg=MARCA, bg=SUPERFICIE).pack(anchor="w")
            tk.Label(entrada, text=descripcion, font=(FUENTE, 9), fg=TINTA, bg=SUPERFICIE,
                     wraplength=196, justify="left").pack(anchor="w")
            linea_separadora(entrada, pady=(8, 0))

        self._tiles = tiles
        self._area = area
        self._actividad = actividad
        self._panel_principal = panel
        self._tarjetas = []

        for hijo in tiles.winfo_children():
            if isinstance(hijo, tk.Frame):
                self._tarjetas.append(hijo)

    def _adaptar_distribucion(self, event=None):
        """Reorganiza la página para que siga siendo usable al reducir la ventana."""
        if event is not None and event.widget is not self:
            return
        if not hasattr(self, "_tiles"):
            return
        ancho = self.winfo_width()
        compacto = ancho < 900
        if compacto and self._buscador_toolbar.winfo_manager():
            self._buscador_toolbar.pack_forget()
        elif not compacto and not self._buscador_toolbar.winfo_manager():
            self._buscador_toolbar.pack(side="right", padx=18, pady=13)
        if compacto:
            self._actividad.pack_forget()
            self._panel_principal.pack_configure(padx=12, pady=12)
        else:
            self._actividad.pack(side="left", fill="y")
            self._panel_principal.pack_configure(padx=26, pady=22)

        columnas = 1 if ancho < 760 else (2 if ancho < 1100 else 3)
        for c in range(3):
            self._tiles.grid_columnconfigure(c, weight=1 if c < columnas else 0,
                                              uniform="tile" if c < columnas else "")
        normales = self._tarjetas[:6]
        for i, tile in enumerate(normales):
            tile.grid_forget()
            tile.grid(row=i // columnas, column=i % columnas, padx=6, pady=6, sticky="nsew")
        pedido = self._tarjetas[6]
        pedido.grid_forget()
        pedido.grid(row=(len(normales) + columnas - 1) // columnas,
                    column=0, columnspan=columnas, padx=6, pady=(10, 6), sticky="nsew")
        filas = (len(normales) + columnas - 1) // columnas + 1
        for fila in range(5):
            self._tiles.grid_rowconfigure(fila, weight=1 if fila < filas else 0, uniform="")

    @staticmethod
    def _descendientes(widget):
        """Devuelve el widget y todos sus hijos (recursivo)."""
        lista = [widget]
        for hijo in widget.winfo_children():
            lista.extend(InterfazPrincipal._descendientes(hijo))
        return lista

    def _crear_tile(self, parent, clave, titulo, icono, descripcion, contador,
                     ancha=False, comando=None):
        oscura = ancha
        fondo = NAV_FONDO if oscura else SUPERFICIE
        fg_titulo = SUPERFICIE if oscura else TINTA
        fg_desc = "#9FADD6" if oscura else APAGADO
        fg_contador = DORADO if oscura else MARCA
        clave_color = clave if clave else "Reportes"
        color_icono = COLOR_ICONO.get(clave_color, MARCA_SUAVE)

        tile = tk.Frame(parent, bg=fondo, highlightbackground=NAV_FONDO if oscura else LINEA,
                         highlightthickness=1, cursor="hand2")

        contenedor = tk.Frame(tile, bg=fondo)
        contenedor.pack(fill="both", expand=True, padx=18, pady=16)

        # Círculo/cuadro de icono
        chip = tk.Label(contenedor, text=icono, font=(FUENTE_ICONO, 18), bg=color_icono,
                        width=3, height=1)
        chip.grid(row=0, column=0, rowspan=3, sticky="n", padx=(0, 14))

        tk.Label(contenedor, text=titulo, font=(FUENTE, 12, "bold"), fg=fg_titulo,
                 bg=fondo, anchor="w", justify="left").grid(row=0, column=1, sticky="w")
        tk.Label(contenedor, text=descripcion, font=(FUENTE, 9), fg=fg_desc, bg=fondo,
                 anchor="w", justify="left", wraplength=360 if ancha else 150).grid(
            row=1, column=1, sticky="w", pady=(3, 6)
        )

        pie = tk.Frame(contenedor, bg=fondo)
        pie.grid(row=2, column=1, sticky="we")
        if contador:
            tk.Label(pie, text=contador, font=(FUENTE, 9, "bold"), fg=fg_contador,
                     bg=fondo, anchor="w").pack(side="left")
        if ancha:
            tk.Label(pie, text="Nueva planilla  →", font=(FUENTE, 9, "bold"),
                     fg=NAV_FONDO, bg=DORADO, padx=12, pady=4).pack(side="right")
        else:
            tk.Label(pie, text="Abrir  →", font=(FUENTE, 9), fg=MARCA,
                     bg=fondo).pack(side="right")

        contenedor.grid_columnconfigure(1, weight=1)

        accion = comando if comando else (lambda c=clave: self._abrir_modulo(c))
        widgets = self._descendientes(tile)
        # Widgets que cambian de color al pasar el mouse (se excluyen iconos y botón dorado)
        self._widgets_tile[tile] = [
            w for w in widgets
            if w is not chip and str(w.cget("bg")).lower() == fondo.lower()
        ]
        for w in widgets:
            w.bind("<Button-1>", lambda e, a=accion: a())
            if not oscura:
                w.bind("<Enter>", lambda e, t=tile: self._hover_tile(t, True))
                w.bind("<Leave>", lambda e, t=tile: self._hover_tile(t, False))

        return tile

    def _hover_tile(self, tile, entrando):
        color = HOVER_SUAVE if entrando else SUPERFICIE
        tile.config(highlightbackground=MARCA if entrando else LINEA)
        for w in self._widgets_tile.get(tile, []):
            try:
                w.config(bg=color)
            except tk.TclError:
                pass

    # ------------------------------------------------------------------
    # Barra de estado
    # ------------------------------------------------------------------
    def _crear_statusbar(self):
        barra = tk.Frame(self, bg=ESTADO_FONDO, height=28)
        barra.pack(side="bottom", fill="x")
        barra.pack_propagate(False)

        def segmento(texto, lado="left", led=False):
            contenedor = tk.Frame(barra, bg=ESTADO_FONDO)
            contenedor.pack(side=lado, padx=14)
            if led:
                tk.Label(contenedor, text="●", font=(FUENTE, 7), fg="#3FB950",
                         bg=ESTADO_FONDO).pack(side="left", padx=(0, 5))
            tk.Label(contenedor, text=texto, font=(FUENTE, 8), fg=ESTADO_TEXTO,
                     bg=ESTADO_FONDO).pack(side="left")

        segmento("macscol.db conectada", led=True)
        segmento("297 registros totales")
        segmento("Usuario: admin")
        segmento(fecha_corta_en_espanol(), lado="right")

    # ------------------------------------------------------------------
    # Funciones del sistema (sin cambios)
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

    # ------------------------------------------------------------------
    # funciones que tocas hacer funcionar en el futuro
    # ------------------------------------------------------------------
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
