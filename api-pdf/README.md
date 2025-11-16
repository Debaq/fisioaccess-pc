# FisioaccessPC - Sistema de Gestión de Estudios Fisiológicos

Sistema web completo para la gestión de prácticas de fisiología, que permite a profesores crear actividades, estudiantes realizar entregas y administradores gestionar el sistema.

**Versión:** 2.1
**Última actualización:** 2025-11-16

---

## 📋 Características

### Para Administradores
- ✅ Gestión de profesores (crear, editar, activar/desactivar)
- ✅ Configuración global del sistema (cuotas, límites)
- ✅ Visualización de estadísticas generales
- ✅ Acceso completo a logs de seguridad

### Para Profesores
- ✅ Creación y gestión de actividades
- ✅ Generación de accesos para estudiantes
- ✅ Subida de material pedagógico (guías, material complementario)
- ✅ Revisión y calificación de entregas
- ✅ Gestión de estudiantes inscritos

### Para Estudiantes
- ✅ Acceso mediante verificación por email institucional
- ✅ Descarga de material pedagógico
- ✅ Entrega de estudios (PDF + RAW)
- ✅ Visualización de retroalimentación y calificaciones

### Tipos de Estudios Soportados
- 🫁 Espirometría
- 💓 Electrocardiograma
- ⚡ Electromiografía
- 🧠 Electroencefalograma

---

## 🚀 Instalación

### Requisitos Previos
- PHP 7.4 o superior
- Servidor web (Apache/Nginx)
- Módulos PHP:
  - `json`
  - `fileinfo`
  - `mbstring`
- Permisos de escritura en carpeta `data/`

### Paso 1: Clonar o Descargar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/fisioaccess-pc.git
cd fisioaccess-pc/api-pdf

# O descargar ZIP y extraer
```

### Paso 2: Configurar Permisos

```bash
# Dar permisos de escritura a la carpeta data
chmod -R 755 data/
chmod -R 777 data/  # Si tienes problemas de permisos

# Crear carpetas necesarias
mkdir -p data/logs
mkdir -p data/uploads
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

**Configurar `.env`:**
```env
# Email SMTP
SMTP_HOST=tu-servidor-smtp.com
SMTP_PORT=465
SMTP_FROM=fisioaccess@tudominio.com
SMTP_FROM_NAME=FisioaccessPC
SMTP_USER=fisioaccess@tudominio.com
SMTP_PASS=tu_contraseña_segura

# Seguridad CORS
ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
# Usar * para desarrollo local

# Modo debug (true/false)
DEBUG_MODE=false
```

### Paso 4: Ejecutar Instalador

1. Accede a: `http://tudominio.com/api-pdf/install.php`
2. Completa el formulario con:
   - Usuario administrador (ej: `admin`)
   - Contraseña segura
   - Nombre completo
   - Email

3. ⚠️ **IMPORTANTE:** Elimina el archivo `install.php` después de instalar

```bash
rm install.php
```

### Paso 5: Verificar Instalación

1. Accede a `http://tudominio.com/api-pdf/`
2. Deberías ver la página principal con las 3 opciones de login
3. Ingresa como administrador con las credenciales creadas

---

## 🔧 Configuración Post-Instalación

### Crear el Primer Profesor

1. Login como admin → **Gestionar Profesores**
2. Click en **Crear Nuevo Profesor**
3. Completar formulario:
   - RUT (formato: 12345678-9)
   - Nombre completo
   - Email institucional
   - Contraseña
   - Cuota de actividades (default: 4)

### Configurar CORS para Producción

Editar `.env`:
```env
# Reemplazar * por dominios específicos
ALLOWED_ORIGINS=https://midominio.com,https://www.midominio.com
```

### Habilitar HTTPS (Recomendado)

Editar `config.php`:
```php
ini_set('session.cookie_secure', 1); // Cambiar 0 a 1
```

---

## 📖 Guía de Uso

### Para Profesores

#### 1. Crear Actividad
1. Login → Dashboard → **Nueva Actividad**
2. Completar información básica:
   - Nombre de la actividad
   - Tipo de estudio (espirometría, ecg, etc.)
   - Fecha inicio y cierre
   - Descripción
3. Subir material pedagógico (opcional):
   - Guía de laboratorio (PDF)
   - Material complementario (PDF/link)
4. Configurar accesos:
   - Seleccionar tipo de sesión (real/simulada)
   - Añadir estudiantes inscritos (opcional)

#### 2. Generar Accesos para Estudiantes
1. Ir a la actividad creada
2. **Generar Accesos** → Se crea un token único
3. Compartir token o link con estudiantes
4. Opción de enviar por email automático

#### 3. Revisar Entregas
1. Dashboard → **Actividades** → Seleccionar actividad
2. Ver lista de entregas pendientes/revisadas
3. Descargar PDF y RAW
4. Calificar y dar retroalimentación

### Para Estudiantes

#### 1. Acceder a Actividad
1. Recibir token o link del profesor
2. Ir a la URL de acceso
3. Ingresar email institucional
4. Ingresar código de 6 dígitos enviado por email

#### 2. Descargar Material
1. Dashboard → Ver actividad
2. Descargar guía de laboratorio
3. Descargar material complementario (si hay)

#### 3. Realizar Entrega
1. Usar software FisioaccessPC (Python) para generar estudio
2. El software envía automáticamente PDF + RAW al servidor
3. Ver entrega en dashboard

---

## 🔒 Seguridad

El sistema implementa múltiples capas de seguridad:

### Autenticación
- ✅ Contraseñas hasheadas con `password_hash()` (bcrypt)
- ✅ Sesiones con regeneración de ID (previene session fixation)
- ✅ Tokens CSRF en todos los formularios
- ✅ Cookies con flag `HttpOnly`, `SameSite=Strict`

### Rate Limiting
- ✅ Login: 5 intentos fallidos/hora por IP
- ✅ API endpoints: 10 intentos/hora por IP
- ✅ Emails: 5 intentos/hora por email

### Validación de Entrada
- ✅ Sanitización de todos los inputs
- ✅ Validación de RUT chileno con dígito verificador
- ✅ Validación de emails institucionales
- ✅ Protección contra Path Traversal
- ✅ Validación de tipos y tamaños de archivo

### CORS
- ✅ CORS configurado por dominio (no wildcard)
- ✅ Solo métodos GET, POST, OPTIONS permitidos

### Logging y Auditoría
- ✅ Todos los login (exitosos y fallidos) registrados
- ✅ Eventos de seguridad en log separado
- ✅ Rate limits excedidos registrados
- ✅ Intentos de path traversal detectados

### Archivos Protegidos
- ✅ Logs inaccesibles via HTTP (.htaccess)
- ✅ Archivos JSON de datos protegidos
- ✅ PHP deshabilitado en carpeta de uploads
- ✅ Credenciales en `.env` (no versionado)

---

## 📂 Estructura del Proyecto

```
api-pdf/
├── admin/                 # Panel de administración
│   ├── dashboard.php      # Dashboard admin
│   ├── login.php          # Login admin
│   ├── config.php         # Configuración sistema
│   └── profesores.php     # Gestión profesores
├── profesor/              # Panel de profesores
│   ├── dashboard.php      # Dashboard profesor
│   ├── login.php          # Login profesor
│   ├── actividades.php    # Gestión actividades
│   ├── accesos.php        # Generar accesos
│   ├── materiales.php     # Subir materiales
│   ├── estudiantes.php    # Gestión estudiantes
│   └── revisar.php        # Revisar entregas
├── estudiante/            # Panel de estudiantes
│   ├── dashboard.php      # Dashboard estudiante
│   ├── acceso.php         # Acceso con token
│   └── actividad_detalle.php
├── api/                   # API REST
│   ├── auth.php           # Autenticación
│   ├── acceso_estudiante.php  # Envío código verificación
│   ├── verificar_codigo.php   # Verificar código
│   ├── entregas.php       # Recibir entregas
│   ├── materiales.php     # Descargar materiales
│   └── generar_accesos.php
├── data/                  # Datos del sistema
│   ├── *.json             # Archivos de datos
│   ├── logs/              # Logs del sistema
│   │   ├── app.log
│   │   └── security.log
│   └── uploads/           # Archivos subidos
├── config.php             # Configuración global
├── .env                   # Variables de entorno
├── .env.example           # Plantilla de .env
├── .htaccess              # Configuración Apache
├── index.html             # Página principal
└── README.md              # Este archivo
```

---

## 📊 Monitoreo y Logs

### Ver Logs de Seguridad

```bash
# Ver últimos 50 eventos
tail -n 50 data/logs/security.log

# Ver en tiempo real
tail -f data/logs/security.log

# Buscar intentos de login fallidos
grep "fallido" data/logs/security.log

# Buscar rate limits excedidos
grep "Rate limit" data/logs/security.log
```

### Ver Logs Generales

```bash
# Ver últimos 100 eventos
tail -n 100 data/logs/app.log

# Filtrar por nivel ERROR
grep "ERROR" data/logs/app.log

# Ver entregas recibidas
grep "Entrega recibida" data/logs/app.log
```

### Ver Rate Limits Activos

```bash
# Ver todos los rate limits activos
cat data/rate_limits.json | python -m json.tool

# O con jq
cat data/rate_limits.json | jq
```

---

## 🐛 Troubleshooting

### Error: "No se puede enviar email"

1. Verificar credenciales en `.env`
2. Verificar que el puerto 465 (SSL) esté abierto
3. Revisar logs: `grep "email" data/logs/app.log`
4. Probar con `mail()` nativo si PHPMailer falla

### Error: "No se puede escribir en data/"

```bash
# Dar permisos de escritura
chmod -R 777 data/
# O ajustar owner
chown -R www-data:www-data data/
```

### Error: "CORS blocked"

Verificar en `.env` que tu dominio esté en `ALLOWED_ORIGINS`:
```env
ALLOWED_ORIGINS=https://tudominio.com
```

### Rate Limit Bloqueando Usuario Legítimo

```bash
# Limpiar rate limits manualmente
echo "{}" > data/rate_limits.json
```

### Sesión Expirada Constantemente

Verificar en `config.php`:
```php
define('SESSION_TIMEOUT', 7200); // 2 horas, ajustar si necesario
```

---

## 🔄 Actualización

### Actualizar Código

```bash
# Backup de datos
cp -r data/ data_backup/

# Actualizar código
git pull origin main

# O reemplazar archivos manualmente, EXCEPTO:
# - data/ (NO reemplazar)
# - .env (NO reemplazar)
```

### Migración de Datos

Si hay cambios en estructura de datos, revisar `CHANGELOG.md` para scripts de migración.

---

## 📝 API Documentation

### POST /api/auth.php?action=login
Autenticar usuario (admin, profesor, estudiante)

**Request:**
```json
{
  "rol": "profesor",
  "rut": "12345678-9",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "rol": "profesor",
    "rut": "12345678-9",
    "nombre": "Juan Pérez"
  }
}
```

### POST /api/entregas.php
Recibir entrega desde software externo

**Request (multipart/form-data):**
```
pdf: archivo.pdf
raw: datos.json
owner: juan@uach.cl
type: espirometria
comments: Estudio realizado en laboratorio
actividad_id: ACT123 (opcional)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ENT12AB34CD",
    "actividad_id": "ACT123",
    "timestamp": "2025-11-16T14:30:00Z"
  }
}
```

Ver documentación completa de API en: `API_DOCS.md` (próximamente)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir Pull Request

---

## 📄 Licencia

Este proyecto es software educativo desarrollado para la Universidad Austral de Chile, Sede Puerto Montt.

---

## 👥 Créditos

**Desarrollado por:** TecMedHub
**Universidad:** Universidad Austral de Chile - Sede Puerto Montt
**Versión:** 2.1
**Año:** 2025

---

## 📞 Soporte

Para reportar bugs o solicitar features:
- Crear un issue en GitHub
- Email: soporte@tudominio.com

---

## 📚 Documentación Adicional

- [`SECURITY_IMPROVEMENTS.md`](SECURITY_IMPROVEMENTS.md) - Mejoras de seguridad implementadas
- [`MEJORAS_PRIORIDAD_ALTA.md`](MEJORAS_PRIORIDAD_ALTA.md) - Rate limiting, logging y validaciones
- [`REVISION_COMPLETA.md`](REVISION_COMPLETA.md) - Revisión completa de seguridad

---

**¡Gracias por usar FisioaccessPC!** 🫁
