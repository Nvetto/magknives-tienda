import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from dotenv import load_dotenv
import pyodbc
from werkzeug.security import check_password_hash # Para verificar la contraseña
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required # La nueva librería
from flask import abort
from functools import wraps
from flask_login import current_user

load_dotenv()

app = Flask(__name__, template_folder='../templates')

app.secret_key = os.getenv("SECRET_KEY")

@app.after_request
def add_header(response):
    """
    Añade cabeceras para prevenir que el navegador guarde en caché las respuestas de la API.
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Configuración de CORS
CORS(app, resources={
     r"/login": {"origins": "http://127.0.0.1:5500","supports_credentials": True},
    r"/logout": {"origins": "http://127.0.0.1:5500","supports_credentials": True}, 
    r"/contacto": {"origins": "http://127.0.0.1:5500"},
    r"/api/*": {"origins": "http://127.0.0.1:5500", "supports_credentials": True}
})

# Obtenemos las variables de entorno
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Obtenemos la nueva cadena de conexión a la base de datos
DB_CONNECTION_STRING = os.getenv("DATABASE_CONNECTION_STRING")

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Si un usuario no logeado intenta acceder a una página protegida, lo redirige aquí

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si el usuario no está logeado, Flask-Login lo maneja como siempre
        if not current_user.is_authenticated:
            return login_manager.unauthorized()

        # Si está logeado, verificamos su rol en la base de datos
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        # Buscamos si el usuario actual tiene el rol 'admin' (RolID = 1)
        sql_query = "SELECT 1 FROM UsuarioRoles WHERE UsuarioID = ? AND RolID = 1"
        cursor.execute(sql_query, current_user.id)
        is_admin = cursor.fetchone()
        conn.close()

        # Si la consulta no devuelve nada, el usuario no es admin
        if not is_admin:
            abort(403)  # Error "Forbidden": no tienes permiso para ver esto

        # Si es admin, le dejamos pasar a la ruta original
        return f(*args, **kwargs)
    return decorated_function

# Creo una clase 'User' que Flask-Login puede entender
class User(UserMixin):
    def __init__(self, id, email, nombre):
        self.id = id
        self.email = email
        self.nombre = nombre

# Esta función le dice a Flask-Login cómo encontrar a un usuario por su ID
@login_manager.user_loader
def load_user(user_id):
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("SELECT UsuarioID, Email, Nombre FROM Usuarios WHERE UsuarioID = ?", user_id)
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(id=user_data.UsuarioID, email=user_data.Email, nombre=user_data.Nombre)
    return None

# --- RUTA PARA OBTENER PRODUCTOS (MODIFICADA) ---
@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    productos_dict = {} # Usaremos un diccionario para agrupar las imágenes por producto

    try:
        # Nos conectamos a la base de datos usando la cadena de conexión
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Ejecutamos una consulta SQL que une Productos con sus Imágenes
        # sql_query = "EXEC usp_ObtenerTodosLosProductos;"
        sql_query = """
            SELECT p.ProductoID, p.Nombre, p.Descripcion, p.Precio, p.Stock, p.Categoria, i.URL
            FROM Productos p
            LEFT JOIN ImagenesProducto i ON p.ProductoID = i.ProductoID
            ORDER BY p.ProductoID;
        """
        cursor.execute(sql_query)
        
        # Procesamos las filas que nos devuelve la base de datos
        for row in cursor.fetchall():
            producto_id = row.ProductoID
            # Si es la primera vez que vemos este producto, creamos su entrada
            if producto_id not in productos_dict:
                productos_dict[producto_id] = {
                    "nombre": row.Nombre,
                    "descripcion": row.Descripcion,
                    "precio": float(row.Precio), # Convertimos de Decimal a float
                    "stock": row.Stock,
                    "categoria": row.Categoria,
                    "imagenes": []
                }
            # Añadimos la URL de la imagen a la lista de imágenes del producto
            if row.URL:
                productos_dict[producto_id]["imagenes"].append(row.URL)

    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    finally:
        #Cerramos la conexión a la base de datos
        if 'conn' in locals() and conn:
            conn.close()

    # Convertimos el diccionario de productos en una lista y la devolvemos como JSON
    lista_productos = list(productos_dict.values())
    return jsonify(lista_productos)


# --- NUEVA RUTA PARA CERRAR SESIÓN ---
@app.route('/logout')
@login_required # Solo un usuario logueado puede cerrar sesión
def logout():
    logout_user() # Esta función de Flask-Login limpia la sesión del usuario
    return jsonify({"success": True, "message": "Sesión cerrada correctamente."})


# --- NUEVAS RUTAS PARA AUTENTICACIÓN ---
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("SELECT UsuarioID, Email, Nombre, HashContrasena FROM Usuarios WHERE Email = ?", email)
    user_data = cursor.fetchone()
    conn.close()

    if user_data and check_password_hash(user_data.HashContrasena, password):
        # Si las credenciales son correctas, creamos el usuario y la sesión
        user = User(id=user_data.UsuarioID, email=user_data.Email, nombre=user_data.Nombre)
        login_user(user)
        # Devolvemos una respuesta de éxito en JSON
        return jsonify({"success": True, "nombre": user.nombre})
    else:
        # Si las credenciales son incorrectas, devolvemos un error en JSON
        return jsonify({"success": False, "error": "Email o contraseña incorrectos"})


    # --- RUTA PROTEGIDA PARA EL PANEL DE ADMINISTRACIÓN ---
@app.route('/admin/dashboard')
@admin_required  # Solo usuarios logeados como admin pueden ver esta página.
def admin_dashboard():
    # Pasamos el nombre del usuario actual a la plantilla
    return render_template('admin_dashboard.html', nombre_usuario=current_user.nombre)


# --- NUEVO ENDPOINT PARA VERIFICAR ESTADO DE AUTENTICACIÓN ---
@app.route('/api/auth/status')
def auth_status():
    # Primero, verificamos si hay un usuario logeado
    if current_user.is_authenticated:
        # Si está logeado, consultamos si tiene el rol de 'admin'
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        sql_query = "SELECT 1 FROM UsuarioRoles WHERE UsuarioID = ? AND RolID = 1" # RolID 1 = admin
        cursor.execute(sql_query, current_user.id)
        is_admin = cursor.fetchone()
        conn.close()

        # Si es admin, devolvemos un JSON que lo confirme
        if is_admin:
            return jsonify({
                "is_authenticated": True,
                "role": "admin",
                "nombre": current_user.nombre
            })
        else:
            # Si es un usuario logeado pero no admin (ej. un futuro 'cliente')
            return jsonify({
                "is_authenticated": True,
                "role": "cliente",
                "nombre": current_user.nombre
            })
            
    # Si no hay nadie logeado
    return jsonify({"is_authenticated": False})

# --- RUTA PARA ACTUALIZAR STOCK (MODIFICADA) ---
@app.route("/api/actualizar-stock", methods=["POST"])
def actualizar_stock_ruta():
    carrito = request.get_json()
    if not carrito:
        return jsonify({"success": False, "error": "No se recibió el carrito."}), 400

    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        for item_carrito in carrito:
            # Llamamos al stored procedure para actualizar el stock de forma segura
            # O ejecutamos una consulta directa con validación
            sql = "{CALL usp_ActualizarStockPorVenta (?, ?)}"
            params = (item_carrito['nombre'], item_carrito['cantidad'])
            # Nota: El Stored Procedure debe buscar el producto por nombre y validar el stock
            cursor.execute(sql, params)

        conn.commit() # Confirmamos todos los cambios en la base de datos
        return jsonify({"success": True, "message": "Stock actualizado correctamente."})

    except Exception as e:
        print(f"Error al actualizar el stock: {e}")
        return jsonify({"success": False, "error": f"Error en la base de datos: {e}"}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()


# --- RUTA DE CONTACTO (SIN CAMBIOS) ---
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

    body = f"Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header("Nuevo mensaje de contacto", "utf-8")
    msg["From"] = formataddr((Header("Formulario Web", "utf-8").encode(), EMAIL_FROM))
    msg["To"] = EMAIL_TO

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return {"success": False, "error": "No se pudo enviar el correo"}, 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)