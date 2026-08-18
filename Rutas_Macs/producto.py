"""
================================================================================
 PRODUCTOS - MACS COL
================================================================================

Este módulo gestiona los productos de MACS COL.

Los datos se almacenan de forma permanente en SQLite mediante:
    almacenamiento.py

La información se guarda en:
    datos/macscol.db

Funciones principales:
    - Cargar productos desde la base de datos.
    - Agregar nuevos productos.
    - Eliminar productos.
    - Eliminar productos por ID.
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

FUENTE_BOTON = ("Segoe UI", 12, "bold")
FUENTE_TITULO = ("Cooper Black", 24)
FUENTE_ETIQUETA = ("Segoe UI", 11)


# ==============================================================================
# VENTANA PRODUCTOS
# ==============================================================================

class VentanaProducto(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        # ----------------------------------------------------------------------
        # CONFIGURACIÓN DE LA VENTANA
        # ----------------------------------------------------------------------

        self.title("Producto")
        self.geometry("1000x550")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # CREAR COMPONENTES
        # ----------------------------------------------------------------------

        self.crear_componentes()

        # ----------------------------------------------------------------------
        # CARGAR PRODUCTOS DESDE SQLITE
        # ----------------------------------------------------------------------

        self.cargar_productos()

    # ==========================================================================
    # CREAR COMPONENTES
    # ==========================================================================

    def crear_componentes(self):

        # ----------------------------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------------------------

        titulo = tk.Label(
            self,
            text="PRODUCTO",
            font=FUENTE_TITULO,
            fg="navy",
            bg=COLOR_FONDO
        )

        titulo.pack(
            pady=15
        )

        # ----------------------------------------------------------------------
        # FRAME CENTRAL
        # ----------------------------------------------------------------------

        centro = tk.Frame(
            self,
            bg=COLOR_FONDO
        )

        centro.pack(
            pady=10
        )

        # ----------------------------------------------------------------------
        # COLUMNAS
        # ----------------------------------------------------------------------

        columnas = (
            "ID",
            "Nombre",
            "Embalaje",
            "Peso Canastilla (KG)",
            "Descripción"
        )

        # ----------------------------------------------------------------------
        # TREEVIEW
        # ----------------------------------------------------------------------

        self.tabla = ttk.Treeview(
            centro,
            columns=columnas,
            show="headings",
            height=12
        )

        # ----------------------------------------------------------------------
        # ENCABEZADOS
        # ----------------------------------------------------------------------

        self.tabla.heading(
            "ID",
            text="ID"
        )

        self.tabla.heading(
            "Nombre",
            text="Nombre"
        )

        self.tabla.heading(
            "Embalaje",
            text="Embalaje"
        )

        self.tabla.heading(
            "Peso Canastilla (KG)",
            text="Peso Canastilla (KG)"
        )

        self.tabla.heading(
            "Descripción",
            text="Descripción"
        )

        # ----------------------------------------------------------------------
        # ANCHO DE COLUMNAS
        # ----------------------------------------------------------------------

        self.tabla.column(
            "ID",
            width=60,
            anchor="center"
        )

        self.tabla.column(
            "Nombre",
            width=150,
            anchor="center"
        )

        self.tabla.column(
            "Embalaje",
            width=120,
            anchor="center"
        )

        self.tabla.column(
            "Peso Canastilla (KG)",
            width=150,
            anchor="center"
        )

        self.tabla.column(
            "Descripción",
            width=250,
            anchor="center"
        )

        self.tabla.grid(
            row=0,
            column=0
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

    # ==========================================================================
    # CARGAR PRODUCTOS
    # ==========================================================================

    def cargar_productos(self):
        """
        Carga todos los productos almacenados en SQLite
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
            # CONSULTAR PRODUCTOS
            # ------------------------------------------------------------------

            cursor.execute("""
                SELECT
                    id,
                    nombre,
                    embalaje,
                    peso_canastilla,
                    descripcion
                FROM productos
                ORDER BY id
            """)

            productos = cursor.fetchall()

            # ------------------------------------------------------------------
            # CERRAR CONEXIÓN
            # ------------------------------------------------------------------

            conexion.close()

            # ------------------------------------------------------------------
            # MOSTRAR PRODUCTOS
            # ------------------------------------------------------------------

            for producto in productos:

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        producto[0],
                        producto[1],
                        producto[2],
                        producto[3],
                        producto[4]
                    )
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los productos:\n\n{e}"
            )

    # ==========================================================================
    # ABRIR VENTANA AGREGAR
    # ==========================================================================

    def abrir_ventana_agregar(self):

        ventana = tk.Toplevel(self)

        ventana.title("Agregar producto")
        ventana.geometry("350x420")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # ID
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="El ID se asigna automáticamente al guardar.",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 5)
        )

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
        entrada_nombre.focus()

        # ----------------------------------------------------------------------
        # EMBALAJE
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Embalaje:",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 5)
        )

        entrada_embalaje = tk.Entry(
            ventana,
            width=30
        )

        entrada_embalaje.pack(
            padx=20,
            pady=5
        )

        # ----------------------------------------------------------------------
        # PESO
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Peso Canastilla (KG):",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 5)
        )

        entrada_peso = tk.Entry(
            ventana,
            width=30
        )

        entrada_peso.pack(
            padx=20,
            pady=5
        )

        # ----------------------------------------------------------------------
        # DESCRIPCIÓN
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Descripción:",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 5)
        )

        entrada_descripcion = tk.Entry(
            ventana,
            width=30
        )

        entrada_descripcion.pack(
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
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.guardar_producto(
                entrada_nombre,
                entrada_embalaje,
                entrada_peso,
                entrada_descripcion,
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
            lambda event: self.guardar_producto(
                entrada_nombre,
                entrada_embalaje,
                entrada_peso,
                entrada_descripcion,
                ventana
            )
        )

    # ==========================================================================
    # GUARDAR PRODUCTO
    # ==========================================================================

    def guardar_producto(
        self,
        entrada_nombre,
        entrada_embalaje,
        entrada_peso,
        entrada_descripcion,
        ventana
    ):
        """
        Guarda un nuevo producto en SQLite.
        """

        # ----------------------------------------------------------------------
        # OBTENER DATOS
        # ----------------------------------------------------------------------

        nombre = entrada_nombre.get().strip()
        embalaje = entrada_embalaje.get().strip()
        peso = entrada_peso.get().strip()
        descripcion = entrada_descripcion.get().strip()

        # ----------------------------------------------------------------------
        # VALIDAR CAMPOS
        # ----------------------------------------------------------------------

        if (
            not nombre
            or not embalaje
            or not peso
            or not descripcion
        ):

            messagebox.showwarning(
                "Producto",
                "Debes llenar todos los campos."
            )

            return

        # ----------------------------------------------------------------------
        # VALIDAR PESO
        # ----------------------------------------------------------------------

        try:

            peso_numerico = float(
                peso.replace(",", ".")
            )

        except ValueError:

            messagebox.showwarning(
                "Producto",
                "El peso debe ser un número válido.\n\n"
                "Ejemplo: 10.5"
            )

            return

        # ----------------------------------------------------------------------
        # VALIDAR QUE EL PESO SEA POSITIVO
        # ----------------------------------------------------------------------

        if peso_numerico <= 0:

            messagebox.showwarning(
                "Producto",
                "El peso debe ser mayor que cero."
            )

            return

        try:

            # ------------------------------------------------------------------
            # CONECTAR CON SQLITE
            # ------------------------------------------------------------------

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # ------------------------------------------------------------------
            # INSERTAR PRODUCTO
            # ------------------------------------------------------------------

            cursor.execute(
                """
                INSERT INTO productos (
                    nombre,
                    embalaje,
                    peso_canastilla,
                    descripcion
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    nombre,
                    embalaje,
                    peso_numerico,
                    descripcion
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

            self.cargar_productos()

            # ------------------------------------------------------------------
            # CERRAR VENTANA
            # ------------------------------------------------------------------

            ventana.destroy()

            # ------------------------------------------------------------------
            # CONFIRMACIÓN
            # ------------------------------------------------------------------

            messagebox.showinfo(
                "Producto",
                "Producto guardado correctamente."
            )

        except Exception as e:

            # ------------------------------------------------------------------
            # ID DUPLICADO
            # ------------------------------------------------------------------

            if "UNIQUE constraint failed" in str(e):

                messagebox.showwarning(
                    "Producto",
                    f"Ya existe un producto con el ID "
                    f"'{id_producto}'."
                )

            else:

                messagebox.showerror(
                    "Error",
                    f"No se pudo guardar el producto:\n\n{e}"
                )

    # ==========================================================================
    # ELIMINAR PRODUCTO
    # ==========================================================================

    def eliminar(self):

        # ----------------------------------------------------------------------
        # COMPROBAR SELECCIÓN
        # ----------------------------------------------------------------------

        seleccionado = self.tabla.selection()

        # Si hay un producto seleccionado
        if seleccionado:

            fila = seleccionado[0]

            valores = self.tabla.item(
                fila,
                "values"
            )

            if not valores:
                return

            id_producto = str(
                valores[0]
            )

            nombre_producto = str(
                valores[1]
            )

            confirmar = messagebox.askyesno(
                "Eliminar producto",
                f"¿Seguro que deseas eliminar el producto:\n\n"
                f"{nombre_producto}\n"
                f"ID: {id_producto}?"
            )

            if not confirmar:
                return

            self.eliminar_producto_por_id(
                id_producto
            )

            return

        # ----------------------------------------------------------------------
        # SI NO HAY SELECCIÓN, BUSCAR POR ID
        # ----------------------------------------------------------------------

        self.abrir_ventana_eliminar_por_id()

    # ==========================================================================
    # VENTANA ELIMINAR POR ID
    # ==========================================================================

    def abrir_ventana_eliminar_por_id(self):

        ventana = tk.Toplevel(self)

        ventana.title("Eliminar producto")
        ventana.geometry("350x200")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        # ----------------------------------------------------------------------
        # ETIQUETA
        # ----------------------------------------------------------------------

        tk.Label(
            ventana,
            text="Ingrese el ID a eliminar:",
            bg=COLOR_FONDO,
            font=FUENTE_ETIQUETA
        ).pack(
            anchor="w",
            padx=20,
            pady=(25, 5)
        )

        # ----------------------------------------------------------------------
        # CAMPO ID
        # ----------------------------------------------------------------------

        entrada_id = tk.Entry(
            ventana,
            width=30
        )

        entrada_id.pack(
            padx=20,
            pady=5
        )

        entrada_id.focus()

        # ----------------------------------------------------------------------
        # BOTÓN ELIMINAR
        # ----------------------------------------------------------------------

        tk.Button(
            ventana,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.eliminar_por_id(
                entrada_id,
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
            lambda event: self.eliminar_por_id(
                entrada_id,
                ventana
            )
        )

    # ==========================================================================
    # ELIMINAR POR ID
    # ==========================================================================

    def eliminar_por_id(
        self,
        entrada_id,
        ventana
    ):
        """
        Elimina un producto de SQLite utilizando su ID.
        """

        id_buscado = entrada_id.get().strip()

        # ----------------------------------------------------------------------
        # VALIDAR ID
        # ----------------------------------------------------------------------

        if not id_buscado:

            messagebox.showwarning(
                "Producto",
                "Debe escribir un ID."
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
                DELETE FROM productos
                WHERE id = ?
                """,
                (
                    id_buscado,
                )
            )

            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            # ------------------------------------------------------------------
            # PRODUCTO NO ENCONTRADO
            # ------------------------------------------------------------------

            if filas_eliminadas == 0:

                messagebox.showwarning(
                    "Producto",
                    f"No se encontró ningún producto con el ID "
                    f"'{id_buscado}'."
                )

                return

            # ------------------------------------------------------------------
            # ACTUALIZAR TABLA
            # ------------------------------------------------------------------

            self.cargar_productos()

            # ------------------------------------------------------------------
            # CERRAR VENTANA
            # ------------------------------------------------------------------

            ventana.destroy()

            # ------------------------------------------------------------------
            # CONFIRMACIÓN
            # ------------------------------------------------------------------

            messagebox.showinfo(
                "Producto",
                "Producto eliminado correctamente."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo eliminar el producto:\n\n{e}"
            )

    # ==========================================================================
    # ELIMINAR PRODUCTO POR ID
    # ==========================================================================

    def eliminar_producto_por_id(
        self,
        id_producto
    ):
        """
        Elimina directamente un producto utilizando su ID.
        """

        try:

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                """
                DELETE FROM productos
                WHERE id = ?
                """,
                (
                    id_producto,
                )
            )

            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:

                messagebox.showwarning(
                    "Producto",
                    f"No se encontró ningún producto con el ID "
                    f"'{id_producto}'."
                )

                return

            # ------------------------------------------------------------------
            # ACTUALIZAR TABLA
            # ------------------------------------------------------------------

            self.cargar_productos()

            messagebox.showinfo(
                "Producto",
                "Producto eliminado correctamente."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo eliminar el producto:\n\n{e}"
            )

    # ==========================================================================
    # ACTUALIZAR
    # ==========================================================================

    def actualizar(self):

        """
        Vuelve a consultar SQLite y actualiza el Treeview.
        """

        self.cargar_productos()

        messagebox.showinfo(
            "Producto",
            "Datos actualizados."
        )


# ==============================================================================
# EJECUCIÓN DIRECTA
# ==============================================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.withdraw()

    VentanaProducto(root)

    root.mainloop()
