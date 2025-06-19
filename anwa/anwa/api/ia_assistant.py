# inventario/ia_assistant.py

import os
import json
from openai import OpenAI
from .models import Producto, Producto_Categoria, Pedido,Conversacion
from datetime import datetime, timedelta
client = OpenAI(api_key=os.getenv('OPENAI_KEY'))


# Lista de herramientas que la IA puede usar
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "obtener_lista_productos",
            "description": "Devuelve la lista de productos disponibles en el restaurante",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "obtener_productos_por_categoria",
        "description": "Devuelve los productos disponibles filtrados por categoría",
        "parameters": {
            "type": "object",
            "properties": {
                "categoria": {
                    "type": "string",
                    "description": "Nombre de la categoría, por ejemplo: Entrantes, Bebidas, Postres"
                }
            },
            "required": ["categoria"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "realizar_pedido",
        "description": "Registra un nuevo pedido del cliente. Si falta información como el nombre o dirección, el sistema pedirá esos datos al cliente. El total se calcula automáticamente según los productos pedidos.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre_cliente": {"type": "string"},
                "telefono": {"type": "string"},
                "direccion_domicilio": {"type": "string"},
                "metodo_pago": {"type": "string"},
                "detalles_pedido": {"type": "string"}
            }
            
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "consultar_estado_pedido",
        "description": "Consulta el estado actual de un pedido usando el número de teléfono del cliente",
        "parameters": {
            "type": "object",
            "properties": {
                "telefono": {"type": "string"}
            },
            "required": ["telefono"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "cancelar_pedido",
        "description": "Cancela un pedido en curso si no ha sido entregado",
        "parameters": {
            "type": "object",
            "properties": {
                "telefono": {"type": "string"},
                "motivo": {"type": "string", "description": "Razón por la cual se cancela el pedido"}
            },
            "required": ["telefono", "motivo"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "obtener_horario_atencion",
        "description": "Devuelve el horario de atención del restaurante",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "obtener_metodos_pago",
        "description": "Devuelve los métodos de pago aceptados por el restaurante",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}






]

def obtener_historial_conversacion(numero_telefono, limite_horas=24):
    """Obtiene el historial de conversación de las últimas X horas"""
    hace_x_horas = datetime.now() - timedelta(hours=limite_horas)
    conversaciones = Conversacion.objects.filter(
        numero_telefono=numero_telefono,
        fecha_hora__gte=hace_x_horas
    ).order_by('fecha_hora')
    
    historial = []
    for conv in conversaciones:
        role = "user" if conv.es_usuario else "assistant"
        historial.append({"role": role, "content": conv.mensaje})
    
    return historial

def guardar_mensaje_conversacion(numero_telefono, mensaje, es_usuario=True):
    """Guarda un mensaje en el historial de conversación"""
    Conversacion.objects.create(
        numero_telefono=numero_telefono,
        mensaje=mensaje,
        es_usuario=es_usuario
    )

def limpiar_conversaciones_antiguas():
    """Función para limpiar conversaciones más antiguas de 7 días"""
    hace_7_dias = datetime.now() - timedelta(days=7)
    Conversacion.objects.filter(fecha_hora__lt=hace_7_dias).delete()

def obtener_lista_productos():
    productos = Producto.objects.all()
    return [{"nombre": p.nombre, "precio": str(p.precio)} for p in productos]

def obtener_productos_por_categoria(categoria):
    try:
        cat = Producto_Categoria.objects.get(nombre__iexact=categoria)
        productos = Producto.objects.filter(categoria=cat, disponible=True)
        return [{"nombre": p.nombre, "precio": str(p.precio)} for p in productos]
    except Producto_Categoria.DoesNotExist:
        return []


def realizar_pedido(**params):
    faltantes = []
    for campo in ['nombre_cliente', 'telefono', 'direccion_domicilio', 'metodo_pago', 'detalles_pedido']:
        if campo not in params or not params[campo]:
            faltantes.append(campo)

    if faltantes:
        preguntas = {
            'nombre_cliente': "Por favor indícame tu nombre completo.",
            'telefono': "Por favor indícame tu número de contacto.",
            'direccion_domicilio': "Por favor indícame tu dirección de entrega.",
            'metodo_pago': "Por favor indícame el método de pago (Efectivo, Tarjeta, Transferencia).",
            'detalles_pedido': "Por favor dime qué deseas pedir."
        }
        return {"mensaje": "Necesito más información:\n" + "\n".join([preguntas[f] for f in faltantes])}

    # Calcular total automáticamente
    productos_pedidos = [p.strip() for p in params['detalles_pedido'].split(',')]
    total = 0
    productos_no_encontrados = []

    for nombre in productos_pedidos:
        try:
            producto = Producto.objects.get(nombre__iexact=nombre)
            total += float(producto.precio)
        except Producto.DoesNotExist:
            productos_no_encontrados.append(nombre)

    if productos_no_encontrados:
        return {"mensaje": f"Estos productos no fueron encontrados en el menú: {', '.join(productos_no_encontrados)}. Por favor verifica tu pedido."}

    if total == 0:
        return {"mensaje": "Por favor dime qué deseas pedir (producto válido del menú)."}

    # Crear el pedido
    pedido = Pedido.objects.create(
        nombre_cliente=params['nombre_cliente'],
        telefono=params['telefono'],
        direccion_domicilio=params['direccion_domicilio'],
        metodo_pago=params['metodo_pago'],
        detalles_pedido=params['detalles_pedido'],
        total=total,
        estado_pedido='recibido'
    )
    return {"mensaje": f"Pedido registrado exitosamente con ID: {pedido.id}. Total: ${total}"}



def consultar_estado_pedido(telefono):
    pedidos = Pedido.objects.filter(telefono=telefono).order_by('-fecha_hora')
    if pedidos.exists():
        ultimo_pedido = pedidos.first()
        return {"estado": ultimo_pedido.estado_pedido, "total": str(ultimo_pedido.total)}
    return {"mensaje": "No se encontró ningún pedido con este teléfono."}


def cancelar_pedido(telefono, motivo):
    pedidos = Pedido.objects.filter(telefono=telefono, estado_pedido__in=['en_preparacion', 'en_camino']).order_by('-fecha_hora')
    if pedidos.exists():
        pedido = pedidos.first()
        pedido.estado_pedido = 'cancelado'
        pedido.comentarios = (pedido.comentarios or '') + f"\nMotivo de cancelación: {motivo}"
        pedido.save()
        return {"mensaje": "Pedido cancelado exitosamente."}
    return {"mensaje": "No se encontró ningún pedido cancelable con este teléfono."}


def obtener_horario_atencion():
    return {"horario": "Lunes a Domingo, de 9:00 AM a 10:00 PM"}


def obtener_metodos_pago():
    return {"metodos": ["Efectivo", "Tarjeta", "Transferencia"]}




# 💬 Procesar mensaje del usuario
def procesar_mensaje_usuario(mensaje_usuario,numero_telefono):
    try:
        
        guardar_mensaje_conversacion(numero_telefono, mensaje_usuario, True) #Guarda el mensaje del usuario
        historial = obtener_historial_conversacion(numero_telefono) #Obtiene el historial de conversación
        
         # Construir mensajes para OpenAI incluyendo el historial
        mensajes = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente virtual del restaurante Anwa. "
                    "Recuerda el contexto de la conversación anterior con este cliente. "
                    "Si el cliente mencionó productos anteriormente o está en proceso de hacer un pedido, "
                    "ten en cuenta esa información. "
                    "Cuando el usuario mencione explícitamente un producto o desee ordenar/comprar/realizar un pedido, "
                    "usa la función 'realizar_pedido' con el producto mencionado en 'detalles_pedido'. "
                    "Si el usuario solicita solo ver el menú, usa 'obtener_lista_productos'. "
                    "Si el usuario pregunta por una categoría, usa 'obtener_productos_por_categoria'. "
                    "Mantén un tono amable y profesional."
                )
            }
        ]
        
        # Agregar el historial de conversación
        mensajes.extend(historial)
        
        # Siempre agregar el mensaje actual (ya está guardado en BD)
        # No agregamos aquí porque ya está incluido en el historial
        # El historial ya contiene el mensaje actual que acabamos de guardar
        print(mensajes)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensajes,
            tools=openai_tools,
            tool_choice="auto",
            max_tokens=500,
            temperature=0.2
        )
        choice = response.choices[0]
        respuesta_bot = ""

        # 7. Procesar respuesta (igual que antes)
        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                params = json.loads(tool_call.function.arguments)
                print(f"Tool call: {tool_call.function.name} with params: {params}")
                
                if tool_call.function.name == "obtener_lista_productos":
                    resultado = obtener_lista_productos()
                    respuesta_bot = "Productos disponibles:\n" + "\n".join([f"- {p['nombre']}: ${p['precio']}" for p in resultado])
                elif tool_call.function.name == "obtener_productos_por_categoria":
                    resultado = obtener_productos_por_categoria(params["categoria"])
                    if resultado:
                        respuesta_bot = f"Productos en la categoría {params['categoria']}:\n" + "\n".join([f"- {p['nombre']}: ${p['precio']}" for p in resultado])
                    else:
                        respuesta_bot = f"No hay productos en la categoría {params['categoria']}."
                elif tool_call.function.name == "realizar_pedido":
                    resultado = realizar_pedido(**params)
                    respuesta_bot = resultado["mensaje"]
                elif tool_call.function.name == "consultar_estado_pedido":
                    resultado = consultar_estado_pedido(params["telefono"])
                    respuesta_bot = resultado.get("mensaje") or f"Estado del pedido: {resultado['estado']}, Total: ${resultado['total']}"
                elif tool_call.function.name == "cancelar_pedido":
                    resultado = cancelar_pedido(params["telefono"], params["motivo"])
                    respuesta_bot = resultado["mensaje"]
                elif tool_call.function.name == "obtener_horario_atencion":
                    resultado = obtener_horario_atencion()
                    respuesta_bot = f"Nuestro horario de atención es: {resultado['horario']}."
                elif tool_call.function.name == "obtener_metodos_pago":
                    resultado = obtener_metodos_pago()
                    respuesta_bot = "Métodos de pago aceptados:\n" + ", ".join(resultado["metodos"])
        else:
            respuesta_bot = choice.message.content.strip()

        # 8. Guardar la respuesta del bot
        guardar_mensaje_conversacion(numero_telefono, respuesta_bot, False)
        
        return respuesta_bot
            
    except Exception as e:
        print(f"Error en OpenAI: {e}")
        return "Lo siento, no pude procesar tu mensaje en este momento."
