from config.pagination import StandardPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Bitacora
from .serializers import BitacoraSerializer, BitacoraCreateSerializer


class BitacoraListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Listar registros de bitácora", responses={200: BitacoraSerializer(many=True)})
    def get(self, request):
        registros = Bitacora.objects.select_related('usuario').order_by('-fecha', '-id')
        paginator = StandardPagination()
        pagina = paginator.paginate_queryset(registros, request)
        return paginator.get_paginated_response(BitacoraSerializer(pagina, many=True).data)

    @swagger_auto_schema(operation_summary="Crear registro de bitácora", request_body=BitacoraCreateSerializer, responses={201: BitacoraSerializer})
    def post(self, request):
        serializer = BitacoraCreateSerializer(data=request.data)
        if serializer.is_valid():
            bitacora = serializer.save()
            return Response(BitacoraSerializer(bitacora).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BitacoraDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Bitacora.objects.select_related('usuario').get(pk=pk)
        except Bitacora.DoesNotExist:
            return None

    @swagger_auto_schema(operation_summary="Obtener registro de bitácora", responses={200: BitacoraSerializer})
    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(BitacoraSerializer(obj).data)

    @swagger_auto_schema(operation_summary="Eliminar registro de bitácora", responses={200: openapi.Response('Eliminado')})
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj is None:
            return Response({'error': 'Registro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({'mensaje': 'Registro eliminado exitosamente'}, status=status.HTTP_200_OK)
