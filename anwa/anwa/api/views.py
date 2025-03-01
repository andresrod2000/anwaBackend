from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
import requests
from rest_framework import generics
from django.http import JsonResponse
from .models import (
    Usuario,
    Roles,
    Inventario,
    Categorias,
    Movimiento,
    Documento,
    Transaccion,
    Pedido
)
from .serializers import (
    UsuarioSerializer,
    RolesSerializer,
    InventarioSerializer,
    CategoriasSerializer,
    MovimientoSerializer,
    DocumentoSerializer,
    TransaccionSerializer,
    PedidoSerializer
)

class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer

class StrictDjangoModelPermissions(permissions.DjangoModelPermissions):
    """
    Versión más estricta de DjangoModelPermissions que bloquea usuarios sin permisos asignados.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False  # 🔹 Bloquea usuarios no autenticados

        if not request.user.user_permissions.exists() and not request.user.groups.exists():
            return False  # 🔹 Bloquea usuarios sin permisos asignados

        return super().has_permission(request, view)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [StrictDjangoModelPermissions] 

class PerfilViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  # 🔹 Permite acceso solo a usuarios autenticados

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Devuelve los datos del usuario autenticado"""
        print(f"🔍 Intento de acceso a /user/ por: {request.user}")
        usuario = request.user
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)


class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categorias.objects.all()
    serializer_class = CategoriasSerializer


class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer


class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer

def get_phrase_of_the_day(request):
    url = "https://frasedeldia.azurewebsites.net/api/phrase"  # URL de la API original

    try:
        response = requests.get(url)  # Hacer la solicitud a la API original
        data = response.json()  # Convertir la respuesta a JSON
        return JsonResponse(data)  # Devolver la respuesta JSON
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Error fetching the phrase"}, status=500)


class PedidoEnProcesoListView(generics.ListAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.AllowAny] #SOLO PARA TESTAR


    def get_queryset(self):
        return Pedido.objects.filter(estado_pedido__in=['en_preparacion', 'en_camino'])