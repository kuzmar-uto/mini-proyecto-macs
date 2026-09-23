"""
================================================================================
 VEHÍCULOS - MACS COL
================================================================================
Ventana de gestión de vehículos, con el mismo diseño "software de escritorio"
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


class VentanaVehiculo(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Vehículos")
        self.geometry("760x560")
        self.resizable(False, False)
        self.configure(bg=CHROME)

        self.crear_componentes()
        self.cargar_vehiculos()

    # ------------------------------------------------------------------
    # COMPONENTES
    # ------------------------------------------------------------------
    def crear_componentes(self):
        barra_titulo_ventana(self, "Vehículos")

        cuerpo = tk.Frame(self, bg=CHROME)
        cuerpo.pack(fill="both", expand=True, padx=24, pady=18)

        encabezado = tk.Frame(cuerpo, bg=CHROME)
        encabezado.pack(fill="x", pady=(0, 12))
        tk.Label(encabezado, text="Flota de vehículos", font=FUENTE_SUBTITULO,
                 fg=INK, bg=CHROME).pack(side="left")
        tk.Label(encabezado, text="Principal › Vehículos", font=("Segoe UI", 9),
                 fg=GRAY, bg=CHROME).pack(side="right")

        # ---- Tarjeta con la tabla ----
        tarjeta = tk.Frame(cuerpo, bg=WHITE, highlightbackground=CHROME_LINE,
                            highlightthickness=1)
        tarjeta.pack(fill="both", expand=True)

        estilo_tabla = configurar_estilo_treeview("Vehiculos.Treeview")
        self.tabla = ttk.Treeview(
            tarjeta,
            columns=("Placa", "Capacidad"),
            show="headings",
            height=14,
            style=estilo_tabla,
        )
        self.tabla.heading("Placa", text="Placa")
        self.tabla.heading("Capacidad", text="Capacidad")
        self.tabla.column("Placa", width=200, anchor="center")
        self.tabla.column("Capacidad", width=200, anchor="center")
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

    # ------------------------------------------------------------------
    # CARGAR
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # AGREGAR
    # ------------------------------------------------------------------
    def abrir_ventana_agregar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar vehículo")
        ventana.geometry("360x280")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Agregar vehículo")

        contenido = tk.Frame(ventana, bg=CHROME)
        contenido.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(contenido, text="Placa:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(4, 4))
        entrada_placa = tk.Entry(contenido, width=28, font=FUENTE_TEXTO, relief="solid",
                                  highlightbackground=CHROME_LINE, bd=1)
        entrada_placa.pack(fill="x", ipady=4)
        entrada_placa.focus()

        tk.Label(contenido, text="Capacidad:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(14, 4))
        entrada_capacidad = tk.Entry(contenido, width=28, font=FUENTE_TEXTO, relief="solid",
                                      highlightbackground=CHROME_LINE, bd=1)
        entrada_capacidad.pack(fill="x", ipady=4)

        boton_primario(
            contenido, "Guardar",
            lambda: self.guardar_vehiculo(entrada_placa, entrada_capacidad, ventana),
            ancho=16,
        ).pack(pady=(22, 0))

        ventana.bind(
            "<Return>",
            lambda event: self.guardar_vehiculo(entrada_placa, entrada_capacidad, ventana)
        )

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

    # ------------------------------------------------------------------
    # ELIMINAR
    # ------------------------------------------------------------------
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
        ventana.title("Eliminar vehículo")
        ventana.geometry("360x220")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Eliminar vehículo")

        contenido = tk.Frame(ventana, bg=CHROME)
        contenido.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(contenido, text="Ingrese la placa a eliminar:", font=FUENTE_ETIQUETA,
                 fg=INK, bg=CHROME).pack(anchor="w", pady=(4, 4))

        entrada_placa = tk.Entry(contenido, width=28, font=FUENTE_TEXTO, relief="solid",
                                  highlightbackground=CHROME_LINE, bd=1)
        entrada_placa.pack(fill="x", ipady=4)
        entrada_placa.focus()

        boton_primario(
            contenido, "Eliminar",
            lambda: self.eliminar_por_placa(entrada_placa, ventana),
            ancho=16,
        ).pack(pady=(22, 0))

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

    # ------------------------------------------------------------------
    # ACTUALIZAR
    # ------------------------------------------------------------------
    def actualizar(self):
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