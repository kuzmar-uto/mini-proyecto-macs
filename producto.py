"""
================================================================================
 PRODUCTOS - MACS COL
================================================================================

Este módulo gestiona los productos de MACS COL, con el mismo diseño "software
de escritorio" (mockup: macscol_app_menu_escritorio.html) que usan Principal
y las demás ventanas de la aplicación. Los colores, fuentes y helpers viven
en estilo.py.

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
from estilo import (
    CHROME, CHROME_LINE, NAVY, NAVY_DEEP, ACCENT, ACCENT_BG, INK, GRAY, WHITE,
    FUENTE_SUBTITULO, FUENTE_ETIQUETA, FUENTE_TEXTO,
    boton_primario, boton_secundario, configurar_estilo_treeview,
    barra_titulo_ventana, linea_separadora,
)


# ==============================================================================
# VENTANA PRODUCTOS
# ==============================================================================

class VentanaProducto(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Productos")
        self.geometry("980x580")
        self.resizable(False, False)
        self.configure(bg=CHROME)

        self.crear_componentes()
        self.cargar_productos()

    # ==========================================================================
    # CREAR COMPONENTES
    # ==========================================================================

    def crear_componentes(self):
        barra_titulo_ventana(self, "Productos")

        cuerpo = tk.Frame(self, bg=CHROME)
        cuerpo.pack(fill="both", expand=True, padx=24, pady=18)

        encabezado = tk.Frame(cuerpo, bg=CHROME)
        encabezado.pack(fill="x", pady=(0, 12))
        tk.Label(encabezado, text="Catálogo de productos", font=FUENTE_SUBTITULO,
                 fg=INK, bg=CHROME).pack(side="left")
        tk.Label(encabezado, text="Principal › Productos", font=("Segoe UI", 9),
                 fg=GRAY, bg=CHROME).pack(side="right")

        # ---- Tarjeta con la tabla ----
        tarjeta = tk.Frame(cuerpo, bg=WHITE, highlightbackground=CHROME_LINE,
                            highlightthickness=1)
        tarjeta.pack(fill="both", expand=True)

        columnas = ("ID", "Nombre", "Embalaje", "Peso Canastilla (KG)", "Descripción")

        estilo_tabla = configurar_estilo_treeview("Productos.Treeview")
        self.tabla = ttk.Treeview(
            tarjeta,
            columns=columnas,
            show="headings",
            height=13,
            style=estilo_tabla,
        )

        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Embalaje", text="Embalaje")
        self.tabla.heading("Peso Canastilla (KG)", text="Peso Canastilla (KG)")
        self.tabla.heading("Descripción", text="Descripción")

        self.tabla.column("ID", width=60, anchor="center")
        self.tabla.column("Nombre", width=170, anchor="center")
        self.tabla.column("Embalaje", width=130, anchor="center")
        self.tabla.column("Peso Canastilla (KG)", width=160, anchor="center")
        self.tabla.column("Descripción", width=300, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=12, pady=12)

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
    # CARGAR PRODUCTOS
    # ==========================================================================

    def cargar_productos(self):
        """
        Carga todos los productos almacenados en SQLite
        y los muestra en el Treeview.
        """
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id, nombre, embalaje, peso_canastilla, descripcion
                FROM productos
                ORDER BY id
            """)

            productos = cursor.fetchall()
            conexion.close()

            for producto in productos:
                self.tabla.insert(
                    "", "end",
                    values=(producto[0], producto[1], producto[2], producto[3], producto[4])
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
        ventana.geometry("380x480")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Agregar producto")

        contenido = tk.Frame(ventana, bg=CHROME)
        contenido.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(contenido, text="El ID se asigna automáticamente al guardar.",
                 font=("Segoe UI", 9), fg=GRAY, bg=CHROME).pack(anchor="w", pady=(0, 10))

        tk.Label(contenido, text="Nombre:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(4, 4))
        entrada_nombre = tk.Entry(contenido, width=30, font=FUENTE_TEXTO, relief="solid",
                                   highlightbackground=CHROME_LINE, bd=1)
        entrada_nombre.pack(fill="x", ipady=4)
        entrada_nombre.focus()

        tk.Label(contenido, text="Embalaje:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(12, 4))
        entrada_embalaje = tk.Entry(contenido, width=30, font=FUENTE_TEXTO, relief="solid",
                                     highlightbackground=CHROME_LINE, bd=1)
        entrada_embalaje.pack(fill="x", ipady=4)

        tk.Label(contenido, text="Peso Canastilla (KG):", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(12, 4))
        entrada_peso = tk.Entry(contenido, width=30, font=FUENTE_TEXTO, relief="solid",
                                 highlightbackground=CHROME_LINE, bd=1)
        entrada_peso.pack(fill="x", ipady=4)

        tk.Label(contenido, text="Descripción:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(12, 4))
        entrada_descripcion = tk.Entry(contenido, width=30, font=FUENTE_TEXTO, relief="solid",
                                        highlightbackground=CHROME_LINE, bd=1)
        entrada_descripcion.pack(fill="x", ipady=4)

        boton_primario(
            contenido, "Guardar",
            lambda: self.guardar_producto(
                entrada_nombre, entrada_embalaje, entrada_peso, entrada_descripcion, ventana
            ),
            ancho=16,
        ).pack(pady=(22, 0))

        ventana.bind(
            "<Return>",
            lambda event: self.guardar_producto(
                entrada_nombre, entrada_embalaje, entrada_peso, entrada_descripcion, ventana
            )
        )

    # ==========================================================================
    # GUARDAR PRODUCTO
    # ==========================================================================

    def guardar_producto(self, entrada_nombre, entrada_embalaje, entrada_peso,
                          entrada_descripcion, ventana):
        """
        Guarda un nuevo producto en SQLite.
        """
        nombre = entrada_nombre.get().strip()
        embalaje = entrada_embalaje.get().strip()
        peso = entrada_peso.get().strip()
        descripcion = entrada_descripcion.get().strip()

        if not nombre or not embalaje or not peso or not descripcion:
            messagebox.showwarning(
                "Producto",
                "Debes llenar todos los campos."
            )
            return

        try:
            peso_numerico = float(peso.replace(",", "."))
        except ValueError:
            messagebox.showwarning(
                "Producto",
                "El peso debe ser un número válido.\n\nEjemplo: 10.5"
            )
            return

        if peso_numerico <= 0:
            messagebox.showwarning(
                "Producto",
                "El peso debe ser mayor que cero."
            )
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO productos (nombre, embalaje, peso_canastilla, descripcion)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, embalaje, peso_numerico, descripcion)
            )

            conexion.commit()
            conexion.close()

            self.cargar_productos()
            ventana.destroy()

            messagebox.showinfo(
                "Producto",
                "Producto guardado correctamente."
            )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showwarning(
                    "Producto",
                    "Ya existe un producto con ese identificador."
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
        seleccionado = self.tabla.selection()

        if seleccionado:
            fila = seleccionado[0]
            valores = self.tabla.item(fila, "values")

            if not valores:
                return

            id_producto = str(valores[0])
            nombre_producto = str(valores[1])

            confirmar = messagebox.askyesno(
                "Eliminar producto",
                f"¿Seguro que deseas eliminar el producto:\n\n"
                f"{nombre_producto}\n"
                f"ID: {id_producto}?"
            )

            if not confirmar:
                return

            self.eliminar_producto_por_id(id_producto)
            return

        # Si no hay selección, buscar por ID
        self.abrir_ventana_eliminar_por_id()

    # ==========================================================================
    # VENTANA ELIMINAR POR ID
    # ==========================================================================

    def abrir_ventana_eliminar_por_id(self):
        ventana = tk.Toplevel(self)
        ventana.title("Eliminar producto")
        ventana.geometry("360x220")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Eliminar producto")

        contenido = tk.Frame(ventana, bg=CHROME)
        contenido.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(contenido, text="Ingrese el ID a eliminar:", font=FUENTE_ETIQUETA,
                 fg=INK, bg=CHROME).pack(anchor="w", pady=(4, 4))

        entrada_id = tk.Entry(contenido, width=28, font=FUENTE_TEXTO, relief="solid",
                               highlightbackground=CHROME_LINE, bd=1)
        entrada_id.pack(fill="x", ipady=4)
        entrada_id.focus()

        boton_primario(
            contenido, "Eliminar",
            lambda: self.eliminar_por_id(entrada_id, ventana),
            ancho=16,
        ).pack(pady=(22, 0))

        ventana.bind(
            "<Return>",
            lambda event: self.eliminar_por_id(entrada_id, ventana)
        )

    # ==========================================================================
    # ELIMINAR POR ID
    # ==========================================================================

    def eliminar_por_id(self, entrada_id, ventana):
        """
        Elimina un producto de SQLite utilizando su ID.
        """
        id_buscado = entrada_id.get().strip()

        if not id_buscado:
            messagebox.showwarning(
                "Producto",
                "Debe escribir un ID."
            )
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("DELETE FROM productos WHERE id = ?", (id_buscado,))
            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:
                messagebox.showwarning(
                    "Producto",
                    f"No se encontró ningún producto con el ID '{id_buscado}'."
                )
                return

            self.cargar_productos()
            ventana.destroy()

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

    def eliminar_producto_por_id(self, id_producto):
        """
        Elimina directamente un producto utilizando su ID.
        """
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:
                messagebox.showwarning(
                    "Producto",
                    f"No se encontró ningún producto con el ID '{id_producto}'."
                )
                return

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