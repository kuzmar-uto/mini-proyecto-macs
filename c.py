
from copy import deepcopy
from collections import OrderedDict

import docx


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
        for row in data_rows[n_data_rows:]:
            row._element.getparent().remove(row._element)

    elif n_data_rows > current:

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

# Tabla 

CAMPOS_TABLA_DESPACHO = (
    "cliente", "producto", "cantidad", "agregado",
    "no_envio", "consumo", "devolucion", "remision",
)


def fill_dispatch_table(table, filas):
    set_table_row_count(table, len(filas), header_rows=1)
    for row, fila in zip(table.rows[1:], filas):
        valores = [fila.get(campo, "") for campo in CAMPOS_TABLA_DESPACHO]
        _fill_row(row, valores)



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


def generar_planilla_despacho(filas, plantilla, salida):
    """
    filas: lista de dicts con las llaves de CAMPOS_TABLA_DESPACHO
           (cliente, producto, cantidad, agregado, no_envio, consumo,
           devolucion, remision). Puede tener 1 fila o 100, la tabla se
           ajusta sola.
    plantilla: ruta al .docx original (el formato oficial de la planilla).
    salida: ruta donde guardar el .docx ya diligenciado.
    """
    doc = docx.Document(plantilla)
    tablas = doc.tables 

    tabla_despacho = tablas[0]
    fill_dispatch_table(tabla_despacho, filas)

    for t in tablas[1:]:
        encabezados = [c.text.strip().lower() for c in t.rows[0].cells]
        if encabezados[:2] == ["producto", "cantidad"]:
            fill_resumen_table(t, filas)
            break

    doc.save(salida)
    return salida


if __name__ == "__main__":
    filas_ejemplo = [
        {"cliente": "Panaderia El Trigal", "producto": "Pan tajado",
         "cantidad": 10, "remision": "REM-0456"},
        {"cliente": "Tienda Naturales", "producto": "Arepa",
         "cantidad": 5, "remision": "REM-0457"},
        {"cliente": "Panaderia El Trigal", "producto": "Masa",
         "cantidad": 3, "remision": "REM-0458"},
        {"cliente": "Panaderia El Trigal", "producto": "Masa",
         "cantidad": 3, "remision": "REM-0458"},
        {"cliente": "Tienda Naturales", "producto": "Arepa",
         "cantidad": 5, "remision": "REM-0457"},
        {"cliente": "Panaderia El Trigal", "producto": "Masa",
         "cantidad": 3, "remision": "REM-0458"},
        {  "cliente": "Panaderia El Trigal", "producto": "Masa",
         "cantidad": 3, "remision": "REM-0458"},
         {"cliente": "Tienda Naturales", "producto": "Arepa",
         "cantidad": 5, "remision": "REM-0457"},
         {"cliente": "Panaderia El Trigal", "producto": "Masa",
         "cantidad": 3, "remision": "REM-0458"},
         {"cliente": "Panaderia El Trigal", "producto": "Masa",
         "cantidad": 3, "remision": "REM-0458"},
    ]
    generar_planilla_despacho(
        filas_ejemplo,
        "17092026EYZ9456262F PASTO.docx",
        "planilla_generada_ejemplo.docx",
    )
    print("OK")
