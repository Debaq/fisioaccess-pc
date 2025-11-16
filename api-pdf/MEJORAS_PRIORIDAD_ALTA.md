# Mejoras de Prioridad ALTA Implementadas
**Fecha:** 2025-11-16
**Versión:** FisioaccessPC v2.0.1

## 🚀 Nuevas Funcionalidades

### 1. Sistema de Rate Limiting Avanzado

**Implementación:**
- Rate limiting por IP, email y tipo de operación
- Ventana deslizante de 1 hora
- Límites configurables por tipo:
  - IP: 10 intentos/hora
  - Email: 5 intentos/hora
  - Login: 5 intentos fallidos/hora

**Funciones en config.php:**
- `verificarRateLimit($tipo, $clave, $max_intentos)` - Verifica si se excedió el límite
- `registrarIntento($tipo, $clave, $exitoso)` - Registra un intento
- `limpiarRateLimits()` - Limpia entradas expiradas

**Aplicado en:**
- `api/acceso_estudiante.php` - Rate limiting por IP y email
- `admin/login.php` - Rate limiting por IP
- `profesor/login.php` - Rate limiting por IP

**Configuración:**
```php
define('RATE_LIMIT_WINDOW', 3600); // 1 hora
define('RATE_LIMIT_MAX_ATTEMPTS_IP', 10);
define('RATE_LIMIT_MAX_ATTEMPTS_EMAIL', 5);
define('RATE_LIMIT_LOGIN_ATTEMPTS', 5);
```

---

### 2. Sistema de Logging Completo

**Implementación:**
- Logs separados: `app.log` (general) y `security.log` (seguridad)
- Niveles: INFO, WARNING, ERROR, SECURITY
- Incluye: timestamp, nivel, IP, mensaje, URI, contexto

**Funciones en config.php:**
- `registrarLog($nivel, $mensaje, $contexto)` - Log general
- `registrarEventoSeguridad($evento, $detalles)` - Log de seguridad específico

**Eventos Registrados:**
- ✅ Login exitoso/fallido (admin, profesor, estudiante)
- ✅ CSRF token inválido
- ✅ Rate limit excedido
- ✅ Código de verificación enviado
- ✅ Error al enviar email
- ✅ Estudiante verificado y autenticado
- ✅ Cuenta desactivada
- ✅ Usuario no encontrado

**Ubicación de logs:**
```
api-pdf/data/logs/
├── app.log          # Logs generales (INFO, WARNING, ERROR)
└── security.log     # Logs de seguridad
```

**Formato de log:**
```
[2025-11-16 14:30:45] [SECURITY] [IP: 192.168.1.100] Login profesor exitoso /api-pdf/profesor/login.php {"rut":"12345678-9","ip":"192.168.1.100"}
```

---

### 3. Validaciones Centralizadas

**Funciones Implementadas:**

#### `validarRUT($rut)`
Valida RUT chileno con dígito verificador

```php
$valido = validarRUT('12345678-9'); // true o false
```

#### `validarEmail($email, $opciones)`
Validación avanzada de email con opciones

```php
$resultado = validarEmail('usuario@uach.cl', [
    'dominio_requerido' => 'uach.cl',
    'blacklist' => ['spam@uach.cl']
]);
// Retorna: ['valido' => bool, 'error' => string, 'email' => string]
```

#### `sanitizarString($string, $opciones)`
Sanitización configurable para prevenir XSS

```php
$limpio = sanitizarString($input, [
    'trim' => true,
    'strip_tags' => true,
    'max_length' => 255
]);
```

#### `validarNoVacio($valor, $nombre_campo)`
Validación de campos requeridos

```php
$resultado = validarNoVacio($username, 'Usuario');
// Retorna: ['valido' => bool, 'error' => string, 'valor' => string]
```

#### `validarLongitud($string, $min, $max, $nombre_campo)`
Validación de longitud de strings

```php
$resultado = validarLongitud($password, 8, 64, 'Contraseña');
// Retorna: ['valido' => bool, 'error' => string]
```

#### `obtenerIP()`
Obtiene IP real del cliente (considerando proxies)

```php
$ip = obtenerIP(); // Retorna IP válida o '0.0.0.0'
```

---

### 4. File Locking en Operaciones JSON

**Problema Resuelto:**
Race conditions al escribir archivos JSON simultáneamente

**Implementación:**
```php
function guardarJSON($archivo, $datos) {
    $fp = fopen($archivo, 'c');
    if ($fp) {
        if (flock($fp, LOCK_EX)) { // Bloqueo exclusivo
            ftruncate($fp, 0);
            fwrite($fp, $json);
            fflush($fp);
            flock($fp, LOCK_UN); // Liberar bloqueo
            fclose($fp);
            return true;
        }
    }
    return false;
}
```

**Beneficios:**
- ✅ Previene corrupción de datos
- ✅ Asegura integridad en escrituras concurrentes
- ✅ Logs de errores si falla el lock

---

## 📂 Archivos Modificados

```
api-pdf/
├── config.php                    [MODIFICADO] - +400 líneas de funciones nuevas
├── .htaccess                     [MODIFICADO] - Protección de logs
├── api/
│   ├── acceso_estudiante.php    [MODIFICADO] - Rate limiting + logging
│   └── verificar_codigo.php     [MODIFICADO] - Logging de autenticación
├── admin/
│   └── login.php                [MODIFICADO] - Rate limiting + logging
├── profesor/
│   └── login.php                [MODIFICADO] - Rate limiting + logging
└── data/
    ├── rate_limits.json         [NUEVO] - Almacena contadores de rate limiting
    └── logs/
        ├── app.log              [NUEVO] - Logs generales
        └── security.log         [NUEVO] - Logs de seguridad
```

---

## 🔒 Mejoras de Seguridad

### Antes vs Ahora

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Rate Limiting** | Básico (60s) | Avanzado (por IP/email/tipo) |
| **Logging** | Solo error_log | Sistema completo con niveles |
| **File Locking** | ❌ | ✅ Locks exclusivos |
| **Validaciones** | Dispersas | Centralizadas y reutilizables |
| **Detección de IP** | REMOTE_ADDR | Considera proxies |
| **Auditoría** | Limitada | Completa (security.log) |

---

## 📊 Ejemplo de Uso

### Rate Limiting
```php
// En cualquier endpoint crítico
$ip = obtenerIP();

if (!verificarRateLimit('login', $ip)) {
    registrarEventoSeguridad('Rate limit excedido', ['ip' => $ip]);
    responderJSON([
        'error' => 'Demasiados intentos. Intenta en 1 hora.'
    ], 429);
}

// Registrar el intento
registrarIntento('login', $ip, $login_exitoso);
```

### Logging
```php
// Log general
registrarLog('INFO', 'Actividad creada', ['actividad_id' => $id]);

// Log de seguridad
registrarEventoSeguridad('Acceso no autorizado', [
    'usuario' => $username,
    'ip' => obtenerIP()
]);
```

### Validaciones
```php
// Validar email institucional
$validacion = validarEmail($email, ['dominio_requerido' => 'uach.cl']);
if (!$validacion['valido']) {
    responderJSON(['error' => $validacion['error']], 400);
}

// Validar RUT
if (!validarRUT($rut)) {
    responderJSON(['error' => 'RUT inválido'], 400);
}
```

---

## 🛡️ Protecciones Adicionales

### .htaccess
```apache
# Proteger archivos de logs
<FilesMatch "\.(log)$">
    Require all denied
</FilesMatch>

# Proteger archivos JSON sensibles
<FilesMatch "rate_limits\.json$">
    Require all denied
</FilesMatch>
```

---

## 📈 Monitoreo

### Ver Logs
```bash
# Ver últimos eventos de seguridad
tail -f api-pdf/data/logs/security.log

# Ver todos los logs
tail -f api-pdf/data/logs/app.log

# Buscar intentos fallidos
grep "fallido" api-pdf/data/logs/security.log

# Ver rate limits activos
cat api-pdf/data/rate_limits.json | jq
```

---

## 🔜 Mejoras Futuras Recomendadas

1. **Rotación de Logs:** Implementar rotación automática de logs por tamaño/fecha
2. **Dashboard de Logs:** Interfaz web para visualizar logs
3. **Alertas por Email:** Notificaciones de eventos críticos
4. **Geolocalización de IPs:** Detectar accesos desde ubicaciones inusuales
5. **Blacklist Automática:** Bloquear IPs con intentos maliciosos repetidos
6. **Webhook Notifications:** Integración con Slack/Discord para alertas
7. **Análisis de Patrones:** Machine learning para detectar comportamiento anómalo

---

## 📚 Referencias

- [OWASP Rate Limiting](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)
- [PHP File Locking](https://www.php.net/manual/en/function.flock.php)
- [Security Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
