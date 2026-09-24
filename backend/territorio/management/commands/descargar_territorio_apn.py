import json
import os
import urllib.request
import urllib.parse
import urllib.error

from django.core.management.base import BaseCommand, CommandError

from territorio.models import DivisionTerritorial

BASE = "https://apisegen.apn.gob.ve"


class Command(BaseCommand):
    help = (
        "Descarga Estado→Municipio→Parroquia→Comunidad desde la API de la APN "
        "(División Político Territorial y de Población). Requiere credenciales de "
        "desarrollador registradas en https://apisegen.apn.gob.ve/registroUsuario/ "
        "(arg --usuario/--clave o variables APN_USUARIO/APN_CLAVE)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--usuario", help="Usuario registrado como desarrollador en la APN")
        parser.add_argument("--clave", help="Clave del desarrollador en la APN")
        parser.add_argument("--borrar", action="store_true", help="Vacía la tabla de territorio antes de importar")
        parser.add_argument("--sin-comunidades", action="store_true", help="No descarga el nivel COMUNIDAD")

    def handle(self, *args, **opts):
        usuario = opts["usuario"] or os.getenv("APN_USUARIO", "")
        clave = opts["clave"] or os.getenv("APN_CLAVE", "")
        if not usuario or not clave:
            raise CommandError("Indique --usuario y --clave o defina APN_USUARIO/APN_CLAVE.")

        if opts["borrar"]:
            DivisionTerritorial.objects.all().delete()
            self.stdout.write("División territorial previa eliminada.")

        self.stdout.write(f"Obteniendo token para {usuario} ...")
        token = self._login(usuario, clave)
        self.stdout.write(self.style.SUCCESS("Token obtenido."))

        totales = {"ESTADO": 0, "MUNICIPIO": 0, "PARROQUIA": 0, "COMUNIDAD": 0}
        estados = self._get(f"/api/v1/listadoEntidad", token)
        self.stdout.write(f"Entidades federales recibidas: {len(estados)}")
        for ent in estados:
            ent_cod = ent.get("cod_entidad_ine") or ""
            ent_nombre = self._titulo(ent.get("entidad_ine") or "")
            if not ent_nombre:
                self.stderr.write(f"Entidad sin nombre (código {ent_cod}): omitida.")
                continue
            estado, _ = self._crear("ESTADO", ent_nombre, ent_cod, None)
            self.stdout.write(f"→ {ent_nombre}")
            if estado is None:
                continue
            totales["ESTADO"] += 1
            municipios = self._get("/api/v1/listadoMunicipio", token, {"codEntidad": ent_cod})
            for mun in municipios:
                mun_cod = mun.get("cod_municipio_ine") or ""
                mun_nombre = self._titulo(mun.get("municipio_ine") or "")
                if not mun_nombre:
                    continue
                muni, _ = self._crear("MUNICIPIO", mun_nombre, mun_cod, estado)
                if muni is None:
                    continue
                totales["MUNICIPIO"] += 1
                parroquias = self._get(
                    "/api/v1/listadoParroquia", token, {"codEntidad": ent_cod, "codMunicipio": mun_cod}
                )
                for par in parroquias:
                    parr_cod = par.get("cod_parroquia_ine") or ""
                    parr_nombre = self._titulo(par.get("parroquia_ine") or "")
                    if not parr_nombre:
                        continue
                    parroq, _ = self._crear("PARROQUIA", parr_nombre, parr_cod, muni)
                    if parroq is None:
                        continue
                    totales["PARROQUIA"] += 1
                    if not opts["sin_comunidades"]:
                        comunidades = self._get(
                            "/api/v1/listadoComunidad",
                            token,
                            {"codEntidad": ent_cod, "codMunicipio": mun_cod, "codParroquia": parr_cod},
                        )
                        for com in comunidades:
                            com_nombre = self._titulo(com.get("nombre_comunidad") or "")
                            if not com_nombre:
                                continue
                            com_cod = com.get("id_comunidad_ine") or ""
                            creado, _ = self._crear("COMUNIDAD", com_nombre, com_cod, parroq)
                            if creado is not None:
                                totales["COMUNIDAD"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Importa terminada: "
            + ", ".join(f"{k}={v}" for k, v in totales.items())
        ))

    @staticmethod
    def _titulo(nombre):
        partes = [p.strip().title() for p in nombre.replace("/", " / ").replace("(", " ( ").replace(")", " ) ").split() if p.strip()]
        return " ".join(partes)

    def _login(self, usuario, clave):
        datos = urllib.parse.urlencode({"usuario": usuario, "clave": clave}).encode("utf-8")
        resp = self._llamar(BASE + "/api/v1/login", datos=datos, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token = (resp.get("token") or "").strip()
        if not token:
            raise CommandError("La API no devolvió token. Revise el usuario/clave o la aprobación como desarrollador.")
        return token

    def _get(self, ruta, token, params=None):
        qs = dict(params or {})
        qs["token"] = token
        url = BASE + ruta + "?" + urllib.parse.urlencode(qs)
        resp = self._llamar(url)
        data = resp.get("data") or []
        if not isinstance(data, list):
            data = []
        return data

    def _llamar(self, url, datos=None, headers=None):
        req_headers = {"Accept": "application/json"}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(url, data=datos, headers=req_headers, method="POST" if datos else "GET")
        try:
            with urllib.request.urlopen(req, timeout=90) as f:
                raw = f.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            raise CommandError(f"HTTP {e.code} en {url}: {body}")
        except urllib.error.URLError as e:
            raise CommandError(f"No se pudo contactar la API: {e}")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise CommandError(f"Respuesta no JSON en {url}: {raw[:200]}")

    def _crear(self, nivel, nombre, codigo, padre):
        if not nombre:
            return None, False
        obj, creado = DivisionTerritorial.objects.get_or_create(
            nivel=nivel,
            nombre=nombre,
            padre=padre,
            defaults={"codigo": codigo or ""},
        )
        if not creado and codigo and not obj.codigo:
            obj.codigo = codigo
            obj.save(update_fields=["codigo"])
        return obj, creado