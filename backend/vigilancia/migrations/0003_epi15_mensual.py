# El EPI-15 es un consolidado **mensual**, no semanal: el periodo va de 1 a 12
# (DOCUMENTO.PERIODO con TIPO=2 en el legado), así que 'semana' pasa a 'mes'.
# La semana epidemiológica (1-53) es del EPI-12/EPI-14 (ConsolidadoSemanal).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vigilancia", "0002_consolidadosemanal_legacy_documento_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="consolidadoepi15",
            options={
                "ordering": ["-anio", "-mes"],
                "verbose_name": "Consolidado mensual EPI-15",
                "verbose_name_plural": "Consolidados mensuales EPI-15",
            },
        ),
        migrations.RenameField(
            model_name="consolidadoepi15",
            old_name="semana",
            new_name="mes",
        ),
        migrations.AlterField(
            model_name="consolidadoepi15",
            name="mes",
            field=models.PositiveSmallIntegerField(verbose_name="Mes (1-12)"),
        ),
        migrations.RemoveConstraint(
            model_name="consolidadoepi15",
            name="uq_consolidado_epi15",
        ),
        migrations.AddConstraint(
            model_name="consolidadoepi15",
            constraint=models.UniqueConstraint(
                fields=("organizacion", "anio", "mes"), name="uq_consolidado_epi15"
            ),
        ),
    ]
