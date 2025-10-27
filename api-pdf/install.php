<?php
/**
 * install.php - Instalador del sistema
 * Crea estructura de carpetas, archivos JSON y primer admin
 * 
 * ⚠️ ELIMINAR ESTE ARCHIVO DESPUÉS DE LA INSTALACIÓN
 */

require_once 'config.php';

$instalado = false;
$mensaje = '';
$tipo_mensaje = '';

// Verificar si ya está instalado
if (file_exists(CONFIG_FILE) && file_exists(ADMINS_FILE)) {
    $instalado = true;
    $mensaje = '⚠️ El sistema ya está instalado. Si desea reinstalar, elimine la carpeta /data primero.';
    $tipo_mensaje = 'warning';
}

// Procesar instalación
if ($_SERVER['REQUEST_METHOD'] === 'POST' && !$instalado) {
    $username = trim($_POST['username'] ?? 'admin');
    $password = $_POST['password'] ?? '';
    $nombre = trim($_POST['nombre'] ?? 'Administrador');
    $email = trim($_POST['email'] ?? '');
    
    if (empty($password)) {
        $mensaje = '❌ La contraseña es requerida';
        $tipo_mensaje = 'error';
    } else {
        try {
            // Crear estructura de carpetas
            $carpetas = [
                DATA_PATH,
                UPLOADS_PATH
            ];
            
            foreach ($carpetas as $carpeta) {
                if (!is_dir($carpeta)) {
                    mkdir($carpeta, 0755, true);
                }
            }
            
            // Crear config.json
            $config = [
                'version' => '2.0.0',
                'instalado' => formatearFecha(),
                'cuotas_default' => [
                    'actividades_profesor' => 4,
                    'estudios_por_tipo' => 1
                ]
            ];
            guardarJSON(CONFIG_FILE, $config);
            
            // Crear admin
            $admins = [
                $username => [
                    'username' => $username,
                    'password_hash' => password_hash($password, PASSWORD_DEFAULT),
                    'nombre' => $nombre,
                    'email' => $email,
                    'created' => formatearFecha(),
                    'last_login' => null
                ]
            ];
            guardarJSON(ADMINS_FILE, $admins);
            
            // Crear archivos vacíos
            guardarJSON(PROFESORES_FILE, []);
            guardarJSON(ESTUDIANTES_FILE, []);
            guardarJSON(ACTIVIDADES_FILE, []);
            guardarJSON(ENTREGAS_FILE, []);
            guardarJSON(RESERVAS_FILE, []);
            
            $mensaje = '✅ ¡Instalación completada exitosamente!<br><br>' .
                      '<strong>Usuario administrador creado:</strong><br>' .
                      'Usuario: ' . htmlspecialchars($username) . '<br>' .
                      'Contraseña: (la que ingresaste)<br><br>' .
                      '⚠️ <strong>IMPORTANTE:</strong> Elimina el archivo install.php por seguridad.<br><br>' .
                      '<a href="admin/login.php" style="color: white; text-decoration: underline;">Ir al login de administrador →</a>';
            $tipo_mensaje = 'success';
            $instalado = true;
            
        } catch (Exception $e) {
            $mensaje = '❌ Error en la instalación: ' . $e->getMessage();
            $tipo_mensaje = 'error';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instalación - FisioaccessPC</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #c084fc 0%, #a855f7 50%, #7c3aed 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: white;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .mensaje {
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            color: white;
        }
        
        .mensaje.success {
            background: rgba(34, 197, 94, 0.3);
            border: 1px solid rgba(34, 197, 94, 0.5);
        }
        
        .mensaje.error {
            background: rgba(239, 68, 68, 0.3);
            border: 1px solid rgba(239, 68, 68, 0.5);
        }
        
        .mensaje.warning {
            background: rgba(251, 191, 36, 0.3);
            border: 1px solid rgba(251, 191, 36, 0.5);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: white;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
        }
        
        input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            background: white;
            color: #7c3aed;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .info {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 12px;
            margin-top: 20px;
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Instalación del Sistema</h1>
        <p class="subtitle">FisioaccessPC v2.0</p>
        
        <?php if ($mensaje): ?>
            <div class="mensaje <?= $tipo_mensaje ?>">
                <?= $mensaje ?>
            </div>
        <?php endif; ?>
        
        <?php if (!$instalado): ?>
            <form method="POST">
                <div class="form-group">
                    <label>Usuario Administrador</label>
                    <input type="text" name="username" value="admin" required>
                </div>
                
                <div class="form-group">
                    <label>Contraseña *</label>
                    <input type="password" name="password" required>
                </div>
                
                <div class="form-group">
                    <label>Nombre Completo</label>
                    <input type="text" name="nombre" value="Administrador del Sistema" required>
                </div>
                
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" placeholder="admin@universidad.cl">
                </div>
                
                <button type="submit" class="btn">Instalar Sistema</button>
            </form>
            
            <div class="info">
                <strong>ℹ️ Nota:</strong> Este proceso creará la estructura de carpetas, 
                archivos de configuración y el usuario administrador inicial.
            </div>
        <?php endif; ?>
    </div>
</body>
</html>