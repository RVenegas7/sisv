from rest_framework import serializers

from despacho.models import NovedadCertificado, Talonario


class TalonarioSerializer(serializers.ModelSerializer):
    centro_nombre = serializers.SerializerMethodField()
    tipo_label = serializers.SerializerMethodField()
    resumen = serializers.SerializerMethodField()

    class Meta:
        model = Talonario
        fields = [
            "id", "tipo", "tipo_label", "centro", "centro_nombre", "fecha_entrega",
            "serie_desde", "serie_hasta", "cantidad",
            "responsable_recibe", "responsable_entrega", "observaciones",
            "creado_en", "resumen",
        ]
        read_only_fields = ["cantidad", "creado_en", "centro_nombre", "tipo_label", "resumen"]

    def get_centro_nombre(self, obj):
        return obj.centro.nombre if obj.centro_id else None

    def get_tipo_label(self, obj):
        return obj.get_tipo_display()

    def get_resumen(self, obj):
        from despacho.services import resumen_talonario

        resumen = resumen_talonario(obj)
        # La lista de faltantes puede ser enorme; en el resumen solo va el conteo.
        resumen.pop("faltantes", None)
        return resumen

    def validate(self, attrs):
        desde = attrs.get("serie_desde", getattr(self.instance, "serie_desde", None))
        hasta = attrs.get("serie_hasta", getattr(self.instance, "serie_hasta", None))
        if desde is not None and hasta is not None and hasta < desde:
            raise serializers.ValidationError(
                {"serie_hasta": "La serie hasta no puede ser menor que la serie desde."}
            )
        centro = attrs.get("centro", getattr(self.instance, "centro", None))
        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))
        if centro and tipo and desde is not None and hasta is not None:
            duplicado = Talonario.objects.filter(
                centro=centro, tipo=tipo, serie_desde=desde, serie_hasta=hasta
            )
            if self.instance is not None:
                duplicado = duplicado.exclude(pk=self.instance.pk)
            if duplicado.exists():
                raise serializers.ValidationError(
                    {"serie_desde": "Ya existe un talonario de ese tipo con esa serie en el centro."}
                )
        return attrs


class NovedadCertificadoSerializer(serializers.ModelSerializer):
    estado_label = serializers.SerializerMethodField()
    centro = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()

    class Meta:
        model = NovedadCertificado
        fields = [
            "id", "talonario", "numero", "estado", "estado_label", "centro", "tipo",
            "justificacion_numero", "justificacion_fecha",
            "transitado_nombres", "transitado_apellidos", "fecha_salio_centro",
            "observaciones",
        ]

    def get_estado_label(self, obj):
        return obj.get_estado_display()

    def get_centro(self, obj):
        return obj.talonario.centro_id

    def get_tipo(self, obj):
        return obj.talonario.tipo

    def validate(self, attrs):
        talonario = attrs.get("talonario", getattr(self.instance, "talonario", None))
        numero = attrs.get("numero", getattr(self.instance, "numero", None))
        if talonario and numero is not None:
            if not (talonario.serie_desde <= numero <= talonario.serie_hasta):
                raise serializers.ValidationError(
                    {"numero": f"El número debe estar dentro de la serie "
                               f"{talonario.serie_desde}-{talonario.serie_hasta}."}
                )
        return attrs
