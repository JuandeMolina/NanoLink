# NanoLink

Aplicación web para acortar URLs con autenticación de usuarios, panel de control personal y panel de administración.

## Características

- ✅ Acortador de URLs rápido, sin necesidad de registro
- ✅ Autenticación de usuarios (registro / login / logout)
- ✅ Panel de control personal para gestionar tus enlaces
- ✅ Panel de administración para gestionar usuarios y todos los enlaces
- ✅ Superusuario creado automáticamente al arrancar desde variables de entorno
- ✅ Manejo centralizado de errores (403, 404, 405, 500, 503)
- ✅ API REST para acortar y gestionar enlaces
- ✅ Base de datos SQLite (desarrollo) o PostgreSQL (producción)
- ✅ Almacenamiento persistente con Flask-SQLAlchemy y migraciones con Flask-Migrate
- ✅ Diseño responsive sin dependencias de CSS externas

## Requisitos previos

- Python 3.8+
- pip

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/JuandeMolina/NanoLink.git
cd NanoLink
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```
FLASK_APP=nanolink.py
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-segura
DATABASE_URL=sqlite:///data/app.db

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@ejemplo.com
ADMIN_PASSWORD=tu-contraseña-segura
```

> ⚠️ `SECRET_KEY` debe ser idéntica en todos los entornos donde se compartan sesiones.  
> ⚠️ Nunca subas `.env` al repositorio.

### 5. Aplicar migraciones

```bash
flask db upgrade
```

### 6. Ejecutar la aplicación

```bash
python nanolink.py
```

Al arrancar, el script crea automáticamente el superusuario si no existe.  
La aplicación estará disponible en `http://127.0.0.1:5000`.

## Trabajar con dos ordenadores

Al hacer pull en el segundo ordenador, ejecuta siempre:

```bash
git pull
flask db upgrade   # aplica migraciones nuevas si las hay
python nanolink.py
```

Cada máquina tiene su propia base de datos local. Las migraciones (`migrations/`) se comparten en el repositorio para mantener el esquema sincronizado.

## Estructura del proyecto

```
NanoLink/
├── nanolink.py               # Punto de entrada principal
├── config.py                 # Configuración por entorno (dev, prod, test)
├── requirements.txt          # Dependencias de Python
├── pyproject.toml            # Metadatos del proyecto
├── .env                      # Variables de entorno (no subir a git)
├── .flaskenv                 # Variables de Flask para el CLI
├── .gitignore
├── data/                     # Base de datos SQLite (ignorada por git)
├── logs/                     # Logs de la aplicación (ignorados por git)
├── migrations/               # Migraciones de base de datos (Flask-Migrate)
├── scripts/
│   └── init_db.py            # Inicialización de BD y creación de superusuario
└── app/
    ├── __init__.py
    ├── models.py             # Modelos User y URL
    ├── core/
    │   └── __init__.py       # App factory, extensiones (db, login_manager)
    ├── routes/
    │   ├── main.py           # Rutas principales y API
    │   ├── auth.py           # Registro, login, logout
    │   └── admin.py          # Panel de administración
    ├── services/
    │   └── __init__.py       # URLService: lógica de negocio
    ├── errors/
    │   └── __init__.py       # Handlers de error (403, 404, 405, 500, 503)
    ├── utils/
    │   └── __init__.py       # Validación de URLs, decoradores (admin_required)
    ├── templates/
    │   ├── base.html         # Plantilla base con sistema de diseño
    │   ├── index.html        # Página principal
    │   ├── dashboard.html    # Panel de control del usuario
    │   ├── admin.html        # Panel de administración
    │   ├── login.html
    │   ├── register.html
    │   └── error.html        # Plantilla unificada de errores
    └── static/
        ├── manifest.json     # PWA manifest
        └── img/              # Iconos y favicon
```

## API Endpoints

### Público

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/<alias>` | Redirige a la URL original |
| `POST` | `/api/shorten` | Crea un enlace acortado |

**POST `/api/shorten`**
```json
// Body
{ "url": "https://ejemplo.com/url-larga" }

// Respuesta 201
{ "shortUrl": "http://localhost:5000/ABC123", "alias": "ABC123" }
```

### Requieren autenticación

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/dashboard` | Panel de control del usuario |
| `GET` | `/api/urls` | Lista de URLs del usuario autenticado |
| `DELETE` | `/api/urls/<id>` | Eliminar una URL propia |

### Autenticación

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET/POST` | `/auth/register` | Registro de nuevo usuario |
| `GET/POST` | `/auth/login` | Inicio de sesión |
| `GET/POST` | `/auth/logout` | Cierre de sesión |

### Panel de administración (requieren `is_admin`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/admin` | Dashboard con stats, usuarios y URLs |
| `POST` | `/admin/users/<id>/toggle-admin` | Promover o degradar un usuario |
| `DELETE` | `/admin/users/<id>` | Eliminar un usuario y sus enlaces |
| `DELETE` | `/admin/urls/<id>` | Eliminar cualquier enlace |

## Uso con PostgreSQL (producción)

1. Instalar el driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Actualizar `.env`:
   ```
   DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nanolink
   ```

3. Aplicar migraciones:
   ```bash
   flask db upgrade
   ```

## Despliegue con Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 nanolink:app
```

## Notas de seguridad

- Cambia `SECRET_KEY` por una cadena aleatoria fuerte: `openssl rand -hex 32`
- Usa PostgreSQL en producción
- Habilita HTTPS
- Nunca subas `.env` al repositorio

## Licencia

MIT — ver `LICENSE.txt` para más detalles.

---
*Copyright (c) 2026 Juande Molina*