from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from dotenv import load_dotenv 

load_dotenv() #Carga las variables del archivo .env al entorno


app = Flask(__name__)

# Ampliamos CORS para que cubra las nuevas rutas de la API
CORS(app, resources={
    r"/contacto": {"origins": "http://127.0.0.1:5500"},
    r"/api/*": {"origins": "http://127.0.0.1:5500"}
})

STOCK_FILE = 'stock.json'
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def leer_stock():
    """Lee la base de datos de productos desde stock.json."""
    if not os.path.exists(STOCK_FILE):
        return []
    with open(STOCK_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def escribir_stock(data):
    """Escribe la base de datos de productos en stock.json."""
    with open(STOCK_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- NUEVA RUTA: Para que el frontend obtenga los productos ---
@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    productos = leer_stock()
    return jsonify(productos)

# --- NUEVA RUTA: Para actualizar el stock después de una compra ---
@app.route("/api/actualizar-stock", methods=["POST"])
def actualizar_stock_ruta():
    carrito = request.get_json()
    if not carrito:
        return jsonify({"success": False, "error": "No se recibió el carrito."}), 400

    stock_actual = leer_stock()
    
    for item_carrito in carrito:
        producto_en_stock = next((p for p in stock_actual if p['nombre'] == item_carrito['nombre']), None)
        if producto_en_stock:
            if producto_en_stock['stock'] >= item_carrito['cantidad']:
                producto_en_stock['stock'] -= item_carrito['cantidad']
            else:
                return jsonify({"success": False, "error": f"Stock insuficiente para {item_carrito['nombre']}"}), 400
        else:
            return jsonify({"success": False, "error": f"Producto no encontrado: {item_carrito['nombre']}"}), 404
            
    escribir_stock(stock_actual)
    return jsonify({"success": True, "message": "Stock actualizado correctamente."})

# --- RUTA DE CONTACTO ---
@app.route("/contacto", methods=["POST", "OPTIONS"])
def contacto():
    if request.method == "OPTIONS":
        return {"status": "ok"}, 200

    data = request.get_json()
    nombre = data.get("nombre", "")
    email = data.get("email", "")
    mensaje = data.get("mensaje", "")

    if not all([nombre, email, mensaje]):
        return {"success": False, "error": "Todos los campos son obligatorios."}, 400

 #Construcción del cuerpo del mensaje
    body = f"Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header("Nuevo mensaje de contacto", "utf-8")
    msg["From"] = formataddr((Header("Formulario Web", "utf-8").encode(), EMAIL_FROM))
    msg["To"] = EMAIL_TO


    # Lógica de envío de email...
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print("Mensaje de contacto enviado con éxito.")
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return {"success": False, "error": "No se pudo enviar el correo"}, 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)