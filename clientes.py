"""
================================================================================
 CLIENTES - MACS COL
================================================================================

Este módulo gestiona los clientes de MACS COL, con el mismo diseño "software
de escritorio" (mockup: macscol_app_menu_escritorio.html) que usan Principal
y las demás ventanas de la aplicación. Los colores, fuentes y helpers viven
en estilo.py.

Los datos se almacenan de forma permanente en SQLite mediante:
    almacenamiento.py

La información se guarda en:
    datos/macscol.db

Funciones principales:
    - Cargar clientes desde la base de datos.
    - Agregar nuevos clientes.
    - Eliminar clientes.
    - Actualizar/refrescar la tabla.
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox

from almacenamiento import obtener_conexion
from estilo import (
    CHROME, CHROME_LINE, NAVY, NAVY_DEEP, ACCENT, ACCENT_BG, INK, GRAY, WHITE,
    FUENTE_SUBTITULO, FUENTE_ETIQUETA, FUENTE_TEXTO,
    boton_primario, boton_secundario, configurar_estilo_treeview,
    barra_titulo_ventana, linea_separadora,
)


# ==============================================================================
# VENTANA CLIENTES
# ==============================================================================

class VentanaCliente(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Clientes")
        self.geometry("760x560")
        self.resizable(False, False)
        self.configure(bg=CHROME)

        self.crear_componentes()
        self.cargar_clientes()

    # ==========================================================================
    # CREAR COMPONENTES
    # ==========================================================================

    def crear_componentes(self):
        barra_titulo_ventana(self, "Clientes")

        cuerpo = tk.Frame(self, bg=CHROME)
        cuerpo.pack(fill="both", expand=True, padx=24, pady=18)

        encabezado = tk.Frame(cuerpo, bg=CHROME)
        encabezado.pack(fill="x", pady=(0, 12))
        tk.Label(encabezado, text="Clientes registrados", font=FUENTE_SUBTITULO,
                 fg=INK, bg=CHROME).pack(side="left")
        tk.Label(encabezado, text="Principal › Clientes", font=("Segoe UI", 9),
                 fg=GRAY, bg=CHROME).pack(side="right")

        # ---- Tarjeta con la tabla ----
        tarjeta = tk.Frame(cuerpo, bg=WHITE, highlightbackground=CHROME_LINE,
                            highlightthickness=1)
        tarjeta.pack(fill="both", expand=True)

        frame_tabla = tk.Frame(tarjeta, bg=WHITE)
        frame_tabla.pack(fill="both", expand=True, padx=12, pady=12)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        estilo_tabla = configurar_estilo_treeview("Clientes.Treeview")
        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=("id", "nombre"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15,
            style=estilo_tabla,
        )
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.column("id", width=100, anchor="center")
        self.tabla.column("nombre", width=450, anchor="center")
        self.tabla.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.tabla.yview)

        # ---- Barra de acciones ----
        botones = tk.Frame(cuerpo, bg=CHROME)
        botones.pack(fill="x", pady=(14, 0))

        boton_primario(botones, "➕  Agregar", self.abrir_ventana_agregar, ancho=14).pack(
            side="left", padx=(0, 10)
        )
        boton_secundario(botones, "🗑  Eliminar", self.eliminar, ancho=14).pack(
            side="left", padx=(0, 10)
        )
        boton_secundario(botones, "🔄  Actualizar", self.actualizar, ancho=14).pack(
            side="left"
        )

    # ==========================================================================
    # CARGAR CLIENTES
    # ==========================================================================

    def cargar_clientes(self):
        """
        Carga todos los clientes almacenados en SQLite
        y los muestra en el Treeview.
        """
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id, nombre
                FROM clientes
                ORDER BY id
            """)

            clientes = cursor.fetchall()
            conexion.close()

            for cliente in clientes:
                self.tabla.insert("", "end", values=(cliente[0], cliente[1]))

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los clientes:\n\n{e}"
            )

    # ==========================================================================
    # ABRIR VENTANA AGREGAR
    # ==========================================================================

    def abrir_ventana_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar cliente")
        ventana.geometry("360x230")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Agregar cliente")

        contenido = tk.Frame(ventana, bg=CHROME)
        contenido.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(contenido, text="Nombre:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(4, 4))

        entrada_nombre = tk.Entry(contenido, width=28, font=FUENTE_TEXTO, relief="solid",
                                   highlightbackground=CHROME_LINE, bd=1)
        entrada_nombre.pack(fill="x", ipady=4)
        entrada_nombre.focus()

        boton_primario(
            contenido, "Guardar",
            lambda: self.guardar_cliente(entrada_nombre, ventana),
            ancho=16,
        ).pack(pady=(22, 0))

        ventana.bind(
            "<Return>",
            lambda event: self.guardar_cliente(entrada_nombre, ventana)
        )

    # ==========================================================================
    # GUARDAR CLIENTE
    # ==========================================================================

    def guardar_cliente(self, entrada_nombre, ventana):
        """
        Guarda un nuevo cliente en la base de datos SQLite.
        """
        nombre = entrada_nombre.get().strip()

        if not nombre:
            messagebox.showwarning(
                "Cliente",
                "Debes escribir el nombre del cliente."
            )
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # No enviamos el ID: SQLite lo genera automáticamente gracias a
            # "id INTEGER PRIMARY KEY AUTOINCREMENT".
            cursor.execute(
                "INSERT INTO clientes (nombre) VALUES (?)",
                (nombre,)
            )

            conexion.commit()
            conexion.close()

            self.cargar_clientes()
            ventana.destroy()

            messagebox.showinfo(
                "Cliente",
                "Cliente guardado correctamente."
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo guardar el cliente:\n\n{e}"
            )

    # ==========================================================================
    # ELIMINAR CLIENTE
    # ==========================================================================

    def eliminar(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Cliente",
                "Selecciona un cliente para eliminar."
            )
            return

        fila = seleccion[0]
        valores = self.tabla.item(fila, "values")

        if not valores:
            return

        id_cliente = valores[0]
        nombre_cliente = valores[1]

        confirmar = messagebox.askyesno(
            "Eliminar cliente",
            f"¿Seguro que deseas eliminar al cliente:\n\n"
            f"{nombre_cliente}?"
        )

        if not confirmar:
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                "DELETE FROM clientes WHERE id = ?",
                (id_cliente,)
            )

            conexion.commit()
            conexion.close()

            self.cargar_clientes()

            messagebox.showinfo(
                "Cliente",
                "Cliente eliminado correctamente."
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo eliminar el cliente:\n\n{e}"
            )

    # ==========================================================================
    # ACTUALIZAR
    # ==========================================================================

    def actualizar(self):
        """
        Vuelve a consultar la base de datos y actualiza el Treeview.
        """
        self.cargar_clientes()

        messagebox.showinfo(
            "Cliente",
            "Datos actualizados."
        )


# ==============================================================================
# EJECUCIÓN DIRECTA
# ==============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    VentanaCliente(root)

    root.mainloop()