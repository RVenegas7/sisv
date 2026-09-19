from rest_framework import serializers

from .models import CIE10, CIE11, MapeoCIE


class CIE10Serializer(serializers.ModelSerializer):
    class Meta:
        model = CIE10
        fields = ["id", "codigo", "descripcion", "capitulo"]


class CIE11SlimSerializer(serializers.ModelSerializer):
    nivel_label = serializers.CharField(source="get_nivel_display", read_only=True)

    class Meta:
        model = CIE11
        fields = ["id", "codigo", "titulo", "nivel", "nivel_label", "requiere_subgrupo"]


class CIE11NodoSerializer(serializers.ModelSerializer):
    nivel_label = serializers.CharField(source="get_nivel_display", read_only=True)
    hijos = serializers.SerializerMethodField()

    class Meta:
        model = CIE11
        fields = ["id", "codigo", "titulo", "nivel", "nivel_label", "requiere_subgrupo", "hijos"]

    def get_hijos(self, obj):
        depth = self.context.get("depth", 4)
        if depth <= 1:
            return []
        hijos = obj.hijos.filter(activo=True)
        ser = CIE11NodoSerializer(hijos, many=True, context={**self.context, "depth": depth - 1})
        return ser.data


class MapeoCIESerializer(serializers.ModelSerializer):
    cie10 = CIE10Serializer(read_only=True)
    cie11 = CIE11SlimSerializer(read_only=True)
    tipo_label = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = MapeoCIE
        fields = ["id", "cie10", "cie11", "tipo", "tipo_label", "creado_en"]