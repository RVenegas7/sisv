#!/usr/bin/env python3
"""Genera la plantilla Excel para pedir la lista oficial de registros civiles.

Acompaña a `docs/requerimiento-registros-civiles.md`: es el archivo que se envía a
la oficina para que lo llene. Tiene cuatro hojas: «Instrucciones» y las tres de
datos (Registros civiles, Registradores, Designaciones), con el encabezado en la
fila 1 y los campos obligatorios marcados con « *».

No usa dependencias: arma el `.xlsx` con la librería estándar (zipfile + XML), así
que corre con el propio `.venv` del proyecto.

Uso:

    ./.venv/bin/python migracion/plantilla_registros_civiles.py [salida.xlsx]

El importador (cuando llegue la lista) lee las hojas **por nombre** y las columnas
**por encabezado**, así que el orden de las columnas puede cambiar y las columnas
de más se ignoran.
"""

import os
import sys
import zipfile

DESTINO_POR_DEFECTO = os.path.join("docs", "plantillas", "registros_civiles_plantilla.xlsx")

# (título de la columna, ancho en caracteres)
CIVILES = [
    ("Nombre del registro civil *", 40),
    ("Estado *", 14),
    ("Municipio *", 18),
    ("Parroquia *", 22),
    ("Centro de salud adscrito", 32),
    ("Activo *", 10),
    ("Observaciones", 44),
]

REGISTRADORES = [
    ("Nacionalidad *", 13),
    ("Cédula *", 13),
    ("Nombres *", 26),
    ("Apellidos *", 26),
    ("Teléfono", 16),
    ("Correo", 28),
    ("Activo *", 10),
    ("Observaciones", 40),
]

DESIGNACIONES = [
    ("Registro civil *", 40),
    ("Nacionalidad del registrador *", 22),
    ("Cédula del registrador *", 18),
    ("Cargo *", 13),
    ("Vigente desde *", 15),
    ("Vigente hasta", 15),
    ("Fecha de toma de posesión", 20),
    ("Acta / nombramiento", 22),
    ("Observaciones", 36),
]

# Fila de encabezado solamente: cualquier fila de ejemplo se importaría como dato.
# Las listas desplegables van por índice de columna (0 = A).
HOJAS_DATOS = [
    ("1-Registros civiles", CIVILES, [(5, ["Sí", "No"])]),
    ("2-Registradores", REGISTRADORES, [(0, ["V", "E", "P", "I", "O"]), (6, ["Sí", "No"])]),
    (
        "3-Designaciones",
        DESIGNACIONES,
        [(1, ["V", "E", "P", "I", "O"]), (3, ["TITULAR", "SUPLENTE", "ENCARGADO"])],
    ),
]

INSTRUCCIONES = [
    ["Plantilla para la lista oficial de registros civiles y registradores"],
    [],
    ["Qué se pide: la lista de las oficinas de registro civil del estado Lara, con los"],
    ["registradores que han estado a su cargo y desde/hasta cuándo. Con eso SISV puede"],
    ["responder «¿quién firmaba este certificado?» en cualquier fecha."],
    [],
    ["Cómo llenarla"],
    ["1. Una fila por registro. No borre ni mueva la fila 1 (el encabezado)."],
    ["2. Los campos con « *» son obligatorios; el resto se puede dejar vacío."],
    ["3. Fechas en AAAA-MM-DD (por ejemplo 2019-03-15). Si ya las tiene en otro formato,"],
    ["   déjelas como están y avise: aquí se convierten."],
    ["4. Cédula: solo los números, sin puntos ni la letra (ejemplo: 7449239)."],
    ["5. Activo: Sí o No. Una oficina o un registrador que ya no ejerce va con No,"],
    ["   para no perder el historial."],
    ["6. Si una hoja no aplica a su caso, déjela con el encabezado y nada más."],
    ["7. No agregue filas de totales ni de títulos intermedios."],
    [],
    ["Las tres hojas"],
    ["Hoja 1 — Registros civiles: las oficinas. «Centro de salud adscrito» es opcional:"],
    ["   solo si la oficina depende de un hospital, ambulatorio o CDI."],
    ["Hoja 2 — Registradores: las personas (jueces/registradores civiles), con su cédula."],
    ["   Se puede repetir una persona en varios registros civiles: eso se ve en la hoja 3."],
    ["Hoja 3 — Designaciones: quién estuvo en qué oficina y cuándo. Una fila por periodo."],
    ["   «Vigente hasta» vacío significa «sigue en el cargo». Si el mismo registrador tuvo"],
    ["   dos periodos separados, van dos filas. Titular y suplente pueden coincidir en fechas."],
    [],
    ["Ejemplo (solo ilustrativo, no lo copie a las hojas de datos)"],
    ["1-Registros civiles: Registro Civil Parroquia Concepción | Lara | Iribarren | Concepción | Hospital Central de Barquisimeto | Sí |"],
    ["2-Registradores:    V | 7449239 | NELIDA | ESPINOZA | 0251-1234567 | | Sí |"],
    ["3-Designaciones:    Registro Civil Parroquia Concepción | V | 7449239 | TITULAR | 2015-04-01 | | 2015-03-27 | Acta 12-2015 |"],
    [],
    ["Qué NO hace falta enviar"],
    ["Los certificados, las planillas ni las actas escaneadas: solo el listado."],
    [],
    ["Cómo devolverla"],
    ["Devuélvala en Excel (.xlsx) con el mismo nombre de hojas. Si ya tiene la lista en"],
    ["otro formato (Word, PDF, tablas sueltas), mándela igual: aquí se adapta."],
    [],
    ["Alcance esperado del estado Lara: 9 municipios y 57 parroquias (una oficina por"],
    ["parroquia, como mínimo). Si una parroquia no tiene registro civil, indíquelo."],
]

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"


def _letra(indice):
    """0 → A, 25 → Z, 26 → AA."""
    letras = ""
    indice += 1
    while indice:
        indice, resto = divmod(indice - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def _escapar(valor):
    return (
        str(valor)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _fila_xml(numero, valores, estilo=None):
    celdas = []
    for columna, valor in enumerate(valores):
        if valor is None or valor == "":
            continue
        formato = f' s="{estilo}"' if estilo is not None else ""
        celdas.append(
            f'<c r="{_letra(columna)}{numero}" t="inlineStr"{formato}>'
            f'<is><t xml:space="preserve">{_escapar(valor)}</t></is></c>'
        )
    return f'<row r="{numero}">' + "".join(celdas) + "</row>"


def _validacion(columna, opciones, hasta=1000):
    letra = _letra(columna)
    valores = ",".join(opciones)
    return (
        '<dataValidation type="list" allowBlank="1" showInputMessage="1" '
        'showErrorMessage="1" errorTitle="Valor no válido" '
        f'error="Elija uno de: {valores}." sqref="{letra}2:{letra}{hasta}">'
        f"<formula1>\"{valores}\"</formula1></dataValidation>"
    )


def _hoja(columnas, filas, estilo_fila1=1, validaciones=()):
    partes = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<worksheet xmlns="{NS_MAIN}">',
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        "</sheetView></sheetViews>",
        "<cols>",
    ]
    for indice, (_, ancho) in enumerate(columnas):
        partes.append(
            f'<col min="{indice + 1}" max="{indice + 1}" width="{ancho}" customWidth="1"/>'
        )
    partes.append("</cols><sheetData>")
    for numero, valores in enumerate(filas, start=1):
        partes.append(_fila_xml(numero, valores, estilo=estilo_fila1 if numero == 1 else None))
    partes.append("</sheetData>")
    if validaciones:
        partes.append(f'<dataValidations count="{len(validaciones)}">')
        partes.extend(_validacion(columna, opciones) for columna, opciones in validaciones)
        partes.append("</dataValidations>")
    partes.append("</worksheet>")
    return "".join(partes)


def _contenido_types(total_hojas):
    partes = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<Types xmlns="{NS_CT}">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    for numero in range(1, total_hojas + 1):
        partes.append(
            f'<Override PartName="/xl/worksheets/sheet{numero}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    partes.append("</Types>")
    return "".join(partes)


def _workbook(nombres):
    partes = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<workbook xmlns="{NS_MAIN}" xmlns:r="{NS_REL}"><sheets>',
    ]
    for indice, nombre in enumerate(nombres, start=1):
        partes.append(
            f'<sheet name="{_escapar(nombre)}" sheetId="{indice}" r:id="rId{indice}"/>'
        )
    partes.append("</sheets></workbook>")
    return "".join(partes)


def _rels_workbook(total_hojas):
    partes = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<Relationships xmlns="{NS_PKG}">',
    ]
    for numero in range(1, total_hojas + 1):
        partes.append(
            f'<Relationship Id="rId{numero}" Type="{NS_REL}/worksheet" '
            f'Target="worksheets/sheet{numero}.xml"/>'
        )
    partes.append(
        f'<Relationship Id="rId{total_hojas + 1}" Type="{NS_REL}/styles" Target="styles.xml"/>'
    )
    partes.append("</Relationships>")
    return "".join(partes)


RELS_RAIZ = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f'<Relationships xmlns="{NS_PKG}">'
    f'<Relationship Id="rId1" Type="{NS_REL}/officeDocument" Target="xl/workbook.xml"/>'
    "</Relationships>"
)

ESTILOS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f'<styleSheet xmlns="{NS_MAIN}">'
    '<fonts count="2">'
    '<font><sz val="11"/><color theme="1"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><color theme="1"/><name val="Calibri"/></font>'
    "</fonts>"
    '<fills count="2"><fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill></fills>'
    '<borders count="1"><border/></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="2">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    "</cellXfs>"
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    "</styleSheet>"
)


def construir(destino):
    """Escribe el .xlsx en `destino` y devuelve la ruta."""
    hojas = [
        # Instrucciones primero: es lo que se ve al abrir el archivo.
        ("Instrucciones", [("Texto", 100)], INSTRUCCIONES, ()),
    ]
    for nombre, columnas, validaciones in HOJAS_DATOS:
        # Solo la fila de encabezado: una fila de ejemplo se importaría como dato.
        encabezado = [[titulo for titulo, _ in columnas]]
        hojas.append((nombre, columnas, encabezado, validaciones))

    carpeta = os.path.dirname(destino)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _contenido_types(len(hojas)))
        z.writestr("_rels/.rels", RELS_RAIZ)
        z.writestr("xl/workbook.xml", _workbook([h[0] for h in hojas]))
        z.writestr("xl/_rels/workbook.xml.rels", _rels_workbook(len(hojas)))
        z.writestr("xl/styles.xml", ESTILOS)
        for numero, (_nombre, columnas, filas, validaciones) in enumerate(hojas, start=1):
            z.writestr(
                f"xl/worksheets/sheet{numero}.xml",
                _hoja(columnas, filas, validaciones=validaciones),
            )
    return destino


def main(argv):
    destino = argv[1] if len(argv) > 1 else DESTINO_POR_DEFECTO
    ruta = construir(destino)
    print(f"Plantilla escrita en {ruta}")
    print("Hojas: " + ", ".join([h[0] for h in HOJAS_DATOS]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
