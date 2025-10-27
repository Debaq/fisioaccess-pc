<?php
/**
 * profesor/dashboard.php - Panel principal del profesor
 */

require_once '../config.php';

session_start();

if (!verificarRol('profesor')) {
    header('Location: login.php');
    exit;
}

$rut = $_SESSION['rut'];
$profesores = cargarJSON(PROFESORES_FILE);
$profesor = $profesores[$rut];

// Cargar actividades del profesor
$todas_actividades = cargarJSON(ACTIVIDADES_FILE);
$mis_actividades = array_filter($todas_actividades, fn($a) => $a['profesor_rut'] === $rut);

// Cargar entregas
$todas_entregas = cargarJSON(ENTREGAS_FILE);
$mis_entregas = array_filter($todas_entregas, function($e) use ($mis_actividades) {
    return isset($mis_actividades[$e['actividad_id']]);
});

$stats = [
    'actividades_creadas' => count($mis_actividades),
    'cuota_disponible' => $profesor['cuota_actividades'] - $profesor['actividades_usadas'],
    'entregas_totales' => count($mis_entregas),
    'entregas_pendientes' => count(array_filter($mis_entregas, fn($e) => $e['revision']['estado'] === 'pendiente'))
];
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Profesor - FisioaccessPC</title>
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
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .navbar-brand {
            color: white;
            font-size: 20px;
            font-weight: 600;
        }
        
        .navbar-user {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 36px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            text-align: center;
            color: white;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .action-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 30px;
            text-align: center;
            text-decoration: none;
            color: white;
            transition: all 0.3s;
        }
        
        .action-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.2);
        }
        
        .action-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .action-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .action-description {
            font-size: 13px;
            opacity: 0.9;
        }
        
        .logout-btn {
            background: rgba(239, 68, 68, 0.3);
            border: 1px solid rgba(239, 68, 68, 0.5);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .logout-btn:hover {
            background: rgba(239, 68, 68, 0.4);
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">🫁 FisioaccessPC</div>
        <div style="display: flex; gap: 15px; align-items: center;">
            <span class="navbar-user">👨‍🏫 <?= htmlspecialchars($_SESSION['nombre']) ?></span>
            <a href="../api/auth.php?action=logout" class="logout-btn">Cerrar Sesión</a>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>Panel del Profesor</h1>
            <p class="subtitle">Gestiona tus actividades y revisa entregas</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value"><?= $stats['actividades_creadas'] ?></div>
                <div class="stat-label">Actividades Creadas</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value"><?= $stats['cuota_disponible'] ?></div>
                <div class="stat-label">Cuota Disponible</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value"><?= $stats['entregas_totales'] ?></div>
                <div class="stat-label">Entregas Recibidas</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value"><?= $stats['entregas_pendientes'] ?></div>
                <div class="stat-label">Pendientes de Revisar</div>
            </div>
        </div>
        
        <div class="actions-grid">
            <a href="actividades.php" class="action-card">
                <div class="action-icon">📚</div>
                <div class="action-title">Mis Actividades</div>
                <div class="action-description">
                    Crear, editar y gestionar actividades
                </div>
            </a>
            
            <a href="estudiantes.php" class="action-card">
                <div class="action-icon">👥</div>
                <div class="action-title">Mis Estudiantes</div>
                <div class="action-description">
                    Subir CSV y gestionar estudiantes
                </div>
            </a>
            
            <a href="revisar.php" class="action-card">
                <div class="action-icon">✅</div>
                <div class="action-title">Revisar Entregas</div>
                <div class="action-description">
                    Calificar y retroalimentar trabajos
                </div>
            </a>
            
            <a href="../index.html" class="action-card">
                <div class="action-icon">🏠</div>
                <div class="action-title">Volver al Inicio</div>
                <div class="action-description">
                    Regresar a la página principal
                </div>
            </a>
        </div>
    </div>
</body>
</html>