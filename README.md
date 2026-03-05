# AcortadorEnlaces

Aplicación web para acortar URLs con soporte para registro de usuarios, autenticación y gestión de enlaces personalizados.

## Características

- ✅ Acortador de URLs simple y rápido
- ✅ Autenticación de usuarios (registro/login/logout)
- ✅ Panel de control para gestionar tus enlaces acortados
- ✅ Base de datos SQLite (desarrollo) o PostgreSQL (producción)
- ✅ API REST para acortar enlaces
- ✅ Almacenamiento persistente con Flask-SQLAlchemy

## Requisitos previos

- Python 3.8+
- pip (gestor de paquetes de Python)

## Instalación y setup

### 1. Clonar el repositorio y navegar a la carpeta

```bash
cd AcortadorEnlaces
```

### 2. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
cat > .env <<EOF
FLASK_APP=acortadorenlaces.py
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
DATABASE_URL=sqlite:////ruta/absoluta/a/data/app.db
EOF
```

**IMPORTANTE**: Cambiar `SECRET_KEY` por una cadena segura y `DATABASE_URL` con la ruta absoluta a tu sistema.

### 5. Inicializar la base de datos

```bash
export FLASK_APP=acortadorenlaces.py
flask db init          # Solo si no existe migrations/
flask db migrate -m "Initial migration"
flask db upgrade       # Crear tablas
```

### 6. Ejecutar la aplicación

```bash
python acortadorenlaces.py
# o con Flask:
flask run
```

La aplicación estará disponible en `http://127.0.0.1:5001`

## Uso

### Para usuarios no autenticados

1. Visita la página principal
2. Ingresa una URL larga en el campo
3. Haz clic en "Acortar"
4. Copia el enlace corto generado

### Para usuarios autenticados

1. Haz clic en "Registrarse" en la página principal
2. Completa el formulario y confirma tu contraseña
3. Se te redirigirá automáticamente a tu panel
4. Desde el panel puedes:
   - Crear nuevos enlaces acortados
   - Ver el historial de tus URLs
   - Copiar enlaces fácilmente

## Estructura del proyecto

```
AcortadorEnlaces/
├── acortadorenlaces.py          # Punto de entrada principal
├── config.py                     # Configuración de la aplicación
├── README.md                     # Este archivo
├── requirements.txt              # Dependencias de Python
├── SQLAlchemy_SETUP.txt          # Notas de configuración de SQLAlchemy
├── tests.py                      # Pruebas básicas
├── .env                          # Variables de entorno (no subir a git)
├── .gitignore                    # Archivos ignorados por git
├── data/                         # Directorio para la base de datos
├── logs/                         # Logs de la aplicación
├── migrations/                   # Migraciones de BD (Flask-Migrate)
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── 405b0646522c_initial_migration.py
├── scripts/                      # Scripts auxiliares
│   └── init_db.py                # Inicialización de la base de datos
├── tests/                        # Pruebas unitarias
│   ├── __init__.py
│   └── test_basic.py
└── app/                          # Código de la aplicación
    ├── __init__.py              # Inicialización del paquete app
    ├── models.py                # Modelos de BD (User, URL)
    ├── core/                     # Configuración central
    │   └── __init__.py          # Creación de la app y configuración de extensiones
    ├── routes/                   # Rutas de la aplicación
    │   ├── __init__.py
    │   ├── main.py              # Rutas de acortamiento y redirección
    │   └── auth.py              # Rutas de autenticación (registro/login/logout)
    ├── services/                 # Lógica de negocio
    │   └── __init__.py          # Servicios para URLs y usuarios
    ├── templates/                # Plantillas HTML
    │   ├── index.html           # Página principal
    │   ├── login.html           # Formulario de login
    │   ├── register.html        # Formulario de registro
    │   ├── dashboard.html       # Panel de control del usuario
    │   └── 404.html             # Página de error 404
    └── utils/                    # Utilidades
        └── __init__.py          # Funciones auxiliares
```

## API Endpoints

### Acortador de URLs

**POST** `/api/shorten`
- **Cuerpo**: `{ "url": "https://ejemplo.com/url-larga" }`
- **Respuesta exitosa** (201):
  ```json
  {
    "shortUrl": "http://localhost:5001/ABC123",
    "alias": "ABC123"
  }
  ```
- **Notas**: Si el usuario está autenticado, el enlace se asocia a su cuenta

### Redirección

**GET** `/<alias>`
- Redirige automáticamente a la URL original
- Ej: `http://localhost:5001/ABC123` → `https://ejemplo.com/url-larga`

### URLs del usuario (requiere autenticación)

**GET** `/api/urls`
- Devuelve lista de URLs acortadas del usuario autenticado
- **Respuesta** (200):
  ```json
  [
    {
      "alias": "ABC123",
      "original_url": "https://ejemplo.com/url-larga",
      "created_at": "2025-11-27T10:30:45.123456"
    }
  ]
  ```

### Autenticación

**POST** `/auth/register`
- Crear nueva cuenta de usuario

**POST** `/auth/login`
- Iniciar sesión con credenciales

**GET/POST** `/auth/logout`
- Cerrar sesión

## Uso con PostgreSQL (Producción)

Para cambiar de SQLite a PostgreSQL:

1. Instalar driver de PostgreSQL:
   ```bash
   pip install psycopg2-binary
   ```

2. Actualizar `.env`:
   ```
   DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/acortador
   ```

3. Aplicar migraciones (la BD debe existir):
   ```bash
   export FLASK_APP=acortadorenlaces.py
   flask db upgrade
   ```

## Deployment (producción)

### Con Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 acortadorenlaces:app
```

### En Heroku

1. Crear archivo `Procfile`:
   ```
   web: gunicorn acortadorenlaces:app
   ```

2. Deployar:
   ```bash
   heroku create tu-app-name
   heroku config:set SECRET_KEY=tu-clave-segura
   heroku config:set DATABASE_URL=postgresql://...
   git push heroku main
   ```

## Notas de seguridad

⚠️ **En desarrollo:**
- `SECRET_KEY` es una clave dummy
- La BD es local en SQLite

🔒 **Para producción:**
- Cambiar `SECRET_KEY` a una cadena aleatoria fuerte (ej: `openssl rand -hex 32`)
- Usar PostgreSQL en lugar de SQLite
- Habilitar HTTPS (certificados SSL/TLS)
- No subir `.env` al repositorio
- Usar variables de entorno del servidor para secretos

## Solución de problemas

### Error: "unable to open database file"
- Verificar que la carpeta `data/` existe
- Verificar que `DATABASE_URL` en `.env` apunta a una ruta válida

### Error: "flask: command not found"
- Asegurar que el entorno virtual está activado: `source .venv/bin/activate`

### Error de migración: "Can't locate revision"
- Borrar carpeta `migrations/` y reintentar:
  ```bash
  rm -rf migrations/
  flask db init
  flask db migrate -m "Initial migration"
  flask db upgrade
  ```

## Contribuciones

Las contribuciones son bienvenidas. Para cambios mayores, abre un issue primero para discutir qué te gustaría cambiar.

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

---
*Copyright (c) 2026 Juande Molina*
