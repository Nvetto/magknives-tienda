import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps
import cloudinary
import cloudinary.uploader
import cloudinary.api
from supabase import create_client, Client
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# Cargar variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.getenv("SECRET_KEY")

# --- CONFIGURACIÓN DE CORS ---
# Asegúrate de que los orígenes coincidan con tu frontend en desarrollo y producción
origins = [
    "http://127.0.0.1:5500",
    "https://magknives.netlify.app"
]
CORS(app, resources={r"/api/*": {"origins": origins}, r"/*": {"origins": origins}}, supports_credentials=True)


# --- INICIALIZACIÓN DE CLIENTES EXTERNOS ---

# Cliente de Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Configuración de Cloudinary (sin cambios)
cloudinary.config(
  cloud_name = os.getenv("CLOUD_NAME"), 
  api_key = os.getenv("API_KEY"), 
  api_secret = os.getenv("API_SECRET"),
  secure = True
)

# Configuración de Email (sin cambios)
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASS = os.getenv("EMAIL_PASS")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


# --- DECORADOR DE AUTENTICACIÓN PARA ADMINS ---
def admin_required(f):
    """
    Verifica que se provea un JWT válido en el header 'Authorization',
    y que el usuario asociado a ese token tenga el rol 'admin'.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "error": "Token de autorización no válido o ausente."}), 401
        
        jwt_token = auth_header.split(" ")[1]
        
        try:
            # 1. Valida el token y obtiene el usuario de Supabase
            user_res = supabase.auth.get_user(jwt_token)
            user_id = user_res.user.id

            # 2. Verifica el rol en nuestra tabla 'profiles'
            profile_res = supabase.table('profiles').select('role').eq('id', user_id).single().execute()
            
            if profile_res.data and profile_res.data['role'] == 'admin':
                # Si es admin, permite el acceso a la ruta
                return f(*args, **kwargs)
            else:
                # Si no es admin, prohíbe el acceso
                return jsonify({"success": False, "error": "Acceso denegado. Se requieren permisos de administrador."}), 403
        
        except Exception:
            return jsonify({"success": False, "error": "Token inválido o expirado."}), 401
            
    return decorated_function


# --- FUNCIONES AUXILIARES ---
def extraer_public_id_de_url(url):
    """Extrae el public_id de una URL de Cloudinary para poder eliminar la imagen."""
    try:
        parte_esencial = url.split('/upload/')[1]
        sin_version = parte_esencial.split('/', 1)[1]
        public_id = os.path.splitext(sin_version)[0]
        return public_id
    except IndexError:
        return None

def _get_all_products():
    """Obtiene y formatea todos los productos y sus imágenes desde Supabase."""
    try:
        response = supabase.table('Productos').select('*, ImagenesProducto(*)').execute()
        productos_formateados = []
        for prod in response.data:
            producto = {
                "id": prod['ProductoID'],
                "nombre": prod['Nombre'],
                "descripcion": prod['Descripcion'],
                "precio": float(prod['Precio']),
                "stock": prod['Stock'],
                "categoria": prod['Categoria'],
                "imagenes": [img['URL'] for img in prod.get('ImagenesProducto', [])]
            }
            productos_formateados.append(producto)
        return productos_formateados
    except Exception as e:
        print(f"Error al consultar productos en Supabase: {e}")
        return []

# --- RUTAS DE LA API ---

# --- RUTAS DE PRODUCTOS (CRUD) ---

@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    """Endpoint público para obtener todos los productos."""
    lista_productos = _get_all_products()
    if not lista_productos:
        return jsonify([]) # Devolver lista vacía si no hay productos o hay error
    return jsonify(lista_productos)

@app.route('/api/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    """Endpoint protegido para obtener un solo producto por su ID."""
    try:
        response = supabase.table('Productos').select('*, ImagenesProducto(*)').eq('ProductoID', producto_id).single().execute()
        if not response.data:
            return jsonify({"success": False, "error": "Producto no encontrado"}), 404
        
        prod = response.data
        producto_formateado = {
            "id": prod['ProductoID'],
            "nombre": prod['Nombre'],
            "descripcion": prod['Descripcion'],
            "precio": float(prod['Precio']),
            "stock": prod['Stock'],
            "categoria": prod['Categoria'],
            "imagenes": [{"id": img['ImagenID'], "url": img['URL']} for img in prod.get('ImagenesProducto', [])]
        }
        return jsonify({"success": True, "producto": producto_formateado})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/productos', methods=['POST'])
@admin_required
def crear_producto():
    """Endpoint protegido para crear un nuevo producto."""
    data = request.get_json()
    required_fields = ['nombre', 'precio', 'stock', 'categoria', 'imagenes_urls']
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "error": "Faltan campos obligatorios."}), 400

    try:
        producto_data = {
            'Nombre': data['nombre'], 'Descripcion': data.get('descripcion', ''),
            'Precio': float(data['precio']), 'Stock': int(data['stock']), 'Categoria': data['categoria']
        }
        response_prod = supabase.table('Productos').insert(producto_data).execute()
        nuevo_producto_id = response_prod.data[0]['ProductoID']

        if nuevo_producto_id and data['imagenes_urls']:
            imagenes_data = [{'ProductoID': nuevo_producto_id, 'URL': url} for url in data['imagenes_urls']]
            supabase.table('ImagenesProducto').insert(imagenes_data).execute()
        
        return jsonify({"success": True, "message": "Producto creado con éxito", "producto_id": nuevo_producto_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/productos/<int:producto_id>', methods=['PUT'])
@admin_required
def actualizar_producto(producto_id):
    """Endpoint protegido para actualizar un producto existente."""
    data = request.get_json()
    try:
        update_data = {
            'Nombre': data['nombre'], 'Descripcion': data.get('descripcion', ''),
            'Precio': float(data['precio']), 'Stock': int(data['stock']), 'Categoria': data['categoria']
        }
        supabase.table('Productos').update(update_data).eq('ProductoID', producto_id).execute()
        return jsonify({"success": True, "message": "Producto actualizado con éxito."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/productos/<int:producto_id>', methods=['DELETE'])
@admin_required
def eliminar_producto(producto_id):
    """Endpoint protegido para eliminar un producto y sus imágenes."""
    try:
        response_imgs = supabase.table('ImagenesProducto').select('URL').eq('ProductoID', producto_id).execute()
        urls_a_borrar = [img['URL'] for img in response_imgs.data]

        for url in urls_a_borrar:
            public_id = extraer_public_id_de_url(url)
            if public_id:
                cloudinary.uploader.destroy(public_id)

        supabase.table('Productos').delete().eq('ProductoID', producto_id).execute()
        return jsonify({"success": True, "message": "Producto y sus imágenes eliminados con éxito."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- RUTAS DE IMÁGENES ---

@app.route('/api/upload-image', methods=['POST'])
@admin_required
def upload_image():
    """Endpoint protegido para subir una imagen a Cloudinary."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No se encontró el archivo"}), 400
    try:
        upload_result = cloudinary.uploader.upload(request.files['file'])
        return jsonify({"success": True, "image_url": upload_result.get('secure_url')})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/productos/<int:producto_id>/imagenes', methods=['POST'])
@admin_required
def agregar_imagenes_a_producto(producto_id):
    """Endpoint protegido para añadir imágenes a un producto ya existente."""
    data = request.get_json()
    urls = data.get('imagenes_urls')
    if not urls or not isinstance(urls, list):
        return jsonify({"success": False, "error": "Se requiere una lista de URLs de imágenes."}), 400
    try:
        imagenes_data = [{'ProductoID': producto_id, 'URL': url} for url in urls]
        supabase.table('ImagenesProducto').insert(imagenes_data).execute()
        return jsonify({"success": True, "message": "Imágenes agregadas con éxito."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/imagenes/<int:imagen_id>', methods=['DELETE'])
@admin_required
def eliminar_imagen(imagen_id):
    """Endpoint protegido para eliminar una imagen específica por su ID."""
    try:
        response_img = supabase.table('ImagenesProducto').select('URL').eq('ImagenID', imagen_id).single().execute()
        if not response_img.data:
            return jsonify({"success": False, "error": "Imagen no encontrada."}), 404
        
        public_id = extraer_public_id_de_url(response_img.data['URL'])
        if public_id:
            cloudinary.uploader.destroy(public_id)

        supabase.table('ImagenesProducto').delete().eq('ImagenID', imagen_id).execute()
        return jsonify({"success": True, "message": "Imagen eliminada con éxito."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/api/register', methods=['POST'])
def registrar_usuario():
    """Endpoint público para el registro de nuevos usuarios."""
    data = request.get_json()
    email, password, nombre = data.get('email'), data.get('password'), data.get('nombre')
    if not all([email, password, nombre]):
        return jsonify({"success": False, "error": "Email, contraseña y nombre son obligatorios."}), 400
    try:
        supabase.auth.sign_up({
            "email": email, "password": password,
            "options": {"data": {"nombre": nombre, "apellido": data.get('apellido', '')}}
        })
        return jsonify({"success": True, "message": "Usuario registrado. Revisa tu email para confirmar la cuenta."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 409

@app.route('/login', methods=['POST'])
def login():
    """Endpoint público para el inicio de sesión."""
    data = request.form if request.form else request.get_json()
    email, password = data.get('email'), data.get('password')
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user_profile = supabase.table('profiles').select('nombre, role').eq('id', res.user.id).single().execute()
        return jsonify({
            "success": True,
            "access_token": res.session.access_token,
            "user": {
                "id": res.user.id,
                "email": res.user.email,
                "nombre": user_profile.data.get('nombre', ''),
                "role": user_profile.data.get('role', 'cliente')
            }
        })
    except Exception:
        return jsonify({"success": False, "error": "Email o contraseña incorrectos"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    """Endpoint para invalidar un token en el servidor."""
    # El frontend es responsable de eliminar el token del localStorage.
    # Esta ruta es opcional pero recomendada para invalidar el token en Supabase.
    return jsonify({"success": True, "message": "Sesión cerrada en el frontend."})

@app.route('/api/me')
@admin_required # Re-usamos el decorador para validar el token
def get_current_user_profile():
    """Endpoint protegido para obtener el perfil del usuario actual basado en su token."""
    # El decorador ya validó el token y el rol de admin, aquí solo devolvemos los datos.
    # Esta ruta puede ser expandida para devolver datos del usuario al propio usuario (no solo al admin).
    auth_header = request.headers.get('Authorization')
    jwt_token = auth_header.split(" ")[1]
    user_res = supabase.auth.get_user(jwt_token)
    profile_res = supabase.table('profiles').select('*').eq('id', user_res.user.id).single().execute()
    return jsonify({"success": True, "user": profile_res.data})


# --- OTRAS RUTAS DE LA API ---

@app.route("/api/actualizar-stock", methods=["POST"])
def actualizar_stock_ruta():
    """Endpoint que usa una función de base de datos para actualizar el stock de forma segura."""
    carrito = request.get_json()
    if not carrito:
        return jsonify({"success": False, "error": "No se recibió el carrito."}), 400
    try:
        # Llamamos a la función de PostgreSQL que creamos
        result = supabase.rpc('actualizar_stock_venta', {'items_json': carrito}).execute()
        
        if 'Error' in result.data:
            return jsonify({"success": False, "error": result.data}), 400
        
        return jsonify({"success": True, "message": "Stock actualizado correctamente."})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error en la base de datos: {e}"}), 500

@app.route("/contacto", methods=["POST"])
def contacto():
    """Endpoint para el formulario de contacto (sin cambios)."""
    data = request.get_json()
    nombre, email, mensaje = data.get("nombre", ""), data.get("email", ""), data.get("mensaje", "")
    if not all([nombre, email, mensaje]):
        return jsonify({"success": False, "error": "Todos los campos son obligatorios."}), 400
    
    body = f"Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header("Nuevo mensaje de contacto", "utf-8")
    msg["From"] = formataddr((Header("Formulario Web", "utf-8").encode(), EMAIL_FROM))
    msg["To"] = EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return jsonify({"success": False, "error": "No se pudo enviar el correo"}), 500


# --- EJECUCIÓN DE LA APLICACIÓN (PARA DESARROLLO LOCAL) ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)