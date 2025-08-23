import requests
import json

# URL del backend en producción (Render)
PRODUCTION_URL = "https://magknives-backend.onrender.com"

# Datos de prueba
test_data = {
    'nombre': 'Test Usuario',
    'email': 'test@test.com',
    'mensaje': 'Este es un mensaje de prueba para verificar que el endpoint de contacto funciona correctamente en producción.'
}

try:
    print(f"🌐 Probando endpoint de contacto en: {PRODUCTION_URL}")
    print(f"📧 Datos de prueba: {test_data}")
    print("-" * 50)
    
    # Hacer la petición POST al endpoint de contacto en producción
    response = requests.post(
        f'{PRODUCTION_URL}/contacto',
        json=test_data,
        headers={'Content-Type': 'application/json'},
        timeout=30  # Timeout más largo para producción
    )
    
    print(f'📊 Status Code: {response.status_code}')
    print(f'📄 Response: {response.text}')
    print("-" * 50)
    
    if response.status_code == 200:
        print('✅ El endpoint de contacto está funcionando correctamente en producción')
        print('📧 El email debería haberse enviado a: nicovettovalli@hotmail.com')
    else:
        print('❌ Error en el endpoint de contacto')
        print(f'🔍 Detalles del error: {response.text}')
        
except requests.exceptions.ConnectionError:
    print('❌ No se pudo conectar al servidor de producción')
    print('🔍 Verifica que el backend esté desplegado correctamente en Render')
except requests.exceptions.Timeout:
    print('⏰ Timeout: El servidor tardó demasiado en responder')
    print('🔍 Esto puede ser normal en Render en el primer request (cold start)')
except Exception as e:
    print(f'❌ Error inesperado: {e}')
