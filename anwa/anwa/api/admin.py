from django.contrib import admin
from .models import Usuario,ModeloPrueba # Asegúrate de que MiModelo esté en tu archivo models.py
from django.contrib import admin


# Registro simple del modelo
admin.site.register(Usuario)
admin.site.register(ModeloPrueba)