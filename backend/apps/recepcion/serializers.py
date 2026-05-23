from rest_framework import serializers
from .models import Cobro


class CobroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobro
        fields = ['id', 'monto_total', 'metodo_pago', 'fecha']


class CobroCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobro
        fields = ['monto_total', 'metodo_pago', 'fecha']
        extra_kwargs = {
            'monto_total': {'required': True},
            'metodo_pago': {'required': True},
            'fecha': {'required': True},
        }

    def validate_monto_total(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a 0.")
        return value


class CobroUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobro
        fields = ['monto_total', 'metodo_pago', 'fecha']

    def validate_monto_total(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("El monto total debe ser mayor a 0.")
        return value

