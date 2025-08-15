# Usamos una imagen oficial de Python como base
FROM python:3.10-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Cambiamos al usuario root TEMPORALMENTE para instalar dependencias del sistema
USER root

# --- INICIO: COMANDOS CORREGIDOS PARA INSTALAR EL DRIVER ODBC ---

# 1. Instalamos las dependencias necesarias
RUN apt-get update && apt-get install -y curl gnupg lsb-release

# 2. Descargamos y registramos la clave de Microsoft de la forma moderna
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg

# 3. Registramos el repositorio de Microsoft, asegurándonos de que use la clave que descargamos
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# 4. Actualizamos la lista de paquetes (ahora confiará en el repo de MS)
RUN apt-get update

# 5. Aceptamos la licencia e instalamos el controlador
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# --- FIN: COMANDOS CORREGIDOS ---

# Copiamos el archivo de requerimientos primero
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de nuestra aplicación
COPY . .

# Exponemos el puerto que Render usará
EXPOSE 10000

# Comando para iniciar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "servidor:app"]