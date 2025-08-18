import os
import pyodbc
import psycopg2
from dotenv import load_dotenv
from pathlib import Path # Importamos la librería Path

# Le decimos a python que busque el archivo .env en la misma carpeta que este script
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

AZURE_CONN_STR = os.getenv("DATABASE_CONNECTION_STRING")
SUPABASE_CONN_STR = os.getenv("SUPABASE_CONNECTION_STRING")

def migrar_datos():
    # --- INICIO DEL CAMBIO: Verificación de las variables de entorno ---
    if not AZURE_CONN_STR or not SUPABASE_CONN_STR:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR: Faltan las cadenas de conexión.")
        print("Asegúrate de que tu archivo .env contenga las variables:")
        print("1. DATABASE_CONNECTION_STRING (para Azure)")
        print("2. SUPABASE_CONNECTION_STRING (para Supabase)")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return
    # --- FIN DEL CAMBIO ---

    try:
        print("Conectando a las bases de datos...")
        conn_azure = pyodbc.connect(AZURE_CONN_STR)
        conn_supabase = psycopg2.connect(SUPABASE_CONN_STR)
        
        cursor_azure = conn_azure.cursor()
        cursor_supabase = conn_supabase.cursor()
        print("Conexión exitosa.")

        # ... (el resto del script de migración no cambia) ...

    except Exception as e:
        print(f"\nERROR: Ocurrió un error durante la migración.")
        print(e)
        if 'conn_supabase' in locals() and conn_supabase:
            conn_supabase.rollback()
    finally:
        if 'conn_azure' in locals() and conn_azure:
            conn_azure.close()
        if 'conn_supabase' in locals() and conn_supabase:
            conn_supabase.close()
        print("Conexiones cerradas.")

if __name__ == '__main__':
    migrar_datos()