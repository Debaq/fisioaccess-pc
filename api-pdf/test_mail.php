<?php
require_once 'config.php';

echo "<h2>Probando configuración de email</h2>";
echo "<p><strong>Host:</strong> " . SMTP_HOST . "</p>";
echo "<p><strong>Port:</strong> " . SMTP_PORT . "</p>";
echo "<p><strong>From:</strong> " . SMTP_FROM . "</p>";
echo "<hr>";

$resultado = enviarEmail(
    'davil004@gmail.com',  // ← Cambia por tu email
    'Test FisioaccessPC',
    '<h1>¡Funciona!</h1><p>El sistema de correos está configurado correctamente.</p>'
);

if ($resultado) {
    echo "✅ <strong>Email enviado.</strong> Revisa tu bandeja de entrada y spam.";
} else {
    echo "❌ <strong>Error al enviar.</strong> Verifica usuario/contraseña y que el puerto 465 esté abierto.";
}
?>
