<?php
/**
 * profesor/login.php - Login de profesor
 */

require_once '../config.php';

session_start();

// Si ya está autenticado, redirigir al dashboard
if (verificarRol('profesor')) {
    header('Location: dashboard.php');
    exit;
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Validar token CSRF
    $csrf_token = $_POST['csrf_token'] ?? '';
    if (!validarTokenCSRF($csrf_token)) {
        $error = 'Token de seguridad inválido. Recarga la página e intenta nuevamente.';
        registrarEventoSeguridad('CSRF token inválido en login profesor', ['ip' => obtenerIP()]);
    } else {
        $rut = trim($_POST['rut'] ?? '');
        $password = $_POST['password'] ?? '';

        // Rate limiting por IP
        $ip = obtenerIP();
        if (!verificarRateLimit('login', $ip)) {
            $error = 'Demasiados intentos de login. Intenta nuevamente en 1 hora.';
            registrarEventoSeguridad('Rate limit login profesor excedido', ['ip' => $ip, 'rut' => $rut]);
        } elseif (empty($rut) || empty($password)) {
            $error = 'Por favor complete todos los campos';
        } else {
        $profesores = cargarJSON(PROFESORES_FILE);
        
        if (isset($profesores[$rut])) {
            $profesor = $profesores[$rut];
            
            if (!$profesor['activo']) {
                $error = 'Usuario desactivado. Contacte al administrador';
                registrarEventoSeguridad('Login profesor - cuenta desactivada', ['rut' => $rut, 'ip' => $ip]);
            } elseif (password_verify($password, $profesor['password_hash'])) {
                // Login exitoso - regenerar sesión para prevenir session fixation
                session_regenerate_id(true);
                $_SESSION['authenticated'] = true;
                $_SESSION['rol'] = 'profesor';
                $_SESSION['rut'] = $rut;
                $_SESSION['nombre'] = $profesor['nombre'];
                $_SESSION['email'] = $profesor['email'];
                $_SESSION['login_time'] = time();

                // Actualizar último login
                $profesores[$rut]['last_login'] = formatearFecha();
                guardarJSON(PROFESORES_FILE, $profesores);

                // Registrar login exitoso y resetear contador
                registrarIntento('login', $ip, true);
                registrarEventoSeguridad('Login profesor exitoso', ['rut' => $rut, 'ip' => $ip]);

                header('Location: dashboard.php');
                exit;
            } else {
                $error = 'Contraseña incorrecta';
                registrarIntento('login', $ip, false);
                registrarEventoSeguridad('Login profesor fallido - contraseña incorrecta', ['rut' => $rut, 'ip' => $ip]);
            }
        } else {
            $error = 'RUT no registrado';
            registrarIntento('login', $ip, false);
            registrarEventoSeguridad('Login profesor fallido - RUT no registrado', ['rut' => $rut, 'ip' => $ip]);
        }
        }
    }
}

// Generar token CSRF para el formulario
$csrf_token = generarTokenCSRF();
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Profesor - FisioaccessPC</title>
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
        
        .login-container {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 40px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .icon {
            text-align: center;
            font-size: 64px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.8);
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .error {
            background: rgba(239, 68, 68, 0.3);
            border: 1px solid rgba(239, 68, 68, 0.5);
            color: white;
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 14px;
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
        
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        
        .back-link a {
            color: white;
            text-decoration: none;
            font-size: 14px;
            opacity: 0.8;
        }
        
        .back-link a:hover {
            opacity: 1;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="icon">👨‍🏫</div>
        <h1>Profesor</h1>
        <p class="subtitle">Ingrese sus credenciales</p>
        
        <?php if ($error): ?>
            <div class="error">❌ <?= htmlspecialchars($error) ?></div>
        <?php endif; ?>
        
        <form method="POST">
            <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($csrf_token) ?>">

            <div class="form-group">
                <label>RUT</label>
                <input type="text" name="rut" placeholder="12345678-9" required autofocus>
            </div>

            <div class="form-group">
                <label>Contraseña</label>
                <input type="password" name="password" required>
            </div>

            <button type="submit" class="btn">Ingresar</button>
        </form>
        
        <div class="back-link">
            <a href="../index.html">← Volver al inicio</a>
        </div>
    </div>
</body>
</html>