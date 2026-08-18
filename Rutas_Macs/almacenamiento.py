"""
================================================================================
 ALMACENAMIENTO - MACS COL
================================================================================

Este módulo se encarga de la base de datos SQLite de MACS COL.

La aplicación utilizará una única base de datos:

    datos/macscol.db

Aquí se crearán las tablas principales del sistema.
================================================================================
"""

import os
import sqlite3


# ==============================================================================
# RUTA DE LA BASE DE DATOS
# ==============================================================================

# Carpeta donde está este archivo almacenamiento.py
CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))

# Carpeta donde guardaremos los datos
CARPETA_DATOS = os.path.join(CARPETA_PROYECTO, "datos")

# Archivo de base de datos
RUTA_BASE_DATOS = os.path.join(CARPETA_DATOS, "macscol.db")


# ==============================================================================
# CONEXIÓN
# ==============================================================================

def obtener_conexion():
    """
    Abre y devuelve una conexión con la base de datos.

    Si la carpeta 'datos' no existe, se crea automáticamente.
    """

    os.makedirs(CARPETA_DATOS, exist_ok=True)

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


# ==============================================================================
# CREAR BASE DE DATOS
# ==============================================================================

def crear_base_datos():
    """
    Crea todas las tablas necesarias para MACS COL.

    Si las tablas ya existen, no se vuelven a crear.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # --------------------------------------------------------------------------
    # TABLA CLIENTES
    # --------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------------------------
    # TABLA PRODUCTOS
    # --------------------------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        embalaje TEXT,
        peso_canastilla REAL,
        descripcion TEXT
        )
    """)

    # --------------------------------------------------------------------------
    # TABLA VEHÍCULOS
    # --------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL UNIQUE,
            capacidad REAL
        )
    """)

    # --------------------------------------------------------------------------
    # TABLA DESTINOS
    # --------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS destinos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
    )
    """)

    # --------------------------------------------------------------------------
    # TABLA CONDUCTORES
    # --------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conductores (
            cedula TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------------------------
    # TABLA PEDIDOS
    # --------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            vehiculo_id INTEGER,
            destino_id INTEGER,
            conductor_cedula TEXT,
            numero_ruta TEXT,
            observaciones TEXT,
            fecha TEXT NOT NULL,

            FOREIGN KEY (cliente_id)
                REFERENCES clientes(id),

            FOREIGN KEY (vehiculo_id)
                REFERENCES vehiculos(id),

            FOREIGN KEY (destino_id)
                REFERENCES destinos(id),

            FOREIGN KEY (conductor_cedula)
                REFERENCES conductores(cedula)
        )
    """)

    # --------------------------------------------------------------------------
    # DETALLE DE PEDIDOS
    # --------------------------------------------------------------------------
    #
    # Un pedido puede contener varios productos.
    #
    # Ejemplo:
    #
    # Pedido 1
    #     ├── Producto A -> 10 unidades
    #     ├── Producto B -> 5 unidades
    #     └── Producto C -> 3 unidades
    #
    # Esta tabla permite guardar cada producto asociado a un pedido.
    # --------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            peso_total REAL,

            FOREIGN KEY (pedido_id)
                REFERENCES pedidos(id)
                ON DELETE CASCADE,

            FOREIGN KEY (producto_id)
                REFERENCES productos(id)
        )
    """)

    # Guardamos los cambios
    conexion.commit()

    # Cerramos la conexión
    conexion.close()


# ==============================================================================
# EJECUCIÓN DIRECTA
# ==============================================================================

if __name__ == "__main__":

    crear_base_datos()

    print("Base de datos creada correctamente.")
    print(f"Ubicación: {RUTA_BASE_DATOS}")
