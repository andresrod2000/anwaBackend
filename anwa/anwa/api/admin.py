from django.contrib import admin
from .models import Usuario,Inventario,Roles,Categorias,Documento,Transaccion # Asegúrate de que MiModelo esté en tu archivo models.py
from django.contrib import admin


# Registro simple del modelo
admin.site.register(Usuario)
admin.site.register(Inventario)
admin.site.register(Roles)
admin.site.register(Categorias)
admin.site.register(Documento)
admin.site.register(Transaccion)