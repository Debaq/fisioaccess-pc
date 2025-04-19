import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Slot
import numpy as np

class DataManager:
    """
    Clase para manejar la gestión de datos para diferentes tipos de gráficos.
    Almacena y procesa datos según el tipo de gráfico.
    """
    def __init__(self, data_types):
        """
        Inicializa un gestor de datos con los tipos de datos especificados.
        
        Args:
            data_types (list): Lista de tipos de datos a gestionar (p.ej. ['t', 'p', 'f', 'v'])
        """
        # Datos originales para almacenamiento
        self.data = {data_type: [] for data_type in data_types}
        
        # Datos calibrados para visualización
        self.display_data = {data_type: [] for data_type in data_types}
        
        # Tiempo inicial para calibración
        self.initial_time = None
        
        # Bandera para control de grabación
        self.record = True
        
        # Información adicional específica (min/max, etc.)
        self.metadata = {}

    def calibrate_time(self, time_value):
        """
        Calibra el tiempo relativo.
        
        Args:
            time_value: Valor de tiempo a calibrar
            
        Returns:
            float: Tiempo calibrado en segundos
        """
        if self.initial_time is None:
            self.initial_time = time_value
        return (time_value - self.initial_time) / 1000.0

    def add_data_point(self, new_data):
        """
        Añade un punto de datos al conjunto correspondiente.
        
        Args:
            new_data (dict): Diccionario con los nuevos datos
        """
        if not self.record:
            return

        try:
            # Actualizar datos originales
            for key in new_data:
                if key in self.data:
                    self.data[key].append(new_data[key])

            # Actualizar datos de visualización
            if 't' in new_data and 't' in self.display_data:
                self.display_data['t'].append(self.calibrate_time(new_data['t']))
                
            for key in new_data:
                if key != 't' and key in self.display_data:
                    self.display_data[key].append(new_data[key])

            # Mantener solo los últimos 1000 puntos (configurable)
            max_points = 1000
            for key in self.display_data:
                if len(self.display_data[key]) > max_points:
                    self.display_data[key] = self.display_data[key][-max_points:]
                    
        except Exception as e:
            print(f"Error en add_data_point: {e}")

    def clear_data(self):
        """Limpia todos los datos"""
        for key in self.data:
            self.data[key] = []
        for key in self.display_data:
            self.display_data[key] = []
            
        self.initial_time = None
        self.record = True
        self.metadata = {}

    def start_record(self):
        """Inicia la grabación de datos"""
        self.record = True

    def stop_record(self):
        """Detiene la grabación de datos"""
        self.record = False

    def get_min_max(self, data_type):
        """
        Obtiene los valores mínimo y máximo para un tipo de dato.
        
        Args:
            data_type (str): Tipo de dato a analizar
            
        Returns:
            tuple: (min_value, max_value) o (None, None) si no hay datos
        """
        if data_type in self.display_data and self.display_data[data_type]:
            if isinstance(self.display_data[data_type], list):
                return min(self.display_data[data_type]), max(self.display_data[data_type])
        return None, None

    def get_y_value_at_x(self, x_data_type, y_data_type, x_pos):
        """
        Obtiene el valor Y en la posición X de la curva.
        
        Args:
            x_data_type (str): Tipo de dato para el eje X
            y_data_type (str): Tipo de dato para el eje Y
            x_pos (float): Posición en X donde obtener el valor Y
            
        Returns:
            float: Valor interpolado de Y en la posición X, o None si no se puede obtener
        """
        if (not self.display_data[x_data_type] or 
            not self.display_data[y_data_type] or
            len(self.display_data[x_data_type]) != len(self.display_data[y_data_type])):
            return None

        x_data = np.array(self.display_data[x_data_type])
        y_data = np.array(self.display_data[y_data_type])

        # Verificar rango
        if x_pos < x_data[0] or x_pos > x_data[-1]:
            return None

        # Interpolación
        idx = np.searchsorted(x_data, x_pos)
        if idx > 0:
            x0, x1 = x_data[idx-1], x_data[idx]
            y0, y1 = y_data[idx-1], y_data[idx]
            
            if x1 == x0:
                return y0
                
            y_interp = y0 + (y1 - y0) * (x_pos - x0) / (x1 - x0)
            return y_interp

        return None


class BaseGraphManager(QWidget):
    """
    Clase base para gestores de gráficos.
    Define la interfaz común para diferentes tipos de visualizaciones.
    """
    def __init__(self, parent=None, layout_type='horizontal'):
        """
        Inicializa un gestor de gráficos base.
        
        Args:
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        
        # Configurar el layout principal según el tipo especificado
        if layout_type.lower() == 'vertical':
            self.layout = QVBoxLayout(self)
        elif layout_type.lower() == 'grid':
            self.layout = QGridLayout(self)
        else:  # Por defecto, horizontal
            self.layout = QHBoxLayout(self)
            
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Inicializar el gestor de datos (a implementar en subclases)
        self.setup_data_manager()
        
        # Crear los gráficos (a implementar en subclases)
        self.setup_graphs()
        
        # Configurar estilos de las curvas (a implementar en subclases)
        self.setup_curve_styles()
        
        # Configurar marcadores/líneas (a implementar en subclases)
        self.setup_markers()

    def setup_data_manager(self):
        """
        Inicializa el gestor de datos.
        A implementar en las subclases con los tipos de datos específicos.
        """
        self.data_manager = DataManager(['t'])
        
    def setup_graphs(self):
        """
        Configura los widgets de gráficos.
        A implementar en las subclases con la estructura específica.
        """
        pass
        
    def setup_curve_styles(self):
        """
        Configura los estilos de las curvas de gráficos.
        A implementar en las subclases con los estilos específicos.
        """
        pass
        
    def setup_markers(self):
        """
        Configura los marcadores (líneas, etiquetas, etc.).
        A implementar en las subclases con los marcadores específicos.
        """
        pass

    @Slot(dict)
    def update_data(self, new_data):
        """
        Actualiza los datos y gráficos.
        
        Args:
            new_data (dict): Nuevos datos a añadir
        """
        # Añadir datos al gestor
        self.data_manager.add_data_point(new_data)
        
        # Actualizar gráficos
        self.update_plots()

    def update_plots(self):
        """
        Actualiza la visualización de los gráficos.
        A implementar en las subclases según la estructura de cada gráfico.
        """
        pass

    def clear_data(self):
        """
        Limpia todos los datos y restablece la visualización.
        """
        self.data_manager.clear_data()
        self.update_plots()
        self.reset_markers()

    def reset_markers(self):
        """
        Restablece los marcadores a su posición inicial.
        A implementar en las subclases según los marcadores específicos.
        """
        pass

    def start_record(self):
        """Inicia la grabación de datos"""
        self.data_manager.start_record()

    def stop_record(self):
        """Detiene la grabación de datos"""
        self.data_manager.stop_record()
