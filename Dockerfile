# Usa una imagen oficial de Python como base
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que correrá Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
