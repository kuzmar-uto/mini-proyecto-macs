
# -*- coding: utf-8 -*-
"""
generar_planilla.py
===================
Genera la PLANILLA DE DESPACHO (.docx) completamente desde cero, con el mismo
diseño de "plantilla_de_ejemplo.docx":

    * Encabezado: logo, título, dirección/teléfono y cuadro NIT / Ruta / N°
    * Campos: Vehículo, Origen, Destino, Conductor y Fecha
    * Tabla principal: CLIENTE | PRODUCTO | CANTIDAD | AGREGADO | NO ENVIO |
                       CONSUMO | DEVOLUCION | REMISION
    * Resumen de productos (suma de cantidades por producto)
    * Control Canasta Bodega
    * Observaciones

Ya NO depende de ninguna plantilla .docx externa: todo el documento se dibuja
con código, así que no puede fallar por un archivo faltante o por el formato
interno de una plantilla.

Dependencia:   pip install python-docx
Archivo opcional (misma carpeta que este .py):   logo_macs.png
"""

import os
from datetime import date, datetime

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, Twips

# ----------------------------------------------------------------------------
# AJUSTES FÁCILES DE CAMBIAR
# ----------------------------------------------------------------------------
NIT_EMPRESA = ""          # Si es siempre el mismo, escríbelo aquí. Ej: "900.123.456-7"
ORIGEN_POR_DEFECTO = ""   # Se usa si el pedido no trae "origen". Ej: "Bodega Los Cristales"
LOGO = "logo_macs.png"    # Se busca junto a este archivo; si no existe, se omite
MINIMO_FILAS = 10         # La plantilla tiene 10 filas; si hay más datos, crece sola

FUENTE = "Arial"
GRIS = "D8D8D8"
ANCHO_UTIL = 11520        # Legal (8.5") menos márgenes de 0.25"  -> en twips (1" = 1440)

TIPOS_CANASTA = ["TIO CAMPO", "MACS", "PANADERAS", "CARRULLERAS", "INTEGRA", "CUBOS", "OTRA"]

# ----------------------------------------------------------------------------
# UTILIDADES DE DATOS
# ----------------------------------------------------------------------------


def _formatear_fecha(valor):
    """'2026-09-17' (o date/datetime) -> '17/09/2026'. Si no se reconoce, lo deja igual."""
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")
    texto = str(valor or "").strip()
    for formato in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(texto, formato).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return texto


def _a_numero(valor):
    """Devuelve float si el valor es numérico, o None si no lo es."""
    try:
        return float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def _texto_numero(numero):
    return str(int(numero)) if float(numero).is_integer() else f"{numero:.2f}".rstrip("0").rstrip(".")


def _texto_cantidad(valor):
    """Muestra la cantidad sin decimales sobrantes (12.0 -> '12'). Texto no numérico se deja tal cual."""
    if valor is None or valor == "":
        return ""
    numero = _a_numero(valor)
    return _texto_numero(numero) if numero is not None else str(valor)


def _resumen_por_producto(filas):
    """Suma las cantidades por producto, respetando el orden de aparición."""
    totales = {}
    for fila in filas:
        producto = str(fila.get("producto", "") or "").strip()
        if not producto:
            continue
        numero = _a_numero(fila.get("cantidad")) or 0
        totales[producto] = totales.get(producto, 0) + numero
    return list(totales.items())


# ----------------------------------------------------------------------------
# UTILIDADES DE FORMATO (XML de Word)
# ----------------------------------------------------------------------------
_ORDEN_TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd",
               "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"]
_ORDEN_TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
                "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
                "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"]


def _hijo(padre, nombre):
    """Obtiene (o crea al final) un hijo w:<nombre>."""
    el = padre.find(qn(f"w:{nombre}"))
    if el is None:
        el = OxmlElement(f"w:{nombre}")
        padre.append(el)
    return el


def _ordenar_hijos(el, orden):
    """Word exige un orden concreto de los hijos de tcPr / tblPr."""
    def clave(h):
        nombre = h.tag.split("}")[1]
        return orden.index(nombre) if nombre in orden else len(orden)
    hijos = sorted(list(el), key=clave)
    for h in hijos:
        el.remove(h)
    for h in hijos:
        el.append(h)


def _bordes_celda(celda, **lados):
    """lados: top/left/bottom/right = tamaño (1/8 pt) o None para sin borde."""
    tc_pr = celda._tc.get_or_add_tcPr()
    bordes = _hijo(tc_pr, "tcBorders")
    for lado, tam in lados.items():
        borde = bordes.find(qn(f"w:{lado}"))
        if borde is None:
            borde = OxmlElement(f"w:{lado}")
            bordes.append(borde)
        if tam is None:
            borde.set(qn("w:val"), "nil")
        else:
            borde.set(qn("w:val"), "single")
            borde.set(qn("w:sz"), str(tam))
            borde.set(qn("w:space"), "0")
            borde.set(qn("w:color"), "000000")


def _sombrear(celda, relleno):
    tc_pr = celda._tc.get_or_add_tcPr()
    sombra = _hijo(tc_pr, "shd")
    sombra.set(qn("w:val"), "clear")
    sombra.set(qn("w:color"), "auto")
    sombra.set(qn("w:fill"), relleno)


def _bordes_tabla(tabla, tam=None):
    """tam=None -> tabla sin bordes; tam=n -> todos los bordes de grosor n."""
    tbl_pr = tabla._tbl.tblPr
    bordes = _hijo(tbl_pr, "tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = bordes.find(qn(f"w:{lado}"))
        if b is None:
            b = OxmlElement(f"w:{lado}")
            bordes.append(b)
        if tam is None:
            b.set(qn("w:val"), "nil")
        else:
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), str(tam))
            b.set(qn("w:space"), "0")
            b.set(qn("w:color"), "000000")


def _configurar_tabla(tabla, anchos, margen_h=60, margen_v=30, sangria=0):
    """Ancho fijo en twips: columnas, celdas y tabla suman exactamente lo mismo."""
    tabla.autofit = False
    tbl_pr = tabla._tbl.tblPr

    ancho_total = _hijo(tbl_pr, "tblW")
    ancho_total.set(qn("w:w"), str(sum(anchos)))
    ancho_total.set(qn("w:type"), "dxa")

    ind = _hijo(tbl_pr, "tblInd")
    ind.set(qn("w:w"), str(sangria))
    ind.set(qn("w:type"), "dxa")

    margenes = _hijo(tbl_pr, "tblCellMar")
    for lado, valor in (("top", margen_v), ("left", margen_h), ("bottom", margen_v), ("right", margen_h)):
        m = margenes.find(qn(f"w:{lado}"))
        if m is None:
            m = OxmlElement(f"w:{lado}")
            margenes.append(m)
        m.set(qn("w:w"), str(valor))
        m.set(qn("w:type"), "dxa")

    for i, ancho in enumerate(anchos):
        tabla.columns[i].width = Twips(ancho)
    for fila in tabla.rows:
        for i, celda in enumerate(fila.cells):
            celda.width = Twips(anchos[i])


def _alto_fila(fila, twips, no_partir=True, repetir=False):
    tr_pr = fila._tr.get_or_add_trPr()
    alto = OxmlElement("w:trHeight")
    alto.set(qn("w:val"), str(twips))
    alto.set(qn("w:hRule"), "atLeast")
    tr_pr.append(alto)
    if no_partir:
        tr_pr.append(OxmlElement("w:cantSplit"))
    if repetir:
        tr_pr.append(OxmlElement("w:tblHeader"))


def _formato_parrafo(p, alinear=None, antes=0, despues=0, izquierda=None, juntar=False):
    pf = p.paragraph_format
    pf.space_before = Pt(antes)
    pf.space_after = Pt(despues)
    pf.line_spacing = 1.0
    if izquierda is not None:
        pf.left_indent = Twips(izquierda)
    if juntar:
        pf.keep_with_next = True
    if alinear is not None:
        p.alignment = alinear


def _marca_parrafo(p, tam):
    """Tamaño de la marca de párrafo: evita que un párrafo vacío agrande la fila."""
    p_pr = p._p.get_or_add_pPr()
    r_pr = OxmlElement("w:rPr")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(tam * 2)))
    r_pr.append(sz)
    p_pr.append(r_pr)


def _agregar_texto(p, texto, tam, negrita=False):
    r = p.add_run(str(texto))
    r.font.name = FUENTE
    r.font.size = Pt(tam)
    r.font.bold = negrita
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    return r


def _escribir(celda, texto, tam=9, negrita=False, alinear=WD_ALIGN_PARAGRAPH.LEFT,
              relleno=None, vertical=WD_CELL_VERTICAL_ALIGNMENT.CENTER):
    """Escribe texto en una celda con formato uniforme."""
    p = celda.paragraphs[0]
    _formato_parrafo(p, alinear)
    if texto not in (None, ""):
        _agregar_texto(p, texto, tam, negrita)
    _marca_parrafo(p, tam)
    celda.vertical_alignment = vertical
    if relleno:
        _sombrear(celda, relleno)


def _espaciador(doc, tam=4):
    p = doc.add_paragraph()
    _formato_parrafo(p)
    _marca_parrafo(p, tam)
    return p


def _tabla_en_celda(celda, filas, columnas):
    """Inserta una tabla anidada y quita el párrafo vacío inicial de la celda."""
    primero = celda.paragraphs[0]
    tabla = celda.add_table(filas, columnas)
    primero._element.getparent().remove(primero._element)
    final = celda.paragraphs[-1]          # párrafo obligatorio después de la tabla
    _formato_parrafo(final)
    _marca_parrafo(final, 1)
    return tabla


# ----------------------------------------------------------------------------
# BLOQUES DEL DOCUMENTO
# ----------------------------------------------------------------------------


def _bloque_encabezado(doc, nit, numero):
    t = doc.add_table(rows=1, cols=3)
    anchos = [1900, 7220, 2400]
    _configurar_tabla(t, anchos, margen_h=0, margen_v=0)
    _bordes_tabla(t, None)
    c_logo, c_titulo, c_caja = t.rows[0].cells

    # --- Logo
    p = c_logo.paragraphs[0]
    _formato_parrafo(p, WD_ALIGN_PARAGRAPH.LEFT)
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO)
    if os.path.exists(ruta_logo):
        p.add_run().add_picture(ruta_logo, width=Inches(0.95))

    # --- Título + dirección
    p = c_titulo.paragraphs[0]
    _formato_parrafo(p, WD_ALIGN_PARAGRAPH.CENTER, antes=4)
    _agregar_texto(p, "PLANILLA DE DESPACHO", 14, negrita=True)
    for linea in ("Direccion: Cra 1 N 8-37 B/ Los Cristales", "Telefono: (8) 2451559"):
        p = c_titulo.add_paragraph()
        _formato_parrafo(p, WD_ALIGN_PARAGRAPH.CENTER)
        _agregar_texto(p, linea, 11)

    # --- Cuadro NIT / Ruta / N°
    caja = _tabla_en_celda(c_caja, 3, 1)
    _configurar_tabla(caja, [2188], margen_h=80, margen_v=30)
    _bordes_tabla(caja, 8)
    _escribir(caja.rows[0].cells[0], f"NIT: {nit}".rstrip(), 12)
    _escribir(caja.rows[1].cells[0], "Ruta", 12, alinear=WD_ALIGN_PARAGRAPH.CENTER, relleno=GRIS)
    _escribir(caja.rows[2].cells[0], f"N° {numero}".rstrip(), 12)
    for fila in caja.rows:
        _alto_fila(fila, 372)
    # La caja se alinea a la derecha de su celda
    jc = _hijo(caja._tbl.tblPr, "jc")
    jc.set(qn("w:val"), "right")


def _bloque_campos(doc, enc):
    """Vehículo / Origen / Destino / Conductor / Fecha como campos con línea inferior."""
    t = doc.add_table(rows=2, cols=6)
    anchos = [1450, 1800, 1000, 2750, 1100, 3420]
    _configurar_tabla(t, anchos, margen_h=50, margen_v=40, sangria=60)
    _bordes_tabla(t, None)

    f1, f2 = t.rows
    etiquetas = [(f1.cells[0], "Vehículo:"), (f1.cells[2], "Origen:"), (f1.cells[4], "Destino:"),
                 (f2.cells[0], "Conductor:"), (f2.cells[4], "Fecha:")]
    valores = [(f1.cells[1], enc["vehiculo"]), (f1.cells[3], enc["origen"]), (f1.cells[5], enc["destino"]),
               (f2.cells[5], enc["fecha"])]

    # Conductor ocupa el ancho de tres columnas (nombres largos)
    conductor = f2.cells[1].merge(f2.cells[3])
    valores.append((conductor, enc["conductor"]))

    for celda, texto in etiquetas:
        _escribir(celda, texto, 11)
    for celda, texto in valores:
        _escribir(celda, texto, 11, negrita=True)
        _bordes_celda(celda, bottom=8)
    for fila in t.rows:
        _alto_fila(fila, 400)


def _bloque_tabla_principal(doc, filas):
    columnas = ["CLIENTE", "PRODUCTO", "CANTIDAD", "AGREGADO", "NO ENVIO", "CONSUMO", "DEVOLUCION", "REMISION"]
    anchos = [2000, 2900, 1000, 1050, 1000, 1050, 1250, 1270]
    total = max(MINIMO_FILAS, len(filas))

    t = doc.add_table(rows=total + 1, cols=len(columnas))
    _configurar_tabla(t, anchos, margen_h=70, margen_v=30)
    _bordes_tabla(t, 8)

    for celda, nombre in zip(t.rows[0].cells, columnas):
        _escribir(celda, nombre, 8, negrita=True, alinear=WD_ALIGN_PARAGRAPH.CENTER, relleno=GRIS)
    _alto_fila(t.rows[0], 380, repetir=True)      # el encabezado se repite si hay más de una hoja

    centro = WD_ALIGN_PARAGRAPH.CENTER
    for i in range(total):
        fila = filas[i] if i < len(filas) else {}
        celdas = t.rows[i + 1].cells
        _escribir(celdas[0], fila.get("cliente", ""), 9)
        _escribir(celdas[1], fila.get("producto", ""), 9)
        _escribir(celdas[2], _texto_cantidad(fila.get("cantidad")), 9, alinear=centro)
        _escribir(celdas[3], "", 9)                                              # AGREGADO (a mano)
        _escribir(celdas[4], _texto_cantidad(fila.get("no_envio")), 9, alinear=centro)
        for j in (5, 6, 7):                                                      # CONSUMO / DEVOLUCION / REMISION
            _escribir(celdas[j], "", 9)
        _alto_fila(t.rows[i + 1], 380)


def _titulo_seccion(doc, texto):
    p = doc.add_paragraph()
    _formato_parrafo(p, antes=8, despues=4, izquierda=185, juntar=True)
    _agregar_texto(p, texto, 14, negrita=True)
    return p


def _tabla_resumen(celda, resumen):
    total = max(MINIMO_FILAS, len(resumen))
    t = _tabla_en_celda(celda, total + 1, 2)
    _configurar_tabla(t, [3468, 1368], margen_h=70, margen_v=25)
    _bordes_tabla(t, 8)
    _escribir(t.rows[0].cells[0], "Producto", 9.5, True, WD_ALIGN_PARAGRAPH.CENTER, GRIS)
    _escribir(t.rows[0].cells[1], "Cantidad", 9.5, True, WD_ALIGN_PARAGRAPH.CENTER, GRIS)
    _alto_fila(t.rows[0], 330)
    for i in range(total):
        producto, cantidad = resumen[i] if i < len(resumen) else ("", None)
        _escribir(t.rows[i + 1].cells[0], producto, 9)
        _escribir(t.rows[i + 1].cells[1], _texto_numero(cantidad) if cantidad is not None else "",
                  9, alinear=WD_ALIGN_PARAGRAPH.CENTER)
        _alto_fila(t.rows[i + 1], 290)


def _tabla_control_canasta(celda):
    t = _tabla_en_celda(celda, 2 + len(TIPOS_CANASTA), 3)
    _configurar_tabla(t, [1448, 1455, 1448], margen_h=70, margen_v=25)
    _bordes_tabla(t, 8)

    titulo = t.rows[0].cells[0].merge(t.rows[0].cells[2])
    _escribir(titulo, "Control Canasta Bodega", 12, True, WD_ALIGN_PARAGRAPH.CENTER, GRIS)
    _alto_fila(t.rows[0], 364)

    for celda_h, texto in zip(t.rows[1].cells, ("Tipo Canasta", "Salida", "Entrada")):
        _escribir(celda_h, texto, 8, True, WD_ALIGN_PARAGRAPH.CENTER, GRIS)
    _alto_fila(t.rows[1], 296)

    for i, tipo in enumerate(TIPOS_CANASTA):
        fila = t.rows[i + 2]
        _escribir(fila.cells[0], tipo, 8)
        _escribir(fila.cells[1], "", 8)
        _escribir(fila.cells[2], "", 8)
        _alto_fila(fila, 288)


def _bloque_resumen_y_canastas(doc, resumen):
    """Resumen (izquierda) y Control Canasta Bodega (derecha), lado a lado."""
    t = doc.add_table(rows=1, cols=4)
    anchos = [4850, 400, 4363, ANCHO_UTIL - 4850 - 400 - 4363]
    _configurar_tabla(t, anchos, margen_h=0, margen_v=0, sangria=190)
    _bordes_tabla(t, None)
    _alto_fila(t.rows[0], 100)
    c_resumen, _, c_canastas, _ = t.rows[0].cells
    for c in t.rows[0].cells:
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    _tabla_resumen(c_resumen, resumen)
    _tabla_control_canasta(c_canastas)
    # Las celdas vacías (separador y margen derecho) también necesitan marca pequeña
    for c in t.rows[0].cells:
        if not c.tables:
            _marca_parrafo(c.paragraphs[0], 1)


def _bloque_observaciones(doc, observaciones):
    _titulo_seccion(doc, "Observaciones:")
    texto = (observaciones or "").strip()
    lineas = texto.splitlines() if texto else [""] * 3      # sin texto: espacio para escribir a mano
    for linea in lineas:
        p = doc.add_paragraph()
        _formato_parrafo(p, izquierda=185, despues=2)
        if linea:
            _agregar_texto(p, linea, 11)
        else:
            _marca_parrafo(p, 14)


# ----------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ----------------------------------------------------------------------------


def generar_planilla_despacho(filas, plantilla, archivo_salida, encabezado=None):
    """
    Crea la planilla de despacho y la guarda en `archivo_salida` (.docx).

    filas       lista de dicts: {"cliente", "producto", "cantidad", "no_envio"}
    plantilla   YA NO SE USA (se conserva para no cambiar las llamadas de pedido.py;
                puede ser None).
    encabezado  dict con: vehiculo, origen, destino, conductor, fecha,
                numero_planilla, numero_ruta, observaciones, nit  (todos opcionales)

    Devuelve la ruta del archivo creado.
    """
    filas = list(filas or [])
    enc = dict(encabezado or {})

    datos = {
        "vehiculo": str(enc.get("vehiculo") or ""),
        "origen": str(enc.get("origen") or ORIGEN_POR_DEFECTO),
        "destino": str(enc.get("destino") or ""),
        "conductor": str(enc.get("conductor") or ""),
        "fecha": _formatear_fecha(enc.get("fecha")),
    }
    nit = str(enc.get("nit") or NIT_EMPRESA)
    # En el cuadro "Ruta N°" va el número de planilla (en planillas por ruta ya es el número de ruta)
    numero = str(enc.get("numero_planilla") or enc.get("numero_ruta") or "")

    doc = Document()

    # --- Página: Legal, márgenes como la plantilla
    seccion = doc.sections[0]
    seccion.page_width = Twips(12240)
    seccion.page_height = Twips(20160)
    seccion.left_margin = seccion.right_margin = Twips(360)
    seccion.top_margin = Twips(460)
    seccion.bottom_margin = Twips(500)
    seccion.header_distance = seccion.footer_distance = Twips(300)

    # --- Estilo base
    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.line_spacing = 1.0

    # --- Contenido
    _bloque_encabezado(doc, nit, numero)
    _espaciador(doc, 6)
    _bloque_campos(doc, datos)
    _espaciador(doc, 6)
    _bloque_tabla_principal(doc, filas)
    _titulo_seccion(doc, "Resumen:")
    _bloque_resumen_y_canastas(doc, _resumen_por_producto(filas))
    _bloque_observaciones(doc, enc.get("observaciones"))

    # --- Orden de elementos exigido por Word (incluye tablas anidadas)
    cuerpo = doc.element.body
    for tc_pr in cuerpo.iter(qn("w:tcPr")):
        _ordenar_hijos(tc_pr, _ORDEN_TCPR)
    for tbl_pr in cuerpo.iter(qn("w:tblPr")):
        _ordenar_hijos(tbl_pr, _ORDEN_TBLPR)

    carpeta = os.path.dirname(os.path.abspath(archivo_salida))
    os.makedirs(carpeta, exist_ok=True)
    doc.save(archivo_salida)
    return archivo_salida


# ----------------------------------------------------------------------------
# PRUEBA RÁPIDA:  python generar_planilla.py
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    ejemplo_filas = [
        {"cliente": "Panadería La Espiga", "producto": "Pan tajado integral 500 g", "cantidad": 24, "no_envio": ""},
        {"cliente": "Panadería La Espiga", "producto": "Mogolla", "cantidad": 40, "no_envio": ""},
        {"cliente": "Tienda Don Pepe", "producto": "Pan tajado integral 500 g", "cantidad": 12, "no_envio": ""},
        {"cliente": "Tienda Don Pepe", "producto": "Almojábana", "cantidad": 30, "no_envio": ""},
    ]
    ejemplo_encabezado = {
        "vehiculo": "EYZ945", "origen": "Bodega Los Cristales", "destino": "Pasto",
        "conductor": "Juan Pérez", "fecha": "2026-09-17", "numero_planilla": 1,
        "observaciones": "Entregar antes de las 8:00 a.m.",
    }
    salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "planilla_prueba.docx")
    print("Planilla creada en:", generar_planilla_despacho(ejemplo_filas, None, salida, ejemplo_encabezado))