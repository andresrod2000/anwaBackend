from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Inventario, Roles, Categorias, Documento, Transaccion, Movimiento,Pedido

class UsuarioAdmin(UserAdmin):
    ordering = ['id']
    list_display = ['correo', 'nombre', 'is_staff', 'is_superuser']
    search_fields = ['correo', 'nombre']
    fieldsets = (
        (None, {'fields': ('correo', 'nombre', 'password')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Información adicional', {'fields': ('telefono', 'direccion', 'roles')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'nombre', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

# Registrar modelos en el admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Inventario)
admin.site.register(Roles)
admin.site.register(Categorias)
admin.site.register(Documento)
admin.site.register(Transaccion)
admin.site.register(Movimiento)
admin.site.register(Pedido)