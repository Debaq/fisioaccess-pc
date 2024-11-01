from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QObject, Signal
import csv
import os

class FileHandler(QObject):
    # Señales para notificar estados
    save_status = Signal(str)
    error_occurred = Signal(str)
    # Nueva señal para datos cargados
    data_loaded = Signal(dict)
    
    def __init__(self):
        super().__init__()
        
    def save_data_to_csv(self, parent, data):
        """
        Guarda los datos en un archivo CSV.
        
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
        Abre y carga datos desde un archivo CSV.
        
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