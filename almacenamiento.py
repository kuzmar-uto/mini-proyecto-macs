"""
================================================================================
 ALMACENAMIENTO - MACS COL
================================================================================
"""

import os
import sqlite3


CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))

CARPETA_DATOS = os.path.join(CARPETA_PROYECTO, "datos")

RUTA_BASE_DATOS = os.path.join(CARPETA_DATOS, "macscol.db")


def obtener_conexion():
    """
    Abre y devuelve una conexión con la base de datos.

    Si la carpeta 'datos' no existe, se crea automáticamente.
    """

    os.makedirs(CARPETA_DATOS, exist_ok=True)

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


def crear_base_datos():
    """
    Crea todas las tablas necesarias para MACS COL.

    Si las tablas ya existen, no se vuelven a crear.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)


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
# DATOS PARA LA PLANILLA DE DESPACHO (por numero de ruta)
# ==============================================================================

def obtener_datos_planilla(numero_ruta):
    """
    Reune todo lo necesario para imprimir la Planilla de Despacho de una
    ruta: puede incluir varios pedidos (uno por cliente) que compartan el
    mismo numero_ruta, tal como el formato fisico (una fila por cliente).

    Devuelve (encabezado: dict, filas: list[dict]).
    `filas` trae una linea por cada producto de cada pedido de la ruta,
    lista para pasarle directo a c.generar_planilla_despacho().
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    registros = cursor.execute("""
        SELECT
            clientes.nombre,
            productos.nombre,
            detalle_pedido.cantidad,
            pedidos.id,
            vehiculos.placa,
            destinos.nombre,
            conductores.nombre,
            pedidos.fecha
        FROM pedidos
        JOIN clientes ON clientes.id = pedidos.cliente_id
        JOIN detalle_pedido ON detalle_pedido.pedido_id = pedidos.id
        JOIN productos ON productos.id = detalle_pedido.producto_id
        LEFT JOIN vehiculos ON vehiculos.id = pedidos.vehiculo_id
        LEFT JOIN destinos ON destinos.id = pedidos.destino_id
        LEFT JOIN conductores ON conductores.cedula = pedidos.conductor_cedula
        WHERE pedidos.numero_ruta = ?
        ORDER BY pedidos.id, detalle_pedido.id
    """, (numero_ruta,)).fetchall()

    conexion.close()

    encabezado = {
        "numero_ruta": numero_ruta,
        "vehiculo": "", "destino": "", "conductor": "", "fecha": "",
    }
    filas = []

    for nombre_cliente, nombre_producto, cantidad, pedido_id, placa, \
            nombre_destino, nombre_conductor, fecha in registros:
        filas.append({
            "cliente": nombre_cliente,
            "producto": nombre_producto,
            "cantidad": cantidad,
            "remision": pedido_id,
        })
        # el encabezado se llena con el primer registro que traiga cada dato
        if not encabezado["vehiculo"] and placa:
            encabezado["vehiculo"] = placa
        if not encabezado["destino"] and nombre_destino:
            encabezado["destino"] = nombre_destino
        if not encabezado["conductor"] and nombre_conductor:
            encabezado["conductor"] = nombre_conductor
        if not encabezado["fecha"] and fecha:
            encabezado["fecha"] = fecha

    return encabezado, filas


# ==============================================================================
# EJECUCIÓN DIRECTA
# ==============================================================================

if __name__ == "__main__":

    crear_base_datos()

    print("Base de datos creada correctamente.")
    print(f"Ubicación: {RUTA_BASE_DATOS}")
