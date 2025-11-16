from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import requests
import json


class LoginDialog(QDialog):
    """Diálogo de autenticación con token de estudiante"""

    # Señal emitida cuando el login es exitoso
    login_successful = Signal(dict)  # Emite los datos del token validado

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Autenticación - FisioaccessPC")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # Datos de autenticación
        self.token_data = None
        self.token = None

        self.setup_ui()

    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título principal
        title_label = QLabel("🫁 FisioaccessPC")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Sistema de Adquisición de Datos Fisiológicos")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 11pt;")
        layout.addWidget(subtitle_label)

        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Instrucciones
        instructions_label = QLabel(
            "Para usar este software, necesitas un token de actividad.\n\n"
            "Pasos para obtener tu token:\n"
            "1. Accede a la plataforma web con el link de tu actividad\n"
            "2. Ingresa tu email institucional\n"
            "3. Verifica tu código de acceso\n"
            "4. En el dashboard, haz clic en 'Generar Token PC'\n"
            "5. Copia el token de 6 caracteres e ingrésalo aquí"
        )
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet(
            "background-color: #f0f9ff; "
            "border: 1px solid #7c3aed; "
            "border-radius: 8px; "
            "padding: 15px; "
            "font-size: 10pt; "
            "line-height: 1.5;"
        )
        layout.addWidget(instructions_label)

        # Campo de token
        token_layout = QVBoxLayout()
        token_layout.setSpacing(8)

        token_label = QLabel("Token de Actividad (6 caracteres):")
        token_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        token_layout.addWidget(token_label)

        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholderText("Ejemplo: A3B7X9")
        self.token_edit.setMaxLength(6)
        self.token_edit.setStyleSheet(
            "QLineEdit {"
            "    font-size: 16pt; "
            "    font-weight: bold; "
            "    letter-spacing: 4px; "
            "    padding: 12px; "
            "    border: 2px solid #7c3aed; "
            "    border-radius: 8px; "
            "    text-transform: uppercase;"
            "}"
            "QLineEdit:focus {"
            "    border: 2px solid #5b21b6; "
            "    background-color: #faf5ff;"
            "}"
        )
        self.token_edit.setAlignment(Qt.AlignCenter)

        # Convertir a mayúsculas automáticamente
        self.token_edit.textChanged.connect(
            lambda text: self.token_edit.setText(text.upper())
        )

        # Enter para validar
        self.token_edit.returnPressed.connect(self.validate_token)

        token_layout.addWidget(self.token_edit)
        layout.addLayout(token_layout)

        # Mensaje de estado
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Espaciador
        layout.addStretch()

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.validate_button = QPushButton("✓ Validar Token")
        self.validate_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #7c3aed; "
            "    color: white; "
            "    border: none; "
            "    padding: 12px 24px; "
            "    border-radius: 8px; "
            "    font-size: 11pt; "
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #6d28d9;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #5b21b6;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #d1d5db; "
            "    color: #9ca3af;"
            "}"
        )
        self.validate_button.clicked.connect(self.validate_token)
        buttons_layout.addWidget(self.validate_button)

        cancel_button = QPushButton("✕ Salir")
        cancel_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #ef4444; "
            "    color: white; "
            "    border: none; "
            "    padding: 12px 24px; "
            "    border-radius: 8px; "
            "    font-size: 11pt; "
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #dc2626;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #b91c1c;"
            "}"
        )
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        # Info adicional
        help_label = QLabel(
            "¿Problemas? Verifica que tu token esté activo y no haya expirado.\n"
            "Contacta a tu profesor si necesitas ayuda."
        )
        help_label.setAlignment(Qt.AlignCenter)
        help_label.setStyleSheet("color: #9ca3af; font-size: 9pt; margin-top: 10px;")
        layout.addWidget(help_label)

    def validate_token(self):
        """Validar el token contra la API"""
        token = self.token_edit.text().strip().upper()

        if not token:
            self.show_error("Por favor ingresa un token")
            return

        if len(token) != 6:
            self.show_error("El token debe tener exactamente 6 caracteres")
            return

        # Deshabilitar botón mientras valida
        self.validate_button.setEnabled(False)
        self.token_edit.setEnabled(False)
        self.show_info("🔄 Validando token...")

        try:
            # Llamar a la API para validar el token
            # Usamos el endpoint de entregas con método HEAD o GET para validar
            # sin subir archivos
            api_url = "https://tmeduca.org/fisioaccess/api/validar_token.php"

            response = requests.post(
                api_url,
                json={"token": token},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    # Token válido
                    self.token = token
                    self.token_data = data.get('data', {})

                    actividad_nombre = self.token_data.get('actividad_nombre', 'Desconocida')
                    estudiante_nombre = self.token_data.get('estudiante_nombre', 'Desconocido')

                    self.show_success(
                        f"✓ Autenticación exitosa\n\n"
                        f"Estudiante: {estudiante_nombre}\n"
                        f"Actividad: {actividad_nombre}"
                    )

                    # Emitir señal de éxito
                    self.login_successful.emit({
                        'token': self.token,
                        'token_data': self.token_data
                    })

                    # Cerrar el diálogo después de 1 segundo
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(1500, self.accept)
                else:
                    self.show_error(data.get('error', 'Token inválido'))
                    self.reset_form()
            else:
                self.show_error(f"Error del servidor ({response.status_code})")
                self.reset_form()

        except requests.exceptions.Timeout:
            self.show_error("Tiempo de espera agotado. Verifica tu conexión a internet.")
            self.reset_form()
        except requests.exceptions.ConnectionError:
            self.show_error("No se puede conectar al servidor. Verifica tu conexión a internet.")
            self.reset_form()
        except Exception as e:
            self.show_error(f"Error inesperado: {str(e)}")
            self.reset_form()

    def reset_form(self):
        """Resetear el formulario después de un error"""
        self.validate_button.setEnabled(True)
        self.token_edit.setEnabled(True)
        self.token_edit.setFocus()
        self.token_edit.selectAll()

    def show_error(self, message):
        """Mostrar mensaje de error"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            "color: #dc2626; "
            "background-color: #fef2f2; "
            "border: 1px solid #fca5a5; "
            "border-radius: 6px; "
            "padding: 10px; "
            "font-weight: bold;"
        )

    def show_info(self, message):
        """Mostrar mensaje informativo"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            "color: #2563eb; "
            "background-color: #eff6ff; "
            "border: 1px solid #93c5fd; "
            "border-radius: 6px; "
            "padding: 10px; "
            "font-weight: bold;"
        )

    def show_success(self, message):
        """Mostrar mensaje de éxito"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            "color: #16a34a; "
            "background-color: #f0fdf4; "
            "border: 1px solid #86efac; "
            "border-radius: 6px; "
            "padding: 10px; "
            "font-weight: bold;"
        )

    def get_token(self):
        """Obtener el token validado"""
        return self.token

    def get_token_data(self):
        """Obtener los datos del token"""
        return self.token_data
