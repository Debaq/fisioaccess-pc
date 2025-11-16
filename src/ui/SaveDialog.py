from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QTextEdit, QPushButton,
                               QFormLayout, QDateEdit, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate

class SaveDialog(QDialog):
    """Diálogo para solicitar comentarios antes de guardar un estudio"""

    def __init__(self, parent=None, patient_data=None, activity_name=None):
        super().__init__(parent)
        self.setWindowTitle("Guardar Estudio")
        self.setModal(True)
        self.setMinimumWidth(450)

        # Datos del formulario
        self.patient_data = patient_data
        self.activity_name = activity_name

        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Título
        title_label = QLabel("📝 Guardar Estudio")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #7c3aed;")
        layout.addWidget(title_label)

        # Información de la actividad (si está disponible)
        if self.activity_name:
            activity_label = QLabel(f"Actividad: {self.activity_name}")
            activity_label.setStyleSheet(
                "background-color: #f0f9ff; "
                "border: 1px solid #7c3aed; "
                "border-radius: 6px; "
                "padding: 10px; "
                "font-weight: bold;"
            )
            layout.addWidget(activity_label)
        
        # Instrucciones
        instructions_label = QLabel(
            "El estudio se guardará y subirá automáticamente a la plataforma.\n"
            "Puedes agregar comentarios opcionales sobre este estudio:"
        )
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(instructions_label)

        # Campo de comentarios (opcional)
        comments_label = QLabel("Comentarios (opcional):")
        comments_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(comments_label)

        self.comments_edit = QTextEdit()
        self.comments_edit.setPlaceholderText(
            "Puedes agregar observaciones sobre este estudio:\n"
            "• Condiciones del sujeto\n"
            "• Observaciones durante la medición\n"
            "• Notas relevantes para el análisis"
        )
        self.comments_edit.setMinimumHeight(120)
        self.comments_edit.setStyleSheet(
            "QTextEdit {"
            "    border: 2px solid #e5e7eb; "
            "    border-radius: 8px; "
            "    padding: 10px; "
            "    font-size: 10pt;"
            "}"
            "QTextEdit:focus {"
            "    border: 2px solid #7c3aed;"
            "}"
        )
        layout.addWidget(self.comments_edit)

        # Espaciador
        layout.addStretch()

        # Información adicional
        info_label = QLabel(
            "ℹ️ Tu identidad ya está registrada con el token de autenticación"
        )
        info_label.setStyleSheet(
            "background-color: #f9fafb; "
            "border: 1px solid #d1d5db; "
            "border-radius: 6px; "
            "padding: 8px; "
            "color: #6b7280; "
            "font-size: 9pt;"
        )
        layout.addWidget(info_label)

        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.cancel_button = QPushButton("✕ Cancelar")
        self.cancel_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #e5e7eb; "
            "    color: #374151; "
            "    border: none; "
            "    padding: 10px 20px; "
            "    border-radius: 6px; "
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #d1d5db;"
            "}"
        )
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("✓ Guardar y Subir")
        self.save_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #7c3aed; "
            "    color: white; "
            "    border: none; "
            "    padding: 10px 20px; "
            "    border-radius: 6px; "
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #6d28d9;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #5b21b6;"
            "}"
        )
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.accept_data)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
    
    def accept_data(self):
        """Aceptar los datos ingresados (solo comentarios opcionales)"""
        # Construir diccionario de datos simplificado
        self.patient_data = {
            'comments': self.comments_edit.toPlainText().strip()
        }

        self.accept()
        
    def get_data(self):
        """Obtener los datos ingresados"""
        return self.patient_data
