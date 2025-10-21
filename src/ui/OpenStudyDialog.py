from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import os
from datetime import datetime
import json
import tempfile


class OpenStudyDialog(QDialog):
    """Diálogo para abrir estudios offline y online"""
    
    # Señal emitida cuando se selecciona un archivo para abrir
    study_selected = Signal(str)  # Emite la ruta del archivo local
    
    def __init__(self, network_handler, file_handler, parent=None):
        super().__init__(parent)
        self.network_handler = network_handler
        self.file_handler = file_handler
        self.has_internet = False
        self.selected_file = None
        
        self.setWindowTitle("Abrir Estudio de Espirometría")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Almacenar información de estudios
        self.studies_info = []  # Lista de {type, path/url, data}
        
        self.setup_ui()
        self.load_studies()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Seleccione un estudio para abrir")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Estado de conexión
        self.status_label = QLabel("Verificando conexión...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        layout.addWidget(self.status_label)
        
        # Lista de estudios
        self.studies_list = QListWidget()
        self.studies_list.setFont(QFont("Monospace", 9))
        self.studies_list.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.studies_list)
        
        # Leyenda
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        
        offline_legend = QLabel("🏠 Offline (local)")
        offline_legend.setStyleSheet("color: #2E7D32; font-size: 10pt;")
        legend_layout.addWidget(offline_legend)
        
        legend_layout.addSpacing(20)
        
        online_legend = QLabel("🌐 Online (servidor)")
        online_legend.setStyleSheet("color: #1565C0; font-size: 10pt;")
        legend_layout.addWidget(online_legend)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Actualizar")
        self.refresh_button.clicked.connect(self.load_studies)
        button_layout.addWidget(self.refresh_button)
        
        self.open_button = QPushButton("Abrir")
        self.open_button.setDefault(True)
        self.open_button.clicked.connect(self.accept_selection)
        self.open_button.setEnabled(False)
        button_layout.addWidget(self.open_button)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Conectar señal de selección
        self.studies_list.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_studies(self):
        """Cargar estudios offline y online"""
        self.studies_list.clear()
        self.studies_info = []
        
        # Verificar conectividad
        self.status_label.setText("Verificando conexión...")
        self.status_label.setStyleSheet("padding: 5px; background-color: #FFF9C4; border-radius: 3px;")
        self.refresh_button.setEnabled(False)
        
        self.has_internet = self.network_handler.check_connectivity()
        
        # Actualizar label de estado
        if self.has_internet:
            self.status_label.setText("✅ Conectado al servidor")
            self.status_label.setStyleSheet("padding: 5px; background-color: #C8E6C9; border-radius: 3px;")
        else:
            self.status_label.setText("⚠️ Sin conexión - Solo estudios offline disponibles")
            self.status_label.setStyleSheet("padding: 5px; background-color: #FFCCBC; border-radius: 3px;")
        
        # Cargar estudios offline
        self.load_offline_studies()
        
        # Cargar estudios online si hay conexión
        if self.has_internet:
            self.load_online_studies()
        
        self.refresh_button.setEnabled(True)
    
    def load_offline_studies(self):
        """Cargar estudios de la carpeta offline"""
        offline_folder = self.file_handler.get_offline_folder()
        
        if not os.path.exists(offline_folder):
            return
        
        # Buscar archivos JSON en la carpeta
        for filename in sorted(os.listdir(offline_folder), reverse=True):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(offline_folder, filename)
            
            try:
                # Leer metadata del archivo
                with open(filepath, 'r') as f:
                    study_data = json.load(f)
                
                # Extraer información
                patient = study_data.get('patient', {})
                nombre = patient.get('nombre', 'Sin nombre')
                rut = patient.get('rut', 'Sin RUT')
                
                # Obtener fecha del timestamp o del nombre del archivo
                timestamp_str = study_data.get('timestamp', '')
                if timestamp_str:
                    try:
                        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        fecha = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        fecha = filename.split('_')[0] if '_' in filename else 'Sin fecha'
                else:
                    # Extraer fecha del nombre del archivo: YYYYMMDD_HHMMSS_...
                    fecha = filename.split('_')[0] if '_' in filename else 'Sin fecha'
                    try:
                        fecha = datetime.strptime(fecha, '%Y%m%d').strftime('%d/%m/%Y')
                    except:
                        fecha = 'Sin fecha'
                
                # Crear item
                display_text = f"🏠 {nombre} ({rut}) - {fecha}"
                item = QListWidgetItem(display_text)
                item.setForeground(Qt.darkGreen)
                
                # Guardar información
                self.studies_info.append({
                    'type': 'offline',
                    'path': filepath,
                    'data': study_data
                })
                
                # Asociar índice al item
                item.setData(Qt.UserRole, len(self.studies_info) - 1)
                
                self.studies_list.addItem(item)
                
            except Exception as e:
                print(f"Error al cargar estudio offline {filename}: {str(e)}")
                continue
    
    def load_online_studies(self):
        """Cargar estudios del servidor"""
        studies = self.network_handler.get_online_studies()
        
        if not studies:
            return
        
        for study_meta in studies:
            try:
                # Extraer información
                owner = study_meta.get('owner', 'Sin nombre')
                tipo = study_meta.get('type', '')
                
                # Obtener fecha
                uploaded = study_meta.get('uploaded', '')
                if uploaded:
                    try:
                        dt = datetime.fromisoformat(uploaded.replace('Z', '+00:00'))
                        fecha = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        fecha = 'Sin fecha'
                else:
                    fecha = 'Sin fecha'
                
                # URL del archivo RAW (si existe)
                raw_info = study_meta.get('raw')
                if raw_info and raw_info.get('url'):
                    raw_url = raw_info['url']
                else:
                    # Si no hay RAW, usar el PDF (pero idealmente necesitamos el RAW)
                    continue
                
                # Crear item
                display_text = f"🌐 {owner} ({tipo}) - {fecha}"
                item = QListWidgetItem(display_text)
                item.setForeground(Qt.darkBlue)
                
                # Guardar información
                self.studies_info.append({
                    'type': 'online',
                    'url': raw_url,
                    'data': study_meta
                })
                
                # Asociar índice al item
                item.setData(Qt.UserRole, len(self.studies_info) - 1)
                
                self.studies_list.addItem(item)
                
            except Exception as e:
                print(f"Error al procesar estudio online: {str(e)}")
                continue
    
    def on_selection_changed(self):
        """Manejar cambio de selección"""
        has_selection = len(self.studies_list.selectedItems()) > 0
        self.open_button.setEnabled(has_selection)
    
    def accept_selection(self):
        """Aceptar la selección y preparar el archivo"""
        selected_items = self.studies_list.selectedItems()
        
        if not selected_items:
            return
        
        item = selected_items[0]
        index = item.data(Qt.UserRole)
        
        if index is None or index >= len(self.studies_info):
            return
        
        study_info = self.studies_info[index]
        
        if study_info['type'] == 'offline':
            # Archivo local, devolver ruta directamente
            self.selected_file = study_info['path']
            self.accept()
            
        elif study_info['type'] == 'online':
            # Archivo online, descargar primero
            self.download_and_open_online_study(study_info)
    
    def download_and_open_online_study(self, study_info):
        """Descargar estudio online y preparar para abrir"""
        try:
            # Mostrar mensaje
            self.status_label.setText("⏳ Descargando estudio...")
            self.status_label.setStyleSheet("padding: 5px; background-color: #FFF9C4; border-radius: 3px;")
            self.refresh_button.setEnabled(False)
            self.open_button.setEnabled(False)
            
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()
            
            # Descargar
            url = study_info['url']
            success = self.network_handler.download_study(url, temp_path)
            
            if success:
                self.selected_file = temp_path
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error de Descarga",
                    "No se pudo descargar el estudio del servidor.\n"
                    "Verifique su conexión e intente nuevamente."
                )
                self.status_label.setText("❌ Error al descargar")
                self.status_label.setStyleSheet("padding: 5px; background-color: #FFCCBC; border-radius: 3px;")
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al descargar estudio:\n{str(e)}"
            )
        finally:
            self.refresh_button.setEnabled(True)
            self.open_button.setEnabled(True)
    
    def get_selected_file(self):
        """Obtener la ruta del archivo seleccionado"""
        return self.selected_file