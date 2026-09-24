"""
================================================================================
 CONDUCTORES - MACS COL
================================================================================

Este mÃ³dulo gestiona los conductores de MACS COL, con el mismo diseÃ±o
"software de escritorio" (mockup: macscol_app_menu_escritorio.html) que usan
Principal y las demÃ¡s ventanas de la aplicaciÃ³n. Los colores, fuentes y
helpers viven en estilo.py.

Los datos se almacenan de forma permanente en SQLite mediante:
    almacenamiento.py

La informaciÃ³n se guarda en:
    datos/macscol.db

Funciones principales:
    - Cargar conductores desde la base de datos.
    - Agregar nuevos conductores.
    - Eliminar conductores.
    - Eliminar por cÃ©dula.
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
# VENTANA CONDUCTORES
# ==============================================================================

class VentanaConductor(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Conductores")
        self.geometry("820x580")
        self.resizable(True, True)
        self.configure(bg=CHROME)

        self.crear_componentes()
        self.cargar_conductores()

    # ==========================================================================
    # CREAR COMPONENTES
    # ==========================================================================

    def crear_componentes(self):
        barra_titulo_ventana(self, "Conductores")

        cuerpo = tk.Frame(self, bg=CHROME)
        cuerpo.pack(fill="both", expand=True, padx=24, pady=18)

        encabezado = tk.Frame(cuerpo, bg=CHROME)
        encabezado.pack(fill="x", pady=(0, 12))
        tk.Label(encabezado, text="Conductores registrados", font=FUENTE_SUBTITULO,
                 fg=INK, bg=CHROME).pack(side="left")
        tk.Label(encabezado, text="Principal â€º Conductores", font=("Segoe UI", 9),
                 fg=GRAY, bg=CHROME).pack(side="right")

        # ---- Tarjeta con la tabla ----
        tarjeta = tk.Frame(cuerpo, bg=WHITE, highlightbackground=CHROME_LINE,
                            highlightthickness=1)
        tarjeta.pack(fill="both", expand=True)

        frame_tabla = tk.Frame(tarjeta, bg=WHITE)
        frame_tabla.pack(fill="both", expand=True, padx=12, pady=12)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        estilo_tabla = configurar_estilo_treeview("Conductores.Treeview")
        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=("cedula", "nombre", "telefono"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15,
            style=estilo_tabla,
        )

        self.tabla.heading("cedula", text="CÃ©dula")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("telefono", text="TelÃ©fono")

        self.tabla.column("cedula", width=180, anchor="center")
        self.tabla.column("nombre", width=320, anchor="center")
        self.tabla.column("telefono", width=180, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tabla.yview)

        # ---- Barra de acciones ----
        botones = tk.Frame(cuerpo, bg=CHROME)
        botones.pack(fill="x", pady=(14, 0))

        boton_primario(botones, "âž•  Agregar", self.abrir_ventana_agregar, ancho=14).pack(
            side="left", padx=(0, 10)
        )
        boton_secundario(botones, "ðŸ—‘  Eliminar", self.eliminar, ancho=14).pack(
            side="left", padx=(0, 10)
        )
        boton_secundario(botones, "ðŸ”„  Actualizar", self.actualizar, ancho=14).pack(
            side="left"
        )

    # ==========================================================================
    # CARGAR CONDUCTORES
    # ==========================================================================

    def cargar_conductores(self):
        """
        Carga todos los conductores almacenados en SQLite
        y los muestra en el Treeview.
        """
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT cedula, nombre, telefono
                FROM conductores
                ORDER BY nombre
            """)

            conductores = cursor.fetchall()
            conexion.close()

            for conductor in conductores:
                self.tabla.insert(
                    "", "end",
                    values=(conductor[0], conductor[1], conductor[2])
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
        ventana.geometry("380x380")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Agregar conductor")

        contenido = tk.Frame(ventana, bg=CHROME)
        contenido.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(contenido, text="CÃ©dula:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(4, 4))
        entrada_cedula = tk.Entry(contenido, width=30, font=FUENTE_TEXTO, relief="solid",
                                   highlightbackground=CHROME_LINE, bd=1)
        entrada_cedula.pack(fill="x", ipady=4)
        entrada_cedula.focus()

        tk.Label(contenido, text="Nombre:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(12, 4))
        entrada_nombre = tk.Entry(contenido, width=30, font=FUENTE_TEXTO, relief="solid",
                                   highlightbackground=CHROME_LINE, bd=1)
        entrada_nombre.pack(fill="x", ipady=4)

        tk.Label(contenido, text="TelÃ©fono:", font=FUENTE_ETIQUETA, fg=INK,
                 bg=CHROME).pack(anchor="w", pady=(12, 4))
        entrada_telefono = tk.Entry(contenido, width=30, font=FUENTE_TEXTO, relief="solid",
                                     highlightbackground=CHROME_LINE, bd=1)
        entrada_telefono.pack(fill="x", ipady=4)

        boton_primario(
            contenido, "Guardar",
            lambda: self.guardar_conductor(
                entrada_cedula, entrada_nombre, entrada_telefono, ventana
            ),
            ancho=16,
        ).pack(pady=(22, 0))

        ventana.bind(
            "<Return>",
            lambda event: self.guardar_conductor(
                entrada_cedula, entrada_nombre, entrada_telefono, ventana
            )
        )

    # ==========================================================================
    # GUARDAR CONDUCTOR
    # ==========================================================================

    def guardar_conductor(self, entrada_cedula, entrada_nombre, entrada_telefono, ventana):
        """
        Guarda un nuevo conductor en SQLite.
        """
        cedula = entrada_cedula.get().strip()
        nombre = entrada_nombre.get().strip()
        telefono = entrada_telefono.get().strip()

        if not cedula or not nombre or not telefono:
            messagebox.showwarning(
                "Conductor",
                "Debes llenar la cÃ©dula, el nombre y el telÃ©fono."
            )
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO conductores (cedula, nombre, telefono)
                VALUES (?, ?, ?)
                """,
                (cedula, nombre, telefono)
            )

            conexion.commit()
            conexion.close()

            self.cargar_conductores()
            ventana.destroy()

            messagebox.showinfo(
                "Conductor",
                "Conductor guardado correctamente."
            )

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showwarning(
                    "Conductor",
                    f"Ya existe un conductor con la cÃ©dula '{cedula}'."
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
        seleccionado = self.tabla.selection()

        if seleccionado:
            fila = seleccionado[0]
            valores = self.tabla.item(fila, "values")

            if not valores:
                return

            cedula = str(valores[0])
            nombre = str(valores[1])

            confirmar = messagebox.askyesno(
                "Eliminar conductor",
                f"Â¿Seguro que deseas eliminar al conductor:\n\n"
                f"{nombre}\n"
                f"CÃ©dula: {cedula}?"
            )

            if not confirmar:
                return

            self.eliminar_conductor_por_cedula(cedula)
            return

        # Si no hay selecciÃ³n, abrir ventana para buscar por cÃ©dula
        self.abrir_ventana_eliminar_por_cedula()

    # ==========================================================================
    # VENTANA ELIMINAR POR CÃ‰DULA
    # ==========================================================================

    def abrir_ventana_eliminar_por_cedula(self):
        ventana = tk.Toplevel(self)
        ventana.title("Eliminar conductor")
        ventana.geometry("360x220")
        ventana.resizable(False, False)
        ventana.configure(bg=CHROME)
        barra_titulo_ventana(ventana, "Eliminar conductor")

        contenido = tk.Frame(ventana, bg=CHROME)
        contenido.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(contenido, text="Ingrese la cÃ©dula a eliminar:", font=FUENTE_ETIQUETA,
                 fg=INK, bg=CHROME).pack(anchor="w", pady=(4, 4))

        entrada_cedula = tk.Entry(contenido, width=28, font=FUENTE_TEXTO, relief="solid",
                                   highlightbackground=CHROME_LINE, bd=1)
        entrada_cedula.pack(fill="x", ipady=4)
        entrada_cedula.focus()

        boton_primario(
            contenido, "Eliminar",
            lambda: self.eliminar_por_cedula(entrada_cedula, ventana),
            ancho=16,
        ).pack(pady=(22, 0))

        ventana.bind(
            "<Return>",
            lambda event: self.eliminar_por_cedula(entrada_cedula, ventana)
        )

    # ==========================================================================
    # ELIMINAR POR CÃ‰DULA
    # ==========================================================================

    def eliminar_por_cedula(self, entrada_cedula, ventana):
        """
        Busca un conductor por su cÃ©dula y lo elimina de SQLite.
        """
        cedula_buscada = entrada_cedula.get().strip()

        if not cedula_buscada:
            messagebox.showwarning(
                "Conductor",
                "Debe escribir una cÃ©dula."
            )
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("DELETE FROM conductores WHERE cedula = ?", (cedula_buscada,))
            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:
                messagebox.showwarning(
                    "Conductor",
                    f"No se encontrÃ³ ningÃºn conductor con la cÃ©dula '{cedula_buscada}'."
                )
                return

            self.cargar_conductores()
            ventana.destroy()

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
    # ELIMINAR CONDUCTOR POR CÃ‰DULA
    # ==========================================================================

    def eliminar_conductor_por_cedula(self, cedula):
        """
        Elimina directamente un conductor utilizando su cÃ©dula.
        """
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("DELETE FROM conductores WHERE cedula = ?", (cedula,))
            filas_eliminadas = cursor.rowcount

            conexion.commit()
            conexion.close()

            if filas_eliminadas == 0:
                messagebox.showwarning(
                    "Conductor",
                    f"No se encontrÃ³ ningÃºn conductor con la cÃ©dula '{cedula}'."
                )
                return

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
# EJECUCIÃ“N DIRECTA
# ==============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    VentanaConductor(root)

    root.mainloop()