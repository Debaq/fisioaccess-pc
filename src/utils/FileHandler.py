from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QObject, Signal
import csv
import json
import os
from datetime import datetime
import tempfile

class FileHandler(QObject):
    # Señales para notificar estados
    save_status = Signal(str)
    error_occurred = Signal(str)
    
    # Señal para datos CSV (legacy)
    data_loaded = Signal(dict)
    
    # Nueva señal para estudio completo
    complete_study_loaded = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.offline_folder = os.path.expanduser("~/Documents/Spirometry_Offline")
        
    def save_data_to_csv(self, parent, data):
        """
        Guarda los datos en un archivo CSV (método legacy).
        
        Args:
            parent: Widget padre para el diálogo
            data (dict): Diccionario con las listas de datos {'t': [], 'p': [], 'f': [], 'v': []}
        """
        try:
            # Verificar si hay datos para guardar
            if not data['t']:
                self.save_status.emit("No hay datos para guardar")
                return False

            # Abrir diálogo para seleccionar ubicación y nombre del archivo
            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                "Guardar Datos",
                os.path.expanduser("~/Documents"),
                "Archivos CSV (*.csv)"
            )

            if file_path:
                # Asegurar que el archivo termine en .csv
                if not file_path.endswith('.csv'):
                    file_path += '.csv'

                # Crear lista de datos para escribir
                data_to_write = []
                
                # Encabezados
                headers = ['tiempo', 'presion', 'flujo', 'volumen']
                data_to_write.append(headers)
                
                # Obtener la longitud de los datos
                data_length = len(data['t'])
                
                # Combinar datos
                for i in range(data_length):
                    row = [
                        data['t'][i],
                        data['p'][i],
                        data['f'][i],
                        data['v'][i]
                    ]
                    data_to_write.append(row)

                # Escribir al archivo CSV
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(data_to_write)

                self.save_status.emit(f"Datos guardados exitosamente en {file_path}")
                return True

            return False

        except Exception as e:
            error_msg = f"Error al guardar datos: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False

    def open_data_file(self, parent):
        """
        Abre y carga datos desde un archivo CSV (método legacy).
        
        Args:
            parent: Widget padre para el diálogo
        """
        try:
            # Abrir diálogo para seleccionar archivo
            file_path, _ = QFileDialog.getOpenFileName(
                parent,
                "Abrir Datos",
                os.path.expanduser("~/Documents"),
                "Archivos CSV (*.csv)"
            )

            if file_path:
                # Inicializar diccionario de datos
                data = {
                    't': [],
                    'p': [],
                    'f': [],
                    'v': []
                }
                
                # Leer archivo CSV
                with open(file_path, 'r') as file:
                    csv_reader = csv.reader(file)
                    
                    # Leer encabezados
                    headers = next(csv_reader)
                    # Verificar formato del archivo
                    expected_headers = ['tiempo', 'presion', 'flujo', 'volumen']
                    if not all(h.lower() in [eh.lower() for eh in expected_headers] for h in headers):
                        raise ValueError("Formato de archivo incorrecto: encabezados no coinciden")
                    
                    # Leer datos
                    for row in csv_reader:
                        if len(row) >= 4:  # Verificar que la fila tenga todos los datos
                            try:
                                data['t'].append(float(row[0]))
                                data['p'].append(float(row[1]))
                                data['f'].append(float(row[2]))
                                data['v'].append(float(row[3]))
                            except ValueError as e:
                                raise ValueError(f"Error en formato de datos: {str(e)}")
                
                # Verificar que se hayan cargado datos
                if not data['t']:
                    raise ValueError("No se encontraron datos válidos en el archivo")
                
                # Emitir datos cargados
                self.data_loaded.emit(data)
                self.save_status.emit(f"Datos cargados exitosamente de {file_path}")
                return True

            return False

        except Exception as e:
            error_msg = f"Error al abrir archivo: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False

    def generate_raw_file(self, graph_handler, metadata):
        """
        Generar archivo RAW con el estado completo del estudio
        
        Args:
            graph_handler: Instancia de GraphHandler con los datos
            metadata (dict): Metadata con datos del paciente
            
        Returns:
            str: Ruta al archivo temporal creado
        """
        try:
            # Obtener todos los datos del GraphHandler
            recordings = graph_handler.get_stored_recordings()
            line_positions = graph_handler.line_positions
            
            # Calcular calidad y promedios
            quality = graph_handler.calculate_quality()
            averages = graph_handler.calculate_averages()
            
            # Crear estructura completa
            study_data = {
                "device": "fisioaccess_espiro",
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "patient": {
                    "nombre": metadata.get('nombre', ''),
                    "rut": metadata.get('rut', ''),
                    "sexo": metadata.get('sexo', ''),
                    "fecha_nacimiento": metadata.get('fecha_nacimiento', ''),
                    "edad": metadata.get('edad', 0),
                    "etnia": metadata.get('etnia', ''),
                    "estatura_cm": metadata.get('estatura_cm', 0),
                    "peso_kg": metadata.get('peso_kg', 0.0),
                    "comments": metadata.get('comments', '')
                },
                "analysis": {
                    "interpretacion": metadata.get('interpretacion', ''),
                    "conclusion": metadata.get('conclusion', '')
                },
                "recordings": recordings,
                "line_positions": line_positions,
                "quality": quality,
                "averages": averages
            }
            
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False
            )
            
            # Guardar como JSON
            json.dump(study_data, temp_file, indent=2)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            error_msg = f"Error generando archivo RAW: {str(e)}"
            self.error_occurred.emit(error_msg)
            return None
        
    def save_study_offline(self, raw_path, pdf_path, metadata):
        """
        Guardar estudio en carpeta offline local (RAW y PDF)
        
        Args:
            raw_path (str): Ruta al archivo RAW temporal
            pdf_path (str): Ruta al archivo PDF temporal
            metadata (dict): Metadata del estudio con datos del paciente
            
        Returns:
            str: Ruta del archivo guardado o None si falla
        """
        try:
            # Crear carpeta offline si no existe
            if not os.path.exists(self.offline_folder):
                os.makedirs(self.offline_folder)
            
            # Generar nombre base de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_clean = metadata.get('nombre', 'paciente').replace(" ", "_")
            rut_clean = metadata.get('rut', '').replace(".", "").replace("-", "")
            
            base_filename = f"{timestamp}_{nombre_clean}_{rut_clean}_espiro"
            
            # Guardar archivo RAW (JSON)
            raw_destination = os.path.join(self.offline_folder, f"{base_filename}.json")
            with open(raw_path, 'r') as src, open(raw_destination, 'w') as dst:
                dst.write(src.read())
            
            # Guardar archivo PDF
            pdf_destination = os.path.join(self.offline_folder, f"{base_filename}.pdf")
            with open(pdf_path, 'rb') as src, open(pdf_destination, 'wb') as dst:
                dst.write(src.read())
            
            self.save_status.emit(f"Estudio guardado offline:\n{raw_destination}\n{pdf_destination}")
            
            return raw_destination
            
        except Exception as e:
            error_msg = f"Error guardando offline: {str(e)}"
            self.error_occurred.emit(error_msg)
            return None

    def open_complete_study(self, parent):
        """
        Abrir y cargar un estudio completo desde archivo JSON
        
        Args:
            parent: Widget padre para el diálogo
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            # Abrir diálogo para seleccionar archivo
            file_path, _ = QFileDialog.getOpenFileName(
                parent,
                "Abrir Estudio Completo",
                os.path.expanduser("~/Documents"),
                "Archivos de Estudio (*.json);;Todos los archivos (*.*)"
            )
            
            if not file_path:
                return False
            
            # Leer archivo JSON
            with open(file_path, 'r') as file:
                study_data = json.load(file)
            
            # ========== MIGRACIÓN AUTOMÁTICA ==========
            # Convertir "comentarios" → "comments" si existe versión antigua
            if 'patient' in study_data and 'comentarios' in study_data['patient']:
                study_data['patient']['comments'] = study_data['patient']['comentarios']
                del study_data['patient']['comentarios']
            
            # Migrar también en analysis si existe
            if 'analysis' in study_data:
                if 'comentarios' in study_data['analysis']:
                    study_data['analysis']['comments'] = study_data['analysis']['comentarios']
                    del study_data['analysis']['comentarios']
            # ==========================================
            
            # Verificar formato
            required_fields = ['device', 'version', 'recordings']
            for field in required_fields:
                if field not in study_data:
                    raise ValueError(f"Archivo inválido: falta campo '{field}'")
            
            
            # Verificar que sea del dispositivo correcto
            if study_data['device'] != 'fisioaccess_espiro':
                response = QMessageBox.question(
                    parent,
                    "Dispositivo diferente",
                    f"Este archivo fue creado con '{study_data['device']}'.\n¿Desea continuar?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.No:
                    return False
            
            # Emitir datos cargados
            self.complete_study_loaded.emit(study_data)
            self.save_status.emit(f"Estudio cargado exitosamente de {file_path}")
            
            return True
            
        except json.JSONDecodeError as e:
            error_msg = f"Error al leer archivo JSON: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Error al abrir estudio: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False

    def get_offline_folder(self):
        """Obtener la ruta de la carpeta offline"""
        return self.offline_folder
    
    def set_offline_folder(self, folder_path):
        """Cambiar la ruta de la carpeta offline"""
        self.offline_folder = folder_path
