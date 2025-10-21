from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QTextEdit, QPushButton,
                               QFormLayout, QDateEdit, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate

class SaveDialog(QDialog):
    """Diálogo para solicitar información antes de guardar un estudio"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guardar Estudio")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        # Datos del formulario
        self.patient_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Datos del Paciente")
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Nombre
        self.nombre_edit = QLineEdit()
        self.nombre_edit.setPlaceholderText("Nombre completo del paciente")
        form_layout.addRow("Nombre:*", self.nombre_edit)
        
        # RUT
        self.rut_edit = QLineEdit()
        self.rut_edit.setPlaceholderText("12.345.678-9")
        form_layout.addRow("RUT:*", self.rut_edit)
        
        # Sexo
        self.sexo_combo = QComboBox()
        self.sexo_combo.addItems([
            "Masculino",
            "Femenino",
            "Otro"
        ])
        form_layout.addRow("Sexo:*", self.sexo_combo)
        
        # Fecha de Nacimiento
        self.fecha_nacimiento = QDateEdit()
        self.fecha_nacimiento.setCalendarPopup(True)
        self.fecha_nacimiento.setDate(QDate.currentDate().addYears(-30))
        self.fecha_nacimiento.setDisplayFormat("dd/MM/yyyy")
        self.fecha_nacimiento.setMaximumDate(QDate.currentDate())
        form_layout.addRow("Fecha Nacimiento:*", self.fecha_nacimiento)
        
        # Edad (se calcula automáticamente)
        self.edad_spin = QSpinBox()
        self.edad_spin.setRange(0, 150)
        self.edad_spin.setValue(30)
        self.edad_spin.setSuffix(" años")
        self.edad_spin.setReadOnly(True)
        self.edad_spin.setEnabled(False)
        form_layout.addRow("Edad:", self.edad_spin)
        
        # Conectar cambio de fecha para actualizar edad
        self.fecha_nacimiento.dateChanged.connect(self.calcular_edad)
        
        # Etnia
        self.etnia_combo = QComboBox()
        self.etnia_combo.addItems([
            "Mestizo",
            "Mapuche",
            "Aymara",
            "Rapa Nui",
            "Diaguita",
            "Quechua",
            "Caucásico",
            "Otro"
        ])
        form_layout.addRow("Etnia:", self.etnia_combo)
        
        # Estatura
        self.estatura_spin = QSpinBox()
        self.estatura_spin.setRange(50, 250)
        self.estatura_spin.setValue(170)
        self.estatura_spin.setSuffix(" cm")
        form_layout.addRow("Estatura:*", self.estatura_spin)
        
        # Peso
        self.peso_spin = QDoubleSpinBox()
        self.peso_spin.setRange(10.0, 300.0)
        self.peso_spin.setValue(70.0)
        self.peso_spin.setSuffix(" kg")
        self.peso_spin.setDecimals(1)
        form_layout.addRow("Peso:*", self.peso_spin)
        
        # Campo Comments (opcional)
        self.comments_edit = QTextEdit()
        self.comments_edit.setPlaceholderText(
            "Observaciones adicionales (opcional):\n"
            "- Condiciones de medición\n"
            "- Medicación actual\n"
            "- Observaciones relevantes"
        )
        self.comments_edit.setMaximumHeight(60)
        form_layout.addRow("Comentarios:", self.comments_edit)
        
        layout.addLayout(form_layout)
        
        # Separador
        separator = QLabel()
        separator.setStyleSheet("border-top: 1px solid #ccc; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Sección de análisis
        analysis_label = QLabel("Análisis Clínico")
        analysis_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout.addWidget(analysis_label)
        
        analysis_form = QFormLayout()
        
        # Interpretación
        self.interpretacion_edit = QTextEdit()
        self.interpretacion_edit.setPlaceholderText(
            "Interpretación de los resultados espirométricos:\n"
            "- Patrones observados\n"
            "- Valores comparados con predichos\n"
            "- Hallazgos relevantes"
        )
        self.interpretacion_edit.setMaximumHeight(80)
        analysis_form.addRow("Interpretación:*", self.interpretacion_edit)
        
        # Conclusión
        self.conclusion_edit = QTextEdit()
        self.conclusion_edit.setPlaceholderText(
            "Conclusión diagnóstica:\n"
            "- Normal / Obstructivo / Restrictivo / Mixto\n"
            "- Severidad\n"
            "- Recomendaciones"
        )
        self.conclusion_edit.setMaximumHeight(80)
        analysis_form.addRow("Conclusión:*", self.conclusion_edit)
        
        layout.addLayout(analysis_form)
        
        # Nota de campos obligatorios
        required_label = QLabel("* Campos obligatorios")
        required_label.setStyleSheet("color: red; font-style: italic; font-size: 9pt;")
        layout.addWidget(required_label)
        
        # Información del dispositivo
        device_label = QLabel("Dispositivo: fisioaccess_espiro")
        device_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(device_label)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.accept_data)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Calcular edad inicial
        self.calcular_edad()
    
    def calcular_edad(self):
        """Calcular edad a partir de fecha de nacimiento"""
        fecha_nac = self.fecha_nacimiento.date()
        fecha_actual = QDate.currentDate()
        
        edad = fecha_nac.daysTo(fecha_actual) // 365
        self.edad_spin.setValue(edad)
        
    def accept_data(self):
        """Validar y aceptar los datos ingresados"""
        # Resetear estilos
        self.nombre_edit.setStyleSheet("")
        self.rut_edit.setStyleSheet("")
        self.estatura_spin.setStyleSheet("")
        self.peso_spin.setStyleSheet("")
        self.interpretacion_edit.setStyleSheet("")
        self.conclusion_edit.setStyleSheet("")
        
        # Validar campos obligatorios
        nombre = self.nombre_edit.text().strip()
        rut = self.rut_edit.text().strip()
        interpretacion = self.interpretacion_edit.toPlainText().strip()
        conclusion = self.conclusion_edit.toPlainText().strip()
        
        errors = []
        
        if not nombre:
            self.nombre_edit.setStyleSheet("border: 2px solid red;")
            errors.append("Nombre")
        
        if not rut:
            self.rut_edit.setStyleSheet("border: 2px solid red;")
            errors.append("RUT")
        
        if not interpretacion:
            self.interpretacion_edit.setStyleSheet("border: 2px solid red;")
            errors.append("Interpretación")
        
        if not conclusion:
            self.conclusion_edit.setStyleSheet("border: 2px solid red;")
            errors.append("Conclusión")
        
        if errors:
            if not nombre:
                self.nombre_edit.setFocus()
            elif not rut:
                self.rut_edit.setFocus()
            elif not interpretacion:
                self.interpretacion_edit.setFocus()
            else:
                self.conclusion_edit.setFocus()
            return
        
        # Construir diccionario de datos
        self.patient_data = {
            'nombre': nombre,
            'rut': rut,
            'sexo': self.sexo_combo.currentText(),
            'fecha_nacimiento': self.fecha_nacimiento.date().toString("dd/MM/yyyy"),
            'edad': self.edad_spin.value(),
            'etnia': self.etnia_combo.currentText(),
            'estatura_cm': self.estatura_spin.value(),
            'peso_kg': self.peso_spin.value(),
            'comentarios': self.comments_edit.toPlainText().strip(),
            'interpretacion': interpretacion,
            'conclusion': conclusion,
            'dispositivo': 'fisioaccess_espiro'
        }
        
        self.accept()
        
    def get_data(self):
        """Obtener los datos ingresados"""
        return self.patient_data
