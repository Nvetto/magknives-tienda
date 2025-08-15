#!/usr/bin/env bash
# exit on error
set -o errexit

# --- Comandos para instalar el controlador ODBC de Microsoft ---
# Descargamos la clave del repositorio de Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Registramos el repositorio de Microsoft para Debian 11 (que usa Render)
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Actualizamos la lista de paquetes del sistema operativo
apt-get update

# Aceptamos la licencia de forma automática e instalamos el controlador
ACCEPT_EULA=Y apt-get install -y msodbcsql18

# --- Comando original para instalar las dependencias de Python ---
pip install -r requirements.txt