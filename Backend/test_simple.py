import requests

print("Iniciando test de contacto...")

try:
    response = requests.post(
        'https://magknives-backend.onrender.com/contacto',
        json={
            'nombre': 'Test Usuario',
            'email': 'test@test.com',
            'mensaje': 'Test desde producción'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
