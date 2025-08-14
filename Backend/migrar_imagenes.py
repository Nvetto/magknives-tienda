# migrar_imagenes_v2.py

import os
import pyodbc
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

# --- CONFIGURACIÓN ---
DB_CONNECTION_STRING = os.getenv("DATABASE_CONNECTION_STRING")
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True
)
# Ahora la ruta apunta a tu carpeta principal "Imagenes"
RUTA_IMAGENES_PRINCIPAL = "Imagenes" 

def migrar_imagenes_recursivo():
    """
    Este script camina recursivamente por la carpeta de Imágenes, usa el nombre
    de cada subcarpeta para encontrar el producto en la DB, sube las imágenes
    de esa carpeta a Cloudinary y las asocia con el producto correcto.
    """
    print("--- Iniciando migración de imágenes desde subcarpetas ---")

    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # 1. os.walk() recorre el árbol de directorios de arriba hacia abajo.
        for dirpath, _, filenames in os.walk(RUTA_IMAGENES_PRINCIPAL):
            if not filenames:
                continue # Si no hay archivos en la carpeta, la saltamos.

            # 2. El nombre del producto es el nombre de la subcarpeta.
            nombre_producto = os.path.basename(dirpath)
            print(f"\nProcesando carpeta para el producto: '{nombre_producto}'")

            try:
                # 3. Buscamos el ProductoID en la base de datos usando el nombre de la carpeta.
                cursor.execute("SELECT ProductoID FROM Productos WHERE Nombre = ?", nombre_producto)
                producto_row = cursor.fetchone()

                if not producto_row:
                    print(f"AVISO: No se encontró un producto llamado '{nombre_producto}' en la DB. Saltando esta carpeta.")
                    continue
                
                producto_id = producto_row.ProductoID

                # 4. Recorremos cada imagen encontrada en la carpeta.
                for filename in filenames:
                    ruta_completa_archivo = os.path.join(dirpath, filename)
                    
                    # Extraemos el nombre del archivo sin extensión para usarlo como parte del public_id
                    nombre_base_archivo = os.path.splitext(filename)[0]

                    print(f"  - Subiendo '{filename}'...")
                    
                    # 5. Subimos la imagen a Cloudinary.
                    upload_result = cloudinary.uploader.upload(
                        ruta_completa_archivo,
                        # Creamos un ID público único para evitar sobreescrituras y organizar en Cloudinary.
                        public_id=f"{nombre_producto.lower().replace(' ', '-')}/{nombre_base_archivo}"
                    )
                    
                    secure_url = upload_result.get('secure_url')

                    if not secure_url:
                        print(f"  - ERROR: La subida para '{filename}' no devolvió una URL.")
                        continue

                    # 6. Insertamos la nueva URL en la tabla ImagenesProducto.
                    print(f"  - URL: {secure_url}")
                    sql_insert = "INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (?, ?)"
                    cursor.execute(sql_insert, producto_id, secure_url)
                    conn.commit()
                    print(f"  - ¡Base de datos actualizada para ProductoID {producto_id}!")

            except Exception as e_inner:
                print(f"!! ERROR procesando la carpeta '{nombre_producto}': {e_inner}")

    except Exception as e_outer:
        print(f"!! ERROR FATAL durante la conexión o el recorrido de archivos: {e_outer}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
        print("\n--- Migración finalizada ---")


if __name__ == "__main__":
    # ¡IMPORTANTE! Haz una copia de seguridad de tu base de datos antes de ejecutar.
    respuesta = input("¿Estás seguro de que quieres iniciar la migración desde subcarpetas? (s/n): ")
    if respuesta.lower() == 's':
        migrar_imagenes_recursivo()
    else:
        print("Migración cancelada.")