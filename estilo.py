"""
================================================================================
 ESTILOS
================================================================================

"""

import tkinter as tk
from tkinter import ttk
from datetime import date

# ------------------------------------------------------------------
# PALETA DE COLORES
# ------------------------------------------------------------------
CHROME ="#FFFFFF"     
CHROME_LINE = "#D7D7D3"   
NAVY = "#0B1F6B"          
NAVY_DEEP = "#071540"     
ACCENT = "#3B5FC7"        
ACCENT_BG = "#E8EDFB"     
INK = "#1B1D1F"           
GRAY = "#68696A"         
WHITE = "#FFFFFF"
DORADO = "#C9932B"    


COLOR_FONDO = CHROME
COLOR_BOTON = NAVY
COLOR_TEXTO_BOTON = WHITE

# ------------------------------------------------------------------
# FUENTES
# ------------------------------------------------------------------
FUENTE_TITULO = ("Segoe UI", 20, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 13, "bold")
FUENTE_ETIQUETA = ("Segoe UI", 11, "bold")
FUENTE_BOTON = ("Segoe UI", 11, "bold")
FUENTE_TEXTO = ("Segoe UI", 10)
FUENTE_MONO = ("Consolas", 9)


# ------------------------------------------------------------------
# FECHA
# ------------------------------------------------------------------
DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def fecha_corta_en_espanol():
    """Devuelve algo como 'mar 28 jul 2026', para la barra de estado."""
    hoy = date.today()
    dia = DIAS_ES[hoy.weekday()][:3]
    mes = MESES_ES[hoy.month - 1][:3]
    return f"{dia} {hoy.day} {mes} {hoy.year}"













def boton_primario(parent, texto, comando, ancho=12, font=None):
    """Botón azul marino con texto blanco, como los del mockup."""
    return tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=NAVY,
        fg=WHITE,
        activebackground=ACCENT,
        activeforeground=WHITE,
        font=font or FUENTE_BOTON,
        relief="flat",
        cursor="hand2",
        width=ancho,
    )


def boton_secundario(parent, texto, comando, ancho=12, font=None):
    """Botón claro (fondo ACCENT_BG, texto navy), para acciones menos importantes."""
    return tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=ACCENT_BG,
        fg=NAVY,
        activebackground=CHROME_LINE,
        activeforeground=NAVY,
        font=font or FUENTE_BOTON,
        relief="flat",
        cursor="hand2",
        width=ancho,
    )


def configurar_estilo_treeview(nombre_estilo="Macscol.Treeview"):
    """
    Configura un estilo de ttk.Treeview coherente con el mockup: encabezados
    en azul claro (ACCENT_BG) y filas blancas con líneas suaves. Se llama
    una vez por ventana, antes de crear la tabla, y se pasa su valor de
    retorno como `style=` al Treeview.
    """
    estilo = ttk.Style()
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass

    estilo.configure(
        nombre_estilo,
        background=WHITE,
        fieldbackground=WHITE,
        rowheight=26,
        bordercolor=CHROME_LINE,
        borderwidth=1,
        relief="solid",
        font=FUENTE_TEXTO,
    )
    estilo.configure(
        f"{nombre_estilo}.Heading",
        font=FUENTE_ETIQUETA,
        background=ACCENT_BG,
        foreground=NAVY_DEEP,
        relief="flat",
        borderwidth=1,
    )
    estilo.map(
        nombre_estilo,
        background=[("selected", ACCENT_BG)],
        foreground=[("selected", INK)],
    )
    return nombre_estilo



def ajustar_geometria_ventana(ventana, ancho, alto, min_ancho=320, min_alto=220):
    """Centra la ventana y limita su tama?o al ?rea visible de la pantalla."""
    ventana.update_idletasks()
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    disponible_ancho = max(320, pantalla_ancho - 40)
    disponible_alto = max(240, pantalla_alto - 80)
    ancho = min(ancho, disponible_ancho)
    alto = min(alto, disponible_alto)
    x = max((pantalla_ancho - ancho) // 2, 0)
    y = max((pantalla_alto - alto) // 2, 0)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    ventana.minsize(min(min_ancho, ancho), min(min_alto, alto))


def barra_titulo_ventana(ventana, texto):
    """
    Barra superior azul marino oscuro con el nombre de la sección (como el
    "titlebar" del mockup), para que cada ventana secundaria se sienta
    parte de la misma aplicación que la ventana Principal.
    """
    barra = tk.Frame(ventana, bg=NAVY_DEEP, height=42)
    barra.pack(side="top", fill="x")
    barra.pack_propagate(False)

    tk.Label(
        barra,
        text=texto,
        font=("Segoe UI", 14, "bold"),
        fg=WHITE,
        bg=NAVY_DEEP,
    ).pack(side="left", padx=18)

    tk.Label(
        barra,
        text="MACS COL",
        font=("Segoe UI", 9, "bold"),
        fg=DORADO,
        bg=NAVY_DEEP,
    ).pack(side="right", padx=18)

    return barra


def linea_separadora(parent, **pack_opts):
    """Línea delgada horizontal, color CHROME_LINE, como las del mockup."""
    opts = {"fill": "x"}
    opts.update(pack_opts)
    linea = tk.Frame(parent, bg=CHROME_LINE, height=1)
    linea.pack(**opts)
    return linea