from rest_framework.response import Response


def ok(data=None, message="Operación exitosa", status=200, **extra):
    payload = {"success": True, "message": message, "data": data if data is not None else []}
    payload.update(extra)
    return Response(payload, status=status)


def error(message="Error en la solicitud", errors=None, status=400):
    return Response({"success": False, "message": message, "errors": errors}, status=status)