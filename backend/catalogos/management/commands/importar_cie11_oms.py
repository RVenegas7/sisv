import json
import re
import time

from django.core.management.base import BaseCommand

from catalogos.models import CIE11

ID_HOST = "http://id.who.int"
URI_RE = re.compile(r"/icd/release/11/[^/]+/mms/([^/]+)$")


class Command(BaseCommand):
    help = "Importa CIE-11 (linealización MMS) desde el contenedor oficial ICD-API (whoicd/icd-api)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url-base",
            default="http://localhost:8080/icd/release/11/2026-01",
            help="Base local del API (sin idioma). Por defecto contenedor whoicd/icd-api.",
        )
        parser.add_argument("--lang", default="es", help="Idioma (es por defecto)")
        parser.add_argument("--no-clean", action="store_true", help="No borrar la tabla antes de importar")

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._meta = {}
        self._visitados = set()

    def handle(self, *args, **opts):
        self.base = opts["url_base"].rstrip("/")
        self.lang = opts["lang"]
        if not opts["no_clean"]:
            CIE11.objects.all().delete()
            self.stdout.write("Catálogo CIE-11 previo eliminado.")

        contador = {"total": 0, "capitulos": 0, "bloques": 0, "categorias": 0, "subgrupos": 0}
        filas = []

        raiz = self._obtener(f"{self.base}/mms")
        hijos = self._hijos(raiz)
        if not hijos:
            self.stdout.write(self.style.ERROR("La raíz MMS no devolvió capítulos. ¿Release correcto?"))
            return
        for uri in hijos:
            nodo = self._obtener(uri)
            self._visitar(nodo, capitulo_uri=None, padre_uri=None, filas=filas, contador=contador)
        if contador["total"] % 500:
            self.stdout.write("")

        objetos = []
        for uri, nivel, codigo, titulo in filas:
            objetos.append(CIE11(codigo=codigo, titulo=titulo, nivel=nivel))
        CIE11.objects.bulk_create(objetos, batch_size=2000)
        indice = dict(zip((f[0] for f in filas), objetos))

        pendientes = []
        for (uri, nivel, _codigo, _titulo), obj in zip(filas, objetos):
            _lv, _cl, _cd, _tt, cap_uri, padre_uri = self._meta[uri]
            obj.padre = indice.get(padre_uri)
            obj.capitulo = indice.get(cap_uri)
            pendientes.append(obj)

        for inicio in range(0, len(pendientes), 2000):
            CIE11.objects.bulk_update(pendientes[inicio : inicio + 2000], ["padre", "capitulo"], batch_size=2000)

        padres_con_subgrupos = set(
            CIE11.objects.filter(nivel=4, padre__nivel=3).values_list("padre_id", flat=True)
        )
        if padres_con_subgrupos:
            CIE11.objects.filter(id__in=padres_con_subgrupos).update(requiere_subgrupo=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"CIE-11 importados: {CIE11.objects.count()} "
                f"(capítulos {contador['capitulos']}, bloques {contador['bloques']}, "
                f"categorías {contador['categorias']}, subgrupos {contador['subgrupos']})"
            )
        )

    def _obtener(self, url):
        url = url.replace(ID_HOST, "http://localhost:8080")
        ultimo = None
        for intento in range(4):
            try:
                import urllib.request

                req = urllib.request.Request(
                    url,
                    headers={
                        "API-Version": "v2",
                        "Accept-Language": self.lang,
                        "Accept": "*/*",
                        "User-Agent": f"{Command.help[:20]}",
                        "Connection": "close",
                    },
                )
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.load(r)
            except Exception as e:  # noqa: BLE001
                ultimo = e
                time.sleep(1.5 * (intento + 1))
        raise RuntimeError(f"No se pudo obtener {url}: {ultimo}")

    @staticmethod
    def _hijos(nodo):
        hijos = nodo.get("child") or []
        if isinstance(hijos, dict):
            out = []
            for urls in hijos.values():
                out.extend(urls or [])
            return out
        return hijos

    def _titulo(self, nodo):
        t = nodo.get("title")
        if not t:
            return ""
        if isinstance(t, dict):
            return (t.get("@value") or "").strip()
        if isinstance(t, list):
            for item in t:
                if isinstance(item, dict) and item.get("@language") == self.lang:
                    return (item.get("@value") or "").strip()
            if t and isinstance(t[0], dict):
                return (t[0].get("@value") or "").strip()
        return str(t).strip()

    def _visitar(self, nodo, capitulo_uri, padre_uri, filas, contador):
        uri = nodo.get("@id")
        if not uri or uri in self._visitados:
            return
        self._visitados.add(uri)
        clase = (nodo.get("classKind") or "").lower()
        codigo = (nodo.get("code") or "").strip()
        titulo = self._titulo(nodo)
        info_padre = self._meta.get(padre_uri)
        padre_nivel = info_padre[0] if info_padre else None

        if clase == "chapter":
            nivel = 1
            contador["capitulos"] += 1
        elif clase == "block":
            nivel = 2
            contador["bloques"] += 1
        elif padre_nivel == 3:
            nivel = 4
            contador["subgrupos"] += 1
        else:
            nivel = 3
            contador["categorias"] += 1

        if not codigo:
            m = URI_RE.search(uri)
            codigo = m.group(1) if m else f"CIE11-{len(filas)}"
        if not titulo:
            titulo = f"(Sin título) {codigo}"

        filas.append((uri, nivel, codigo[:64], titulo[:500]))
        self._meta[uri] = (nivel, clase, codigo, titulo, capitulo_uri, padre_uri)
        contador["total"] += 1
        if contador["total"] % 500 == 0:
            self.stdout.write(f"  … {contador['total']} nodos recorridos ({uri})", ending="\r")

        cap_hijo = uri if nivel == 1 else capitulo_uri
        for u in self._hijos(nodo):
            self._visitar(self._obtener(u), cap_hijo, uri, filas, contador)