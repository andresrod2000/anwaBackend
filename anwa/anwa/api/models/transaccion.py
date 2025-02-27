from django.db import models
from .inventario import Inventario
from .usuario import Usuario

class Movimiento(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='movimientos')
    nombre = models.CharField(max_length=255)
    precio = models.FloatField()
    descripcion = models.TextField()
    obs_movimiento = models.TextField()

    def __str__(self):
        return self.nombre


class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    id_usuario_genera = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='documentos_generados')
    id_transaccion = models.IntegerField()
    descripcion = models.TextField()
    afectacion = models.TextField()
    consecutivo = models.CharField(max_length=255)
    obsDocumento = models.TextField()

    def __str__(self):
        return self.consecutivo


class Transaccion(models.Model):
    id_transaccion = models.AutoField(primary_key=True)
    id_movimiento = models.ForeignKey(Movimiento, on_delete=models.CASCADE, related_name='transacciones')
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='transacciones')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='transacciones')
    obs_Transaccion = models.TextField()

    def __str__(self):
        return f"Transaccion {self.id_transaccion}"
