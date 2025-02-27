from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, contrasena=None):
        """Crea un usuario normal con correo y contraseña"""
        if not correo:
            raise ValueError("El usuario debe tener un correo electrónico")
        
        usuario = self.model(correo=self.normalize_email(correo).lower(), nombre=nombre)
        
        if contrasena:  # Solo aplicar si hay contraseña
            usuario.set_password(contrasena)  # Hashea la contraseña
        
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo, nombre, password=None):
        """Crea un superusuario con todos los permisos"""
        usuario = self.create_user(correo, nombre, password)
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario



class Roles(models.Model):
    id = models.AutoField(primary_key=True)  # Definir el campo id correctamente
    nombre = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    correo = models.EmailField(unique=True)  # Identificador único para autenticación
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    roles = models.ManyToManyField(Roles, related_name='usuarios', blank=True)  # Múltiples roles por usuario

    is_active = models.BooleanField(default=True)  # Necesario para la autenticación
    is_staff = models.BooleanField(default=False)  # Define si puede acceder al admin

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="usuario_set",  # Evita conflicto con `auth.User.groups`
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="usuario_set",  # Evita conflicto con `auth.User.user_permissions`
        blank=True,
        help_text="Specific permissions for this user.",
    )

    objects = UsuarioManager()  # Define el gestor personalizado

    USERNAME_FIELD = 'correo'  # Se usa el correo para autenticación
    REQUIRED_FIELDS = ['nombre']  # Otros campos requeridos al crear usuario

    def __str__(self):
        return self.correo  # Representación en texto del usuario

class Clientes(models.Model):
    id = models.AutoField(primary_key=True)  # Definir el campo id correctamente
    nombre = models.CharField(max_length=255, unique=False)
    apellido = models.CharField(max_length=255, unique=False)
    correo = models.EmailField(unique=True) 
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion_principal = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre