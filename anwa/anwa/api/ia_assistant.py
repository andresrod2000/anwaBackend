# inventario/ia_assistant.py

import os
import json
from openai import OpenAI
from .models import Producto, Producto_Categoria, Pedido,Conversacion
from datetime import datetime, timedelta
from django.conf import settings
client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def construir_url_absoluta(ruta_relativa):
    """Construye una URL absoluta para un archivo de medios"""
    if not ruta_relativa:
        return None
    
    # Obtener el dominio base desde settings o usar uno por defecto
    dominio_base = getattr(settings, 'DOMAIN_BASE', 'https://backend.anwa.pro')
    
    # Si la ruta ya es una URL completa, devolverla tal como está
    if ruta_relativa.startswith('http'):
        return ruta_relativa
    
    # Construir la URL absoluta
    return f"{dominio_base}{ruta_relativa}"

# Lista de herramientas que la IA puede usar
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "obtener_lista_productos",
            "description": "Devuelve la lista completa de productos disponibles. USA ESTA FUNCIÓN cuando el usuario pida ver el menú, productos disponibles, qué hay para comer, o similar.",
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
        "description": "Registra un nuevo pedido del cliente. USA ESTA FUNCIÓN cuando el usuario proporcione información de contacto (nombre, teléfono, dirección, método de pago). Los productos pueden estar en el mensaje actual o en mensajes anteriores. IMPORTANTE: En detalles_pedido usa EXACTAMENTE los nombres de productos del menú, sin cantidades ni artículos (ej: 'Perro Especial, Bebida Clásica' no '1 Perro Especial, 1 Bebida Clásica').",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre_cliente": {"type": "string"},
                "telefono": {"type": "string"},
                "direccion_domicilio": {"type": "string"},
                "metodo_pago": {"type": "string"},
                "detalles_pedido": {"type": "string", "description": "Nombres exactos de productos separados por comas, sin cantidades (ej: 'Perro Especial, Bebida Clásica')"}
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
},
{
    "type": "function",
    "function": {
        "name": "obtener_producto_especifico",
        "description": "Obtiene información detallada de un producto específico incluyendo su imagen. Usa esta función cuando el usuario pregunte por un producto en particular o quiera ver la foto de un producto específico.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre_producto": {
                    "type": "string",
                    "description": "Nombre del producto del cual se quiere obtener información"
                }
            },
            "required": ["nombre_producto"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "listar_pedidos_en_curso",
        "description": "Lista todos los pedidos en curso del cliente. Usa esta función cuando el usuario pregunte por 'mis pedidos en curso', 'qué pedidos tengo', 'todos mis pedidos', o similar.",
        "parameters": {
            "type": "object",
            "properties": {
                "telefono": {
                    "type": "string",
                    "description": "Número de teléfono del cliente"
                }
            },
            "required": ["telefono"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "confirmar_pedido",
        "description": "CONFIRMA O CANCELA un pedido pendiente. USA ESTA FUNCIÓN cuando: 1) Tu mensaje anterior mostró un resumen de pedido con ID, productos, total y preguntó '¿Confirmas este pedido?', Y 2) El usuario responde 'Sí', 'No', 'confirmo', 'cancelar'. NUNCA uses 'realizar_pedido' en este caso.",
        "parameters": {
            "type": "object",
            "properties": {
                "telefono": {
                    "type": "string",
                    "description": "Número de teléfono del cliente"
                },
                "confirmacion": {
                    "type": "string",
                    "description": "Respuesta del cliente: 'Sí', 'No', 'confirmo', 'cancelar', 'si', 'no', etc."
                }
            },
            "required": ["telefono", "confirmacion"]
        }
    }
}






]

def normalizar_telefono(telefono):
    """Normaliza el número de teléfono agregando el código de país si no está presente"""
    if not telefono:
        return telefono
    
    # Remover espacios y caracteres especiales
    telefono_limpio = ''.join(filter(str.isdigit, str(telefono)))
    
    # Si no empieza con 57 (código de Colombia), agregarlo
    if not telefono_limpio.startswith('57') and len(telefono_limpio) == 10:
        telefono_limpio = '57' + telefono_limpio
    
    return telefono_limpio

def obtener_historial_conversacion(numero_telefono, limite_horas=1, max_mensajes=8):
    """Obtiene el historial de conversación de las últimas X horas"""   
    hace_x_horas = datetime.now() - timedelta(hours=limite_horas)
    
    # Tomar los últimos mensajes y luego ordenarlos cronológicamente
    conversaciones = Conversacion.objects.filter(
        numero_telefono=numero_telefono,
        fecha_hora__gte=hace_x_horas
    ).order_by('-fecha_hora')[:max_mensajes]  # Últimos 8 mensajes
    
    # Revertir para orden cronológico (más antiguo → más reciente)
    conversaciones = reversed(list(conversaciones))
    
    historial = []
    for conv in conversaciones:
        role = "user" if conv.es_usuario else "assistant"
        historial.append({"role": role, "content": conv.mensaje})
    
    print(f"DEBUG: Historial construido con {len(historial)} mensajes")
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

def detectar_productos_en_historial(numero_telefono, limite_mensajes=3):
    """Detecta productos mencionados en los últimos mensajes del usuario"""
    conversaciones = Conversacion.objects.filter(
        numero_telefono=numero_telefono,
        es_usuario=True
    ).order_by('-fecha_hora')[:limite_mensajes]
    
    # Obtener todos los productos de la base de datos
    productos_db = Producto.objects.filter(disponible=True)
    productos_mentados = []
    
    for conv in conversaciones:
        mensaje = conv.mensaje.lower()
        
        # Buscar coincidencias con productos de la base de datos
        for producto in productos_db:
            nombre_producto = producto.nombre.lower()
            if nombre_producto in mensaje:
                productos_mentados.append(producto.nombre)
    
    return list(set(productos_mentados))  # Eliminar duplicados

def obtener_lista_productos():
    productos = Producto.objects.all()
    resultado = [{"nombre": p.nombre, "precio": str(p.precio)} for p in productos]
    print(f"DEBUG: obtener_lista_productos devolvió {len(resultado)} productos: {resultado}")
    return resultado

def obtener_productos_por_categoria(categoria):
    try:
        cat = Producto_Categoria.objects.get(nombre__iexact=categoria)
        productos = Producto.objects.filter(categoria=cat, disponible=True)
        return [{"nombre": p.nombre, "precio": str(p.precio)} for p in productos]
    except Producto_Categoria.DoesNotExist:
        return []


def realizar_pedido(**params):
    print(f"DEBUG: realizar_pedido llamado con parámetros: {params}")
    
    # Verificar que tengamos todos los datos necesarios
    # Ser más estricto: solo aceptar datos explícitamente proporcionados en este mensaje
    faltantes = []
    for campo in ['nombre_cliente', 'telefono', 'direccion_domicilio', 'metodo_pago']:
        if campo not in params or not params[campo] or params[campo].strip() == '':
            faltantes.append(campo)

    if faltantes:
        preguntas = {
            'nombre_cliente': "Por favor indícame tu nombre completo.",
            'telefono': "Por favor indícame tu número de contacto.",
            'direccion_domicilio': "Por favor indícame tu dirección de entrega.",
            'metodo_pago': "Por favor indícame el método de pago (Efectivo, Tarjeta, Transferencia)."
        }
        return {"mensaje": "Para procesar tu pedido necesito la siguiente información:\n" + "\n".join([preguntas[f] for f in faltantes])}

    # Si no hay detalles_pedido, buscar en el historial
    detalles_pedido = params.get('detalles_pedido', '').strip()
    if not detalles_pedido:
        productos_historial = detectar_productos_en_historial(params['telefono'])
        if productos_historial:
            detalles_pedido = ', '.join(productos_historial)
            print(f"DEBUG: Productos detectados en historial: {productos_historial}")
        else:
            return {"mensaje": "Por favor dime qué deseas pedir."}

    # Calcular total automáticamente
    productos_pedidos = [p.strip() for p in detalles_pedido.split(',')]
    total = 0
    productos_no_encontrados = []
    productos_encontrados = []

    for nombre in productos_pedidos:
        print(f"DEBUG: Buscando producto: '{nombre}'")
        
        try:
            producto = Producto.objects.get(nombre__iexact=nombre.strip())
            total += float(producto.precio)
            productos_encontrados.append({
                'nombre': producto.nombre,
                'precio': float(producto.precio)
            })
            print(f"DEBUG: Producto encontrado: {producto.nombre} - ${producto.precio}")
        except Producto.DoesNotExist:
            productos_no_encontrados.append(nombre)
            print(f"DEBUG: Producto NO encontrado: '{nombre}'")

    if productos_no_encontrados:
        return {"mensaje": f"Estos productos no fueron encontrados en el menú: {', '.join(productos_no_encontrados)}. Por favor verifica tu pedido."}

    if total == 0:
        return {"mensaje": "Por favor dime qué deseas pedir (producto válido del menú)."}

    # Crear el pedido con estado 'pendiente'
    pedido = Pedido.objects.create(
        nombre_cliente=params['nombre_cliente'],
        telefono=params['telefono'],
        direccion_domicilio=params['direccion_domicilio'],
        metodo_pago=params['metodo_pago'],
        detalles_pedido=detalles_pedido,
        total=total,
        estado_pedido='pendiente'
    )

    # SIEMPRE mostrar resumen y pedir confirmación
    resumen = "🍽️ *Resumen de tu pedido:*\n\n"
    #resumen += f"🆔 *Pedido #{pedido.id}*\n"
    resumen += f"👤 *Cliente:* {params['nombre_cliente']}\n"
    resumen += f"📞 *Teléfono:* {params['telefono']}\n"
    resumen += f"📍 *Dirección:* {params['direccion_domicilio']}\n"
    resumen += f"💳 *Método de pago:* {params['metodo_pago']}\n\n"
    
    resumen += "🍔 *Productos:*\n"
    for producto in productos_encontrados:
        resumen += f"• {producto['nombre']}: ${producto['precio']:,.0f}\n"
    
    resumen += f"\n💰 *Total:* ${total:,.0f}\n\n"
    resumen += "¿Confirmas este pedido? Responde 'Sí' o 'No'."

    return {"mensaje": resumen}



def consultar_estado_pedido(telefono):
    """Consulta el estado del último pedido realizado"""
    pedidos = Pedido.objects.filter(telefono=telefono).order_by('-fecha_hora')
    if pedidos.exists():
        ultimo_pedido = pedidos.first()
        
        # Mapear estados a mensajes más amigables
        estados_amigables = {
            'recibido': '📋 Recibido - Tu pedido ha sido confirmado',
            'en_preparacion': '👨‍🍳 En preparación - Estamos cocinando tu pedido',
            'en_camino': '🚚 En camino - Tu pedido está siendo entregado',
            'entregado': '✅ Entregado - Tu pedido ha sido entregado',
            'cancelado': '❌ Cancelado - Tu pedido ha sido cancelado'
        }
        
        estado_amigable = estados_amigables.get(ultimo_pedido.estado_pedido, ultimo_pedido.estado_pedido)
        
        return {
            "id": ultimo_pedido.id,
            "fecha": ultimo_pedido.fecha_hora.strftime("%d/%m/%Y a las %H:%M"),
            "estado": ultimo_pedido.estado_pedido,
            "estado_amigable": estado_amigable,
            "total": str(ultimo_pedido.total),
            "detalles": ultimo_pedido.detalles_pedido,
            "nombre_cliente": ultimo_pedido.nombre_cliente
        }
    return {"mensaje": "No se encontró ningún pedido con este teléfono."}

def listar_pedidos_en_curso(telefono):
    """Lista todos los pedidos en curso (recibido, en_preparacion, en_camino)"""
    pedidos = Pedido.objects.filter(
        telefono=telefono,
        estado_pedido__in=['recibido', 'en_preparacion', 'en_camino']
    ).order_by('-fecha_hora')
    
    if pedidos.exists():
        lista_pedidos = []
        for pedido in pedidos:
            lista_pedidos.append({
                "id": pedido.id,
                "fecha": pedido.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                "estado": pedido.estado_pedido,
                "total": str(pedido.total),
                "detalles": pedido.detalles_pedido
            })
        return {"pedidos": lista_pedidos}
    return {"mensaje": "No tienes pedidos en curso actualmente."}

def cancelar_pedido(telefono, motivo):
    # Buscar el pedido más reciente que esté en preparación o en camino
    pedidos = Pedido.objects.filter(
        telefono=telefono, 
        estado_pedido__in=['recibido', 'en_preparacion', 'en_camino']
    ).order_by('-fecha_hora')
    
    if pedidos.exists():
        pedido = pedidos.first()  # Ahora sí toma el más reciente (ordenado por -fecha_hora)
        pedido.estado_pedido = 'cancelado'
        pedido.comentarios = (pedido.comentarios or '') + f"\nMotivo de cancelación: {motivo}"
        pedido.save()
        return {"mensaje": f"Pedido #{pedido.id} cancelado exitosamente."}
    return {"mensaje": "No se encontró ningún pedido cancelable con este teléfono."}


def obtener_horario_atencion():
    return {"horario": "Lunes a Domingo, de 9:00 AM a 10:00 PM"}


def obtener_metodos_pago():
    return {"metodos": ["Efectivo", "Tarjeta", "Transferencia"]}


def obtener_producto_especifico(nombre_producto):
    """Obtiene información detallada de un producto específico"""
    try:
        producto = Producto.objects.get(nombre__iexact=nombre_producto)
        return {
            "nombre": producto.nombre,
            "precio": str(producto.precio),
            "descripcion": producto.descripcion or "Sin descripción disponible",
            "imagen": construir_url_absoluta(producto.imagen.url) if producto.imagen else None,
            "categoria": producto.categoria.nombre if producto.categoria else "Sin categoría",
            "disponible": producto.disponible
        }
    except Producto.DoesNotExist:
        return None

# 💬 Procesar mensaje del usuario
def procesar_mensaje_usuario(mensaje_usuario,numero_telefono):
    try:
        
        print(f"DEBUG: Mensaje del usuario recibido: '{mensaje_usuario}'")
        
        guardar_mensaje_conversacion(numero_telefono, mensaje_usuario, True) #Guarda el mensaje del usuario
        historial = obtener_historial_conversacion(numero_telefono) #Obtiene el historial de conversación
        
         # Construir mensajes para OpenAI incluyendo el historial
        mensajes = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente virtual del restaurante Anwa. "
                    "IMPORTANTE: Siempre usa las funciones disponibles en lugar de generar respuestas manuales. "
                    
                    "REGLA CRÍTICA: Antes de elegir una función, revisa tu mensaje anterior. "
                    "Si tu mensaje anterior contenía un resumen de pedido (con ID de pedido, productos, total y '¿Confirmas este pedido?'), "
                    "y el usuario responde 'Sí', 'No', 'confirmo', etc., SIEMPRE usa 'confirmar_pedido'. "
                    "NO uses 'realizar_pedido' si ya existe un resumen pendiente de confirmación. "
                    
                    "Usa 'obtener_lista_productos' cuando el usuario pida ver el menú. "
                    "Usa 'realizar_pedido' SOLO para crear nuevos pedidos (primera vez con datos de contacto). "
                    "Usa 'confirmar_pedido' para confirmar/cancelar pedidos después de mostrar resumen. "
                    "Usa 'consultar_estado_pedido' cuando pregunte por el estado. "
                    "Usa 'obtener_producto_especifico' para productos específicos. "
                    "Mantén un tono amable y profesional."
                )
            }
        ]
        
        # Agregar el historial de conversación
        mensajes.extend(historial)
        
        # Siempre agregar el mensaje actual (ya está guardado en BD)
        # No agregamos aquí porque ya está incluido en el historial
        # El historial ya contiene el mensaje actual que acabamos de guardar
        #print(mensajes)
        print(f"DEBUG: Enviando a OpenAI - Mensaje: '{mensaje_usuario}'")
        print(f"DEBUG: Historial de conversación: {len(historial)} mensajes")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensajes,
            tools=openai_tools,
            tool_choice="auto",
            max_tokens=1000,
            temperature=0.0
        )
        choice = response.choices[0]
        respuesta_bot = ""
        imagenes_productos = []  # Lista para almacenar URLs de imágenes
        nombre_producto = None  # Para almacenar el nombre del producto cuando se consulta uno específico

        # Debug: Imprimir el finish_reason
        print(f"Finish reason: {choice.finish_reason}")
        print(f"Message content: {choice.message.content}")
        if choice.message.tool_calls:
            print(f"Tool calls: {choice.message.tool_calls}")
            print(f"Number of tool calls: {len(choice.message.tool_calls)}")
        else:
            print("DEBUG: No se usaron herramientas")
            print(f"DEBUG: Mensaje del usuario: '{mensaje_usuario}'")

        # 7. Procesar respuesta (igual que antes)
        if choice.finish_reason == "tool_calls":
            # Solo procesar la primera función call para evitar confirmaciones automáticas
            tool_call = choice.message.tool_calls[0]
            params = json.loads(tool_call.function.arguments)
            print(f"Tool call: {tool_call.function.name} with params: {params}")
            print(f"Processing tool call: {tool_call.function.name}")
            
            # Para funciones que usan teléfono, usar el número del webhook
            if tool_call.function.name in ["realizar_pedido", "consultar_estado_pedido", "listar_pedidos_en_curso", "cancelar_pedido", "confirmar_pedido"]:
                if 'telefono' in params:
                    # Reemplazar el teléfono del usuario con el del webhook
                    params['telefono'] = numero_telefono
                    print(f"DEBUG: Reemplazando teléfono del usuario '{params.get('telefono', 'N/A')}' con número del webhook: {numero_telefono}")
            
            if tool_call.function.name == "obtener_lista_productos":
                resultado = obtener_lista_productos()
                print(f"DEBUG: Resultado de obtener_lista_productos: {resultado}")
                respuesta_bot = "Productos disponibles:\n" + "\n".join([f"- {p['nombre']}: ${p['precio']}" for p in resultado])
                print(f"DEBUG: Respuesta formateada: '{respuesta_bot}'")
                # No hay imágenes en la lista general de productos
                imagenes_productos = []
            elif tool_call.function.name == "obtener_productos_por_categoria":
                resultado = obtener_productos_por_categoria(params["categoria"])
                if resultado:
                    respuesta_bot = f"Productos en la categoría {params['categoria']}:\n" + "\n".join([f"- {p['nombre']}: ${p['precio']}" for p in resultado])
                    # No hay imágenes en la lista por categoría
                    imagenes_productos = []
                else:
                    respuesta_bot = f"No hay productos en la categoría {params['categoria']}."
                    imagenes_productos = []
            elif tool_call.function.name == "realizar_pedido":
                print(f"DEBUG: Procesando realizar_pedido - NUEVO pedido")
                print(f"DEBUG: Parámetros recibidos: {params}")
                resultado = realizar_pedido(**params)
                print(f"DEBUG: Resultado de realizar_pedido: {resultado}")
                respuesta_bot = resultado["mensaje"]
                print(f"DEBUG: Respuesta final: {respuesta_bot}")
            elif tool_call.function.name == "consultar_estado_pedido":
                print(f"DEBUG: Procesando consultar_estado_pedido con teléfono: {params['telefono']}")
                resultado = consultar_estado_pedido(params["telefono"])
                print(f"DEBUG: Resultado de consultar_estado_pedido: {resultado}")
                if "mensaje" in resultado:
                    respuesta_bot = resultado["mensaje"]
                else:
                    respuesta_bot = f"📋 *Estado de tu pedido:*\n\n"
                    respuesta_bot += f"🆔 *Pedido #{resultado['id']}*\n"
                    respuesta_bot += f"👤 Cliente: {resultado['nombre_cliente']}\n"
                    respuesta_bot += f"📅 Fecha: {resultado['fecha']}\n"
                    respuesta_bot += f"📊 Estado: {resultado['estado_amigable']}\n"
                    respuesta_bot += f"💰 Total: ${resultado['total']}\n"
                    respuesta_bot += f"🍽️ Detalles: {resultado['detalles']}\n\n"
                    
                    # Agregar mensaje adicional según el estado
                    if resultado['estado'] == 'recibido':
                        respuesta_bot += "⏰ Tu pedido será preparado pronto. ¡Gracias por tu paciencia!"
                    elif resultado['estado'] == 'en_preparacion':
                        respuesta_bot += "🔥 Tu pedido está siendo preparado con mucho amor. ¡No tardará!"
                    elif resultado['estado'] == 'en_camino':
                        respuesta_bot += "🚚 ¡Tu pedido está en camino! Prepárate para disfrutar."
                    elif resultado['estado'] == 'entregado':
                        respuesta_bot += "🎉 ¡Disfruta tu comida! ¡Esperamos verte pronto!"
                    elif resultado['estado'] == 'cancelado':
                        respuesta_bot += "😔 Lamentamos que hayas cancelado. ¡Esperamos verte en otra ocasión!"
                print(f"DEBUG: Respuesta final: {respuesta_bot}")
            elif tool_call.function.name == "listar_pedidos_en_curso":
                resultado = listar_pedidos_en_curso(params["telefono"])
                if "pedidos" in resultado:
                    respuesta_bot = "📋 *Tus pedidos en curso:*\n\n"
                    for pedido in resultado["pedidos"]:
                        respuesta_bot += f"• *Pedido #{pedido['id']}*\n"
                        respuesta_bot += f"📅 Fecha: {pedido['fecha']}\n"
                        respuesta_bot += f"📊 Estado: {pedido['estado']}\n"
                        respuesta_bot += f"💰 Total: ${pedido['total']}\n"
                        respuesta_bot += f"🍽️ Detalles: {pedido['detalles']}\n\n"
                else:
                    respuesta_bot = resultado["mensaje"]
            elif tool_call.function.name == "cancelar_pedido":
                resultado = cancelar_pedido(params["telefono"], params["motivo"])
                respuesta_bot = resultado["mensaje"]
            elif tool_call.function.name == "obtener_horario_atencion":
                resultado = obtener_horario_atencion()
                respuesta_bot = f"Nuestro horario de atención es: {resultado['horario']}."
            elif tool_call.function.name == "obtener_metodos_pago":
                resultado = obtener_metodos_pago()
                respuesta_bot = "Métodos de pago aceptados:\n" + ", ".join(resultado["metodos"])
            elif tool_call.function.name == "obtener_producto_especifico":
                resultado = obtener_producto_especifico(params["nombre_producto"])
                if resultado:
                    respuesta_bot = f"🍔 *{resultado['nombre']}*\n"
                    respuesta_bot += f"💰 Precio: ${resultado['precio']}\n"
                    respuesta_bot += f"📝 Descripción: {resultado['descripcion']}\n"
                    respuesta_bot += f"📂 Categoría: {resultado['categoria']}\n"
                    respuesta_bot += f"✅ Disponible: {'Sí' if resultado['disponible'] else 'No'}"
                    # Extraer URL de imagen
                    imagenes_productos = [resultado.get("imagen")] if resultado.get("imagen") else []
                    nombre_producto = resultado['nombre']
                else:
                    respuesta_bot = f"❌ No se encontró el producto '{params['nombre_producto']}'. Por favor verifica el nombre del producto."
                    imagenes_productos = []
            elif tool_call.function.name == "confirmar_pedido":
                print(f"DEBUG: Procesando confirmar_pedido - confirmación de pedido existente")
                print(f"DEBUG: Confirmación recibida: '{params['confirmacion']}'")
                resultado = confirmar_pedido(params["telefono"], params["confirmacion"])
                print(f"DEBUG: Resultado de confirmar_pedido: {resultado}")
                respuesta_bot = resultado["mensaje"]
        else:
            print("DEBUG: No se usaron herramientas, generando respuesta manual")
            respuesta_bot = choice.message.content.strip()
            print(f"DEBUG: Respuesta manual generada: {respuesta_bot}")

        # 8. Guardar la respuesta del bot
        guardar_mensaje_conversacion(numero_telefono, respuesta_bot, False)
        
        # Devolver tanto el texto como las imágenes
        return {"texto": respuesta_bot, "imagenes": imagenes_productos, "nombre_producto": nombre_producto}
            
    except Exception as e:
        print(f"Error en OpenAI: {e}")
        return {"texto": "Lo siento, no pude procesar tu mensaje en este momento.", "imagenes": [], "nombre_producto": None}

def confirmar_pedido(telefono, confirmacion):
    """Confirma o cancela un pedido pendiente"""
    print(f"DEBUG: confirmar_pedido llamado con teléfono: {telefono}, confirmación: '{confirmacion}'")
    
    # Buscar el último pedido pendiente de este teléfono
    pedidos_pendientes = Pedido.objects.filter(
        telefono=telefono,
        estado_pedido='pendiente'
    ).order_by('-fecha_hora')
    
    print(f"DEBUG: Pedidos pendientes encontrados: {pedidos_pendientes.count()}")
    
    if not pedidos_pendientes.exists():
        # Si no hay pedidos pendientes, buscar el último pedido en general
        ultimo_pedido = Pedido.objects.filter(telefono=telefono).order_by('-fecha_hora').first()
        if ultimo_pedido:
            print(f"DEBUG: No hay pedidos pendientes, último pedido encontrado: #{ultimo_pedido.id} con estado: {ultimo_pedido.estado_pedido}")
            if ultimo_pedido.estado_pedido == 'pendiente':
                # Caso edge: el pedido podría haber sido creado justo antes
                pedido = ultimo_pedido
            else:
                return {"mensaje": "No tienes pedidos pendientes de confirmación. ¿Te gustaría hacer un nuevo pedido?"}
        else:
            return {"mensaje": "No se encontraron pedidos con este número de teléfono. ¿Te gustaría hacer un nuevo pedido?"}
    else:
        pedido = pedidos_pendientes.first()
        print(f"DEBUG: Pedido pendiente encontrado: #{pedido.id}")
    
    if confirmacion.lower() in ['sí', 'si', 'yes', 'confirmo', 'confirmar']:
        pedido.estado_pedido = 'recibido'
        pedido.save()
        print(f"DEBUG: Pedido #{pedido.id} confirmado exitosamente")
        return {"mensaje": f"✅ Pedido #{pedido.id} confirmado exitosamente. Total: ${pedido.total:,.0f}"}
    else:
        pedido.estado_pedido = 'cancelado'
        pedido.comentarios = "Pedido cancelado por el cliente"
        pedido.save()
        print(f"DEBUG: Pedido #{pedido.id} cancelado")
        return {"mensaje": "❌ Pedido cancelado. ¡Esperamos verte en otra ocasión!"}
