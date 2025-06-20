from django.db import models

class Pedido(models.Model):
    ESTADOS = [
        ('en_preparacion', 'En preparación'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
        ('recibido', 'Recibido'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Campos del modelo
    fecha_hora = models.DateTimeField(auto_now_add=True)  # Fecha y hora del pedido
    nombre_cliente = models.CharField(max_length=255)     # Nombre del cliente
    telefono = models.CharField(max_length=20)            # Teléfono del cliente
    direccion_domicilio = models.TextField()              # Dirección de entrega
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)  # Método de pago (Efectivo, Tarjeta, etc.)
    estado_pedido = models.CharField(max_length=50, choices=ESTADOS, default='recibido')  # Estado del pedido
    detalles_pedido = models.TextField(null=True, blank=True)  # Detalles del pedido (comida, bebida, etc.)
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total del pedido
    comentarios = models.TextField(null=True, blank=True)  # Comentarios adicionales

    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente}"

