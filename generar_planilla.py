"""
generar_planilla.py
--------------------
Genera la "Planilla de Despacho" (.docx) de MACS COL a partir de la plantilla
oficial, ajustando automaticamente el numero de filas de las tablas segun la
cantidad de lineas (productos/clientes) que traiga el pedido/ruta.

Uso tipico desde el programa (por ejemplo un boton "Imprimir planilla" en
pedido.py):

    from generar_planilla import generar_planilla_despacho

    filas = [
        {"cliente": "Panaderia El Trigal", "producto": "Pan tajado",
         "cantidad": 10, "agregado": "", "no_envio": "", "consumo": "",
         "devolucion": "", "remision": "REM-0456"},
        {"cliente": "Tienda Naturales", "producto": "Arepa",
         "cantidad": 5, "agregado": "", "no_envio": "", "consumo": "",
         "devolucion": "", "remision": "REM-0457"},
        # ... una fila por cada linea de despacho, sin importar si son 1 o 40
    ]

    generar_planilla_despacho(
        filas=filas,
        plantilla="17092026EYZ9456262F_PASTO.docx",
        salida="planilla_ruta_pasto.docx",
    )

La funcion NO depende de Tkinter ni de sqlite3: recibe listas de diccionarios
ya armadas, para que se pueda conectar facilmente con almacenamiento.py
(basta con hacer el SELECT/JOIN correspondiente y mapear los campos).
"""

from copy import deepcopy
from collections import OrderedDict

import docx
from docx.table import Table
from docx.oxml.ns import qn


# ---------------------------------------------------------------------------
# Utilidad generica: ajustar el numero de filas de datos de cualquier tabla
# ---------------------------------------------------------------------------
def set_table_row_count(table, n_data_rows, header_rows=1):
    """
    Deja la tabla con exactamente `n_data_rows` filas de datos (sin contar
    las `header_rows` filas de encabezado), clonando el formato (bordes,
    anchos, sombreado) de la ultima fila existente. Sirve tanto para achicar
    la tabla (1 producto) como para agrandarla (15, 40, los que sean).
    """
    data_rows = table.rows[header_rows:]
    current = len(data_rows)

    if n_data_rows < current:
        # sobran filas -> se eliminan las de mas, de abajo hacia arriba
        for row in data_rows[n_data_rows:]:
            row._element.getparent().remove(row._element)

    elif n_data_rows > current:
        # faltan filas -> se clona la ultima fila (o el encabezado si la
        # tabla no traia ninguna fila de datos) tantas veces como haga falta
        template_tr = (data_rows[-1]._element if data_rows
                        else table.rows[header_rows - 1]._element)
        for _ in range(n_data_rows - current):
            new_tr = deepcopy(template_tr)
            # limpiar el texto que pudiera traer la fila clonada
            for cell_xml in new_tr.findall(
                ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
            ):
                cell_xml.text = ""
            table._tbl.append(new_tr)

    return table


def _fill_row(row, values):
    for cell, value in zip(row.cells, values):
        cell.text = "" if value is None else str(value)


# ---------------------------------------------------------------------------
# Tabla principal: CLIENTE | PRODUCTO | CANTIDAD | AGREGADO | NO ENVIO |
#                  CONSUMO | DEVOLUCION | REMISION
# ---------------------------------------------------------------------------
CAMPOS_TABLA_DESPACHO = (
    "cliente", "producto", "cantidad", "agregado",
    "no_envio", "consumo", "devolucion", "remision",
)


def fill_dispatch_table(table, filas):
    set_table_row_count(table, len(filas), header_rows=1)
    for row, fila in zip(table.rows[1:], filas):
        valores = [fila.get(campo, "") for campo in CAMPOS_TABLA_DESPACHO]
        _fill_row(row, valores)


# ---------------------------------------------------------------------------
# Tabla "Resumen": Producto | Cantidad (total despachado por producto)
# ---------------------------------------------------------------------------
def fill_resumen_table(table, filas):
    totales = OrderedDict()
    for fila in filas:
        producto = fila.get("producto", "")
        cantidad = fila.get("cantidad", 0) or 0
        try:
            cantidad = float(cantidad)
        except (TypeError, ValueError):
            cantidad = 0
        totales[producto] = totales.get(producto, 0) + cantidad

    set_table_row_count(table, max(len(totales), 1), header_rows=1)
    for row, (producto, total) in zip(table.rows[1:], totales.items()):
        total_str = str(int(total)) if float(total).is_integer() else str(total)
        _fill_row(row, [producto, total_str])


# ---------------------------------------------------------------------------
# La plantilla oficial esta armada con cuadros de texto flotantes (no todo
# son tablas normales del cuerpo del documento). python-docx solo expone
# `document.tables` para las tablas que cuelgan directo del body, asi que
# para llegar a las que estan dentro de los cuadros de texto (NIT/Ruta/N°,
# Resumen) hay que recorrer TODO el XML buscando cualquier <w:tbl>, sin
# importar que tan anidado este.
# ---------------------------------------------------------------------------
def _todas_las_tablas(doc):
    return [Table(tbl_el, doc) for tbl_el in doc.element.body.iter(qn("w:tbl"))]


def _fill_resumen_tables_flotantes(doc, filas):
    """La tabla 'Producto/Cantidad' esta duplicada (una copia para Word
    nuevo y otra de compatibilidad para Word viejo, invisibles entre si);
    se llenan las dos para que se vea igual sin importar la version."""
    encontrada = False
    for t in _todas_las_tablas(doc):
        encabezados = [c.text.strip().lower() for c in t.rows[0].cells]
        if encabezados[:2] == ["producto", "cantidad"]:
            fill_resumen_table(t, filas)
            encontrada = True
    return encontrada


def _fill_caja_nit_ruta(doc, numero_ruta, numero_planilla):
    """Caja NIT / Ruta / N° (arriba a la derecha). Tambien duplicada."""
    for t in _todas_las_tablas(doc):
        if len(t.rows) == 3 and len(t.columns) == 1 and \
                t.rows[0].cells[0].text.strip().upper().startswith("NIT"):
            if numero_ruta:
                t.rows[1].cells[0].text = f"Ruta {numero_ruta}"
            if numero_planilla:
                t.rows[2].cells[0].text = f"N°  {numero_planilla}"


# ---------------------------------------------------------------------------
# Encabezado de texto libre: "Vehiculo: ___ Origen: ___ Destino: ___
# Conductor: ___ Fecha: ___". Son runs dentro de un mismo parrafo (no
# celdas de tabla), asi que se ubica cada etiqueta y se escribe en el
# siguiente run subrayado (el espacio en blanco pensado para llenar a mano).
# ---------------------------------------------------------------------------
def _fill_encabezado_texto(doc, valores):
    """
    valores: dict con llaves entre "Vehiculo", "Origen", "Destino",
    "Conductor", "Fecha" (las que no vengan se dejan en blanco).
    """
    etiquetas = ("Vehiculo", "Origen", "Destino", "Conductor", "Fecha")
    for p in doc.paragraphs:
        runs = p.runs
        if not any(r.text.strip().rstrip(":") in etiquetas for r in runs):
            continue
        i = 0
        while i < len(runs):
            texto = runs[i].text.strip().rstrip(":")
            if texto in etiquetas and texto in valores and valores[texto]:
                for j in range(i + 1, len(runs)):
                    if runs[j].underline:
                        runs[j].text = " " + str(valores[texto])
                        break
            i += 1


# ---------------------------------------------------------------------------
# Orquestador
# ---------------------------------------------------------------------------
def generar_planilla_despacho(filas, plantilla, salida, encabezado=None):
    """
    filas: lista de dicts con las llaves de CAMPOS_TABLA_DESPACHO
           (cliente, producto, cantidad, agregado, no_envio, consumo,
           devolucion, remision). Puede tener 1 fila o 100, la tabla se
           ajusta sola.
    plantilla: ruta al .docx original (el formato oficial de la planilla).
    salida: ruta donde guardar el .docx ya diligenciado.
    encabezado: dict opcional con "vehiculo", "origen", "destino",
           "conductor", "fecha", "numero_ruta", "numero_planilla" para
           llenar tambien la parte superior del formato.
    """
    doc = docx.Document(plantilla)

    fill_dispatch_table(doc.tables[0], filas)
    _fill_resumen_tables_flotantes(doc, filas)

    if encabezado:
        _fill_caja_nit_ruta(
            doc,
            encabezado.get("numero_ruta"),
            encabezado.get("numero_planilla"),
        )
        _fill_encabezado_texto(doc, {
            "Vehiculo": encabezado.get("vehiculo", ""),
            "Origen": encabezado.get("origen", ""),
            "Destino": encabezado.get("destino", ""),
            "Conductor": encabezado.get("conductor", ""),
            "Fecha": encabezado.get("fecha", ""),
        })

    doc.save(salida)
    return salida


if __name__ == "__main__":
    # Ejemplo minimo de verificacion manual
    filas_ejemplo = [
        {"cliente": "Panaderia El Trigal", "producto": "Pan tajado",
         "cantidad": 10, "remision": "REM-0456"},
        {"cliente": "Tienda Naturales", "producto": "Arepa",
         "cantidad": 5, "remision": "REM-0457"},
        {"cliente": "Panaderia El Trigal", "producto": "Masa",
         "cantidad": 3, "remision": "REM-0458"},
    ]
    generar_planilla_despacho(
        filas_ejemplo,
        "17092026EYZ9456262F_PASTO.docx",
        "planilla_generada_ejemplo.docx",
    )
    print("OK")
