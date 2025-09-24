from PySide6.QtCore import QObject, Signal, Slot, QTimer
import time
from typing import Dict, Optional, Any

from utils.SpirometryGraphManager import SpirometryGraphManager
from utils.ECGGraphManager import ECGGraphManager
# from utils.EMGGraphManager import EMGGraphManager  # A implementar
# from utils.EEGGraphManager import EEGGraphManager  # A implementar

class DeviceInfo:
    """Clase para almacenar información de un dispositivo"""
    def __init__(self, device_type: str, device_name: str, port: str = None):
        self.device_type = device_type
        self.device_name = device_name
        self.port = port
        self.connected = False
        self.last_seen = time.time()
        self.graph_manager = None
        self.status = {}
        self.capabilities = {}
        self.tab_index = -1  # Índice de la pestaña correspondiente

class DeviceManager(QObject):
    # Señales para comunicar cambios de estado
    device_detected = Signal(str, dict)  # (device_type, device_info)
    device_connected = Signal(str, dict)  # (device_type, device_info) 
    device_disconnected = Signal(str)  # (device_type)
    device_status_changed = Signal(str, dict)  # (device_type, status)
    active_device_changed = Signal(str)  # (device_type)
    request_tab_switch = Signal(str)  # (device_type) - Nueva señal para UI
    request_tab_disable = Signal(list)  # (disabled_device_types) - Nueva señal
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Registry de dispositivos detectados
        self.devices: Dict[str, DeviceInfo] = {}
        
        # Dispositivo activo actualmente
        self.active_device: Optional[str] = None
        
        # Factory de graph managers
        self.graph_factories = {
            'SPIRO': self._create_spiro_manager,
            'ECG': self._create_ecg_manager,
            'EMG': self._create_emg_manager,
            'EEG': self._create_eeg_manager
        }
        
        # Mapeo de tipos de dispositivo a índices de pestaña
        self.device_tab_mapping = {
            'SPIRO': 0,  # Pestaña de espirometría
            'ECG': 1,    # Pestaña de ECG
            'EMG': 2,    # Pestaña de EMG
            'EEG': 3     # Pestaña de EEG
        }
        
        # Configuraciones por defecto para cada tipo de dispositivo
        self.device_defaults = {
            'SPIRO': {
                'sampling_rate': 200,
                'filter': True,
                'name': 'Espirómetro',
                'units': {'pressure': 'Pa', 'flow': 'L/s', 'volume': 'L'},
                'ranges': {'pressure': (-1000, 1000), 'flow': (-15, 15), 'volume': (0, 8)}
            },
            'ECG': {
                'sampling_rate': 500,
                'filter': True,
                'name': 'Electrocardiógrafo',
                'leads': ['I', 'II', 'III', 'aVR', 'aVL', 'aVF'],
                'units': {'amplitude': 'mV'},
                'ranges': {'amplitude': (-3, 3)}
            },
            'EMG': {
                'sampling_rate': 1000,
                'filter': True,
                'name': 'Electromiografía',
                'channels': 8,
                'units': {'amplitude': 'mV'},
                'ranges': {'amplitude': (-5, 5)}
            },
            'EEG': {
                'sampling_rate': 512,
                'filter': True,
                'name': 'Electroencefalografía',
                'channels': 64,
                'units': {'amplitude': 'µV'},
                'ranges': {'amplitude': (-100, 100)}
            }
        }
        
        # Timer para cleanup de dispositivos desconectados
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_disconnected_devices)
        self.cleanup_timer.start(5000)  # Cada 5 segundos

    @Slot(str, dict)
    def register_device(self, device_type: str, device_info: dict):
        """
        Registrar y conectar un nuevo dispositivo detectado.
        
        Args:
            device_type (str): Tipo de dispositivo (SPIRO, ECG, etc.)
            device_info (dict): Información del dispositivo
        """
        is_new_device = device_type not in self.devices
        
        if is_new_device:
            # Crear nueva entrada de dispositivo
            device = DeviceInfo(
                device_type=device_type,
                device_name=device_info.get('name', self.device_defaults.get(device_type, {}).get('name', f'Dispositivo {device_type}')),
                port=device_info.get('port', None)
            )
            
            # Configurar capacidades por defecto
            device.capabilities = self.device_defaults.get(device_type, {}).copy()
            device.tab_index = self.device_tab_mapping.get(device_type, -1)
            
            # Crear graph manager
            device.graph_manager = self._create_graph_manager(device_type)
            
            # Registrar dispositivo
            self.devices[device_type] = device
            
            # Emitir señal de detección
            self.device_detected.emit(device_type, self._get_device_info_dict(device))
            print(f"Nuevo dispositivo detectado: {device_type}")
        else:
            device = self.devices[device_type]
        
        # Marcar como conectado y actualizar
        device.connected = True
        device.last_seen = time.time()
        
        # Actualizar puerto si cambió
        new_port = device_info.get('port')
        if new_port and device.port != new_port:
            device.port = new_port
        
        # Si es el primer dispositivo conectado o reconexión, hacerlo activo
        if self.active_device is None or not self.devices.get(self.active_device, DeviceInfo('', '')).connected:
            self.set_active_device(device_type)
            
        # Emitir señal de conexión
        self.device_connected.emit(device_type, self._get_device_info_dict(device))
        print(f"Dispositivo {device_type} conectado en puerto {device.port}")
        
        # Solicitar cambio automático de pestaña
        self._request_ui_update(device_type)

    def _request_ui_update(self, connected_device_type: str):
        """
        Solicitar actualización de la UI cuando se conecta un dispositivo.
        
        Args:
            connected_device_type (str): Tipo de dispositivo que se conectó
        """
        # Obtener lista de dispositivos no conectados para desactivar sus pestañas
        disconnected_devices = []
        for dev_type, dev_info in self.devices.items():
            if not dev_info.connected and dev_type != connected_device_type:
                disconnected_devices.append(dev_type)
        
        # Añadir tipos de dispositivo que nunca han sido detectados
        for dev_type in self.device_tab_mapping:
            if dev_type not in self.devices:
                disconnected_devices.append(dev_type)
        
        # Emitir señales para actualizar UI
        self.request_tab_switch.emit(connected_device_type)
        self.request_tab_disable.emit(disconnected_devices)

    def set_active_device(self, device_type: str):
        """
        Establecer el dispositivo activo.
        
        Args:
            device_type (str): Tipo de dispositivo a activar
        """
        if device_type in self.devices and self.devices[device_type].connected:
            old_active = self.active_device
            self.active_device = device_type
            
            # Emitir señal solo si cambió
            if old_active != device_type:
                self.active_device_changed.emit(device_type)
                print(f"Dispositivo activo cambiado a: {device_type}")
        else:
            print(f"Error: Dispositivo {device_type} no está conectado")

    def disconnect_device(self, device_type: str):
        """
        Marcar un dispositivo como desconectado.
        
        Args:
            device_type (str): Tipo de dispositivo
        """
        if device_type in self.devices:
            self.devices[device_type].connected = False
            
            # Si era el dispositivo activo, buscar otro
            if self.active_device == device_type:
                # Buscar otro dispositivo conectado
                for dev_type, dev_info in self.devices.items():
                    if dev_info.connected:
                        self.set_active_device(dev_type)
                        self._request_ui_update(dev_type)
                        break
                else:
                    # No hay dispositivos conectados
                    self.active_device = None
                    self.request_tab_disable.emit(list(self.device_tab_mapping.keys()))
            
            # Emitir señal de desconexión
            self.device_disconnected.emit(device_type)
            print(f"Dispositivo {device_type} desconectado")

    def get_active_device(self) -> Optional[str]:
        """Obtener el tipo de dispositivo activo"""
        return self.active_device

    def get_active_graph_manager(self):
        """Obtener el graph manager del dispositivo activo"""
        if self.active_device and self.active_device in self.devices:
            return self.devices[self.active_device].graph_manager
        return None

    def get_device_graph_manager(self, device_type: str):
        """Obtener el graph manager de un dispositivo específico"""
        if device_type in self.devices:
            return self.devices[device_type].graph_manager
        return None

    def get_connected_devices(self) -> Dict[str, dict]:
        """Obtener lista de dispositivos conectados"""
        connected = {}
        for device_type, device in self.devices.items():
            if device.connected and self._is_device_alive(device):
                connected[device_type] = self._get_device_info_dict(device)
        return connected

    def get_device_capabilities(self, device_type: str) -> dict:
        """Obtener las capacidades de un dispositivo"""
        if device_type in self.devices:
            return self.devices[device_type].capabilities.copy()
        return self.device_defaults.get(device_type, {}).copy()

    def get_tab_index_for_device(self, device_type: str) -> int:
        """Obtener el índice de pestaña para un tipo de dispositivo"""
        return self.device_tab_mapping.get(device_type, -1)

    def update_device_status(self, device_type: str, status: dict):
        """Actualizar el estado de un dispositivo"""
        if device_type in self.devices:
            device = self.devices[device_type]
            device.status.update(status)
            device.last_seen = time.time()
            self.device_status_changed.emit(device_type, device.status.copy())

    def send_command_to_device(self, device_type: str, command: dict) -> bool:
        """Enviar comando a un dispositivo específico"""
        if device_type in self.devices and self.devices[device_type].connected:
            # TODO: Implementar envío vía SerialHandler
            print(f"Enviando comando a {device_type}: {command}")
            return True
        return False

    def send_command_to_active(self, command: dict) -> bool:
        """Enviar comando al dispositivo activo"""
        if self.active_device:
            return self.send_command_to_device(self.active_device, command)
        return False

    def _create_graph_manager(self, device_type: str):
        """Crear el graph manager apropiado para el tipo de dispositivo"""
        factory_func = self.graph_factories.get(device_type)
        if factory_func:
            return factory_func()
        else:
            print(f"Warning: No hay factory para dispositivo {device_type}")
            return None

    def _create_spiro_manager(self):
        return SpirometryGraphManager()

    def _create_ecg_manager(self):
        return ECGGraphManager()

    def _create_emg_manager(self):
        # TODO: Implementar EMGGraphManager
        print("Warning: EMGGraphManager no implementado aún")
        return None

    def _create_eeg_manager(self):
        # TODO: Implementar EEGGraphManager  
        print("Warning: EEGGraphManager no implementado aún")
        return None

    def _is_device_alive(self, device: DeviceInfo) -> bool:
        """Verificar si un dispositivo está vivo basado en last_seen"""
        return (time.time() - device.last_seen) < 10.0

    def _cleanup_disconnected_devices(self):
        """Limpiar dispositivos desconectados automáticamente"""
        disconnected_devices = []
        
        for device_type, device in self.devices.items():
            if device.connected and not self._is_device_alive(device):
                disconnected_devices.append(device_type)
        
        # Marcar como desconectados
        for device_type in disconnected_devices:
            self.disconnect_device(device_type)

    def _get_device_info_dict(self, device: DeviceInfo) -> dict:
        """Convertir DeviceInfo a diccionario"""
        return {
            'name': device.device_name,
            'type': device.device_type,
            'port': device.port,
            'connected': device.connected,
            'last_seen': device.last_seen,
            'status': device.status.copy(),
            'capabilities': device.capabilities.copy(),
            'tab_index': device.tab_index
        }

    def get_device_types(self) -> list:
        """Obtener lista de tipos de dispositivos soportados"""
        return list(self.graph_factories.keys())

    def is_device_supported(self, device_type: str) -> bool:
        """Verificar si un tipo de dispositivo es soportado"""
        return device_type in self.graph_factories