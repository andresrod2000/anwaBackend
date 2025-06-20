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
    Producto,
    Producto_Categoria
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
        fields = ['nombre_cliente', 'telefono', 'direccion_domicilio', 'metodo_pago', 'estado_pedido', 'detalles_pedido', 'total', 'comentarios']

# Serializer completo (para admins)
class PedidoSerializerAdmin(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'  # Admins pueden ver y modificar todo

# Serializer restringido (para meseros)
class PedidoEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['estado_pedido']  # Meseros solo pueden modificar el estado

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'

    def get_categoria_nombre(self, obj):
        return obj.categoria.nombre if obj.categoria else None
    

class CategoriasProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto_Categoria
        fields = '__all__'