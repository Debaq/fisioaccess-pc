from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot
import pyqtgraph as pg
from .main_window import Ui_Main
from serial_comm.serial_handler import SerialHandler  # Asumiendo que crearás esta clase

class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Inicializar el manejador serial
        self.serial_handler = None
        
        # Configurar el gráfico
        self.setup_plot()
        
        # Conectar señales
        self.connect_signals()
        
        # Variables de estado
        self.is_recording = False
        self.current_mode = None  # 'espirometria', 'ecg', o 'emg'
        
    def setup_plot(self):
        """Configura el área de gráfico PyQtGraph"""
        self.plot_widget = pg.PlotWidget()
        self.horizontalLayout_2.addWidget(self.plot_widget)
        
        # Configurar el estilo del gráfico
        self.plot_widget.setBackground('white')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_curve = self.plot_widget.plot(pen='b')
        
    def connect_signals(self):
        """Conecta todos los botones y acciones con sus slots"""
        # Conectar acciones del menú
        self.actionEspirometria.triggered.connect(lambda: self.change_mode('espirometria'))
        self.actionECG.triggered.connect(lambda: self.change_mode('ecg'))
        self.actionEOG.triggered.connect(lambda: self.change_mode('emg'))
        
        # Conectar botones
        self.pushButton.clicked.connect(self.open_port)
        self.pushButton_2.clicked.connect(self.toggle_recording)
        self.pushButton_3.clicked.connect(self.clear_data)
        self.pushButton_4.clicked.connect(self.reset_view)
        self.pushButton_5.clicked.connect(self.save_data)
        
    @Slot()
    def change_mode(self, mode):
        """Cambia el modo de medición"""
        self.current_mode = mode
        # Aquí puedes agregar configuración específica para cada modo
        self.statusbar.showMessage(f"Modo: {mode.upper()}")
        
    @Slot()
    def open_port(self):
        """Abre el puerto serial"""
        try:
            if self.serial_handler is None:
                self.serial_handler = SerialHandler()
                self.serial_handler.data_received.connect(self.update_plot)
                self.pushButton.setText("Cerrar")
            else:
                self.serial_handler.close()
                self.serial_handler = None
                self.pushButton.setText("Abrir")
        except Exception as e:
            self.statusbar.showMessage(f"Error: {str(e)}")
            
    @Slot()
    def toggle_recording(self):
        """Inicia o detiene la grabación"""
        self.is_recording = not self.is_recording
        button_text = "Detener" if self.is_recording else "Iniciar"
        self.pushButton_2.setText(button_text)
        
        if self.serial_handler:
            if self.is_recording:
                self.serial_handler.start_reading()
            else:
                self.serial_handler.stop_reading()
                
    @Slot()
    def clear_data(self):
        """Limpia los datos del gráfico"""
        self.plot_curve.setData([], [])
        
    @Slot()
    def reset_view(self):
        """Resetea la vista del gráfico"""
        self.plot_widget.enableAutoRange()
        
    @Slot()
    def save_data(self):
        """Guarda los datos actuales"""
        # Implementar la lógica de guardado
        pass
        
    @Slot(list)
    def update_plot(self, data):
        """Actualiza el gráfico con nuevos datos"""
        # Implementar la actualización del gráfico
        # Este método será llamado cuando se reciban nuevos datos del puerto serial
        pass