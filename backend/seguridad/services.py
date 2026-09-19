from seguridad.models import Organizacion, Perfil


def rol_de(user):
    """Rol del perfil del usuario (None si no tiene perfil)."""
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    perfil = getattr(user, "perfil", None)
    return perfil.rol if perfil else None


def permisos_de(user):
    """Permisos finos por acción según el rol. El superusuario siempre tiene todo."""
    es_super = bool(user) and bool(getattr(user, "is_superuser", False))
    rol = rol_de(user)
    escribir = es_super or rol in ("TRANSCRIPTOR", "CODIFICADOR", "DIRECTOR")
    return {
        # Rol (para UI): quién puede crear/editar registros
        "puede_escribir": escribir,
        "puede_editar": escribir,
        "puede_eliminar": es_super or rol == "DIRECTOR",
        "puede_configurar": es_super or rol == "DIRECTOR",
    }


def perfil_de(user):
    """Serializa el usuario + su perfil (rol y organización) para la API."""
    perfil = getattr(user, "perfil", None)
    org = None
    if perfil is not None and perfil.organizacion_id:
        o = perfil.organizacion
        org = {
            "id": o.id,
            "codigo": o.codigo,
            "nombre": o.nombre,
            "nivel": o.nivel,
            "nivel_label": o.get_nivel_display(),
            "estado": o.estado,
            "municipio": o.municipio,
        }
    return {
        "id": user.id,
        "username": user.username,
        "nombre": user.get_full_name() or user.username,
        "rol": perfil.rol if perfil else None,
        "rol_label": perfil.get_rol_display() if perfil else None,
        "es_superusuario": bool(getattr(user, "is_superuser", False)),
        "organizacion": org,
        "permisos": permisos_de(user),
    }


def alcance_registros(user):
    """Alcance de datos según el perfil.

    Retorna:
      - "TODOS": Ministerio / Gobernación / sin organización → ve todo.
      - {"tipo": "CENTRO", "organizacion_id": id}: solo su centro y carga fija a él.
      - {"tipo": "REGIONAL", "estado": "Lara"}: ve el estado; puede cargar a cualquier centro.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return "TODOS"
    perfil = getattr(user, "perfil", None)
    if perfil is None or perfil.organizacion_id is None:
        return "TODOS"
    org = perfil.organizacion
    if org.nivel == Organizacion.NIVEL_CENTRO:
        return {"tipo": "CENTRO", "organizacion_id": org.id}
    if org.nivel == Organizacion.NIVEL_REGIONAL:
        return {"tipo": "REGIONAL", "estado": org.estado or ""}
    return "TODOS"


def organizacion_por_defecto(user, payload):
    """ID de organización para un registro nuevo.

    - Centro: se fuerza el centro del usuario (ignora lo enviado).
    - Otros: usa el `organizacion` del payload (centro elegido) o su propia org.
    """
    datos = payload or {}
    alc = alcance_registros(user)
    if isinstance(alc, dict) and alc["tipo"] == "CENTRO":
        return alc["organizacion_id"]
    org = datos.get("organizacion")
    if org:
        return org
    if user is not None and getattr(user, "is_authenticated", False):
        perfil = getattr(user, "perfil", None)
        if perfil is not None and perfil.organizacion_id:
            return perfil.organizacion_id
    return None


def permitido_registro(user, registro):
    """¿Puede el usuario leer/editar este registro?"""
    alc = alcance_registros(user)
    if not isinstance(alc, dict):
        return True
    if alc["tipo"] == "CENTRO":
        return registro.get("organizacion") == alc["organizacion_id"]
    if alc["tipo"] == "REGIONAL" and alc["estado"]:
        return registro.get("estado") == alc["estado"]
    return True