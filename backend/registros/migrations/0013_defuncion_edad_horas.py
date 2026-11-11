# La edad del fallecido admite horas: el certificado legacy guarda la edad del
# recién nacido en horas (``CERTIFICADO.EDAD`` + ``TIPOEDAD='H'``) y el MANUAL del
# EV-14 pide esa precisión. Ver PENDIENTES.md §44.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registros", "0012_alter_defuncion_sugerencia_origen_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="defuncion",
            name="edad_unidad",
            field=models.CharField(
                blank=True,
                choices=[("ANIOS", "Años"), ("MESES", "Meses"), ("DIAS", "Días"), ("HORAS", "Horas")],
                default="",
                max_length=6,
                verbose_name="Unidad de la edad",
            ),
        ),
    ]
