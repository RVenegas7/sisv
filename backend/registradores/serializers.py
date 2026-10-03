from rest_framework import serializers

from registradores.models import DesignacionRegistrador, RegistradorCivil, RegistroCivil


class RegistroCivilSerializer(serializers.ModelSerializer):
    organizacion_nombre = serializers.SerializerMethodField()
    designaciones_count = serializers.SerializerMethodField()

    class Meta:
        model = RegistroCivil
        fields = [
            "id", "nombre", "organizacion", "organizacion_nombre",
            "estado", "municipio", "parroquia", "activo", "observaciones",
            "designaciones_count", "creado_en",
        ]
        read_only_fields = ["creado_en", "organizacion_nombre", "designaciones_count"]

    def get_organizacion_nombre(self, obj):
        return obj.organizacion.nombre if obj.organizacion_id else None

    def get_designaciones_count(self, obj):
        return obj.designaciones.count()


class RegistradorCivilSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    cedula_completa = serializers.CharField(read_only=True)

    class Meta:
        model = RegistradorCivil
        fields = [
            "id", "nacionalidad", "cedula", "cedula_completa", "nombres", "apellidos",
            "nombre_completo", "telefono", "email", "activo", "observaciones", "creado_en",
        ]
        read_only_fields = ["creado_en", "nombre_completo", "cedula_completa"]

    def validate(self, attrs):
        nacionalidad = attrs.get(
            "nacionalidad", getattr(self.instance, "nacionalidad", None)
        )
        cedula = attrs.get("cedula", getattr(self.instance, "cedula", None))
        if nacionalidad and cedula:
            duplicado = RegistradorCivil.objects.filter(
                nacionalidad=nacionalidad, cedula=cedula
            )
            if self.instance is not None:
                duplicado = duplicado.exclude(pk=self.instance.pk)
            if duplicado.exists():
                raise serializers.ValidationError(
                    {"cedula": "Ya existe un registrador con esa nacionalidad y cédula."}
                )
        return attrs


class DesignacionRegistradorSerializer(serializers.ModelSerializer):
    registro_civil_nombre = serializers.SerializerMethodField()
    registrador_nombre = serializers.SerializerMethodField()
    registrador_cedula = serializers.SerializerMethodField()
    cargo_label = serializers.SerializerMethodField()
    vigente = serializers.BooleanField(read_only=True)

    class Meta:
        model = DesignacionRegistrador
        fields = [
            "id", "registro_civil", "registro_civil_nombre",
            "registrador", "registrador_nombre", "registrador_cedula",
            "cargo", "cargo_label", "desde", "hasta", "vigente",
            "fecha_toma_posesion", "acta_nombramiento", "observaciones", "creado_en",
        ]
        read_only_fields = [
            "creado_en", "registro_civil_nombre", "registrador_nombre",
            "registrador_cedula", "cargo_label", "vigente",
        ]

    def get_registro_civil_nombre(self, obj):
        return obj.registro_civil.nombre if obj.registro_civil_id else None

    def get_registrador_nombre(self, obj):
        return obj.registrador.nombre_completo if obj.registrador_id else None

    def get_registrador_cedula(self, obj):
        return obj.registrador.cedula_completa if obj.registrador_id else None

    def get_cargo_label(self, obj):
        return obj.get_cargo_display()

    def validate(self, attrs):
        desde = attrs.get("desde", getattr(self.instance, "desde", None))
        hasta = attrs.get("hasta", getattr(self.instance, "hasta", None))
        if desde and hasta and hasta < desde:
            raise serializers.ValidationError(
                {"hasta": "La fecha «hasta» no puede ser anterior a «desde»."}
            )
        registro_civil = attrs.get(
            "registro_civil", getattr(self.instance, "registro_civil", None)
        )
        registrador = attrs.get(
            "registrador", getattr(self.instance, "registrador", None)
        )
        if registro_civil and registrador and desde:
            duplicado = DesignacionRegistrador.objects.filter(
                registro_civil=registro_civil, registrador=registrador, desde=desde
            )
            if self.instance is not None:
                duplicado = duplicado.exclude(pk=self.instance.pk)
            if duplicado.exists():
                raise serializers.ValidationError(
                    {"desde": "Ya existe una designación de ese registrador en ese registro civil "
                              "con la misma fecha de inicio."}
                )
        return attrs
