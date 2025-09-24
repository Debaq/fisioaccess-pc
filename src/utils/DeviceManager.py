from PySide6.QtCore import QObject, Signal, Slot
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

class DeviceManager(QObject):
    # Señales para comunicar cambios de estado
    device_added = Signal(str, dict)  # (device_type, device_info)
    device_removed = Signal(str)  # (device_type)
    device_status_changed = Signal(str, dict)  # (device_type, status)
    active_device_changed = Signal(str)  # (device_type)
    
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
        
        # Configuraciones por defecto para cada tipo de dispositivo
        self.device_defaults = {
            'SPIRO': {
                'sampling_rate': 200,
                'filter': True,
                'units': {'pressure': 'Pa', 'flow': 'L/s', 'volume': 'L'},
                'ranges': {'pressure': (-1000, 1000), 'flow': (-15, 15), 'volume': (0, 8)}
            },
            'ECG': {
                'sampling_rate': 500,
                'filter': True,
                'leads': ['I', 'II', 'III', 'aVR', 'aVL', 'aVF'],
                'units': {'amplitude': 'mV'},
                'ranges': {'amplitude': (-3, 3)}
            },
            'EMG': {
                'sampling_rate': 1000,
                'filter': True,
                'channels': 8,
                'units': {'amplitude': 'mV'},
                'ranges': {'amplitude': (-5, 5)}
            },
            'EEG': {
                'sampling_rate': 512,
                'filter': True,
                'channels': 64,
                'units': {'amplitude': 'µV'},
                'ranges': {'amplitude': (-100, 100)}
            }
        }
        
        # Timer para cleanup de dispositivos desconectados
        from PySide6.QtCore import QTimer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_disconnected_devices)
        self.cleanup_timer.start(5000)  # Cada 5 segundos

    @Slot(str, dict)
    def register_device(self, device_type: str, device_info: dict):
        """
        Registrar un nuevo dispositivo detectado.
        
        Args:
            device_type (str): Tipo de dispositivo (SPIRO, ECG, etc.)
            device_info (dict): Información del dispositivo
        """
        if device_type not in self.devices:
            # Crear nueva entrada de dispositivo
            device = DeviceInfo(
                device_type=device_type,
                device_name=device_info.get('name', f'Dispositivo {device_type}'),
                port=device_info.get('port', None)
            )
            
            # Configurar capacidades por defecto
            device.capabilities = self.device_defaults.get(device_type, {}).copy()
            
            # Crear graph manager
            device.graph_manager = self._create_graph_manager(device_type)
            
            # Registrar dispositivo
            self.devices[device_type] = device
            
            # Si es el primer dispositivo, hacerlo activo
            if self.active_device is None:
                self.set_active_device(device_type)
            
            # Emitir señal
            self.device_added.emit(device_type, self._get_device_info_dict(device))
            
            print(f"Dispositivo {device_type} registrado exitosamente")
        
        # Actualizar información existente
        else:
            device = self.devices[device_type]
            device.connected = True
            device.last_seen = time.time()
            
            # Actualizar puerto si cambió
            new_port = device_info.get('port')
            if new_port and device.port != new_port:
                device.port = new_port
                
            print(f"Dispositivo {device_type} actualizado")

    def _create_graph_manager(self, device_type: str):
        """
        Crear el graph manager apropiado para el tipo de dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
            
        Returns:
            BaseGraphManager: Graph manager correspondiente
        """
        factory_func = self.graph_factories.get(device_type)
        if factory_func:
            return factory_func()
        else:
            print(f"Warning: No hay factory para dispositivo {device_type}")
            return None

    def _create_spiro_manager(self):
        """Crear SpirometryGraphManager"""
        return SpirometryGraphManager()

    def _create_ecg_manager(self):
        """Crear ECGGraphManager"""
        return ECGGraphManager()

    def _create_emg_manager(self):
        """Crear EMGGraphManager (placeholder)"""
        # TODO: Implementar EMGGraphManager
        print("Warning: EMGGraphManager no implementado aún")
        return None

    def _create_eeg_manager(self):
        """Crear EEGGraphManager (placeholder)"""
        # TODO: Implementar EEGGraphManager
        print("Warning: EEGGraphManager no implementado aún")
        return None

    def set_active_device(self, device_type: str):
        """
        Establecer el dispositivo activo.
        
        Args:
            device_type (str): Tipo de dispositivo a activar
        """
        if device_type in self.devices:
            old_active = self.active_device
            self.active_device = device_type
            
            # Emitir señal solo si cambió
            if old_active != device_type:
                self.active_device_changed.emit(device_type)
                print(f"Dispositivo activo cambiado a: {device_type}")
        else:
            print(f"Error: Dispositivo {device_type} no está registrado")

    def get_active_device(self) -> Optional[str]:
        """
        Obtener el tipo de dispositivo activo.
        
        Returns:
            str: Tipo de dispositivo activo o None
        """
        return self.active_device

    def get_active_graph_manager(self):
        """
        Obtener el graph manager del dispositivo activo.
        
        Returns:
            BaseGraphManager: Graph manager activo o None
        """
        if self.active_device and self.active_device in self.devices:
            return self.devices[self.active_device].graph_manager
        return None

    def get_device_graph_manager(self, device_type: str):
        """
        Obtener el graph manager de un dispositivo específico.
        
        Args:
            device_type (str): Tipo de dispositivo
            
        Returns:
            BaseGraphManager: Graph manager del dispositivo o None
        """
        if device_type in self.devices:
            return self.devices[device_type].graph_manager
        return None

    def get_connected_devices(self) -> Dict[str, dict]:
        """
        Obtener lista de dispositivos conectados.
        
        Returns:
            dict: Diccionario con información de dispositivos conectados
        """
        connected = {}
        for device_type, device in self.devices.items():
            if device.connected and self._is_device_alive(device):
                connected[device_type] = self._get_device_info_dict(device)
        return connected

    def get_device_capabilities(self, device_type: str) -> dict:
        """
        Obtener las capacidades de un dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
            
        Returns:
            dict: Capacidades del dispositivo
        """
        if device_type in self.devices:
            return self.devices[device_type].capabilities.copy()
        return {}

    def update_device_status(self, device_type: str, status: dict):
        """
        Actualizar el estado de un dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
            status (dict): Nuevo estado
        """
        if device_type in self.devices:
            device = self.devices[device_type]
            device.status.update(status)
            device.last_seen = time.time()
            
            # Emitir señal de cambio de estado
            self.device_status_changed.emit(device_type, device.status.copy())

    def send_command_to_device(self, device_type: str, command: dict) -> bool:
        """
        Enviar comando a un dispositivo específico.
        
        Args:
            device_type (str): Tipo de dispositivo
            command (dict): Comando a enviar
            
        Returns:
            bool: True si se pudo enviar el comando
        """
        if device_type in self.devices and self.devices[device_type].connected:
            # TODO: Implementar envío de comando vía SerialHandler
            print(f"Enviando comando a {device_type}: {command}")
            return True
        return False

    def send_command_to_active(self, command: dict) -> bool:
        """
        Enviar comando al dispositivo activo.
        
        Args:
            command (dict): Comando a enviar
            
        Returns:
            bool: True si se pudo enviar el comando
        """
        if self.active_device:
            return self.send_command_to_device(self.active_device, command)
        return False

    def remove_device(self, device_type: str):
        """
        Remover un dispositivo del registry.
        
        Args:
            device_type (str): Tipo de dispositivo a remover
        """
        if device_type in self.devices:
            # Limpiar graph manager si existe
            if self.devices[device_type].graph_manager:
                self.devices[device_type].graph_manager.clear_data()
            
            # Remover del registry
            del self.devices[device_type]
            
            # Si era el dispositivo activo, seleccionar otro
            if self.active_device == device_type:
                remaining_devices = list(self.devices.keys())
                self.active_device = remaining_devices[0] if remaining_devices else None
                if self.active_device:
                    self.active_device_changed.emit(self.active_device)
            
            # Emitir señal
            self.device_removed.emit(device_type)
            print(f"Dispositivo {device_type} removido")

    def _is_device_alive(self, device: DeviceInfo) -> bool:
        """
        Verificar si un dispositivo está vivo basado en last_seen.
        
        Args:
            device (DeviceInfo): Información del dispositivo
            
        Returns:
            bool: True si el dispositivo está vivo
        """
        return (time.time() - device.last_seen) < 10.0  # 10 segundos timeout

    def _cleanup_disconnected_devices(self):
        """Limpiar dispositivos desconectados automáticamente"""
        disconnected_devices = []
        
        for device_type, device in self.devices.items():
            if device.connected and not self._is_device_alive(device):
                device.connected = False
                disconnected_devices.append(device_type)
        
        # Remover dispositivos desconectados
        for device_type in disconnected_devices:
            print(f"Dispositivo {device_type} desconectado por timeout")
            # No remover completamente, solo marcar como desconectado
            # self.remove_device(device_type)

    def _get_device_info_dict(self, device: DeviceInfo) -> dict:
        """
        Convertir DeviceInfo a diccionario para señales.
        
        Args:
            device (DeviceInfo): Información del dispositivo
            
        Returns:
            dict: Información del dispositivo como diccionario
        """
        return {
            'name': device.device_name,
            'type': device.device_type,
            'port': device.port,
            'connected': device.connected,
            'last_seen': device.last_seen,
            'status': device.status.copy(),
            'capabilities': device.capabilities.copy()
        }

    def get_device_types(self) -> list:
        """
        Obtener lista de tipos de dispositivos soportados.
        
        Returns:
            list: Lista de tipos de dispositivos
        """
        return list(self.graph_factories.keys())

    def is_device_supported(self, device_type: str) -> bool:
        """
        Verificar si un tipo de dispositivo es soportado.
        
        Args:
            device_type (str): Tipo de dispositivo
            
        Returns:
            bool: True si es soportado
        """
        return device_type in self.graph_factories

    def configure_device(self, device_type: str, config: dict):
        """
        Configurar un dispositivo específico.
        
        Args:
            device_type (str): Tipo de dispositivo
            config (dict): Configuración a aplicar
        """
        if device_type in self.devices:
            device = self.devices[device_type]
            device.capabilities.update(config)
            
            # Enviar comando de configuración al dispositivo
            cmd = {
                "cmd": "config",
                "params": config
            }
            self.send_command_to_device(device_type, cmd)
            
            print(f"Configuración aplicada a {device_type}: {config}")