"""
================================================================================
 CONDUCTORES - MACS COL
================================================================================

Este módulo gestiona los conductores de MACS COL.

Los datos se almacenan de forma permanente en SQLite mediante:
    almacenamiento.py

La información se guarda en:
    datos/macscol.db

Funciones principales:
    - Cargar conductores desde la base de datos.
    - Agregar nuevos conductores.
    - Eliminar conductores.
    - Eliminar por cédula.
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
# VENTANA CONDUCTORES
# ==============================================================================

class VentanaConductor(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        # ----------------------------------------------------------------------
        # CONFIGURACIÓN DE LA VENTANA
        # ----------------------------------------------------------------------

        self.title("Conductores")
        self.geometry("800x550")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------------------------

        tk.Label(
            self,
            text="Conductores",
            bg=COLOR_FONDO,
            font=FUENTE_TITULO
        ).pack(
            pady=(25, 20)
        )

        # ----------------------------------------------------------------------
        # FRAME DE LA TABLA
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

        # ----------------------------------------------------------------------
        # SCROLLBAR
        # ----------------------------------------------------------------------

        scrollbar = ttk.Scrollbar(
            frame_tabla,
            orient="vertical"
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # ----------------------------------------------------------------------
        # TREEVIEW
        # ----------------------------------------------------------------------

        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=(
                "cedula",
                "nombre",
                "telefono"
            ),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )

        # Encabezado Cédula
        self.tabla.heading(
            "cedula",
            text="Cédula"
        )

        # Encabezado Nombre
        self.tabla.heading(
            "nombre",
            text="Nombre"
        )

        # Encabezado Teléfono
        self.tabla.heading(
            "telefono",
            text="Teléfono"
        )

        # Ancho columna Cédula
        self.tabla.column(
            "cedula",
            width=180,
            anchor="center"
        )

        # Ancho columna Nombre
        self.tabla.column(
            "nombre",
            width=300,
            anchor="center"
        )

        # Ancho columna Teléfono
        self.tabla.column(
            "telefono",
            width=180,
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

        # ----------------------------------------------------------------------
        # BOTÓN AGREGAR
        # ----------------------------------------------------------------------

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

        # ----------------------------------------------------------------------
        # BOTÓN ELIMINAR
        # ----------------------------------------------------------------------

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

        # ----------------------------------------------------------------------
        # BOTÓN ACTUALIZAR
        # ----------------------------------------------------------------------

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
        # CARGAR DATOS DESDE LA BASE DE DATOS
        # ----------------------------------------------------------------------

        self.cargar_conductores()

    # ==========================================================================
    # CARGAR CONDUCTORES
    # ==========================================================================

    def cargar_conductores(self):
        """
        Carga todos los conductores almacenados en SQLite
        y los muestra en el Treeview.
        """

        # ----------------------------------------------------------------------
        # LIMPIAR TABLA
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
            # CONSULTAR CONDUCTORES
            # ------------------------------------------------------------------

            cursor.execute("""
                SELECT cedula, nombre, telefono
                FROM conductores
                ORDER BY nombre
            """)

            conductores = cursor.fetchall()

            # ------------------------------------------------------------------
            # CERRAR CONEXIÓN
            # ------------------------------------------------------------------

            conexion.close()

            # ------------------------------------------------------------------
            # MOSTRAR CONDUCTORES EN LA TABLA
            # ------------------------------------------------------------------

            for conductor in conductores:

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        conductor[0],
                        conductor[1],
                        conductor[2]
                    )
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los conductores:\n\n{e}"
            )

    # ==========================================================================
    # ABRIR VENTANA AGREGAR
    # ==========================================================================

    def abrir_ventana_agregar(self):

        ventana = tk.Toplevel(self)

        ventana.title("Agregar conductor")
        ventana.geometry("350x330")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # CÉDULA
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Cédula:",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

        entrada_cedula = tk.Entry(
            ventana,
            width=30
        )

        entrada_cedula.pack(
            padx=20,
            pady=5
        )

        entrada_cedula.focus()

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
            pady=(10, 5)
        )

        entrada_nombre = tk.Entry(
            ventana,
            width=30
        )

        entrada_nombre.pack(
            padx=20,
            pady=5
        )

        # ----------------------------------------------------------------------
        # TELÉFONO
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Teléfono:",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 5)
        )

        entrada_telefono = tk.Entry(
            ventana,
            width=30
        )

        entrada_telefono.pack(
            padx=20,
            pady=5
        )

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
            command=lambda: self.guardar_conductor(
                entrada_cedula,
                entrada_nombre,
                entrada_telefono,
                ventana
            )
        ).pack(
            pady=20
        )

        # ----------------------------------------------------------------------
        # ENTER PARA GUARDAR
        # ----------------------------------------------------------------------

        ventana.bind(
            "<Return>",
            lambda event: self.guardar_conductor(
                entrada_cedula,
                entrada_nombre,
                entrada_telefono,
                ventana
            )
        )

    # ==========================================================================
    # GUARDAR CONDUCTOR
    # ==========================================================================

    def guardar_conductor(
        self,
        entrada_cedula,
        entrada_nombre,
        entrada_telefono,
        ventana
    ):
        """
        Guarda un nuevo conductor en SQLite.
        """

        # ----------------------------------------------------------------------
        # OBTENER DATOS
        # ----------------------------------------------------------------------

        cedula = entrada_cedula.get().strip()
        nombre = entrada_nombre.get().strip()
        telefono = entrada_telefono.get().strip()

        # ----------------------------------------------------------------------
        # VALIDAR CAMPOS
        # ----------------------------------------------------------------------

        if not cedula or not nombre or not telefono:

            messagebox.showwarning(
                "Conductor",
                "Debes llenar la cédula, el nombre y el teléfono."
            )

            return

        try:

            # ------------------------------------------------------------------
            # CONECTAR CON LA BASE DE DATOS
            # ------------------------------------------------------------------

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # ------------------------------------------------------------------
            # INSERTAR CONDUCTOR
            # ------------------------------------------------------------------

            cursor.execute(
                """
                INSERT INTO conductores (
                    cedula,
                    nombre,
                    telefono
                )
                VALUES (?, ?, ?)
                """,
                (
                    cedula,
                    nombre,
                    telefono
                )
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

            self.cargar_conductores()

            # ------------------------------------------------------------------
            # CERRAR VENTANA
            # ------------------------------------------------------------------

            ventana.destroy()

            # ------------------------------------------------------------------
            # CONFIRMACIÓN
            # ------------------------------------------------------------------

            messagebox.showinfo(
                "Conductor",
                "Conductor guardado correctamente."
            )

        except Exception as e:

            # ------------------------------------------------------------------
            # ERROR DE CÉDULA DUPLICADA
            # ------------------------------------------------------------------

            if "UNIQUE constraint failed" in str(e):

                messagebox.showwarning(
                    "Conductor",
                    f"Ya existe un conductor con la cédula '{cedula}'."
                )

            else:

                messagebox.showerror(
                    "Error",
                    f"No se pudo guardar el conductor:\n\n{e}"
                )

    # ==========================================================================
    # ELIMINAR CONDUCTOR
    # ==========================================================================

    def eliminar(self):

        # ----------------------------------------------------------------------
        # COMPROBAR SI HAY UNA FILA SELECCIONADA
        # ----------------------------------------------------------------------

        seleccionado = self.tabla.selection()

        # Si hay selección, eliminamos directamente
        if seleccionado:

            fila = seleccionado[0]

            valores = self.tabla.item(
                fila,
                "values"
            )

            if not valores:
                return

            cedula = str(
                valores[0]
            )

            nombre = str(
                valores[1]
            )

            confirmar = messagebox.askyesno(
                "Eliminar conductor",
                f"¿Seguro que deseas eliminar al conductor:\n\n"
                f"{nombre}\n"
                f"Cédula: {cedula}?"
            )

            if not confirmar:
                return

            self.eliminar_conductor_por_cedula(
                cedula
            )

            return

        # ----------------------------------------------------------------------
        # SI NO HAY SELECCIÓN, ABRIR VENTANA PARA BUSCAR POR CÉDULA
        # ----------------------------------------------------------------------

        self.abrir_ventana_eliminar_por_cedula()

    # ==========================================================================
    # VENTANA ELIMINAR POR CÉDULA
    # ==========================================================================

    def abrir_ventana_eliminar_por_cedula(self):

        ventana = tk.Toplevel(self)

        ventana.title("Eliminar conductor")
        ventana.geometry("350x200")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # ETIQUETA
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Ingrese la cédula a eliminar:",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(25, 5)
        )

        # ----------------------------------------------------------------------
        # CAMPO CÉDULA
        # ----------------------------------------------------------------------

        entrada_cedula = tk.Entry(
            ventana,
            width=30
        )

        entrada_cedula.pack(
            padx=20,
            pady=5
        )

        entrada_cedula.focus()

        # ----------------------------------------------------------------------
        # BOTÓN ELIMINAR
        # ----------------------------------------------------------------------

        tk.Button(
            ventana,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=lambda: self.eliminar_por_cedula(
                entrada_cedula,
                ventana
            )
        ).pack(
            pady=20
        )

        # ----------------------------------------------------------------------
        # ENTER PARA ELIMINAR
        # ----------------------------------------------------------------------

        ventana.bind(
            "<Return>",
            lambda event: self.eliminar_por_cedula(
                entrada_cedula,
                ventana
            )
        )

    # ==========================================================================
    # ELIMINAR POR CÉDULA
    # ==========================================================================

    def eliminar_por_cedula(
        self,
        entrada_cedula,
        ventana
    ):
        """
        Busca un conductor por su cédula y lo elimina de SQLite.
        """

        cedula_buscada = entrada_cedula.get().strip()

        # ----------------------------------------------------------------------
        # VALIDAR CÉDULA
        # ----------------------------------------------------------------------

        if not cedula_buscada:

            messagebox.showwarning(
                "Conductor",
                "Debe escribir una cédula."
            )

            return

        # ----------------------------------------------------------------------
        # ELIMINAR
        # ----------------------------------------------------------------------

        try:

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                """
                DELETE FROM conductores
                WHERE cedula = ?
                """,
                (
                    cedula_buscada,
                )
            )

            # Comprobar si se eliminó alguna fila
            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            # ------------------------------------------------------------------
            # SI NO EXISTÍA
            # ------------------------------------------------------------------

            if filas_eliminadas == 0:

                messagebox.showwarning(
                    "Conductor",
                    f"No se encontró ningún conductor con la cédula "
                    f"'{cedula_buscada}'."
                )

                return

            # ------------------------------------------------------------------
            # ACTUALIZAR TABLA
            # ------------------------------------------------------------------

            self.cargar_conductores()

            # ------------------------------------------------------------------
            # CERRAR VENTANA
            # ------------------------------------------------------------------

            ventana.destroy()

            # ------------------------------------------------------------------
            # CONFIRMACIÓN
            # ------------------------------------------------------------------

            messagebox.showinfo(
                "Conductor",
                "Conductor eliminado correctamente."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo eliminar el conductor:\n\n{e}"
            )

    # ==========================================================================
    # ELIMINAR CONDUCTOR POR CÉDULA
    # ==========================================================================

    def eliminar_conductor_por_cedula(
        self,
        cedula
    ):
        """
        Elimina directamente un conductor utilizando su cédula.
        """

        try:

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                """
                DELETE FROM conductores
                WHERE cedula = ?
                """,
                (
                    cedula,
                )
            )

            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:

                messagebox.showwarning(
                    "Conductor",
                    f"No se encontró ningún conductor con la cédula "
                    f"'{cedula}'."
                )

                return

            # ------------------------------------------------------------------
            # ACTUALIZAR TABLA
            # ------------------------------------------------------------------

            self.cargar_conductores()

            messagebox.showinfo(
                "Conductor",
                "Conductor eliminado correctamente."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo eliminar el conductor:\n\n{e}"
            )

    # ==========================================================================
    # ACTUALIZAR
    # ==========================================================================

    def actualizar(self):

        """
        Vuelve a consultar SQLite y actualiza el Treeview.
        """

        self.cargar_conductores()

        messagebox.showinfo(
            "Conductor",
            "Datos actualizados."
        )


# ==============================================================================
# EJECUCIÓN DIRECTA
# ==============================================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.withdraw()

    VentanaConductor(root)

    root.mainloop()