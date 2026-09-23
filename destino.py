"""
================================================================================
 DESTINOS - MACS COL
================================================================================
Ventana de gestión de destinos, con el mismo diseño "software de escritorio"
(mockup: macscol_app_menu_escritorio.html) que usan Principal y las demás
ventanas de la aplicación. Los colores, fuentes y helpers viven en estilo.py.
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


class VentanaDestino(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Destinos")
        self.geometry("760x560")
        self.resizable(False, False)
        self.configure(bg=CHROME)

        # Contador simple para ir asignando el ID automáticamente
        # (empieza en 1 y sube de uno en uno con cada destino agregado)
        self.siguiente_id = 1

        self.crear_componentes()
        self.cargar_destinos()

    def crear_componentes(self):
        barra_titulo_ventana(self, "Destinos")

        cuerpo = tk.Frame(self, bg=CHROME)
        cuerpo.pack(fill="both", expand=True, padx=24, pady=18)

        encabezado = tk.Frame(cuerpo, bg=CHROME)
        encabezado.pack(fill="x", pady=(0, 12))
        tk.Label(encabezado, text="Destinos y puntos de entrega", font=FUENTE_SUBTITULO,
                 fg=INK, bg=CHROME).pack(side="left")
        tk.Label(encabezado, text="Principal › Destinos", font=("Segoe UI", 9),
                 fg=GRAY, bg=CHROME).pack(side="right")

        tarjeta = tk.Frame(cuerpo, bg=WHITE, highlightbackground=CHROME_LINE,
                            highlightthickness=1)
        tarjeta.pack(fill="both", expand=True)

        estilo_tabla = configurar_estilo_treeview("Destinos.Treeview")
        self.tabla = ttk.Treeview(
            tarjeta,
            columns=("Nombre", "ID"),
            show="headings",
            height=14,
            style=estilo_tabla,
        )
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("ID", text="ID")
        self.tabla.column("Nombre", width=280, anchor="center")
        self.tabla.column("ID", width=120, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=12, pady=12)

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

    # ------------------------------------------------------------------
    # CARGAR
    # ------------------------------------------------------------------
    def cargar_destinos(self):
        """Consulta los destinos guardados y los muestra en la tabla."""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id, nombre
                FROM destinos
                ORDER BY id
            """)
            destinos = cursor.fetchall()
            conexion.close()

            for id_destino, nombre in destinos:
                self.tabla.insert("", "end", values=(nombre, id_destino))
        except Exception as error:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los destinos:\n\n{error}"
            )

    # ------------------------------------------------------------------
    # AGREGAR
    # ------------------------------------------------------------------
    def abrir_ventana_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar destino")
        ventana.geometry("360x230")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Agregar destino")

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
            lambda: self.guardar_destino(entrada_nombre, ventana),
            ancho=16,
        ).pack(pady=(22, 0))

        # Permite presionar Enter en vez de dar clic en "Guardar"
        ventana.bind(
            "<Return>",
            lambda event: self.guardar_destino(entrada_nombre, ventana)
        )

    def guardar_destino(self, entrada_nombre, ventana):
        nombre = entrada_nombre.get().strip()

        if not nombre:
            messagebox.showwarning(
                "Destino",
                "Debes escribir el nombre del destino."
            )
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO destinos (nombre) VALUES (?)",
                (nombre,)
            )
            conexion.commit()
            conexion.close()

            self.cargar_destinos()
            ventana.destroy()
            messagebox.showinfo("Destino", "Destino guardado correctamente.")
        except Exception as error:
            messagebox.showerror(
                "Error", f"No se pudo guardar el destino:\n\n{error}"
            )

    # ------------------------------------------------------------------
    # ELIMINAR (por selección, o por ID si no hay nada seleccionado)
    # ------------------------------------------------------------------
    def eliminar(self):
        seleccionado = self.tabla.selection()

        if seleccionado:
            valores = self.tabla.item(seleccionado[0], "values")
            self.eliminar_destino(valores[1])
            return

        self.abrir_ventana_eliminar_por_id()

    def abrir_ventana_eliminar_por_id(self):
        ventana = tk.Toplevel(self)
        ventana.title("Eliminar destino")
        ventana.geometry("360x220")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Eliminar destino")

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

    def eliminar_por_id(self, entrada_id, ventana):
        id_buscado = entrada_id.get().strip()

        if not id_buscado:
            messagebox.showwarning(
                "Destino",
                "Debe escribir un ID."
            )
            return

        if self.eliminar_destino(id_buscado):
            ventana.destroy()
            return

        messagebox.showwarning(
            "Destino",
            f"No se encontró ningún destino con el ID '{id_buscado}'."
        )

    def eliminar_destino(self, id_destino):
        """Elimina un destino por su ID y recarga la tabla."""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM destinos WHERE id = ?", (id_destino,))
            filas_eliminadas = cursor.rowcount
            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:
                return False

            self.cargar_destinos()
            messagebox.showinfo("Destino", "Destino eliminado correctamente.")
            return True
        except Exception as error:
            messagebox.showerror(
                "Error", f"No se pudo eliminar el destino:\n\n{error}"
            )
            return False

    # ------------------------------------------------------------------
    # ACTUALIZAR
    # ------------------------------------------------------------------
    def actualizar(self):
        self.cargar_destinos()
        messagebox.showinfo(
            "Destino",
            "Datos actualizados."
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    VentanaDestino(root)

    root.mainloop()