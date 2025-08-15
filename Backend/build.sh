#!/usr/bin/env bash
# exit on error
set -o errexit

# --- Comandos para instalar el controlador ODBC de Microsoft con permisos de administrador ---

# La advertencia "apt-key is deprecated" es normal y no causa fallos, podemos ignorarla por ahora.
# Usamos 'sudo' para ejecutar los comandos como administrador (root).
echo "Instalando dependencias del sistema para el driver ODBC..."

# Agregamos la clave del repositorio de Microsoft
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# Registramos el repositorio de Microsoft
curl -fsSL https://packages.microsoft.com/config/debian/11/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Actualizamos la lista de paquetes del sistema operativo
sudo apt-get update

# Aceptamos la licencia de forma automática e instalamos el controlador
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

echo "Driver ODBC instalado con éxito."

# --- Comando original para instalar las dependencias de Python (este no necesita sudo) ---
echo "Instalando dependencias de Python..."
pip install -r requirements.txt

echo "¡Build completado!"