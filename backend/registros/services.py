import datetime

from django.conf import settings


def version_cie_por_fecha(fecha_evento):
    if fecha_evento is None:
        return "CIE11"
    if isinstance(fecha_evento, str):
        fecha_evento = datetime.date.fromisoformat(fecha_evento)
    return "CIE10" if fecha_evento < settings.FECHA_CORTE_CIE11 else "CIE11"


def validar_seleccion_cie(version, cie10, cie11, fecha_evento):
    errores = {}
    version_esperada = version_cie_por_fecha(fecha_evento)
    if version != version_esperada:
        errores["version_cie"] = f"La fecha del evento exige la versión {version_esperada}."
    if version == "CIE10":
        if not cie10:
            errores["cie10"] = "Código CIE-10 obligatorio para eventos históricos."
        if cie11:
            errores["cie11"] = "No usar CIE-11 en eventos anteriores a la fecha de corte."
    if version == "CIE11":
        if not cie11:
            errores["cie11"] = "Código CIE-11 obligatorio para eventos actuales."
        elif getattr(cie11, "nivel", None) and cie11.requiere_subgrupo and cie11.nivel == 3:
            errores["cie11"] = "Esta categoría CIE-11 exige seleccionar un subgrupo obligatorio."
        if cie10 and version == "CIE11":
            errores["cie10"] = "Use el catálogo CIE-11 para este evento."
    return errores