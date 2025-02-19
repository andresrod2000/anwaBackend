from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet,
    RolesViewSet,
    InventarioViewSet,
    CategoriasViewSet,
    MovimientoViewSet,
    DocumentoViewSet,
    TransaccionViewSet,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolesViewSet)
router.register(r'categorias', CategoriasViewSet)
router.register(r'inventario', InventarioViewSet)
router.register(r'movimientos', MovimientoViewSet)
router.register(r'documentos', DocumentoViewSet)
router.register(r'transacciones', TransaccionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/', UsuarioViewSet.as_view({'get': 'perfil'}), name='user_profile'),  # Nueva ruta para obtener el usuario autenticado
]

