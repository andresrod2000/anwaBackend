from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre del proveedor
    direccion = models.TextField(null=True, blank=True)  # Dirección del proveedor
    telefono = models.CharField(max_length=20, null=True, blank=True)  # Teléfono del proveedor
    email = models.EmailField(null=True, blank=True)  # Email del proveedor
    contacto = models.CharField(max_length=255, null=True, blank=True)  # Persona de contacto
    activo = models.BooleanField(default=True)  # Si el proveedor está activo
    fecha_registro = models.DateField(auto_now_add=True)  # Fecha en la que se registró el proveedor

    def __str__(self):
        return self.nombre
