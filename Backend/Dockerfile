# Usamos una imagen oficial de Python como base
FROM python:3.10-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Cambiamos al usuario root TEMPORALMENTE para instalar dependencias del sistema
USER root

# Instalamos las dependencias necesarias para el driver ODBC de Microsoft
# Estos son los mismos comandos del build.sh, ahora funcionarán
RUN apt-get update && apt-get install -y curl gnupg
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
RUN curl -fsSL https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Copiamos el archivo de requerimientos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de nuestra aplicación
COPY . .

# Exponemos el puerto que Render usará (Render lo asigna dinámicamente)
EXPOSE 10000

# Comando para iniciar la aplicación. Render proveerá la variable $PORT.
# El --bind 0.0.0.0 es crucial para que sea accesible desde fuera del contenedor.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "servidor:app"]