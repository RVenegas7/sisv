from django.core.cache import cache

MAX_INTENTOS = 5
VENTANA_SEG = 300
BLOQUEO_SEG = 900


def control_intentos(ip, usuario=""):
    clave_conteo = f"auth_login:{ip}:{usuario or '*'}"
    clave_bloqueo = f"auth_bloq:{ip}"
    if cache.get(clave_bloqueo):
        return {"permitido": False, "mensaje": "Demasiados intentos de inicio de sesión. Intente en unos minutos."}
    n = int(cache.get(clave_conteo) or 0) + 1
    cache.set(clave_conteo, n, VENTANA_SEG)
    if n > MAX_INTENTOS:
        cache.delete(clave_conteo)
        cache.set(clave_bloqueo, 1, BLOQUEO_SEG)
        return {"permitido": False, "mensaje": "Demasiados intentos de inicio de sesión. Bloqueado temporalmente."}
    return {"permitido": True, "restantes": MAX_INTENTOS - n}


def ip_del_request(request):
    return request.META.get("REMOTE_ADDR", "") or request.META.get("HTTP_X_FORWARDED_FOR", "") or "?"