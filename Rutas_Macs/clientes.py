"""
================================================================================
 CLIENTES - MACS COL
================================================================================

Este módulo gestiona los clientes de MACS COL.

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


# ==============================================================================
# COLORES Y FUENTES
# ==============================================================================

COLOR_FONDO = "#DFFFF7"
COLOR_BOTON = "#0B1F6B"

FUENTE_BOTON = ("Segoe UI", 11, "bold")
FUENTE_TITULO = ("Segoe UI", 20, "bold")
FUENTE_ETIQUETA = ("Segoe UI", 11)


# ==============================================================================
# VENTANA CLIENTES
# ==============================================================================

class VentanaCliente(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        # ----------------------------------------------------------------------
        # CONFIGURACIÓN DE LA VENTANA
        # ----------------------------------------------------------------------

        self.title("Clientes")
        self.geometry("700x550")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------------------------

        tk.Label(
            self,
            text="Clientes",
            bg=COLOR_FONDO,
            font=FUENTE_TITULO
        ).pack(pady=(25, 20))

        # ----------------------------------------------------------------------
        # TABLA DE CLIENTES
        # ----------------------------------------------------------------------

        frame_tabla = tk.Frame(
            self,
            bg=COLOR_FONDO
        )

        frame_tabla.pack(
            padx=30,
            pady=10,
            fill="both",
            expand=True
        )

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(
            frame_tabla,
            orient="vertical"
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Treeview
        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=("id", "nombre"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )

        self.tabla.heading(
            "id",
            text="ID"
        )

        self.tabla.heading(
            "nombre",
            text="Nombre"
        )

        self.tabla.column(
            "id",
            width=100,
            anchor="center"
        )

        self.tabla.column(
            "nombre",
            width=450,
            anchor="center"
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.tabla.yview
        )

        # ----------------------------------------------------------------------
        # BOTONES
        # ----------------------------------------------------------------------

        botones = tk.Frame(
            self,
            bg=COLOR_FONDO
        )

        botones.pack(
            pady=25
        )

        # Botón Agregar
        tk.Button(
            botones,
            text="Agregar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.abrir_ventana_agregar
        ).grid(
            row=0,
            column=0,
            padx=15
        )


        # Botón Eliminar
        tk.Button(
            botones,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.eliminar
        ).grid(
            row=0,
            column=1,
            padx=15
        )

        # Botón Actualizar
        tk.Button(
            botones,
            text="Actualizar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.actualizar
        ).grid(
            row=0,
            column=2,
            padx=15
        )

        # ----------------------------------------------------------------------
        # CARGAR CLIENTES DESDE LA BASE DE DATOS
        # ----------------------------------------------------------------------

        self.cargar_clientes()

    # ==========================================================================
    # CARGAR CLIENTES
    # ==========================================================================

    def cargar_clientes(self):
        """
        Carga todos los clientes almacenados en SQLite
        y los muestra en el Treeview.
        """

        # ----------------------------------------------------------------------
        # LIMPIAR LA TABLA ACTUAL
        # ----------------------------------------------------------------------

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:

            # ------------------------------------------------------------------
            # CONECTAR CON LA BASE DE DATOS
            # ------------------------------------------------------------------

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # ------------------------------------------------------------------
            # CONSULTAR CLIENTES
            # ------------------------------------------------------------------

            cursor.execute("""
                SELECT id, nombre
                FROM clientes
                ORDER BY id
            """)

            clientes = cursor.fetchall()

            # ------------------------------------------------------------------
            # CERRAR CONEXIÓN
            # ------------------------------------------------------------------

            conexion.close()

            # ------------------------------------------------------------------
            # MOSTRAR CLIENTES EN EL TREEVIEW
            # ------------------------------------------------------------------

            for cliente in clientes:

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cliente[0],
                        cliente[1]
                    )
                )

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
        ventana.geometry("350x220")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Nombre:",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(25, 5)
        )

        entrada_nombre = tk.Entry(
            ventana,
            width=30
        )

        entrada_nombre.pack(
            padx=20,
            pady=5
        )

        entrada_nombre.focus()

        # ----------------------------------------------------------------------
        # BOTÓN GUARDAR
        # ----------------------------------------------------------------------

        tk.Button(
            ventana,
            text="Guardar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=lambda: self.guardar_cliente(
                entrada_nombre,
                ventana
            )
        ).pack(
            pady=25
        )

        # ----------------------------------------------------------------------
        # ENTER PARA GUARDAR
        # ----------------------------------------------------------------------

        ventana.bind(
            "<Return>",
            lambda event: self.guardar_cliente(
                entrada_nombre,
                ventana
            )
        )

    # ==========================================================================
    # GUARDAR CLIENTE
    # ==========================================================================

    def guardar_cliente(
        self,
        entrada_nombre,
        ventana
    ):
        """
        Guarda un nuevo cliente en la base de datos SQLite.
        """

        # ----------------------------------------------------------------------
        # OBTENER DATOS DEL FORMULARIO
        # ----------------------------------------------------------------------

        nombre = entrada_nombre.get().strip()

        # ----------------------------------------------------------------------
        # VALIDAR DATOS
        # ----------------------------------------------------------------------

        if not nombre:

            messagebox.showwarning(
                "Cliente",
                "Debes escribir el nombre del cliente."
            )

            return

        try:

            # ------------------------------------------------------------------
            # CONECTAR CON LA BASE DE DATOS
            # ------------------------------------------------------------------

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # ------------------------------------------------------------------
            # INSERTAR CLIENTE
            # ------------------------------------------------------------------
            #
            # No enviamos el ID.
            #
            # SQLite genera automáticamente el ID gracias a:
            #
            # id INTEGER PRIMARY KEY AUTOINCREMENT
            # ------------------------------------------------------------------

            cursor.execute(
                """
                INSERT INTO clientes (nombre)
                VALUES (?)
                """,
                (nombre,)
            )

            # ------------------------------------------------------------------
            # GUARDAR CAMBIOS
            # ------------------------------------------------------------------

            conexion.commit()

            # ------------------------------------------------------------------
            # CERRAR CONEXIÓN
            # ------------------------------------------------------------------

            conexion.close()

            # ------------------------------------------------------------------
            # ACTUALIZAR TABLA
            # ------------------------------------------------------------------

            self.cargar_clientes()

            # ------------------------------------------------------------------
            # CERRAR VENTANA DE AGREGAR
            # ------------------------------------------------------------------

            ventana.destroy()

            # ------------------------------------------------------------------
            # MENSAJE DE CONFIRMACIÓN
            # ------------------------------------------------------------------

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

        # ----------------------------------------------------------------------
        # COMPROBAR SI HAY UNA FILA SELECCIONADA
        # ----------------------------------------------------------------------

        seleccion = self.tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Cliente",
                "Selecciona un cliente para eliminar."
            )

            return

        # ----------------------------------------------------------------------
        # OBTENER LA FILA SELECCIONADA
        # ----------------------------------------------------------------------

        fila = seleccion[0]

        valores = self.tabla.item(
            fila,
            "values"
        )

        if not valores:

            return

        # ----------------------------------------------------------------------
        # OBTENER ID DEL CLIENTE
        # ----------------------------------------------------------------------

        id_cliente = valores[0]

        nombre_cliente = valores[1]

        # ----------------------------------------------------------------------
        # CONFIRMAR ELIMINACIÓN
        # ----------------------------------------------------------------------

        confirmar = messagebox.askyesno(
            "Eliminar cliente",
            f"¿Seguro que deseas eliminar al cliente:\n\n"
            f"{nombre_cliente}?"
        )

        if not confirmar:

            return

        try:

            # ------------------------------------------------------------------
            # CONECTAR CON LA BASE DE DATOS
            # ------------------------------------------------------------------

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # ------------------------------------------------------------------
            # ELIMINAR CLIENTE
            # ------------------------------------------------------------------

            cursor.execute(
                """
                DELETE FROM clientes
                WHERE id = ?
                """,
                (id_cliente,)
            )

            # ------------------------------------------------------------------
            # GUARDAR CAMBIOS
            # ------------------------------------------------------------------

            conexion.commit()

            # ------------------------------------------------------------------
            # CERRAR CONEXIÓN
            # ------------------------------------------------------------------

            conexion.close()

            # ------------------------------------------------------------------
            # ACTUALIZAR TABLA
            # ------------------------------------------------------------------

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

    # Aseguramos que la ventana principal esté disponible
    # para crear el Toplevel.

    VentanaCliente(root)

    root.mainloop()