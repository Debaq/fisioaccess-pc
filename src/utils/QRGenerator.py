from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QClipboard
import qrcode
from io import BytesIO

class QRGenerator:
    """Generador de códigos QR"""
    
    def __init__(self):
        self.qr_size = 300  # Tamaño del QR en píxeles
        
    def generate_qr_image(self, url):
        """
        Generar imagen QR desde una URL
        
        Args:
            url (str): URL a codificar en el QR
            
        Returns:
            QPixmap: Imagen del código QR
        """
        try:
            # Crear código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Generar imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a QPixmap
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            qimage = QImage()
            qimage.loadFromData(buffer.getvalue())
            
            pixmap = QPixmap.fromImage(qimage)
            
            # Redimensionar si es necesario
            if pixmap.width() > self.qr_size or pixmap.height() > self.qr_size:
                pixmap = pixmap.scaled(
                    self.qr_size, 
                    self.qr_size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
            
            return pixmap
            
        except Exception as e:
            print(f"Error generando QR: {str(e)}")
            return None
    
    def save_qr_to_file(self, url, filepath):
        """
        Guardar código QR en un archivo
        
        Args:
            url (str): URL a codificar
            filepath (str): Ruta donde guardar el archivo
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filepath)
            
            return True
            
        except Exception as e:
            print(f"Error guardando QR: {str(e)}")
            return False


class QRDisplayDialog(QDialog):
    """Diálogo para mostrar código QR y URL"""
    
    def __init__(self, url, qr_pixmap, parent=None):
        super().__init__(parent)
        self.url = url
        self.qr_pixmap = qr_pixmap
        
        self.setWindowTitle("Estudio Guardado")
        self.setModal(True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("¡Estudio guardado exitosamente!")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Código QR
        if self.qr_pixmap:
            qr_label = QLabel()
            qr_label.setPixmap(self.qr_pixmap)
            qr_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(qr_label)
        
        # URL
        url_label = QLabel("Accede a tu estudio en:")
        url_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(url_label)
        
        self.url_text = QLabel(f'<a href="{self.url}">{self.url}</a>')
        self.url_text.setOpenExternalLinks(True)
        self.url_text.setAlignment(Qt.AlignCenter)
        self.url_text.setWordWrap(True)
        self.url_text.setStyleSheet("font-size: 10pt; color: blue;")
        layout.addWidget(self.url_text)
        
        # Instrucción
        instruction_label = QLabel("Escanea el código QR o haz clic en el enlace")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(instruction_label)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("Copiar URL")
        self.copy_button.clicked.connect(self.copy_url)
        button_layout.addWidget(self.copy_button)
        
        self.close_button = QPushButton("Cerrar")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def copy_url(self):
        """Copiar URL al portapapeles"""
        clipboard = QClipboard()
        clipboard.setText(self.url)
        
        # Cambiar temporalmente el texto del botón
        self.copy_button.setText("¡Copiado!")
        self.copy_button.setEnabled(False)
        
        # Restaurar después de 2 segundos
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.copy_button.setText("Copiar URL"))
        QTimer.singleShot(2000, lambda: self.copy_button.setEnabled(True))
