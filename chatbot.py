from openai import OpenAI
from controladores.models import Producto, Categoria
from app import db
import re  
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def obtener_contexto_desde_bd():
    productos = Producto.query.all()
    categorias = Categoria.query.all()

    contexto = "Información de la base de datos:\n\nPRODUCTOS:\n"
    for p in productos:
        contexto += f"- {p.Nombre_producto} | Precio: {p.Precio_Unitario} | Descuento: {p.Descuento}% | Categoría ID: {p.ID_Categoria}\n"

    contexto += "\nCATEGORÍAS:\n"
    for c in categorias:
        contexto += f"- {c.ID_Categoria}: {c.Nombre_categoria}\n"

    return contexto


  

def obtener_contexto_desde_bd():
    productos = Producto.query.all()
    categorias = Categoria.query.all()

    contexto = "Información de la base de datos:\n\nPRODUCTOS:\n"
    for p in productos:
        contexto += f"- {p.Nombre_producto} | Precio: {p.Precio_Unitario} | Descuento: {p.Descuento}% | Categoría ID: {p.ID_Categoria}\n"

    contexto += "\nCATEGORÍAS:\n"
    for c in categorias:
        contexto += f"- {c.ID_Categoria}: {c.Nombre_categoria}\n"

    return contexto


def preguntar_chatbot(pregunta):
    coincide = re.findall(r"\d+\.?\d*", pregunta)

    if "presupuesto" in pregunta.lower() or "comprar con" in pregunta.lower() or coincide:
        if coincide:
            presupuesto = coincide[0]
            respuesta = obtener_productos_por_presupuesto(presupuesto)
            if respuesta:
                return respuesta

    contexto_bd = obtener_contexto_desde_bd()
    info_negocio = obtener_informacion_negocio()
    recomendaciones = obtener_informacion_recomendaciones()

    prompt = f"""
Eres un asistente especializado en repostería y en la plataforma web.
Responde SOLO con la información proporcionada.
Si no hay información suficiente, dilo, pero NO inventes datos, 
los links proporcionados puede hacerlo activos para que el usuario solo tenga que hcaer click 
recuerdale a el usuario que copie y pegue el link en una pestaña difernete y sin los corchetes o los parentesis.

INFORMACIÓN DEL NEGOCIO:
{info_negocio}

RECOMENDACIONES:
{recomendaciones}

DATOS DE PRODUCTOS:
{contexto_bd}

Pregunta del usuario:
{pregunta}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def obtener_informacion_negocio():
    return """
INFORMACIÓN DEL NEGOCIO:

- Para comprar en línea debes registrarte con correo y contraseña. Puedes iniciar sesión desde el botón “Iniciar sesión”.
- Puedes personalizar tortas con nombre, sabor y diseño. La personalización requiere mínimo 48 horas de anticipación.
- Métodos de pago aceptados: Efectivo, Transferencia bancaria, Tarjeta y Nequi.
- Tiempos de entrega:
    * Pedidos normales: el mismo día si se realizan antes de las 2pm.
    * Pedidos personalizados: mínimo 48 horas.
- Si necesitas hablar con un asesor, puedes escribirnos por WhatsApp: https://wa.me/573178563246?text=Hola%2C%20quisiera%20más%20información
"""


def obtener_productos_por_presupuesto(presupuesto):
    try:
        presupuesto = float(presupuesto)
    except:
        return None

    productos = Producto.query.filter(Producto.Precio_Unitario <= presupuesto).all()

    if not productos:
        return f"No hay productos disponibles con un presupuesto de {presupuesto}."

    texto = f"Con {presupuesto} puedes comprar:\n"
    for p in productos:
        texto += f"- {p.Nombre_producto} (Precio: {p.Precio_Unitario})\n"

    return texto


def obtener_informacion_recomendaciones():
    return """
RECOMENDACIONES Y PRODUCTOS POPULARES:
- La torta de chocolate es el producto más vendido.
- La personalización más solicitada es “torta con nombre”.
- Las fresas con crema son populares para regalos pequeños.
- Para bodas, se suele pedir torta de tres pisos con crema chantillí.
"""
