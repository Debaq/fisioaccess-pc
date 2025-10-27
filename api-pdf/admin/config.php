<?php
/**
 * admin/config.php - Configuración global del sistema
 */

require_once '../config.php';

session_start();

if (!verificarRol('admin')) {
    header('Location: login.php');
    exit;
}

$mensaje = '';
$tipo_mensaje = '';

// Procesar actualización
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $config = cargarJSON(CONFIG_FILE);
    
    $config['cuotas_default']['actividades_profesor'] = intval($_POST['cuota_actividades'] ?? 4);
    $config['cuotas_default']['estudios_por_tipo'] = intval($_POST['cuota_estudios'] ?? 1);
    
    guardarJSON(CONFIG_FILE, $config);
    
    $mensaje = 'Configuración actualizada exitosamente';
    $tipo_mensaje = 'success';
}

$config = cargarJSON(CONFIG_FILE);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuración - FisioaccessPC</title>
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
            padding: 20px;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 15px 25px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .navbar-brand {
            color: white;
            font-size: 20px;
            font-weight: 600;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        h1 {
            color: white;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: white;
            color: #7c3aed;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }
        
        .mensaje {
            background: rgba(34, 197, 94, 0.3);
            border: 1px solid rgba(34, 197, 94, 0.5);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            color: white;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 30px;
            margin-bottom: 20px;
        }
        
        .section-title {
            color: white;
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
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
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
        }
        
        input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .help-text {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 5px;
        }
        
        .info-box {
            background: rgba(59, 130, 246, 0.2);
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 12px;
            padding: 15px;
            color: white;
            margin-bottom: 20px;
        }
        
        .info-box strong {
            display: block;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">🫁 FisioaccessPC</div>
        <a href="dashboard.php" class="btn btn-secondary btn-small">← Volver al Dashboard</a>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>⚙️ Configuración del Sistema</h1>
            <p class="subtitle">Ajustes globales y cuotas por defecto</p>
        </div>
        
        <?php if ($mensaje): ?>
            <div class="mensaje">
                ✅ <?= htmlspecialchars($mensaje) ?>
            </div>
        <?php endif; ?>
        
        <div class="card">
            <div class="info-box">
                <strong>ℹ️ Información:</strong>
                Estos valores se aplican por defecto al crear nuevos profesores. 
                Las cuotas de profesores existentes deben modificarse individualmente 
                desde la gestión de profesores.
            </div>
            
            <form method="POST">
                <div class="section-title">Cuotas por Defecto</div>
                
                <div class="form-group">
                    <label>Actividades por Profesor</label>
                    <input type="number" name="cuota_actividades" 
                           value="<?= $config['cuotas_default']['actividades_profesor'] ?>" 
                           min="1" max="20" required>
                    <div class="help-text">
                        Número máximo de actividades que puede crear cada profesor por semestre
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Estudios por Tipo</label>
                    <input type="number" name="cuota_estudios" 
                           value="<?= $config['cuotas_default']['estudios_por_tipo'] ?>" 
                           min="1" max="10" required>
                    <div class="help-text">
                        Número máximo de estudios de cada tipo que puede subir cada estudiante por actividad
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    💾 Guardar Configuración
                </button>
            </form>
        </div>
        
        <div class="card">
            <div class="section-title">Información del Sistema</div>
            <div style="color: white; line-height: 1.8;">
                <div><strong>Versión:</strong> <?= $config['version'] ?></div>
                <div><strong>Instalado:</strong> <?= date('d/m/Y H:i', strtotime($config['instalado'])) ?></div>
            </div>
        </div>
    </div>
</body>
</html>