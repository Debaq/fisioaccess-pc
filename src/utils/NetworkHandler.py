from PySide6.QtCore import QObject, Signal
import requests
import os
import json  
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
        DEBUG = True  # ← Cambiar a False para desactivar prints
        
        try:
            if DEBUG:
                print(f"DEBUG: Iniciando upload_files")
                print(f"DEBUG: pdf_path existe: {os.path.exists(pdf_path)}")
                print(f"DEBUG: raw_path existe: {os.path.exists(raw_path)}")
                print(f"DEBUG: API URL: {self.api_url}")
            
            # Verificar que los archivos existen
            if not os.path.exists(pdf_path):
                error_msg = f"Archivo PDF no encontrado: {pdf_path}"
                if DEBUG: print(f"DEBUG ERROR: {error_msg}")
                self.upload_failed.emit(error_msg)
                return None
                
            if not os.path.exists(raw_path):
                error_msg = f"Archivo RAW no encontrado: {raw_path}"
                if DEBUG: print(f"DEBUG ERROR: {error_msg}")
                self.upload_failed.emit(error_msg)
                return None
            
            if DEBUG:
                print(f"DEBUG: Archivos verificados, preparando upload...")
                print(f"DEBUG: metadata = {metadata}")
            
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
                
                if DEBUG:
                    print(f"DEBUG: files keys = {files.keys()}")
                    print(f"DEBUG: data = {data}")
                    print(f"DEBUG: Enviando POST request...")
                
                # Realizar la petición POST
                response = requests.post(
                    self.api_url, 
                    files=files, 
                    data=data,
                    timeout=30  # Timeout mayor para upload
                )
                
                if DEBUG:
                    print(f"DEBUG: Response status code = {response.status_code}")
                    print(f"DEBUG: Response headers = {dict(response.headers)}")
                    print(f"DEBUG: Response text (primeros 1000 chars):")
                    print(response.text[:1000])
                
                # Verificar respuesta
                response.raise_for_status()
                
                if DEBUG:
                    print(f"DEBUG: Parseando respuesta JSON...")
                
                # Parsear respuesta JSON
                response_data = response.json()
                
                if DEBUG:
                    print(f"DEBUG: Response JSON = {response_data}")
                
                self.upload_success.emit(response_data)
                return response_data
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout: El servidor no respondió a tiempo"
            if DEBUG: print(f"DEBUG EXCEPTION: {error_msg}")
            self.upload_failed.emit(error_msg)
            return None
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Error de conexión: No se pudo conectar al servidor - {str(e)}"
            if DEBUG: print(f"DEBUG EXCEPTION: {error_msg}")
            self.upload_failed.emit(error_msg)
            return None
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Error HTTP: {e.response.status_code} - {e.response.reason}"
            if DEBUG: 
                print(f"DEBUG EXCEPTION: {error_msg}")
                print(f"DEBUG: Response text = {e.response.text}")
            self.upload_failed.emit(error_msg)
            return None
            
        except ValueError as e:
            error_msg = f"Error al parsear respuesta del servidor: {str(e)}"
            if DEBUG: 
                print(f"DEBUG EXCEPTION: {error_msg}")
                print(f"DEBUG: Response que falló al parsear = {response.text[:1000]}")
            self.upload_failed.emit(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Error inesperado al subir archivos: {str(e)}"
            if DEBUG: 
                print(f"DEBUG EXCEPTION: {error_msg}")
                import traceback
                traceback.print_exc()
            self.upload_failed.emit(error_msg)
            return None
    
    
    
    def sync_offline_studies(self, file_handler):
        """
        Sincronizar estudios offline con el servidor
        
        Args:
            file_handler: Instancia de FileHandler para acceder a archivos offline
            
        Returns:
            dict: Estadísticas de sincronización {'uploaded': int, 'failed': int, 'migrated': int}
        """
        DEBUG = True
        
        stats = {
            'uploaded': 0,
            'failed': 0,
            'migrated': 0,
            'files': []
        }
        
        try:
            # Verificar conectividad
            if not self.check_connectivity():
                if DEBUG: print("DEBUG SYNC: Sin conexión a internet")
                return stats
            
            if DEBUG: print("DEBUG SYNC: Conexión verificada, buscando archivos offline...")
            
            # Obtener carpeta offline
            offline_folder = file_handler.get_offline_folder()
            
            if not os.path.exists(offline_folder):
                if DEBUG: print(f"DEBUG SYNC: Carpeta offline no existe: {offline_folder}")
                return stats
            
            # Buscar archivos JSON (RAW)
            json_files = [f for f in os.listdir(offline_folder) if f.endswith('.json')]
            
            if DEBUG: print(f"DEBUG SYNC: Encontrados {len(json_files)} archivos offline")
            
            for json_filename in json_files:
                try:
                    json_path = os.path.join(offline_folder, json_filename)
                    
                    # Buscar PDF correspondiente
                    pdf_filename = json_filename.replace('.json', '.pdf')
                    pdf_path = os.path.join(offline_folder, pdf_filename)
                    
                    if not os.path.exists(pdf_path):
                        if DEBUG: print(f"DEBUG SYNC: PDF no encontrado para {json_filename}, saltando...")
                        stats['failed'] += 1
                        continue
                    
                    if DEBUG: print(f"DEBUG SYNC: Procesando {json_filename}...")
                    
                    # Leer y migrar JSON si es necesario
                    with open(json_path, 'r') as f:
                        study_data = json.load(f)
                    
                    migrated = False
                    
                    # Migrar "comentarios" → "comments"
                    if 'patient' in study_data and 'comentarios' in study_data['patient']:
                        study_data['patient']['comments'] = study_data['patient']['comentarios']
                        del study_data['patient']['comentarios']
                        migrated = True
                        if DEBUG: print(f"DEBUG SYNC: Migrado campo 'comentarios' en patient")
                    
                    if 'analysis' in study_data and 'comentarios' in study_data['analysis']:
                        study_data['analysis']['comments'] = study_data['analysis']['comentarios']
                        del study_data['analysis']['comentarios']
                        migrated = True
                        if DEBUG: print(f"DEBUG SYNC: Migrado campo 'comentarios' en analysis")
                    
                    # Si se migró, guardar cambios
                    if migrated:
                        with open(json_path, 'w') as f:
                            json.dump(study_data, f, indent=2)
                        stats['migrated'] += 1
                        if DEBUG: print(f"DEBUG SYNC: Archivo migrado guardado")
                    
                    # Preparar metadata para upload
                    patient_data = study_data.get('patient', {})
                    metadata = {
                        'owner': patient_data.get('nombre', 'Paciente'),
                        'type': 'Espirometría',
                        'comments': patient_data.get('comments', '')
                    }
                    
                    if DEBUG: print(f"DEBUG SYNC: Subiendo {json_filename}...")
                    
                    # Intentar subir
                    response = self.upload_files(pdf_path, json_path, metadata)
                    
                    if response:
                        stats['uploaded'] += 1
                        stats['files'].append({
                            'filename': json_filename,
                            'status': 'uploaded',
                            'url': response.get('url', response.get('link', ''))
                        })
                        if DEBUG: print(f"DEBUG SYNC: ✓ {json_filename} subido exitosamente")
                        
                        # Opcional: Eliminar archivos locales después de subir
                        # os.remove(json_path)
                        # os.remove(pdf_path)
                        
                    else:
                        stats['failed'] += 1
                        stats['files'].append({
                            'filename': json_filename,
                            'status': 'failed'
                        })
                        if DEBUG: print(f"DEBUG SYNC: ✗ {json_filename} falló al subir")
                        
                except Exception as e:
                    stats['failed'] += 1
                    if DEBUG: print(f"DEBUG SYNC: Error procesando {json_filename}: {str(e)}")
                    continue
            
            if DEBUG:
                print(f"\nDEBUG SYNC: Resumen:")
                print(f"  - Subidos: {stats['uploaded']}")
                print(f"  - Fallidos: {stats['failed']}")
                print(f"  - Migrados: {stats['migrated']}")
            
            return stats
            
        except Exception as e:
            if DEBUG: print(f"DEBUG SYNC: Error general: {str(e)}")
            return stats
    
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