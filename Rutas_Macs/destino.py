#esta seccion tiene que estar conectada a el principal por medio del boton de destino


import tkinter as tk
from tkinter import ttk, messagebox

from almacenamiento import obtener_conexion

COLOR_FONDO = "#DFFFF7"
COLOR_BOTON = "#0B1F6B"

FUENTE_BOTON = ("Segoe UI", 12, "bold")
FUENTE_TITULO = ("Cooper Black", 24)


class VentanaDestino(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Destino")
        self.geometry("900x550")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)

        # Contador simple para ir asignando el ID automáticamente
        # (empieza en 1 y sube de uno en uno con cada destino agregado)
        self.siguiente_id = 1
        
        self.crear_componentes()
        self.cargar_destinos()

    def crear_componentes(self):
        titulo = tk.Label(
            self,
            text="DESTINO",
            font=FUENTE_TITULO,
            fg="navy",
            bg=COLOR_FONDO
        )
        titulo.pack(pady=15)

        centro = tk.Frame(self, bg=COLOR_FONDO)
        centro.pack(pady=10)

        columnas = ("Nombre", "ID")

        self.tabla = ttk.Treeview(
            centro,
            columns=columnas,
            show="headings",
            height=12
        )

        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("ID", text="ID")

        self.tabla.column("Nombre", width=250, anchor="center")
        self.tabla.column("ID", width=100, anchor="center")

        self.tabla.grid(row=0, column=0)

        botones = tk.Frame(self, bg=COLOR_FONDO)
        botones.pack(pady=25)

        tk.Button(
            botones,
            text="Agregar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.abrir_ventana_agregar
        ).grid(row=0, column=0, padx=15)

        tk.Button(
            botones,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.eliminar
        ).grid(row=0, column=1, padx=15)

        tk.Button(
            botones,
            text="Actualizar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.actualizar
        ).grid(row=0, column=2, padx=15)

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
        ventana.geometry("320x180")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        tk.Label(
            ventana,
            text="Nombre:",
            bg=COLOR_FONDO,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(20, 5))

        entrada_nombre = tk.Entry(ventana, width=25)
        entrada_nombre.pack(padx=20, pady=5)
        entrada_nombre.focus()

        tk.Button(
            ventana,
            text="Guardar",
            bg=COLOR_BOTON,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.guardar_destino(entrada_nombre, ventana)
        ).pack(pady=20)

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
    # ELIMINAR (por selección, o por nombre si no hay nada seleccionado)
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
        ventana.geometry("320x180")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        tk.Label(
            ventana,
            text="Ingrese el ID a eliminar:",
            bg=COLOR_FONDO,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(20, 5))

        entrada_id = tk.Entry(ventana, width=25)
        entrada_id.pack(padx=20, pady=5)
        entrada_id.focus()

        tk.Button(
            ventana,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.eliminar_por_id(entrada_id, ventana)
        ).pack(pady=20)

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

    # ------------------------------------------------------------------
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
