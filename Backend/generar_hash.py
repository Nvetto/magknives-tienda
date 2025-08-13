from werkzeug.security import generate_password_hash
import getpass

# Pedimos al usuario que ingrese la contraseña de forma segura (no se verá al escribir)
contrasena = getpass.getpass("Ingresa la contraseña para la cuenta de administrador: ")
contrasena_confirm = getpass.getpass("Confirma la contraseña: ")

if contrasena != contrasena_confirm:
    print("\nError: Las contraseñas no coinciden.")
elif not contrasena:
    print("\nError: La contraseña no puede estar vacía.")
else:
    # Generamos el hash a partir de la contraseña
    hash_contrasena = generate_password_hash(contrasena)
    print("\n¡Hash generado con éxito! Cópialo completo (incluyendo el 'pbkdf2:sha256...'):")
    print("======================================================================")
    print(hash_contrasena)
    print("======================================================================")