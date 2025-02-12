from django.db import models

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE, related_name='usuarios')
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    contrasena = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class UsuarioRol(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='roles')
    id_rol = models.ForeignKey(Roles, on_delete=models.CASCADE, related_name='usuarios_roles')

    class Meta:
        unique_together = ('id_usuario', 'id_rol')
