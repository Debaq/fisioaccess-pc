<?php
/**
 * estudiante/dashboard.php - Panel principal del estudiante
 */

require_once '../config.php';

session_start();

if (!verificarRol('estudiante')) {
    header('Location: login.php');
    exit;
}

$rut = $_SESSION['rut'];
$estudiantes = cargarJSON(ESTUDIANTES_FILE);
$estudiante = $estudiantes[$rut];

// Cargar estudios del estudiante
$actividades = cargarJSON(ACTIVIDADES_FILE);
$mis_estudios = array_filter($actividades, function($act) use ($rut) {
    return in_array($rut, $act['estudiantes_inscritos'] ?? []);
});

// Cargar entregas del estudiante
$entregas = cargarJSON(ENTREGAS_FILE);
$mis_entregas = array_filter($entregas, fn($e) => $e['estudiante_rut'] === $rut);

// Estadísticas
$stats = [
    'estudios_activos' => count($mis_estudios),
    'entregas_realizadas' => count($mis_entregas),
    'entregas_pendientes' => count(array_filter($mis_estudios, function($est) use ($mis_entregas) {
        $entregado = false;
        foreach ($mis_entregas as $e) {
            if ($e['actividad_id'] === $est['id']) {
                $entregado = true;
                break;
            }
        }
        return !$entregado;
    })),
'promedio' => 0
];

// Calcular promedio
$calificadas = array_filter($mis_entregas, fn($e) => $e['revision']['estado'] === 'revisada');
if (count($calificadas) > 0) {
    $suma = array_sum(array_map(fn($e) => $e['revision']['nota'] ?? 0, $calificadas));
    $stats['promedio'] = round($suma / count($calificadas), 1);
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Estudiante - FisioaccessPC</title>
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
    color: white;
}

.navbar-brand {
    font-size: 20px;
    font-weight: 600;
}

.user-info {
    display: flex;
    gap: 15px;
    align-items: center;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 25px;
    margin-bottom: 20px;
    color: white;
}

.header h1 {
    font-size: 28px;
    margin-bottom: 5px;
}

.header p {
    opacity: 0.9;
    font-size: 15px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 20px;
    color: white;
    text-align: center;
}

.stat-value {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 5px;
}

.stat-label {
    opacity: 0.9;
    font-size: 14px;
}

.section {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 25px;
    margin-bottom: 20px;
    color: white;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.estudios-grid {
    display: grid;
    gap: 15px;
}

.estudio-card {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 20px;
}

.estudio-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 15px;
}

.estudio-nombre {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 5px;
}

.estudio-tipo {
    display: inline-block;
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    margin-bottom: 8px;
}

.estudio-descripcion {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 15px;
    line-height: 1.5;
}

.estudio-info {
    display: flex;
    gap: 20px;
    font-size: 13px;
    opacity: 0.8;
    margin-bottom: 15px;
}

.estudio-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: all 0.2s;
}

.btn-primary {
    background: white;
    color: #7c3aed;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.3);
}

.btn-success {
    background: rgba(34, 197, 94, 0.3);
    color: white;
    border: 1px solid rgba(34, 197, 94, 0.5);
}

.btn-small {
    padding: 6px 12px;
    font-size: 13px;
}

.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

.badge-pending {
    background: rgba(251, 191, 36, 0.3);
    border: 1px solid rgba(251, 191, 36, 0.5);
}

.badge-completed {
    background: rgba(34, 197, 94, 0.3);
    border: 1px solid rgba(34, 197, 94, 0.5);
}

.badge-graded {
    background: rgba(59, 130, 246, 0.3);
    border: 1px solid rgba(59, 130, 246, 0.5);
}

.token-section {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin-top: 15px;
}

.token-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 10px;
}

.token-description {
    font-size: 14px;
    opacity: 0.8;
    margin-bottom: 15px;
}

.token-display {
    background: rgba(0, 0, 0, 0.3);
    padding: 12px;
    border-radius: 8px;
    font-family: monospace;
    font-size: 13px;
    word-break: break-all;
    margin-bottom: 10px;
    display: none;
}

.token-display.show {
    display: block;
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
}

.empty-icon {
    font-size: 64px;
    margin-bottom: 15px;
}

.empty-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
}

.empty-text {
    opacity: 0.8;
    font-size: 14px;
}
</style>
</head>
<body>
<div class="navbar">
<div class="navbar-brand">🫁 FisioaccessPC</div>
<div class="user-info">
<span><?= htmlspecialchars($estudiante['nombre']) ?></span>
<a href="logout.php" class="btn btn-secondary btn-small">Cerrar Sesión</a>
</div>
</div>

<div class="container">
<div class="header">
<h1>👋 Bienvenido, <?= htmlspecialchars(explode(' ', $estudiante['nombre'])[0]) ?></h1>
<p><?= htmlspecialchars($estudiante['email']) ?></p>
</div>

<div class="stats-grid">
<div class="stat-card">
<div class="stat-value"><?= $stats['estudios_activos'] ?></div>
<div class="stat-label">Estudios Activos</div>
</div>

<div class="stat-card">
<div class="stat-value"><?= $stats['entregas_realizadas'] ?></div>
<div class="stat-label">Entregas Realizadas</div>
</div>

<div class="stat-card">
<div class="stat-value"><?= $stats['entregas_pendientes'] ?></div>
<div class="stat-label">Pendientes</div>
</div>

<div class="stat-card">
<div class="stat-value"><?= $stats['promedio'] ?></div>
<div class="stat-label">Promedio</div>
</div>
</div>

<!-- Token para Desktop -->
<div class="section">
<div class="section-title">🔑 Token de Acceso Desktop</div>
<div class="token-section">
<div class="token-title">Token para Software de Escritorio</div>
<div class="token-description">
Genera un token de autenticación para usar en el software FisioaccessPC de escritorio.
Este token es personal e intransferible.
</div>
<div id="tokenDisplay" class="token-display"></div>
<div style="display: flex; gap: 10px;">
<button onclick="generarToken()" class="btn btn-primary">Generar Token</button>
<button onclick="copiarToken()" class="btn btn-secondary" id="copiarBtn" style="display: none;">
Copiar Token
</button>
</div>
</div>
</div>

<!-- Mis Estudios -->
<div class="section">
<div class="section-title">📚 Mis Estudios y Actividades</div>

<?php if (empty($mis_estudios)): ?>
<div class="empty-state">
<div class="empty-icon">📭</div>
<div class="empty-title">No tienes estudios activos</div>
<div class="empty-text">
Cuando tu profesor te inscriba en un estudio, aparecerá aquí
</div>
</div>
<?php else: ?>
<div class="estudios-grid">
<?php foreach ($mis_estudios as $estudio): ?>
<?php
// Verificar si ya entregó
$entrega = null;
foreach ($mis_entregas as $e) {
    if ($e['actividad_id'] === $estudio['id']) {
        $entrega = $e;
        break;
    }
}

$tiene_entrega = $entrega !== null;
$revisada = $tiene_entrega && $entrega['revision']['estado'] === 'revisada';
?>
<div class="estudio-card">
<div class="estudio-header">
<div>
<div class="estudio-nombre">
<?= htmlspecialchars($estudio['info_basica']['nombre']) ?>
</div>
<span class="estudio-tipo">
<?= htmlspecialchars($estudio['info_basica']['tipo']) ?>
</span>
</div>
<div>
<?php if (!$tiene_entrega): ?>
<span class="badge badge-pending">⏳ Pendiente</span>
<?php elseif ($revisada): ?>
<span class="badge badge-graded">
✓ Calificado: <?= $entrega['revision']['nota'] ?>
</span>
<?php else: ?>
<span class="badge badge-completed">✓ Entregado</span>
<?php endif; ?>
</div>
</div>

<div class="estudio-descripcion">
<?= nl2br(htmlspecialchars($estudio['info_basica']['descripcion'])) ?>
</div>

<div class="estudio-info">
<span>📅 Creado: <?= date('d/m/Y', strtotime($estudio['metadata']['fecha_creacion'])) ?></span>
<span>👨‍🏫 ID Profesor: <?= substr($estudio['profesor_rut'], 0, 8) ?>...</span>
</div>

<div class="estudio-actions">
<?php if ($estudio['archivos']['pdf_path']): ?>
<a href="../<?= htmlspecialchars($estudio['archivos']['pdf_path']) ?>"
download
class="btn btn-primary btn-small">
📄 Descargar PDF
</a>
<?php endif; ?>

<?php if ($estudio['archivos']['material_complementario']): ?>
<a href="../<?= htmlspecialchars($estudio['archivos']['material_complementario']) ?>"
download
class="btn btn-secondary btn-small">
📎 Material Extra
</a>
<?php endif; ?>

<?php if (!$tiene_entrega): ?>
<a href="entregar.php?actividad=<?= $estudio['id'] ?>"
class="btn btn-success btn-small">
✍️ Entregar Trabajo
</a>
<?php elseif ($revisada && $entrega['revision']['retroalimentacion']): ?>
<button onclick="verRetroalimentacion('<?= $estudio['id'] ?>')"
class="btn btn-secondary btn-small">
💬 Ver Retroalimentación
</button>
<?php endif; ?>
</div>
</div>
<?php endforeach; ?>
</div>
<?php endif; ?>
</div>
</div>

<script>
let tokenActual = '';

async function generarToken() {
    try {
        const response = await fetch('generar_token.php', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            tokenActual = data.token;
            document.getElementById('tokenDisplay').textContent = tokenActual;
            document.getElementById('tokenDisplay').classList.add('show');
            document.getElementById('copiarBtn').style.display = 'inline-block';
        } else {
            alert('Error al generar token: ' + data.message);
        }
    } catch (error) {
        alert('Error al generar token');
        console.error(error);
    }
}

function copiarToken() {
    navigator.clipboard.writeText(tokenActual).then(() => {
        const btn = document.getElementById('copiarBtn');
        const textoOriginal = btn.textContent;
        btn.textContent = '✓ Copiado!';
    setTimeout(() => {
        btn.textContent = textoOriginal;
    }, 2000);
    });
}

function verRetroalimentacion(actividadId) {
    // Abrir modal o ventana con retroalimentación
    window.location.href = 'retroalimentacion.php?actividad=' + actividadId;
}
</script>
</body>
</html>
