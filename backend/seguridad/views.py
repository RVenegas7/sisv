from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from seguridad.models import Organizacion, Perfil
from seguridad.services import perfil_de, permisos_de
from sisv_backend.api import error, ok

RolesView = None

User = get_user_model()


def _serializar_org(o):
    return {
        "id": o.id,
        "codigo": o.codigo,
        "nombre": o.nombre,
        "nivel": o.nivel,
        "nivel_label": o.get_nivel_display(),
        "estado": o.estado,
        "municipio": o.municipio,
        "padre_id": o.padre_id,
        "padre_nombre": o.padre.nombre if o.padre else None,
        "hijos": o.hijos.count(),
        "integrantes": o.integrantes.count(),
    }


def _serializar_usuario(u):
    perfil = getattr(u, "perfil", None)
    return {
        "id": u.id,
        "username": u.username,
        "nombre": u.get_full_name() or u.username,
        "rol": perfil.rol if perfil else None,
        "rol_label": perfil.get_rol_display() if perfil else None,
        "organizacion_id": perfil.organizacion_id if perfil else None,
        "organizacion_nombre": perfil.organizacion.nombre if perfil and perfil.organizacion_id else None,
        "activo": u.is_active,
        "es_superusuario": u.is_superuser,
        "permisos": permisos_de(u),
    }


def _denegar():
    return error("No tiene permiso para administrar usuarios y organizaciones.", status=403)


class OrganizacionesView(APIView):
    def get(self, request):
        qs = Organizacion.objects.filter(activo=True).select_related("padre").order_by("nivel", "nombre")
        return ok([_serializar_org(o) for o in qs])

    def post(self, request):
        if not permisos_de(request.user)["puede_configurar"]:
            return _denegar()
        datos = request.data or {}
        codigo = str(datos.get("codigo", "")).strip()
        nombre = str(datos.get("nombre", "")).strip()
        if not codigo or not nombre:
            return error("Código y nombre son obligatorios.", status=400)
        if Organizacion.objects.filter(codigo=codigo).exists():
            return error("El código ya existe.", {"codigo": "Ya existe una organización con este código."}, 400)
        org = Organizacion.objects.create(
            codigo=codigo,
            nombre=nombre,
            nivel=datos.get("nivel") or Organizacion.NIVEL_CENTRO,
            estado=str(datos.get("estado", "")).strip(),
            municipio=str(datos.get("municipio", "")).strip(),
            padre_id=datos.get("padre") or None,
            activo=True,
        )
        return ok(_serializar_org(org), message="Organización creada", status=201)


class OrganizacionDetalleView(APIView):
    def _obtener(self, pk):
        return Organizacion.objects.filter(pk=pk).select_related("padre").first()

    def get(self, request, pk):
        org = self._obtener(pk)
        if org is None:
            return error("Organización no encontrada", status=404)
        return ok(_serializar_org(org))

    def patch(self, request, pk):
        if not permisos_de(request.user)["puede_configurar"]:
            return _denegar()
        org = self._obtener(pk)
        if org is None:
            return error("Organización no encontrada", status=404)
        datos = request.data or {}
        for campo in ["codigo", "nombre", "nivel", "estado", "municipio"]:
            if campo in datos and datos[campo] is not None:
                setattr(org, campo, datos[campo])
        if "padre" in datos:
            org.padre_id = datos.get("padre") or None
        org.save()
        return ok(_serializar_org(org), message="Organización actualizada")

    def delete(self, request, pk):
        if not permisos_de(request.user)["puede_configurar"]:
            return _denegar()
        org = self._obtener(pk)
        if org is None:
            return error("Organización no encontrada", status=404)
        try:
            org.delete()
        except ProtectedError:
            return error(
                "No se puede eliminar: tiene usuarios asignados o depende de ella otra organización.",
                status=400,
            )
        return ok(None, message="Organización eliminada")


class UsuariosView(APIView):
    def get(self, request):
        qs = User.objects.select_related("perfil__organizacion").order_by("username")
        return ok([_serializar_usuario(u) for u in qs])

    def post(self, request):
        if not permisos_de(request.user)["puede_configurar"]:
            return _denegar()
        datos = request.data or {}
        username = str(datos.get("username", "")).strip()
        clave = str(datos.get("password", "") or "")
        if not username or len(clave) < 6:
            return error(
                "Usuario y clave (mínimo 6 caracteres) son obligatorios.",
                {
                    "username": "Obligatorio." if not username else "",
                    "password": "Mínimo 6 caracteres." if len(clave) < 6 else "",
                },
                400,
            )
        if User.objects.filter(username=username).exists():
            return error("El usuario ya existe.", {"username": "Ya existe un usuario con este nombre."}, 400)
        user = User.objects.create_user(username=username, password=clave)
        user.first_name = str(datos.get("nombre", "")).strip()
        user.is_superuser = bool(datos.get("es_superusuario", False))
        user.save()
        rol = datos.get("rol") or None
        org = datos.get("organizacion") or None
        if rol or org:
            Perfil.objects.create(user=user, rol=rol or Perfil.ROL_TRANSCRIPTOR, organizacion_id=org or None)
        return ok(_serializar_usuario(user), message="Usuario creado", status=201)


class UsuarioDetalleView(APIView):
    def _obtener(self, pk):
        return User.objects.filter(pk=pk).select_related("perfil__organizacion").first()

    def get(self, request, pk):
        u = self._obtener(pk)
        if u is None:
            return error("Usuario no encontrado", status=404)
        return ok(_serializar_usuario(u))

    def patch(self, request, pk):
        if not permisos_de(request.user)["puede_configurar"]:
            return _denegar()
        u = self._obtener(pk)
        if u is None:
            return error("Usuario no encontrado", status=404)
        datos = request.data or {}
        if "username" in datos and str(datos.get("username", "")).strip():
            nuevo = str(datos["username"]).strip()
            if nuevo != u.username and User.objects.filter(username=nuevo).exists():
                return error("El usuario ya existe.", {"username": "Ya existe un usuario con este nombre."}, 400)
            u.username = nuevo
        if "nombre" in datos:
            u.first_name = str(datos.get("nombre", "")).strip()
        if "password" in datos and str(datos.get("password", "")):
            u.set_password(str(datos["password"]))
        if "activo" in datos:
            u.is_active = bool(datos["activo"])
        if "es_superusuario" in datos and request.user.is_superuser:
            u.is_superuser = bool(datos["es_superusuario"])
        u.save()
        perfil = getattr(u, "perfil", None)
        if "rol" in datos or "organizacion" in datos:
            rol = datos.get("rol")
            org = datos.get("organizacion")
            if rol or org:
                if perfil is None:
                    perfil = Perfil.objects.create(user=u)
                if rol:
                    perfil.rol = rol
                if org:
                    perfil.organizacion_id = org or None
                perfil.save()
            elif perfil is not None:
                if "rol" in datos:
                    perfil.rol = Perfil.ROL_TRANSCRIPTOR
                if "organizacion" in datos:
                    perfil.organizacion_id = None
                perfil.save()
        return ok(_serializar_usuario(u), message="Usuario actualizado")

    def delete(self, request, pk):
        if not permisos_de(request.user)["puede_configurar"]:
            return _denegar()
        u = self._obtener(pk)
        if u is None:
            return error("Usuario no encontrado", status=404)
        if u.pk == request.user.pk:
            return error("No puede eliminar su propia cuenta.", status=400)
        u.delete()
        return ok(None, message="Usuario eliminado")


class RolesView(APIView):
    def get(self, request):
        return ok([{"valor": v, "rotulo": r} for v, r in Perfil.ROL_CHOICES])


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    def post(self, request):
        usuario = str(request.data.get("username", "")).strip()
        clave = str(request.data.get("password", ""))
        user = authenticate(request, username=usuario, password=clave)
        if user is None or not user.is_active:
            return error("Usuario o clave incorrectos.", status=401)
        login(request, user)
        return ok(perfil_de(user), message="Sesión iniciada")


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return ok(None, message="Sesión cerrada")


class MeView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return ok(perfil_de(request.user))
        return error("No hay sesión iniciada.", status=401)


class CsrfView(APIView):
    def get(self, request):
        return ok({"csrf": get_token(request)})