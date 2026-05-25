from rest_framework import serializers
from .models import Bitacora


class BitacoraSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)

    class Meta:
        model = Bitacora
        fields = ['id', 'modulo', 'accion_realizada', 'fecha', 'direccion_ip', 'usuario', 'usuario_email']


class BitacoraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = ['modulo', 'accion_realizada', 'direccion_ip', 'usuario']

