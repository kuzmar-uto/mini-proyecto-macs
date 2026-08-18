#esta secion tiene que estar conectada a el principal por medio del boton de vehiculo
# cundo se le de al boton en la pestaña de 




import tkinter as tk
from tkinter import ttk, messagebox

from almacenamiento import obtener_conexion

COLOR_FONDO = "#DFFFF7"
COLOR_BOTON = "#0B1F6B"

FUENTE_BOTON = ("Segoe UI", 12, "bold")
FUENTE_TITULO = ("Cooper Black", 24)


class VentanaVehiculo(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Vehículo")
        self.geometry("900x550")
        self.resizable(False, False)
        self.configure(bg=COLOR_FONDO)

        self.crear_componentes()
        self.cargar_vehiculos()

    def crear_componentes(self):
        titulo = tk.Label(
            self,
            text="VEHÍCULO",
            font=FUENTE_TITULO,
            fg="navy",
            bg=COLOR_FONDO
        )
        titulo.pack(pady=15)

        centro = tk.Frame(self, bg=COLOR_FONDO)
        centro.pack(pady=10)

        imagen = tk.Label(
            centro,
            text="CAMIÓN",
            bg="white",
            width=28,
            height=12,
            relief="solid"
        )
        imagen.grid(row=0, column=1, padx=25)

        columnas = ("Placa", "Capacidad")

        self.tabla = ttk.Treeview(
            centro,
            columns=columnas,
            show="headings",
            height=10
        )

        self.tabla.heading("Placa", text="Placa")
        self.tabla.heading("Capacidad", text="Capacidad")

        self.tabla.column("Placa", width=150, anchor="center")
        self.tabla.column("Capacidad", width=150, anchor="center")

        self.tabla.grid(row=0, column=2)

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
            text="Refrescar",
            bg=COLOR_BOTON,
            fg="white",
            font=FUENTE_BOTON,
            width=12,
            command=self.refrescar
        ).grid(row=0, column=2, padx=15)

    def cargar_vehiculos(self):
        """Consulta los vehículos guardados y los muestra en la tabla."""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT placa, capacidad
                FROM vehiculos
                ORDER BY placa
            """)
            vehiculos = cursor.fetchall()
            conexion.close()

            for placa, capacidad in vehiculos:
                self.tabla.insert("", "end", values=(placa, capacidad))
        except Exception as error:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los vehículos:\n\n{error}"
            )

    def abrir_ventana_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar vehiculo")
        ventana.geometry("320x220")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)

        tk.Label(
            ventana,
            text="Placa:",
            bg=COLOR_FONDO,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(20, 5))

        entrada_placa = tk.Entry(ventana, width=25)
        entrada_placa.pack(padx=20, pady=5)

        tk.Label(
            ventana,
            text="Capacidad:",
            bg=COLOR_FONDO,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(10, 5))

        entrada_capacidad = tk.Entry(ventana, width=25)
        entrada_capacidad.pack(padx=20, pady=5)

        tk.Button(
            ventana,
            text="Guardar",
            bg=COLOR_BOTON,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.guardar_vehiculo(entrada_placa, entrada_capacidad, ventana)
        ).pack(pady=20)

    def guardar_vehiculo(self, entrada_placa, entrada_capacidad, ventana):
        placa = entrada_placa.get().strip().upper()
        capacidad = entrada_capacidad.get().strip()

        if not placa or not capacidad:
            messagebox.showwarning(
                "Vehículo",
                "Debes llenar la placa y la capacidad."
            )
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO vehiculos (placa, capacidad) VALUES (?, ?)",
                (placa, capacidad)
            )
            conexion.commit()
            conexion.close()

            self.cargar_vehiculos()
            ventana.destroy()
            messagebox.showinfo("Vehículo", "Vehículo guardado correctamente.")
        except Exception as error:
            messagebox.showerror(
                "Error", f"No se pudo guardar el vehículo:\n\n{error}"
            )

    def eliminar(self):
        # Caso 1: ya hay una fila seleccionada en la tabla -> se borra
        # directamente, igual que antes.
        seleccionado = self.tabla.selection()

        if seleccionado:
            valores = self.tabla.item(seleccionado[0], "values")
            self.eliminar_vehiculo(valores[0])
            return

        # Caso 2: no hay ninguna fila seleccionada -> se abre una ventana
        # para buscar y eliminar el vehículo escribiendo su placa.
        self.abrir_ventana_eliminar_por_placa()

    def abrir_ventana_eliminar_por_placa(self):
        ventana = tk.Toplevel(self)
        ventana.title("Eliminar vehiculo")
        ventana.geometry("320x180")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO)






        
        tk.Label(
            ventana,
            text="Ingrese la placa a eliminar:",
            bg=COLOR_FONDO,
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=(20, 5))

        entrada_placa = tk.Entry(ventana, width=25)
        entrada_placa.pack(padx=20, pady=5)
        entrada_placa.focus()

        tk.Button(
            ventana,
            text="Eliminar",
            bg=COLOR_BOTON,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.eliminar_por_placa(entrada_placa, ventana)
        ).pack(pady=20)

        # Permite presionar Enter en vez de tener que hacer clic en el botón
        ventana.bind(
            "<Return>",
            lambda event: self.eliminar_por_placa(entrada_placa, ventana)
        )

    def eliminar_por_placa(self, entrada_placa, ventana):
        placa_buscada = entrada_placa.get().strip().upper()

        if not placa_buscada:
            messagebox.showwarning(
                "Vehículo",
                "Debe escribir una placa."
            )
            return

        if self.eliminar_vehiculo(placa_buscada):
            ventana.destroy()
            return

        # Si termina el for sin encontrar coincidencia
        messagebox.showwarning(
            "Vehículo",
            f"No se encontró ningún vehículo con la placa '{placa_buscada}'."
        )

    def eliminar_vehiculo(self, placa):
        """Elimina un vehículo por su placa y recarga la tabla."""
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM vehiculos WHERE placa = ?", (placa,))
            filas_eliminadas = cursor.rowcount
            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:
                return False

            self.cargar_vehiculos()
            messagebox.showinfo("Vehículo", "Vehículo eliminado correctamente.")
            return True
        except Exception as error:
            messagebox.showerror(
                "Error", f"No se pudo eliminar el vehículo:\n\n{error}"
            )
            return False

    def refrescar(self):
        self.cargar_vehiculos()
        messagebox.showinfo(
            "Vehículo",
            "Datos actualizados."
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    VentanaVehiculo(root)

    root.mainloop()
