from rest_framework import viewsets, permissions,mixins,status
from rest_framework.response import Response
from rest_framework.decorators import action
import requests
from rest_framework.views import APIView
from rest_framework import generics
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
import os
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from .ia_assistant import procesar_mensaje_usuario
import subprocess 
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
from .serializers import (
    UsuarioSerializer,
    RolesSerializer,
    InventarioSerializer,
    CategoriasSerializer,
    MovimientoSerializer,
    DocumentoSerializer,
    TransaccionSerializer,
    PedidoSerializer,
    PedidoSerializerAdmin,
    PedidoEstadoSerializer,
    ProductoSerializer,
    CategoriasProductoSerializer
)

class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer

class StrictDjangoModelPermissions(permissions.DjangoModelPermissions):
    """
    Versión más estricta de DjangoModelPermissions que bloquea usuarios sin permisos asignados.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False  # 🔹 Bloquea usuarios no autenticados

        if not request.user.user_permissions.exists() and not request.user.groups.exists():
            return False  # 🔹 Bloquea usuarios sin permisos asignados

        return super().has_permission(request, view)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [StrictDjangoModelPermissions] 

class PerfilViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  # 🔹 Permite acceso solo a usuarios autenticados

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Devuelve los datos del usuario autenticado"""
        print(f"🔍 Intento de acceso a /user/ por: {request.user}")
        usuario = request.user
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)


class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categorias.objects.all()
    serializer_class = CategoriasSerializer


class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer


class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer

def get_phrase_of_the_day(request):
    url = "https://frasedeldia.azurewebsites.net/api/phrase"  # URL de la API original

    try:
        response = requests.get(url)  # Hacer la solicitud a la API original
        data = response.json()  # Convertir la respuesta a JSON
        return JsonResponse(data)  # Devolver la respuesta JSON
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Error fetching the phrase"}, status=500)


class PedidoEnProcesoListView(generics.ListAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.AllowAny] #SOLO PARA TESTAR


    def get_queryset(self):
        return Pedido.objects.filter(estado_pedido__in=['en_preparacion', 'en_camino'])
    


class PedidoViewSet(viewsets.ModelViewSet):
    """Vista para manejar pedidos con permisos diferenciados"""
    queryset = Pedido.objects.all()

    def get_serializer_class(self):
        """Determina qué serializer usar según la acción y el usuario"""
        if self.action == 'partial_update':  # Si es un PATCH, verificar permisos
            user = self.request.user
            if user.groups.filter(name="Meseros").exists():  # Si es mesero
                return PedidoEstadoSerializer  # Solo puede modificar estado
        return PedidoSerializerAdmin  # Para todas las demás acciones

    def get_permissions(self):
        """Define los permisos según el rol"""
        user = self.request.user

        if user.is_superuser:  # Admins pueden hacer todo
            return [permissions.AllowAny()]
        
        if user.groups.filter(name="Meseros").exists():  # Si es mesero
            if self.action in ['list', 'create', 'partial_update']:  # Puede ver, crear y modificar estado
                return [permissions.IsAuthenticated()]
            return [permissions.DenyAny()]  # No puede eliminar ni modificar otros campos
        
        return [permissions.IsAuthenticated()]  # Otros usuarios autenticados pueden listar
    
class ProductoListView(APIView):
    permission_classes = [AllowAny]  # Permitir acceso público

    def get(self, request):
        productos = Producto.objects.all()  # Obtiene todos los productos
        serializer = ProductoSerializer(productos, many=True)  # Serializa los datos
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class ProductoViewSet(viewsets.ModelViewSet):

    """Vista para manejar pedidos con permisos diferenciados"""
    queryset = Producto.objects.all()

    def get_serializer_class(self):
        """Determina qué serializer usar según la acción y el usuario"""
        if self.action == 'partial_update':  # Si es un PATCH, verificar permisos
            user = self.request.user
            if user.groups.filter(name="Meseros").exists():  # Si es mesero
                return ProductoSerializer  # Solo puede modificar estado
        return ProductoSerializer  # Para todas las demás acciones

    def get_permissions(self):
        """Define los permisos según el rol"""
        user = self.request.user

        if user.is_superuser:  # Admins pueden hacer todo
            return [permissions.AllowAny()]
        
        if user.groups.filter(name="Meseros").exists():  # Si es mesero
            if self.action in ['list', 'create', 'partial_update']:  # Puede ver, crear y modificar estado
                return [permissions.IsAuthenticated()]
            return [permissions.DenyAny()]  # No puede eliminar ni modificar otros campos
        
        return [permissions.IsAuthenticated()] 
    
VERIFY_TOKEN = os.getenv('META_TOKEN')

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
WHATSAPP_API_URL = "https://graph.facebook.com/v16.0/644996585368566/messages"
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_TOKEN')
client = OpenAI(api_key=OPENAI_API_KEY)
def generar_respuesta_openai(mensaje_usuario):
    prompt = f"Actúa como asistente para un restaurante llamado Anwa. El usuario dice: '{mensaje_usuario}'. Responde de forma clara y amable. SOLO RESPONDE A PREGUNTA SOBRE EL RESTAURANTE ANWA. NO DES INFORMACION PERSONAL NI DE OTROS TEMAS. NO DIGAS QUE ERES UN ASISTENTE VIRTUAL. SOLO RESPONDE CON LA RESPUESTA A LA PREGUNTA DEL USUARIO."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # o "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )
        # La respuesta viene en response.choices[0].message.content
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error en OpenAI: {e}")
        return "Lo siento, tuve un problema al procesar tu mensaje."

def enviar_mensaje_whatsapp(numero, texto):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {"body": texto},
        "type": "text"
    }
    try:
        r = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
        r.raise_for_status()
        print(f"Mensaje enviado a {numero}")
    except Exception as e:
        print(f"Error enviando mensaje WhatsApp: {e}")


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge)
        else:
            return HttpResponse("Forbidden", status=403)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            mensajes = data["entry"][0]["changes"][0]["value"].get("messages")
            if mensajes:
                mensaje = mensajes[0]["text"]["body"]
                numero = mensajes[0]["from"]
                print(f"Mensaje recibido de {numero}: {mensaje}")
                if 'ACTUALIZARTOKEN'in mensaje and numero == '573178231809':
                    try:
                        ruta_archivo = "/etc/systemd/system/django.service"
                        new_token = mensaje.split('ACTUALIZARTOKEN=')[1].strip()
                        nueva_linea = f'Environment="WHATSAPP_TOKEN={new_token}"'
                        # Leer el archivo completo
                        with open(ruta_archivo, "r") as file:
                            lineas = file.readlines()

                        # Actualizar la línea
                        for i, linea in enumerate(lineas):
                            if 'Environment="WHATSAPP_TOKEN=' in linea:
                                lineas[i] = nueva_linea + "\n"
                                break

                        contenido = ''.join(lineas)

                        # Escribir con sudo tee para evitar problema de permisos
                        proc = subprocess.Popen(['sudo', 'tee', ruta_archivo], stdin=subprocess.PIPE)
                        proc.communicate(input=contenido.encode())

                        print("Token actualizado correctamente.")
                        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
                        print("Systemd recargado y servicio reiniciado con éxito.")
                        subprocess.run(["sudo", "systemctl", "restart", "django.service"], check=True)
                        

                   
                    except Exception as e:
                        print(f"Error al actualizar el archivo de servicio: {e}")
                    return HttpResponse("Token Actualizado", status=200)
                else:
                    # Generar respuesta con OpenAI
                    #respuesta = generar_respuesta_openai(mensaje)
                    respuesta = procesar_mensaje_usuario(mensaje)
                    print(respuesta)

                    # Enviar respuesta al usuario vía WhatsApp
                    enviar_mensaje_whatsapp(numero, respuesta)
            else:
                print("No hay mensajes en la actualización recibida.")
        except Exception as e:
            print(f"Error procesando mensaje: {e}")

        return HttpResponse("EVENT_RECEIVED", status=200)
    
class CategoriasProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Producto_Categoria.objects.all()
    serializer_class = CategoriasProductoSerializer