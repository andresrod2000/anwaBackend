from rest_framework import serializers
from .models import (
    Usuario,
    Roles,
    Inventario,
    Categorias,
    Movimiento,
    Documento,
    Transaccion,
    Pedido,
)

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField() 
    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'nombre', 'telefono', 'direccion', 'password', 'roles','rol']  
        extra_kwargs = {'password': {'write_only': True}}  # Ocultar password en respuestas
    def get_rol(self, obj):
        return ", ".join(obj.roles.values_list('nombre', flat=True))  # Retorna los nombres de los roles como string separado por comas
    
    def create(self, validated_data):
        """Crear usuario asegurando que la contraseña sea hasheada y los roles se asignen correctamente"""
        roles_data = validated_data.pop('roles', [])  # Extraer roles antes de crear el usuario
        password = validated_data.pop('password', None)  # Extraer contraseña

        usuario = Usuario(**validated_data)  # Crear usuario sin roles
        if password:
            usuario.set_password(password)  # Hashear contraseña
        
        usuario.save()  # Guardar usuario antes de asignar roles

        usuario.roles.set(roles_data)  # Asignar roles correctamente

        return usuario




class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = '__all__'


class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = '__all__'


class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento
        fields = '__all__'


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = '__all__'


class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'
        
class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'fecha_hora', 'estado_pedido', 'direccion_domicilio']