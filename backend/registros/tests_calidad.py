"""Pruebas del filtro de calidad y del informe de certificados (§35).

El legacy capturó sin validación el número físico del certificado y algunos nombres:
números que no son numéricos (``.141409``, ``C85.9``) y nombres con dígitos
(``0CTAVIA``). Aquí se fija que el filtro ``?sospechosos=1`` de las listas devuelve
esos registros y **no** los sanos, y que el comando ``auditar_certificados`` corre y
escribe sus CSV.
"""
import io
import os
import tempfile
import csv

from django.core.management import call_command

from tests_sisv import SISVBase

from registros.calidad import numero_es_fecha, numero_sospechoso, nombre_sospechoso
from registros.models import Defuncion, Nacimiento


class CalidadUnitTests(SISVBase):
    def test_numero_sospechoso(self):
        self.assertTrue(numero_sospechoso(".141409"))
        self.assertTrue(numero_sospechoso("C85.9"))
        self.assertTrue(numero_sospechoso("ABRAHAM JESUS"))
        self.assertFalse(numero_sospechoso("123456"))
        self.assertFalse(numero_sospechoso(""))  # vacío no es sospechoso
        self.assertFalse(numero_sospechoso(None))

    def test_nombre_sospechoso(self):
        self.assertTrue(nombre_sospechoso("0CTAVIA"))
        self.assertFalse(nombre_sospechoso("ANA MARIA"))

    def test_numero_es_fecha(self):
        import datetime
        self.assertTrue(numero_es_fecha("16032021", datetime.date(2021, 3, 16)))
        self.assertFalse(numero_es_fecha("12345678", datetime.date(2021, 3, 16)))
        self.assertFalse(numero_es_fecha("16032021", None))


class FiltroSospechososTests(SISVBase):
    def setUp(self):
        self.login(self.u_trans_hcb)
        self.bueno = Nacimiento.objects.create(
            registro_numero="N-OK", fecha_evento="2026-05-01", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F", madre_edad=25,
            madre_nombres="ANA MARIA", madre_apellidos="PEREZ",
            numero_planilla="123456", organizacion=self.org_hcb,
        )
        self.malo = Nacimiento.objects.create(
            registro_numero="N-MALO", fecha_evento="2026-05-02", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F", madre_edad=25,
            madre_nombres="ANA MARIA", madre_apellidos="PEREZ",
            numero_planilla=".141409", organizacion=self.org_hcb,
        )
        self.nombre_raro = Nacimiento.objects.create(
            registro_numero="N-NOM", fecha_evento="2026-05-03", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F", madre_edad=25,
            madre_nombres="ANA MARIA", madre_apellidos="PEREZ",
            nino_nombres="0CTAVIA", numero_planilla="999", organizacion=self.org_hcb,
        )

    def test_filtro_devuelve_solo_sospechosos(self):
        r = self.client.get("/api/registros/nacimientos/?sospechosos=1&por_pagina=100")
        self.assertEqual(r.status_code, 200)
        numeros = {x["registro_numero"] for x in r.json()["data"]}
        self.assertIn("N-MALO", numeros)
        self.assertIn("N-NOM", numeros)
        self.assertNotIn("N-OK", numeros)

    def test_sin_filtro_devuelve_todos(self):
        r = self.client.get("/api/registros/nacimientos/?por_pagina=100")
        numeros = {x["registro_numero"] for x in r.json()["data"]}
        self.assertEqual(numeros, {"N-OK", "N-MALO", "N-NOM"})


class FiltroSospechososDefuncionTests(SISVBase):
    def setUp(self):
        self.login(self.u_trans_hcb)
        self.bueno = Defuncion.objects.create(
            registro_numero="D-OK", fecha_evento="2026-05-01", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F",
            fallecido_nombres="PEDRO", fallecido_apellidos="GOMEZ",
            numero_certificado="778899", organizacion=self.org_hcb,
        )
        self.malo = Defuncion.objects.create(
            registro_numero="D-MALO", fecha_evento="2026-05-02", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F",
            fallecido_nombres="PEDRO", fallecido_apellidos="GOMEZ",
            numero_certificado="C85.9", organizacion=self.org_hcb,
        )

    def test_filtro_defunciones(self):
        r = self.client.get("/api/registros/defunciones/?sospechosos=1&por_pagina=100")
        numeros = {x["registro_numero"] for x in r.json()["data"]}
        self.assertEqual(numeros, {"D-MALO"})


class AuditarCertificadosTests(SISVBase):
    def setUp(self):
        Nacimiento.objects.create(
            registro_numero="N-DUP-1", fecha_evento="2026-05-01", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F", madre_edad=25,
            madre_nombres="ANA", madre_apellidos="PEREZ", madre_cedula="V-11111111",
            numero_planilla="555", organizacion=self.org_hcb,
        )
        Nacimiento.objects.create(
            registro_numero="N-DUP-2", fecha_evento="2026-05-02", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F", madre_edad=25,
            madre_nombres="ANA", madre_apellidos="PEREZ", madre_cedula="V-11111111",
            numero_planilla="555", organizacion=self.org_hcb,
        )
        Nacimiento.objects.create(
            registro_numero="N-DUP-3", fecha_evento="2026-05-03", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F", madre_edad=25,
            madre_nombres="BETTY", madre_apellidos="GOMEZ", madre_cedula="V-22222222",
            numero_planilla="555", organizacion=self.org_hcb,
        )

    def test_comando_corre_y_escribe_csv(self):
        carpeta = tempfile.mkdtemp()
        try:
            call_command("auditar_certificados", "--modulo", "nacimientos",
                         "--csv", carpeta, stdout=io.StringIO())
            archivos = os.listdir(carpeta)
            self.assertIn("dup_nacimientos.csv", archivos)
            self.assertIn("numeros_raros_nacimientos.csv", archivos)
            self.assertIn("nombres_raros_nacimientos.csv", archivos)
        finally:
            for f in os.listdir(carpeta):
                os.remove(os.path.join(carpeta, f))
            os.rmdir(carpeta)

    def test_dup_csv_trae_numero_y_cedula(self):
        """Todo reporte de auditoría muestra el número físico y la cédula (§35)."""
        carpeta = tempfile.mkdtemp()
        try:
            call_command("auditar_certificados", "--modulo", "nacimientos",
                         "--csv", carpeta, stdout=io.StringIO())
            with open(os.path.join(carpeta, "dup_nacimientos.csv"), encoding="utf-8-sig") as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(
                list(filas[0]), ["Numero", "Veces", "ID", "Registro", "Cedula", "Persona",
                                 "Fecha", "Centro"])
            # El número repetido 555 aparece 3 veces y la cédula distingue el repetido real.
            self.assertEqual({f["Numero"] for f in filas}, {"555"})
            self.assertEqual({f["Cedula"] for f in filas},
                             {"V-11111111", "V-22222222"})
        finally:
            for f in os.listdir(carpeta):
                os.remove(os.path.join(carpeta, f))
            os.rmdir(carpeta)

    def test_nombres_raros_csv_trae_numero(self):
        """Aun el reporte de nombres debe permitir buscar por el número físico."""
        Nacimiento.objects.create(
            registro_numero="N-NOM", fecha_evento="2026-05-04", version_cie="CIE11",
            cie11=self.cie11_categoria, sexo="F", madre_edad=25,
            madre_nombres="ANA", madre_apellidos="PEREZ", madre_cedula="V-11111111",
            nino_nombres="0CTAVIA", numero_planilla="777", organizacion=self.org_hcb,
        )
        carpeta = tempfile.mkdtemp()
        try:
            call_command("auditar_certificados", "--modulo", "nacimientos",
                         "--csv", carpeta, stdout=io.StringIO())
            with open(os.path.join(carpeta, "nombres_raros_nacimientos.csv"),
                      encoding="utf-8-sig") as f:
                filas = list(csv.DictReader(f))
            self.assertTrue(filas)
            self.assertEqual(filas[0]["Numero"], "777")
            self.assertIn("Cedula", filas[0])
        finally:
            for f in os.listdir(carpeta):
                os.remove(os.path.join(carpeta, f))
            os.rmdir(carpeta)
