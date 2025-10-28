<?php
/**
 * estudiante/acceso.php - Página de acceso para estudiantes con login automático
 * URL: /estudiante/acceso.php?token=ABC123
 */

require_once '../config.php';

// Verificar si ya está autenticado como estudiante
session_start();
if (isset($_SESSION['authenticated']) && $_SESSION['rol'] === 'estudiante') {
    header('Location: dashboard.php');
    exit;
}

$token_actividad = $_GET['token'] ?? '';

if (empty($token_actividad)) {
    die('Token de actividad no proporcionado');
}

// Buscar actividad
$actividades = cargarJSON(ACTIVIDADES_FILE);
$actividad = null;
$actividad_id = null;

foreach ($actividades as $id => $act) {
    if (isset($act['accesos']['token_actividad']) &&
        $act['accesos']['token_actividad'] === $token_actividad) {
        $actividad = $act;
    $actividad_id = $id;
    break;
        }
}

if (!$actividad) {
    die('Actividad no encontrada');
}

// Verificar fechas
$ahora = time();
$fecha_inicio = strtotime($actividad['info_basica']['fecha_inicio']);
$fecha_cierre = strtotime($actividad['info_basica']['fecha_cierre']);

$actividad_abierta = $ahora >= $fecha_inicio && $ahora <= $fecha_cierre;
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?= htmlspecialchars($actividad['info_basica']['nombre']) ?> - FisioaccessPC</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 40px;
    max-width: 500px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.logo {
    text-align: center;
    margin-bottom: 30px;
}

.logo-icon {
    font-size: 48px;
    margin-bottom: 10px;
}

.logo-text {
    font-size: 24px;
    font-weight: 700;
    color: #7c3aed;
}

.actividad-card {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 30px;
}

.actividad-nombre {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 10px;
}

.actividad-detalles {
    font-size: 14px;
    opacity: 0.95;
}

.actividad-detalles p {
    margin: 5px 0;
}

.closed-message {
    text-align: center;
    padding: 40px 20px;
}

.closed-icon {
    font-size: 64px;
    margin-bottom: 20px;
}

h2 {
    color: #1f2937;
    font-size: 24px;
    margin-bottom: 20px;
    text-align: center;
}

.step-indicator {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-bottom: 30px;
}

.step {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #6b7280;
    position: relative;
}

.step.active {
    background: #7c3aed;
    color: white;
}

.step.completed {
    background: #10b981;
    color: white;
}

.form-section {
    display: none;
}

.form-section.active {
    display: block;
}

.form-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 8px;
    color: #374151;
    font-weight: 500;
}

input {
    width: 100%;
    padding: 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.2s;
}

input:focus {
    outline: none;
    border-color: #7c3aed;
}

.btn {
    width: 100%;
    padding: 14px;
    background: #7c3aed;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 10px;
}

.btn:hover {
    background: #6d28d9;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
}

.btn:disabled {
    background: #9ca3af;
    cursor: not-allowed;
    transform: none;
}

.btn-secondary {
    background: white;
    color: #7c3aed;
    border: 2px solid #7c3aed;
}

.btn-secondary:hover {
    background: #f3f4f6;
}

.alert {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 14px;
}

.alert-info {
    background: #dbeafe;
    border: 1px solid #93c5fd;
    color: #1e40af;
}

.alert-success {
    background: #d1fae5;
    border: 1px solid #6ee7b7;
    color: #065f46;
}

.alert-error {
    background: #fee2e2;
    border: 1px solid #fca5a5;
    color: #991b1b;
}

.help-text {
    font-size: 13px;
    color: #6b7280;
    margin-top: 5px;
}

.success-card {
    text-align: center;
    padding: 20px;
}

.success-icon {
    font-size: 64px;
    margin-bottom: 20px;
}

.loading {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.redirect-message {
    text-align: center;
    padding: 20px;
    background: #f3f4f6;
    border-radius: 8px;
    margin-top: 20px;
}

.redirect-message .loading {
    border-color: #7c3aed;
    border-top-color: transparent;
    width: 24px;
    height: 24px;
    margin: 0 auto 10px;
}
</style>
</head>
<body>
<div class="container">
<div class="logo">
<div class="logo-icon">🫁</div>
<div class="logo-text">FisioaccessPC</div>
</div>

<div class="actividad-card">
<div class="actividad-nombre"><?= htmlspecialchars($actividad['info_basica']['nombre']) ?></div>
<div class="actividad-detalles">
<p><strong>📊 Tipo:</strong> <?= TIPOS_ESTUDIO[$actividad['info_basica']['tipo_estudio']] ?></p>
<p><strong>📅 Cierre:</strong> <?= date('d/m/Y H:i', $fecha_cierre) ?></p>
</div>
</div>

<?php if (!$actividad_abierta): ?>
<div class="closed-message">
<div class="closed-icon">⏰</div>
<?php if ($ahora < $fecha_inicio): ?>
<h2>Actividad no disponible</h2>
<p style="color: #6b7280; margin-top: 10px;">
Esta actividad comienza el <?= date('d/m/Y H:i', $fecha_inicio) ?>
</p>
<?php else: ?>
<h2>Actividad finalizada</h2>
<p style="color: #6b7280; margin-top: 10px;">
Esta actividad cerró el <?= date('d/m/Y H:i', $fecha_cierre) ?>
</p>
<?php endif; ?>
</div>
<?php else: ?>

<div class="step-indicator">
<div class="step active" id="step-1">1</div>
<div class="step" id="step-2">2</div>
<div class="step" id="step-3">3</div>
</div>

<div id="alert-container"></div>

<!-- Paso 1: Ingresar email -->
<div class="form-section active" id="section-email">
<h2>Ingresa tu email institucional</h2>

<form id="form-email">
<div class="form-group">
<label for="email">Email</label>
<input type="email"
id="email"
placeholder="tu.nombre<?= htmlspecialchars($actividad['accesos']['dominio_email'] ?? '@universidad.cl') ?>"
required
autocomplete="email">
<div class="help-text">
Usa tu email institucional <?= htmlspecialchars($actividad['accesos']['dominio_email'] ?? '') ?>
</div>
</div>

<button type="submit" class="btn" id="btn-enviar-codigo">
Enviar código de verificación
</button>
</form>
</div>

<!-- Paso 2: Verificar código -->
<div class="form-section" id="section-codigo">
<h2>Ingresa el código de verificación</h2>

<div class="alert alert-info">
📧 Hemos enviado un código de 6 dígitos a <strong id="email-display"></strong>.
Revisa tu bandeja de entrada y carpeta de spam.
</div>

<form id="form-codigo">
<div class="form-group">
<label for="codigo">Código de verificación</label>
<input type="text"
id="codigo"
placeholder="123456"
maxlength="6"
pattern="[0-9]{6}"
required
autocomplete="off">
<div class="help-text">
El código expira en 20 minutos
</div>
</div>

<button type="submit" class="btn" id="btn-verificar">
Verificar código
</button>

<button type="button" class="btn btn-secondary" id="btn-reenviar">
Reenviar código
</button>
</form>
</div>

<!-- Paso 3: Redirigiendo al dashboard -->
<div class="form-section" id="section-success">
<div class="success-card">
<div class="success-icon">✅</div>
<h2>¡Acceso verificado!</h2>

<div class="redirect-message">
<div class="loading"></div>
<p><strong>Redirigiendo a tu dashboard...</strong></p>
</div>
</div>
</div>

<?php endif; ?>
</div>

<script>
const API_URL = '../api';
const TOKEN_ACTIVIDAD = '<?= $token_actividad ?>';
let userEmail = null;

// Elementos
const formEmail = document.getElementById('form-email');
const formCodigo = document.getElementById('form-codigo');
const btnEnviarCodigo = document.getElementById('btn-enviar-codigo');
const btnVerificar = document.getElementById('btn-verificar');
const btnReenviar = document.getElementById('btn-reenviar');

// Funciones auxiliares
function goToStep(step) {
    // Actualizar indicadores
    document.querySelectorAll('.step').forEach((el, index) => {
        el.classList.remove('active', 'completed');
        if (index + 1 < step) {
            el.classList.add('completed');
        } else if (index + 1 === step) {
            el.classList.add('active');
        }
    });

    // Mostrar sección
    document.querySelectorAll('.form-section').forEach(el => {
        el.classList.remove('active');
    });
    document.getElementById(`section-${step === 1 ? 'email' : step === 2 ? 'codigo' : 'success'}`).classList.add('active');
}

function showAlert(type, message) {
    const container = document.getElementById('alert-container');
    container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

// Paso 1: Enviar código
formEmail.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    userEmail = email;

    btnEnviarCodigo.disabled = true;
    btnEnviarCodigo.innerHTML = '<span class="loading"></span> Enviando...';

try {
    const response = await fetch(`${API_URL}/acceso_estudiante.php`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            token_actividad: TOKEN_ACTIVIDAD,
            email: email,
            reenviar: false
        })
    });

    const data = await response.json();

    if (data.success) {
        showAlert('success', data.message);
        document.getElementById('email-display').textContent = email;
        goToStep(2);
    } else {
        showAlert('error', data.error);
    }
} catch (error) {
    showAlert('error', 'Error de conexión. Intenta nuevamente.');
} finally {
    btnEnviarCodigo.disabled = false;
    btnEnviarCodigo.textContent = 'Enviar código de verificación';
}
});

// Paso 2: Verificar código y login automático
formCodigo.addEventListener('submit', async (e) => {
    e.preventDefault();

    const codigo = document.getElementById('codigo').value.trim();

    btnVerificar.disabled = true;
    btnVerificar.innerHTML = '<span class="loading"></span> Verificando...';

try {
    const response = await fetch(`${API_URL}/verificar_codigo.php`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: userEmail,
            codigo: codigo
        })
    });

    const data = await response.json();

    if (data.success) {
        showAlert('success', '¡Código verificado! Iniciando sesión...');
        goToStep(3);

        // Redirigir al dashboard después de 1.5 segundos
        setTimeout(() => {
            window.location.href = 'dashboard.php';
        }, 1500);
    } else {
        showAlert('error', data.error);
        btnVerificar.disabled = false;
        btnVerificar.textContent = 'Verificar código';
    }
} catch (error) {
    showAlert('error', 'Error de conexión. Intenta nuevamente.');
    btnVerificar.disabled = false;
    btnVerificar.textContent = 'Verificar código';
}
});

// Reenviar código
btnReenviar.addEventListener('click', async () => {
    btnReenviar.disabled = true;
    btnReenviar.innerHTML = '<span class="loading"></span> Reenviando...';

try {
    const response = await fetch(`${API_URL}/acceso_estudiante.php`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            token_actividad: TOKEN_ACTIVIDAD,
            email: userEmail,
            reenviar: true
        })
    });

    const data = await response.json();

    if (data.success) {
        showAlert('success', 'Código reenviado. Revisa tu email.');
    } else {
        showAlert('error', data.error);
    }
} catch (error) {
    showAlert('error', 'Error de conexión. Intenta nuevamente.');
} finally {
    btnReenviar.disabled = false;
    btnReenviar.textContent = 'Reenviar código';
}
});
</script>
</body>
</html>
