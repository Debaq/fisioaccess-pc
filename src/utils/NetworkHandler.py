from PySide6.QtCore import QObject, Signal
import requests
import os

class NetworkHandler(QObject):
    """Manejador de operaciones de red"""
    
    # Señales
    upload_success = Signal(dict)  # Emite la respuesta del servidor
    upload_failed = Signal(str)    # Emite mensaje de error
    connectivity_checked = Signal(bool)  # Emite True si hay internet
    
    def __init__(self):
        super().__init__()
        self.api_url = "https://tmeduca.org/api-pdf/index.php"
        self.timeout = 5  # segundos
        
    def check_connectivity(self):
        """
        Verificar si hay conexión a internet
        
        Returns:
            bool: True si hay conexión, False en caso contrario
        """
        try:
            # Intentar conectar al servidor de la API
            response = requests.head(self.api_url, timeout=self.timeout)
            has_connection = response.status_code < 500
            self.connectivity_checked.emit(has_connection)
            return has_connection
            
        except requests.exceptions.RequestException:
            # Sin conexión
            self.connectivity_checked.emit(False)
            return False
    
    def upload_files(self, pdf_path, raw_path, metadata):
        """
        Subir archivos al servidor
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            raw_path (str): Ruta al archivo RAW
            metadata (dict): Diccionario con 'owner', 'type', 'comments'
            
        Returns:
            dict: Respuesta del servidor si exitoso, None si falla
        """
        try:
            # Verificar que los archivos existen
            if not os.path.exists(pdf_path):
                error_msg = f"Archivo PDF no encontrado: {pdf_path}"
                self.upload_failed.emit(error_msg)
                return None
                
            if not os.path.exists(raw_path):
                error_msg = f"Archivo RAW no encontrado: {raw_path}"
                self.upload_failed.emit(error_msg)
                return None
            
            # Preparar archivos para subir
            with open(pdf_path, "rb") as pdf_file, open(raw_path, "rb") as raw_file:
                files = {
                    "pdf": (os.path.basename(pdf_path), pdf_file, "application/pdf"),
                    "raw": (os.path.basename(raw_path), raw_file, "application/octet-stream")
                }
                
                data = {
                    "owner": metadata.get('owner', 'Lab Física'),
                    "type": metadata.get('type', 'Mediciones'),
                    "comments": metadata.get('comments', '')
                }
                
                # Realizar la petición POST
                response = requests.post(
                    self.api_url, 
                    files=files, 
                    data=data,
                    timeout=30  # Timeout mayor para upload
                )
                
                # Verificar respuesta
                response.raise_for_status()
                
                # Parsear respuesta JSON
                response_data = response.json()
                
                self.upload_success.emit(response_data)
                return response_data
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout: El servidor no respondió a tiempo"
            self.upload_failed.emit(error_msg)
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = "Error de conexión: No se pudo conectar al servidor"
            self.upload_failed.emit(error_msg)
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Error HTTP: {e.response.status_code} - {e.response.reason}"
            self.upload_failed.emit(error_msg)
            return None
            
        except ValueError as e:
            error_msg = f"Error al parsear respuesta del servidor: {str(e)}"
            self.upload_failed.emit(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Error inesperado al subir archivos: {str(e)}"
            self.upload_failed.emit(error_msg)
            return None
    
    def set_api_url(self, url):
        """
        Cambiar la URL de la API
        
        Args:
            url (str): Nueva URL de la API
        """
        self.api_url = url
    
    def set_timeout(self, timeout):
        """
        Cambiar el timeout de las peticiones
        
        Args:
            timeout (int): Timeout en segundos
        """
        self.timeout = timeout
    
    def get_online_studies(self):
        """
        Obtener listado de estudios disponibles en el servidor
        
        Returns:
            list: Lista de diccionarios con información de estudios, None si falla
        """
        try:
            # Construir URL del listado (mismo servidor, archivo listado.php)
            base_url = self.api_url.rsplit('/', 1)[0]  # Quitar index.php
            listado_url = f"{base_url}/listado.php"
            
            # Realizar petición GET
            response = requests.get(listado_url, timeout=self.timeout)
            
            # Verificar respuesta
            response.raise_for_status()
            
            # Parsear respuesta JSON
            studies = response.json()
            
            # Validar que sea una lista
            if not isinstance(studies, list):
                raise ValueError("La respuesta no es una lista válida")
            
            return studies
            
        except requests.exceptions.Timeout:
            error_msg = "Timeout: El servidor no respondió a tiempo"
            self.upload_failed.emit(error_msg)
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = "Error de conexión: No se pudo conectar al servidor"
            self.upload_failed.emit(error_msg)
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Error HTTP: {e.response.status_code} - {e.response.reason}"
            self.upload_failed.emit(error_msg)
            return None
            
        except ValueError as e:
            error_msg = f"Error al parsear respuesta del servidor: {str(e)}"
            self.upload_failed.emit(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Error inesperado al obtener listado: {str(e)}"
            self.upload_failed.emit(error_msg)
            return None
    
    def download_study(self, url, output_path):
        """
        Descargar un archivo de estudio desde URL
        
        Args:
            url (str): URL del archivo a descargar
            output_path (str): Ruta donde guardar el archivo
            
        Returns:
            bool: True si se descargó exitosamente, False en caso contrario
        """
        try:
            # Descargar archivo
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Guardar en disco
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
            
        except Exception as e:
            error_msg = f"Error descargando archivo: {str(e)}"
            self.upload_failed.emit(error_msg)
            return False