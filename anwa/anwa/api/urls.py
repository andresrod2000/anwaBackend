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
    PerfilViewSet,
    get_phrase_of_the_day,
    PedidoEnProcesoListView,
    PedidoViewSet,
    ProductoListView,
    ProductoViewSet,
    whatsapp_webhook,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolesViewSet)
router.register(r'categorias', CategoriasViewSet)
router.register(r'inventario', InventarioViewSet)
router.register(r'movimientos', MovimientoViewSet)
router.register(r'documentos', DocumentoViewSet)
router.register(r'transacciones', TransaccionViewSet)
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'productosmod',ProductoViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('user/', PerfilViewSet.as_view({'get': 'perfil'}), name='user_profile'),
    path("api/phrase/", get_phrase_of_the_day),  # Ruta del nuevo endpoint  # Nueva ruta para obtener el usuario autenticado
    path('pedidos-en-proceso/', PedidoEnProcesoListView.as_view(), name='pedidos-en-proceso'),
    #path('gestionar-pedidos/', PedidoViewSet.as_view(), name='crear-pedido'),
    path('productos/', ProductoListView.as_view(), name='productos-list'),
    path('webhook/', whatsapp_webhook, name='whatsapp-webhook'),

]

