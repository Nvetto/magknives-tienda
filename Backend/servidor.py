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
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 


load_dotenv()

app = Flask(__name__, template_folder='../templates')

app.secret_key = os.getenv("SECRET_KEY")

origins = [
    "http://127.0.0.1:5500", # Tu entorno de desarrollo local
    "https://magknives.netlify.app/" # Tu sitio en producción
]

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
     r"/login": {"origins": origins, "supports_credentials": True},
     r"/logout": {"origins": origins, "supports_credentials": True}, 
     r"/contacto": {"origins": origins},
     r"/api/*": {"origins": origins, "supports_credentials": True}
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

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.getenv("CLOUD_NAME"), 
  api_key = os.getenv("API_KEY"), 
  api_secret = os.getenv("API_SECRET"),
  secure = True
)

# --- RUTA PARA SUBIR IMÁGENES ---
@app.route('/api/upload-image', methods=['POST'])
@admin_required # ¡Protegemos la ruta! Solo un admin puede subir imágenes.
def upload_image():
    # Verificamos si se envió un archivo en la petición
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No se encontró el archivo"}), 400

    file_to_upload = request.files['file']

    try:
        # Enviamos el archivo a Cloudinary para que lo suba
        upload_result = cloudinary.uploader.upload(file_to_upload)
        
        # Cloudinary nos devuelve mucha información, pero la más importante es la URL segura.
        image_url = upload_result.get('secure_url')

        # Devolvemos la URL pública de la imagen al frontend
        return jsonify({"success": True, "image_url": image_url})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

def extraer_public_id_de_url(url):
    """
    Extrae el public_id de una URL de Cloudinary para poder eliminar la imagen.
    Ej: '.../upload/v1234/folder/image.jpg' -> 'folder/image'
    """
    try:
        # Encuentra la parte de la URL después de '/upload/'
        parte_esencial = url.split('/upload/')[1]
        # Quita el número de versión (ej. 'v12345/')
        sin_version = parte_esencial.split('/', 1)[1]
        # Quita la extensión del archivo (ej. '.jpg')
        public_id = os.path.splitext(sin_version)[0]
        return public_id
    except IndexError:
        return None    

# --- FUNCIÓN AUXILIAR PARA OBTENER PRODUCTOS---
def _get_all_products():
    """
    Función interna para obtener y formatear todos los productos de la base de datos.
    """
    productos_dict = {}
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        sql_query = """
            SELECT p.ProductoID, p.Nombre, p.Descripcion, p.Precio, p.Stock, p.Categoria, i.URL
            FROM Productos p
            LEFT JOIN ImagenesProducto i ON p.ProductoID = i.ProductoID
            ORDER BY p.ProductoID;
        """
        cursor.execute(sql_query)
        
        for row in cursor.fetchall():
            producto_id = row.ProductoID
            if producto_id not in productos_dict:
                productos_dict[producto_id] = {
                    "id": producto_id, # Añadimos el ID para futuras acciones
                    "nombre": row.Nombre,
                    "descripcion": row.Descripcion,
                    "precio": float(row.Precio),
                    "stock": row.Stock,
                    "categoria": row.Categoria,
                    "imagenes": []
                }
            if row.URL:
                productos_dict[producto_id]["imagenes"].append(row.URL)
    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        return [] # Devuelve lista vacía en caso de error
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    
    return list(productos_dict.values())

# --- RUTA PARA OBTENER PRODUCTOS ---
@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    # Ahora esta ruta simplemente llama a nuestra función auxiliar
    lista_productos = _get_all_products()
    if not lista_productos and "error" in locals(): # Manejo de error básico
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    return jsonify(lista_productos)


# --- RUTA PARA CERRAR SESIÓN ---
@app.route('/logout')
@login_required # Solo un usuario logueado puede cerrar sesión
def logout():
    logout_user() # Esta función de Flask-Login limpia la sesión del usuario
    return jsonify({"success": True, "message": "Sesión cerrada correctamente."})


# --- RUTAS PARA AUTENTICACIÓN ---
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("SELECT UsuarioID, Email, Nombre, HashContrasena FROM [dbo].[Usuarios] WHERE Email = ?", email)
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
@admin_required
def admin_dashboard():
    productos = _get_all_products()
    return render_template('admin_dashboard.html', nombre_usuario=current_user.nombre, productos=productos)

# --- RUTA PARA CREAR UN PRODUCTO ---
@app.route('/api/productos', methods=['POST'])
@admin_required
def crear_producto():
    data = request.get_json()

    # Verificamos que 'data' no sea None antes de usarlo
    if not data:
        return jsonify({"success": False, "error": "No se recibieron datos"}), 400

    # Verificación de campos
    required_fields = ['nombre', 'precio', 'stock', 'categoria', 'imagenes_urls']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Falta el campo obligatorio: {field}"}), 400

    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # 1. Llamamos al Stored Procedure de forma explícita
        sql_exec_sp = """
            DECLARE @NuevoProductoID INT;
            EXEC usp_CrearProducto ?, ?, ?, ?, ?, @NuevoProductoID OUTPUT;
            SELECT @NuevoProductoID;
        """
        params = (
            data['nombre'],
            data.get('descripcion', ''),
            float(data['precio']),
            int(data['stock']),
            data['categoria']
        )
        cursor.execute(sql_exec_sp, params)
        nuevo_producto_id = cursor.fetchone()[0]

        # 2. Iteramos sobre el array de URLs (usando la clave correcta 'imagenes_urls') y las insertamos una por una.
        if nuevo_producto_id and data['imagenes_urls']:
            sql_insert_img = "INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (?, ?)"
            urls_a_insertar = [(nuevo_producto_id, url) for url in data['imagenes_urls']]
            cursor.executemany(sql_insert_img, urls_a_insertar)

        conn.commit()
        return jsonify({"success": True, "message": "Producto creado con éxito", "producto_id": nuevo_producto_id})

    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# ---RUTA PARA REGISTRAR USUARIOS ---
@app.route('/api/register', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    nombre = data.get('nombre')
    apellido = data.get('apellido') 
    email = data.get('email')
    password = data.get('password')

    if not all([nombre, apellido, email, password]):
        return jsonify({"success": False, "error": "Todos los campos son obligatorios."}), 400

    hash_contrasena = generate_password_hash(password)

    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        sql_call_sp = "{CALL usp_CrearUsuarioCliente(?, ?, ?, ?)}" 
        cursor.execute(sql_call_sp, email, nombre, apellido, hash_contrasena)
        
        conn.commit()
        return jsonify({"success": True, "message": "Usuario registrado con éxito."})

    except pyodbc.Error as e:
        # Capturamos el error específico de la base de datos (ej: email duplicado)
        conn.rollback()
        # El error de SQL Server viene en e.args[1]
        error_message = str(e.args[1])
        return jsonify({"success": False, "error": error_message}), 409 # 409 Conflict
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- RUTA PARA ELIMINAR UN PRODUCTO (DELETE) ---
@app.route('/api/productos/<int:producto_id>', methods=['DELETE'])
@admin_required
def eliminar_producto(producto_id):
    conn = None  # Definimos conn fuera del try para que esté disponible en el finally
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # 1. OBTENEMOS LAS URLS DE LAS IMÁGENES ANTES DE BORRAR EL PRODUCTO
        sql_select_imgs = "SELECT URL FROM ImagenesProducto WHERE ProductoID = ?"
        cursor.execute(sql_select_imgs, producto_id)
        urls_a_borrar = [row.URL for row in cursor.fetchall()]

        # 2. ITERAMOS Y BORRAMOS CADA IMAGEN DE CLOUDINARY
        if urls_a_borrar:
            print(f"Eliminando {len(urls_a_borrar)} imágenes de Cloudinary para el producto {producto_id}...")
            for url in urls_a_borrar:
                public_id = extraer_public_id_de_url(url)
                if public_id:
                    # Usamos la API de Cloudinary para destruir la imagen
                    cloudinary.uploader.destroy(public_id)
                    print(f" - Imagen {public_id} eliminada de Cloudinary.")

        # 3. FINALMENTE, ELIMINAMOS EL PRODUCTO DE NUESTRA BASE DE DATOS
        print(f"Eliminando producto {producto_id} de la base de datos...")
        sql_call_sp = "{CALL usp_EliminarProducto(?)}"
        cursor.execute(sql_call_sp, producto_id)
        
        conn.commit()
        print("Producto eliminado con éxito de la base de datos.")
        return jsonify({"success": True, "message": "Producto y sus imágenes eliminados con éxito."})

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"ERROR al eliminar producto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# ---RUTA PARA OBTENER UN SOLO PRODUCTO (GET) ---
@app.route('/api/productos/<int:producto_id>', methods=['GET'])
@admin_required
def obtener_producto(producto_id):
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Buscamos los detalles del producto
        sql_producto = "SELECT ProductoID, Nombre, Descripcion, Precio, Stock, Categoria FROM Productos WHERE ProductoID = ?"
        cursor.execute(sql_producto, producto_id)
        producto_data = cursor.fetchone()

        if not producto_data:
            return jsonify({"success": False, "error": "Producto no encontrado"}), 404

        producto = {
            "id": producto_data.ProductoID,
            "nombre": producto_data.Nombre,
            "descripcion": producto_data.Descripcion,
            "precio": float(producto_data.Precio),
            "stock": producto_data.Stock,
            "categoria": producto_data.Categoria,
            "imagenes": []
        }
        
        # Buscamos sus imágenes
        sql_imagenes = "SELECT ImagenID, URL FROM ImagenesProducto WHERE ProductoID = ?"
        cursor.execute(sql_imagenes, producto_id)
        for img in cursor.fetchall():
            producto['imagenes'].append({"id": img.ImagenID, "url": img.URL})

        return jsonify({"success": True, "producto": producto})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- RUTA PARA ACTUALIZAR UN PRODUCTO (PUT) ---
@app.route('/api/productos/<int:producto_id>', methods=['PUT'])
@admin_required
def actualizar_producto(producto_id):
    data = request.get_json()
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        sql_call_sp = "{CALL usp_ActualizarProducto(?, ?, ?, ?, ?, ?)}"
        params = (
            producto_id,
            data['nombre'],
            data.get('descripcion', ''),
            float(data['precio']),
            int(data['stock']),
            data['categoria']
        )
        cursor.execute(sql_call_sp, params)
        conn.commit()
        return jsonify({"success": True, "message": "Producto actualizado con éxito."})

    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- RUTA PARA AGREGAR IMAGENES A UN PRODUCTO EXISTENTE  ---
@app.route('/api/productos/<int:producto_id>/imagenes', methods=['POST'])
@admin_required
def agregar_imagenes_a_producto(producto_id):
    data = request.get_json()
    urls = data.get('imagenes_urls')

    if not urls or not isinstance(urls, list):
        return jsonify({"success": False, "error": "Se requiere una lista de URLs de imágenes."}), 400

    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        sql_call_sp = "{CALL usp_AgregarImagenProducto(?, ?)}"
        for url in urls:
            cursor.execute(sql_call_sp, producto_id, url)

        conn.commit()
        return jsonify({"success": True, "message": "Imágenes agregadas con éxito."})

    except Exception as e:
        if 'conn' in locals() and conn: conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn: conn.close()


# --- RUTA PARA ELIMINAR UNA IMAGEN ESPECÍFICA (DELETE) ---
@app.route('/api/imagenes/<int:imagen_id>', methods=['DELETE'])
@admin_required
def eliminar_imagen(imagen_id):
    conn = None
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # 1. Obtenemos la URL de la imagen para poder borrarla de Cloudinary
        cursor.execute("SELECT URL FROM ImagenesProducto WHERE ImagenID = ?", imagen_id)
        row = cursor.fetchone()
        if not row:
            return jsonify({"success": False, "error": "Imagen no encontrada."}), 404
        
        # 2. Eliminamos la imagen de Cloudinary
        public_id = extraer_public_id_de_url(row.URL)
        if public_id:
            cloudinary.uploader.destroy(public_id)

        # 3. Eliminamos la imagen de nuestra base de datos
        cursor.execute("{CALL usp_EliminarImagenProducto(?)}", imagen_id)
        
        conn.commit()
        return jsonify({"success": True, "message": "Imagen eliminada con éxito."})

    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn: conn.close()

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

# --- RUTA PARA ACTUALIZAR STOCK ---
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


# --- RUTA DE CONTACTO  ---
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


#if __name__ == "__main__":
 #   app.run(debug=True, port=5000)