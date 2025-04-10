# Django PostgreSQL Project

## 🚀 Configuración del entorno

Este proyecto utiliza Django con PostgreSQL como base de datos. Sigue estos pasos para configurar y ejecutar el proyecto.

## 📋 Requisitos previos

- [Python](https://www.python.org/downloads/) (3.8 o superior)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🐳 Iniciar la base de datos (PostgreSQL)

1. Inicia los contenedores de PostgreSQL y pgAdmin con Docker Compose:

```bash
docker-compose up -d
```

Este comando iniciará:

- PostgreSQL en el puerto 5432
- pgAdmin en http://localhost:5050

2. Credenciales de acceso:

**PostgreSQL:**

- **Usuario:** admin
- **Contraseña:** admin
- **Puerto:** 5432

**pgAdmin:**

- **URL:** http://localhost:5050
- **Email:** admin@admin.cl
- **Contraseña:** admin

## 📊 Configuración y uso de pgAdmin

1. Accede a pgAdmin en tu navegador: http://localhost:5050
2. Inicia sesión con las credenciales:

   - Email: admin@admin.cl
   - Contraseña: admin

3. Registrar un nuevo servidor:

   - Haz clic derecho en "Servers" en el panel izquierdo
   - Selecciona "Register" > "Server..."
   - En la pestaña "General", asigna un nombre (ej. "Local PostgreSQL")
   - En la pestaña "Connection", introduce:
     - Host: db (si estás usando pgAdmin desde el contenedor) o localhost (si accedes externamente)
     - Port: 5432
     - Maintenance database: postgres
     - Username: admin
     - Password: admin
   - Haz clic en "Save"

4. Explorar la base de datos:

   - Expande el servidor recién creado
   - Navega a Databases > postgres > Schemas > public > Tables
   - Haz clic derecho en cualquier tabla para ver opciones como:
     - View/Edit Data
     - Query Tool
     - Properties

5. Ejecutar consultas SQL:
   - Haz clic en Tools > Query Tool
   - Escribe tu consulta SQL
   - Presiona F5 o el botón "Execute" para ejecutarla

## 🐍 Configuración del proyecto Django

1. Crea un entorno virtual:

```bash
python -m venv venv
```

2. Activa el entorno virtual:

```bash
# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Aplica las migraciones para verificar la conexión:

```bash
python manage.py migrate
```

Si el comando se ejecuta sin errores, ¡la conexión ha sido exitosa!

## 🚀 Ejecutando el proyecto

1. Inicia el servidor de desarrollo:

```bash
python manage.py runserver
```

2. Accede a la aplicación en tu navegador:

```
http://127.0.0.1:8000/
```

## 🔧 Solución de problemas comunes

### Error de conexión a la base de datos

Si encuentras problemas al conectarte a PostgreSQL:

- Verifica que los contenedores estén funcionando: `docker ps`
- Asegúrate de que los puertos no estén siendo utilizados por otras aplicaciones
- Revisa los logs de Docker: `docker logs local_pgdb`

### Error al conectar pgAdmin con PostgreSQL

Si no puedes conectar pgAdmin con la base de datos:

- Si usas pgAdmin desde el navegador local, prueba con `Host: localhost`
- Si el error persiste, intenta con `Host: host.docker.internal` (para Mac/Windows)
- Verifica que el contenedor de PostgreSQL esté funcionando correctamente

### Error al instalar psycopg2

Si tienes problemas al instalar psycopg2:

```bash
pip install psycopg2-binary
```

## 📝 Comandos útiles

```bash
# Crear superusuario de Django
python manage.py createsuperuser

# Hacer migraciones después de cambios en modelos
python manage.py makemigrations

# Ver el estado de las migraciones
python manage.py showmigrations

# Detener los contenedores de Docker
docker-compose down
```

---

Desarrollado con ❤️ usando Django y PostgreSQL
