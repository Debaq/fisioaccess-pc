<?php
/**
 * estudiante/acceso.php - Página de acceso para estudiantes
 * URL: /estudiante/acceso.php?token=ABC123
 */

require_once '../config.php';

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
            color: #7c3aed;
            font-size: 24px;
            font-weight: 700;
        }
        
        .actividad-info {
            background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            border: 2px solid #7c3aed;
        }
        
        .actividad-nombre {
            font-size: 20px;
            font-weight: 600;
            color: #5b21b6;
            margin-bottom: 10px;
        }
        
        .actividad-detalles {
            font-size: 14px;
            color: #6b7280;
        }
        
        .actividad-detalles p {
            margin: 5px 0;
        }
        
        .step-indicator {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            gap: 10px;
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
            color: #9ca3af;
            transition: all 0.3s;
        }
        
        .step.active {
            background: #7c3aed;
            color: white;
            transform: scale(1.1);
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
        
        h2 {
            color: #1f2937;
            font-size: 22px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #4b5563;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #7c3aed;
            box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            background: #7c3aed;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #6d28d9;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(124, 58, 237, 0.3);
        }
        
        .btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: #6b7280;
            margin-top: 10px;
        }
        
        .btn-secondary:hover {
            background: #4b5563;
        }
        
        .alert {
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .alert-error {
            background: #fee2e2;
            border: 1px solid #fecaca;
            color: #991b1b;
        }
        
        .alert-success {
            background: #d1fae5;
            border: 1px solid #a7f3d0;
            color: #065f46;
        }
        
        .alert-info {
            background: #dbeafe;
            border: 1px solid #bfdbfe;
            color: #1e40af;
        }
        
        .alert-warning {
            background: #fef3c7;
            border: 1px solid #fde68a;
            color: #92400e;
        }
        
        .help-text {
            font-size: 13px;
            color: #6b7280;
            margin-top: 5px;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .success-card {
            text-align: center;
            padding: 30px 20px;
        }
        
        .success-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        
        .token-display {
            background: #f9fafb;
            border: 2px dashed #7c3aed;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }
        
        .token-value {
            font-size: 28px;
            font-weight: 700;
            color: #7c3aed;
            letter-spacing: 4px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        
        .copy-btn {
            background: #10b981;
            margin-top: 10px;
        }
        
        .copy-btn:hover {
            background: #059669;
        }
        
        .closed-message {
            text-align: center;
            padding: 40px 20px;
        }
        
        .closed-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <div class="logo-icon">🫁</div>
            <div class="logo-text">FisioaccessPC</div>
        </div>
        
        <div class="actividad-info">
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
            
            <!-- Paso 3: Éxito y token -->
            <div class="form-section" id="section-success">
                <div class="success-card">
                    <div class="success-icon">✅</div>
                    <h2>¡Acceso verificado!</h2>
                    
                    <div class="alert alert-success" style="text-align: left; margin-top: 20px;">
                        <strong>✓ Ya puedes realizar tus estudios</strong><br>
                        Tu sesión está activa en este dispositivo.
                    </div>
                    
                    <h3 style="margin-top: 30px; color: #4b5563;">Para usar la aplicación de escritorio:</h3>
                    
                    <button type="button" class="btn" id="btn-generar-token" style="margin-top: 15px;">
                        🔑 Generar token de acceso
                    </button>
                    
                    <div id="token-container" style="display: none;">
                        <div class="token-display">
                            <div style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">
                                Tu token de acceso:
                            </div>
                            <div class="token-value" id="token-value"></div>
                            <div style="font-size: 13px; color: #6b7280; margin-top: 10px;">
                                Válido por 4 horas
                            </div>
                        </div>
                        
                        <button type="button" class="btn copy-btn" id="btn-copiar-token">
                            📋 Copiar token
                        </button>
                        
                        <div class="help-text" style="margin-top: 15px; text-align: left;">
                            <strong>Instrucciones:</strong><br>
                            1. Abre la aplicación de escritorio<br>
                            2. Ingresa este token cuando te lo solicite<br>
                            3. Ya podrás realizar estudios
                        </div>
                    </div>
                </div>
            </div>
            
        <?php endif; ?>
    </div>
    
    <script>
        const API_URL = '../api';
        const TOKEN_ACTIVIDAD = '<?= $token_actividad ?>';
        let sessionId = null;
        let userEmail = null;
        
        // Elementos
        const formEmail = document.getElementById('form-email');
        const formCodigo = document.getElementById('form-codigo');
        const btnEnviarCodigo = document.getElementById('btn-enviar-codigo');
        const btnVerificar = document.getElementById('btn-verificar');
        const btnReenviar = document.getElementById('btn-reenviar');
        const btnGenerarToken = document.getElementById('btn-generar-token');
        const btnCopiarToken = document.getElementById('btn-copiar-token');
        
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
        
        // Paso 2: Verificar código
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
                    sessionId = data.data.session_id;
                    showAlert('success', '¡Código verificado correctamente!');
                    setTimeout(() => goToStep(3), 1000);
                } else {
                    showAlert('error', data.error);
                }
            } catch (error) {
                showAlert('error', 'Error de conexión. Intenta nuevamente.');
            } finally {
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
        
        // Generar token para app
        btnGenerarToken.addEventListener('click', async () => {
            btnGenerarToken.disabled = true;
            btnGenerarToken.innerHTML = '<span class="loading"></span> Generando...';
            
            try {
                const response = await fetch(`${API_URL}/tokens_app.php?action=generar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('token-value').textContent = data.data.token;
                    document.getElementById('token-container').style.display = 'block';
                    btnGenerarToken.style.display = 'none';
                } else {
                    showAlert('error', data.error);
                    btnGenerarToken.disabled = false;
                    btnGenerarToken.textContent = '🔑 Generar token de acceso';
                }
            } catch (error) {
                showAlert('error', 'Error de conexión. Intenta nuevamente.');
                btnGenerarToken.disabled = false;
                btnGenerarToken.textContent = '🔑 Generar token de acceso';
            }
        });
        
        // Copiar token
        btnCopiarToken.addEventListener('click', () => {
            const token = document.getElementById('token-value').textContent;
            navigator.clipboard.writeText(token).then(() => {
                btnCopiarToken.textContent = '✓ Copiado';
                btnCopiarToken.style.background = '#059669';
                setTimeout(() => {
                    btnCopiarToken.textContent = '📋 Copiar token';
                    btnCopiarToken.style.background = '#10b981';
                }, 2000);
            });
        });
        
        // Funciones auxiliares
        function goToStep(step) {
            // Ocultar todas las secciones
            document.querySelectorAll('.form-section').forEach(s => s.classList.remove('active'));
            
            // Actualizar indicadores
            document.querySelectorAll('.step').forEach((s, i) => {
                s.classList.remove('active', 'completed');
                if (i + 1 < step) s.classList.add('completed');
                if (i + 1 === step) s.classList.add('active');
            });
            
            // Mostrar sección correspondiente
            if (step === 1) document.getElementById('section-email').classList.add('active');
            if (step === 2) document.getElementById('section-codigo').classList.add('active');
            if (step === 3) document.getElementById('section-success').classList.add('active');
        }
        
        function showAlert(type, message) {
            const container = document.getElementById('alert-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            
            container.innerHTML = '';
            container.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
    </script>
</body>
</html>