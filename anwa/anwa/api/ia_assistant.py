# inventario/ia_assistant.py

import os
import json
from openai import OpenAI
from .models import Producto

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
    }
]

def obtener_lista_productos():
    productos = Producto.objects.all()
    return [{"nombre": p.nombre, "precio": str(p.precio)} for p in productos]



def procesar_mensaje_usuario(mensaje_usuario):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente virtual del restaurante Anwa. Solo respondes preguntas relacionadas "
                        "con el restaurante, como los productos disponibles, los precios, agendar o consultar pedidos, "
                        "horarios de atención, ubicación o métodos de pago. No respondes preguntas que no estén relacionadas "
                        "con el restaurante. Si el usuario pregunta algo fuera de contexto, responde de forma amable "
                        "que solo puedes ayudar con temas del restaurante."
                    )
                },
                {"role": "user", "content": mensaje_usuario}
            ],
            tools=openai_tools,
            tool_choice="auto"
        )

        choice = response.choices[0]

        # Si se invoca una función
        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "obtener_lista_productos":
                    resultado = obtener_lista_productos()
                    return "Estos son los productos disponibles:\n" + "\n".join(
                        [f"- {p['nombre']}: ${p['precio']}" for p in resultado]
                    )
        else:
            return choice.message.content.strip()

    except Exception as e:
        print(f"Error en OpenAI: {e}")
        return "Lo siento, no pude procesar tu mensaje en este momento."
