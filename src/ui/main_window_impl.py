from PySide6.QtWidgets import QMainWindow, QListWidgetItem, QMenu
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtGui import QColor, QBrush, QAction
import serial.tools.list_ports
from .main_window import Ui_Main
from serial_comm.serial_handler import SerialHandler  
from serial_comm.SerialDataHandler import SerialDataHandler
from utils.GraphHandler import GraphHandler
from utils.FileHandler import FileHandler

from ui.SaveDialog import SaveDialog
from utils.NetworkHandler import NetworkHandler
from utils.QRGenerator import QRGenerator, QRDisplayDialog
import os
from utils.PDFGenerator import PDFGenerator



class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Variables de estado
        self.is_calibrated = False
        self.is_testing = False
        self.test_counter = 0
        
        # Variable para almacenar info de calidad actual
        self.current_quality = None
        
        # Iniciar metodos de guardado
        self.file_handler = FileHandler()
        
        self.network_handler = NetworkHandler()
        self.qr_generator = QRGenerator()

        # Inicializar el manejador serial
        self.serial_handler = SerialHandler()
        self.data_handler = SerialDataHandler()
 
        # Inicializar los gráficos
        self.graph_handler = GraphHandler()
        self.horizontalLayout_2.addWidget(self.graph_handler)

        # Configurar el timer para actualizar la lista de puertos
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.update_port_list)
        self.port_timer.start(1000)  # Actualizar cada segundo
        
        # Lista para mantener track de los puertos disponibles
        self.available_ports = []
        
        # Habilitar menú contextual en list_test
        self.list_test.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Conectar señales
        self.connect_signals()
        
        # Actualizar lista inicial de puertos
        self.update_port_list()
        
        # Estado inicial de botones
        self.update_button_states()

    def connect_signals(self):
        """Conectar todas las señales necesarias"""
        
        self.file_handler.save_status.connect(self.statusbar.showMessage)
        self.file_handler.error_occurred.connect(self.statusbar.showMessage)
        self.file_handler.complete_study_loaded.connect(self.load_complete_study)

        self.btn_save.clicked.connect(self.save_data)

        self.btn_clear.clicked.connect(self.clear_data)
        
        # Cambiar reset por calibración
        self.btn_cal.clicked.connect(self.calibrate)
        
        # Conectar el botón de abrir
        self.btn_open.clicked.connect(self.open_file_dialog)
        
        # Conectar la señal de datos cargados del file_handler
        self.file_handler.data_loaded.connect(self.load_data_to_graph)

        # Conectar el botón de conexión
        self.btn_connect.clicked.connect(self.handle_connection)
        
        # Conectar el cambio de selección del combo box
        self.serial_list.currentIndexChanged.connect(self.port_selected)

        # Verificar la conexión de señales del serial_handler
        try:
            # Desconectar primero para evitar conexiones duplicadas
            try:
                self.serial_handler.data_received_serial.disconnect(self.data_handler.analisis_input_serial)
            except:
                pass
            
            # Reconectar la señal
            self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
        except Exception as e:
            print(f"Error al conectar serial_handler.data_received: {str(e)}")

        # Verificar la conexión del data_handler
        try:
            self.data_handler.new_data.connect(self.graph_handler.update_data)
            self.data_handler.other_string.connect(self.handle_calibration_response)

            print("Señal new_data conectada exitosamente a graph_handler")
        except Exception as e:
            print(f"Error al conectar data_handler.new_data: {str(e)}")
        
        # Conectar señal de prueba completada
        try:
            self.graph_handler.new_recording_created.connect(self.on_test_completed)
            print("Señal new_recording_created conectada")
        except Exception as e:
            print(f"Error al conectar new_recording_created: {str(e)}")
        
        # Conectar señal de calidad
        try:
            self.graph_handler.quality_changed.connect(self.update_test_list_colors)
            print("Señal quality_changed conectada")
        except Exception as e:
            print(f"Error al conectar quality_changed: {str(e)}")
        
        self.btn_start.clicked.connect(self.start_test)
        
        # Conectar señales del list_test
        self.list_test.itemSelectionChanged.connect(self.on_test_selection_changed)
        self.list_test.itemClicked.connect(self.on_test_clicked)
        
        # Conectar menú contextual
        self.list_test.customContextMenuRequested.connect(self.show_context_menu)
        
        # Conectar botón para eliminar pruebas
        self.btn_delete_test.clicked.connect(self.delete_selected_test)

        print("Conexión de señales completada\n")

    def show_context_menu(self, position):
        """Mostrar menú contextual para cambiar estado PRE/POST"""
        item = self.list_test.itemAt(position)
        if not item:
            return
        
        recording_number = item.data(Qt.UserRole)
        if recording_number is None:
            return
        
        # Obtener estado actual
        current_status = self.graph_handler.get_bronchodilator_status(recording_number)
        
        # Crear menú
        menu = QMenu(self)
        
        # Acción PRE
        action_pre = QAction("Marcar como PRE", self)
        action_pre.setCheckable(True)
        action_pre.setChecked(current_status == 'PRE')
        action_pre.triggered.connect(lambda: self.set_test_status(recording_number, 'PRE'))
        menu.addAction(action_pre)
        
        # Acción POST
        action_post = QAction("Marcar como POST", self)
        action_post.setCheckable(True)
        action_post.setChecked(current_status == 'POST')
        action_post.triggered.connect(lambda: self.set_test_status(recording_number, 'POST'))
        menu.addAction(action_post)
        
        # Mostrar menú
        menu.exec(self.list_test.viewport().mapToGlobal(position))

    def set_test_status(self, recording_number, status):
        """
        Establecer el estado PRE/POST de una prueba
        
        Args:
            recording_number (int): Número de grabación
            status (str): 'PRE' o 'POST'
        """
        try:
            # Actualizar en GraphHandler
            success = self.graph_handler.set_bronchodilator_status(recording_number, status)
            
            if success:
                # Actualizar texto del item en la lista
                self.update_test_item_text(recording_number)
                
                # Actualizar display de resultados
                self.graph_handler.update_results_display()
                
                self.statusbar.showMessage(f"Prueba {recording_number} marcada como {status}")
            else:
                self.statusbar.showMessage(f"Error: No se encontró la prueba {recording_number}")
                
        except Exception as e:
            self.statusbar.showMessage(f"Error al cambiar estado: {str(e)}")
            print(f"Error en set_test_status: {str(e)}")

    def update_test_item_text(self, recording_number):
        """
        Actualizar el texto de un item en la lista según su estado y calidad
        
        Args:
            recording_number (int): Número de grabación
        """
        # Buscar el item en la lista
        for i in range(self.list_test.count()):
            item = self.list_test.item(i)
            if item.data(Qt.UserRole) == recording_number:
                # Obtener estado
                status = self.graph_handler.get_bronchodilator_status(recording_number)
                
                # Construir texto base
                text = f"Prueba {recording_number} [{status}]"
                
                # Agregar badge de calidad si existe
                if self.current_quality:
                    # Buscar en la calidad del tipo correcto
                    quality_info = self.current_quality.get(status)
                    if quality_info and quality_info.get('grade'):
                        text += f" [{quality_info['grade']}]"
                        
                        # Verificar si está en sugerencias de eliminación
                        if quality_info.get('suggestions'):
                            for suggestion in quality_info['suggestions']:
                                if suggestion['recording_number'] == recording_number:
                                    text += "*"
                                    break
                
                item.setText(text)
                break

    def update_button_states(self):
        """Actualizar el estado de los botones según el estado actual"""
        is_connected = self.btn_connect.isChecked()
        
        # Botón calibrar: solo disponible si está conectado y no está probando
        self.btn_cal.setEnabled(is_connected and not self.is_testing)
        
        # Botón iniciar: solo disponible si está calibrado y no está probando
        self.btn_start.setEnabled(is_connected and self.is_calibrated and not self.is_testing)
        
        # Botón limpiar: disponible si está conectado y no está probando
        self.btn_clear.setEnabled(is_connected and not self.is_testing)
        
        # Botón eliminar test: disponible si hay algo seleccionado en la lista
        self.btn_delete_test.setEnabled(self.list_test.currentItem() is not None)
        
        # Lista de puertos: deshabilitada si está conectado o probando
        self.serial_list.setEnabled(not is_connected and not self.is_testing)

    @Slot()
    def calibrate(self):
        """Enviar comando de calibración"""
        try:
            if self.serial_handler:
                # Asegurar que la lectura esté activa
                if not hasattr(self.serial_handler, 'reader_thread') or self.serial_handler.reader_thread is None:
                    self.serial_handler.start_reading()
                
                # Enviar comando de calibración
                self.serial_handler.write_data("r")
                self.statusbar.showMessage("Enviando comando de calibración...")
                # El estado se actualizará cuando llegue la respuesta de calibración
        except Exception as e:
            self.statusbar.showMessage(f"Error al calibrar: {str(e)}")
            print(f"Error en calibración: {str(e)}")

    @Slot()
    def handle_calibration_response(self, data):
        """Manejar la respuesta de calibración"""
        if data.startswith("Iniciando calibración"):
            self.statusbar.showMessage("Calibración iniciada...")
            self.btn_cal.setEnabled(False)  # Deshabilitar botón durante calibración
        elif data.startswith("Asegúrese que no hay flujo"):
            self.statusbar.showMessage("IMPORTANTE: Asegúrese que no hay flujo de aire")
        elif data.startswith("Calibrando:"):
            # Mostrar progreso de calibración
            self.statusbar.showMessage(f"Calibrando... {data}")
        elif data.startswith("Calibración completada."):
            self.statusbar.showMessage("Calibración completada - Configurando sistema...")
        elif data.startswith("Desviación estándar:"):
            self.statusbar.showMessage(f"Calibración exitosa - {data}")
        elif data.startswith("Iniciando mediciones..."):
            # Aquí es donde realmente está listo
            self.is_calibrated = True
            self.graph_handler.reset_data()
            self.statusbar.showMessage("Sistema calibrado y listo para iniciar prueba")
            self.update_button_states()
        elif data.startswith("Tiempo(ms),Presion(kPa)"):
            # Headers de datos, ignorar o registrar
            pass
        else:
            self.statusbar.showMessage(f"Dispositivo: {data}")


    @Slot()
    def start_test(self):
        """Iniciar una nueva prueba"""
        
        if not self.is_calibrated:
            self.statusbar.showMessage("Debe calibrar antes de iniciar una prueba")
            return
            
        try:
            self.is_testing = True
            self.update_button_states()
            
            # ORDEN CORRECTO:
            # 1. Preparar el GraphHandler ANTES de enviar comando al hardware
            self.graph_handler.prepare_new_recording()
            
            # 2. Enviar comando al hardware
            if self.serial_handler:
                if not hasattr(self.serial_handler, 'reader_thread') or self.serial_handler.reader_thread is None:
                    self.serial_handler.start_reading()
                
                self.serial_handler.write_data("v")
                self.statusbar.showMessage("Comando de reset enviado, iniciando prueba...")
            
        except Exception as e:
            self.is_testing = False
            self.update_button_states()
            self.statusbar.showMessage(f"Error al iniciar prueba: {str(e)}")
            print(f"Error al iniciar prueba: {str(e)}")

    @Slot()
    def on_test_completed(self, recording_data):
        """Manejar cuando se completa una prueba"""
        try:
            self.is_testing = False
            self.test_counter += 1
            
            # Obtener número de grabación
            if isinstance(recording_data, dict) and 'recording_number' in recording_data:
                recording_number = recording_data['recording_number']
            else:
                recording_number = recording_data
            
            # Obtener estado broncodilatador
            status = self.graph_handler.get_bronchodilator_status(recording_number)
            
            # Crear item en la lista de pruebas
            test_name = f"Prueba {recording_number} [{status}]"
            item = QListWidgetItem(test_name)
            item.setData(Qt.UserRole, recording_number)
            self.list_test.addItem(item)
            
            print(f"Test agregado: {test_name}, recording_number: {recording_number}")
            
            self.statusbar.showMessage(f"Prueba completada - {test_name} agregada a la lista")
            self.update_button_states()
            
            # Detener la lectura serial
            if self.serial_handler:
                self.serial_handler.stop_reading()
                
        except Exception as e:
            self.statusbar.showMessage(f"Error al completar prueba: {str(e)}")
            print(f"Error al completar prueba: {str(e)}")

    @Slot(dict)
    def update_test_list_colors(self, quality_info):
        """
        Actualizar colores y badges de las pruebas según calidad
        
        Args:
            quality_info (dict): Diccionario con claves 'PRE' y/o 'POST', cada una con su info de calidad
        """
        try:
            self.current_quality = quality_info
            
            # Definir colores por grado
            grade_colors = {
                'A': QColor(0, 200, 0),      # Verde
                'B': QColor(150, 200, 0),    # Verde-amarillo
                'C': QColor(255, 165, 0),    # Naranja
                'D': QColor(200, 100, 0)     # Naranja-rojo
            }
            
            # Actualizar cada item en la lista
            for i in range(self.list_test.count()):
                item = self.list_test.item(i)
                recording_number = item.data(Qt.UserRole)
                
                # Obtener estado de esta grabación
                status = self.graph_handler.get_bronchodilator_status(recording_number)
                
                # Obtener info de calidad del grupo correcto
                quality_data = quality_info.get(status)
                
                if not quality_data or quality_data.get('grade') is None:
                    # Sin calidad calculada, mostrar solo status
                    item.setText(f"Prueba {recording_number} [{status}]")
                    item.setForeground(QBrush(QColor(0, 0, 0)))  # Negro por defecto
                    continue
                
                grade = quality_data['grade']
                
                # Verificar si está en sugerencias de eliminación
                is_suggested = False
                if quality_data.get('suggestions'):
                    for suggestion in quality_data['suggestions']:
                        if suggestion['recording_number'] == recording_number:
                            is_suggested = True
                            break
                
                if is_suggested:
                    # Marcar en rojo con asterisco
                    item.setText(f"Prueba {recording_number} [{status}] [{grade}]*")
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                else:
                    # Marcar con badge de grado y color correspondiente
                    item.setText(f"Prueba {recording_number} [{status}] [{grade}]")
                    grade_color = grade_colors.get(grade, QColor(128, 128, 128))
                    item.setForeground(QBrush(grade_color))
            
        except Exception as e:
            print(f"Error actualizando colores de lista: {str(e)}")

    @Slot()
    def on_test_selection_changed(self):
        """Manejar cambio de selección en la lista de pruebas"""
        current_item = self.list_test.currentItem()
        if current_item:
            # Actualizar estado del botón eliminar
            self.update_button_states()
        else:
            # Ninguna prueba seleccionada
            self.update_button_states()

    @Slot()
    def on_test_clicked(self, item):
        """Manejar click en una prueba de la lista"""
        try:
            recording_number = item.data(Qt.UserRole)
            test_name = item.text()
            
            print(f"Prueba seleccionada: {test_name}, recording_number: {recording_number}")
            
            # Activar esta grabación en el GraphHandler
            self.graph_handler.set_active_recording(recording_number)
            
            self.statusbar.showMessage(f"Mostrando: {test_name}")
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al seleccionar prueba: {str(e)}")
            print(f"Error al seleccionar prueba: {str(e)}")

    @Slot()
    def delete_selected_test(self):
        """Eliminar la prueba seleccionada"""
        current_item = self.list_test.currentItem()
        if not current_item:
            self.statusbar.showMessage("No hay prueba seleccionada para eliminar")
            return
            
        try:
            test_name = current_item.text()
            row = self.list_test.row(current_item)
            recording_number = current_item.data(Qt.UserRole)
            
            print(f"Intentando eliminar: {test_name}, recording_number: {recording_number}")
            print(f"Lista actual de grabaciones: {self.graph_handler.get_recording_list()}")
            
            # Eliminar del graph_handler primero
            if hasattr(self.graph_handler, 'delete_recording') and recording_number is not None:
                success = self.graph_handler.delete_recording(recording_number)
                print(f"Eliminación del gráfico: {'exitosa' if success else 'falló'}")
                print(f"Lista después de eliminar: {self.graph_handler.get_recording_list()}")
            
            # Eliminar de la lista visual
            self.list_test.takeItem(row)
            
            # Actualizar estados de botones
            self.update_button_states()
            
            self.statusbar.showMessage(f"Prueba eliminada: {test_name}")
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al eliminar prueba: {str(e)}")
            print(f"Error al eliminar prueba: {str(e)}")

    @Slot()
    def update_port_list(self):
        """Actualizar la lista de puertos seriales disponibles"""
        # Obtener puertos actuales
        ports = self.serial_handler.get_available_ports()
        
        # Si la lista es diferente a la anterior, actualizar el combo box
        if ports != self.available_ports:
            # Guardar el puerto seleccionado actualmente
            current_port = self.serial_list.currentText()
            
            # Actualizar la lista de puertos
            self.serial_list.clear()
            self.serial_list.addItems(ports)
            
            # Intentar mantener el puerto seleccionado si aún existe
            if current_port in ports:
                self.serial_list.setCurrentText(current_port)
            
            # Actualizar la lista de puertos disponibles
            self.available_ports = ports
            
            # Deshabilitar el botón de conexión si no hay puertos
            self.btn_connect.setEnabled(len(ports) > 0 and not self.is_testing)
            
            # Si no hay puertos y estaba conectado, desconectar
            if not ports and self.btn_connect.isChecked():
                self.btn_connect.setChecked(False)
                self.handle_connection()

    @Slot()
    def handle_connection(self):
        """Manejar la conexión/desconexión del puerto serial"""
        if self.btn_connect.isChecked():
            try:
                port = self.serial_list.currentText()
                
                # Crear nueva instancia de SerialHandler
                self.serial_handler = SerialHandler(port=port)
                
                # Reconectar la señal data_received
                try:
                    self.serial_handler.data_received_serial.disconnect(self.data_handler.analisis_input_serial)
                except:
                    pass
                self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
                
                if self.serial_handler.open():
                    self.statusbar.showMessage(f"Conectado a {port} - Debe calibrar antes de iniciar pruebas")
                    self.btn_connect.setText("Desconectar")
                    
                    # Reset del estado de calibración al conectar
                    self.is_calibrated = False
                    self.update_button_states()
                
                else:
                    raise Exception("No se pudo conectar al puerto")
                    
            except Exception as e:
                print(f"Error en conexión: {str(e)}")
                self.statusbar.showMessage(f"Error de conexión: {str(e)}")
                self.btn_connect.setChecked(False)
                self.update_button_states()
        else:
            try:
                if self.serial_handler:
                    self.serial_handler.stop_reading()
                    self.serial_handler.close()
                self.statusbar.showMessage("Desconectado")
                self.btn_connect.setText("Conectar")
                
                # Reset de estados al desconectar
                self.is_calibrated = False
                self.is_testing = False
                self.update_button_states()

            except Exception as e:
                self.statusbar.showMessage(f"Error al desconectar: {str(e)}")


    @Slot(dict)
    def load_data_to_graph(self, data):
        """
        Cargar datos en el gráfico
        
        Args:
            data (dict): Diccionario con los datos cargados
        """
        try:
            # Activar grabación de gráficos
            self.graph_handler.graph_record = True
            
            # Asignar datos directamente a display_data
            self.graph_handler.display_data = {
                't': data['t'].copy(),
                'p': data['p'].copy(),
                'f': data['f'].copy(),
                'v': data['v'].copy()
            }
            
            # Actualizar visualización
            self.graph_handler.update_plots()
            
            # Deshabilitar botones de control serial
            self.is_testing = False
            self.is_calibrated = False
            self.update_button_states()
            
            self.statusbar.showMessage(f"Datos cargados: {len(data['t'])} puntos")
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al cargar datos en el gráfico: {str(e)}")

    @Slot(int)
    def port_selected(self, index):
        """Manejar la selección de un puerto en el combo box"""
        # Si hay un puerto seleccionado y no está probando, habilitar el botón de conexión
        self.btn_connect.setEnabled(index >= 0 and not self.is_testing)
        
        # Si cambia el puerto y estaba conectado, desconectar
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()


    @Slot()
    def save_data(self):
        """Guardar estudio completo con datos del paciente"""
        
        # Verificar que hay datos para guardar
        if not self.graph_handler.stored_recordings:
            self.statusbar.showMessage("No hay grabaciones para guardar")
            return
        
        # Abrir diálogo para solicitar datos
        dialog = SaveDialog(self)
        
        if dialog.exec() != SaveDialog.Accepted:
            return
        
        # Obtener datos del paciente
        patient_data = dialog.get_data()
        
        if not patient_data:
            self.statusbar.showMessage("No se ingresaron datos del paciente")
            return
        
        try:
            # Generar archivo RAW
            self.statusbar.showMessage("Generando archivo de datos...")
            raw_path = self.file_handler.generate_raw_file(
                self.graph_handler,
                patient_data
            )
            
            if not raw_path:
                self.statusbar.showMessage("Error al generar archivo de datos")
                return
            
            # Verificar conectividad
            self.statusbar.showMessage("Verificando conexión a internet...")
            has_internet = self.network_handler.check_connectivity()
            
            if has_internet:
                # Guardar ONLINE
                self.statusbar.showMessage("Subiendo estudio al servidor...")
                
                pdf_generator = PDFGenerator()
                study_data_complete = self.get_study_data_for_pdf()

                # Agregar los datos del paciente y análisis
                study_data_complete['patient'] = patient_data
                study_data_complete['analysis'] = {
                    'interpretacion': patient_data.get('interpretacion', ''),
                    'conclusion': patient_data.get('conclusion', '')
                }
                study_data_complete['timestamp'] = datetime.now().isoformat()

                # Generar PDF
                pdf_path = pdf_generator.generate_pdf(study_data_complete)
                
                # Subir archivos
                response = self.network_handler.upload_files(
                    pdf_path,
                    raw_path,
                    patient_data
                )
                
                # Limpiar archivo temporal PDF
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                
                if response:
                    # Obtener URL de la respuesta
                    # Ajustar según el formato real de respuesta del servidor
                    url = response.get('url', '') or response.get('link', '')
                    
                    if url:
                        # Generar QR
                        qr_pixmap = self.qr_generator.generate_qr_image(url)
                        
                        # Mostrar diálogo con QR
                        qr_dialog = QRDisplayDialog(url, qr_pixmap, self)
                        qr_dialog.exec()
                        
                        self.statusbar.showMessage("¡Estudio guardado exitosamente en línea!")
                    else:
                        self.statusbar.showMessage("Subido pero sin URL de respuesta")
                else:
                    # Si falla, guardar offline como backup
                    self.statusbar.showMessage("Error al subir, guardando offline...")
                    self.file_handler.save_study_offline(raw_path, patient_data)
            
            else:
                # Guardar OFFLINE
                self.statusbar.showMessage("Sin conexión, guardando offline...")
                offline_path = self.file_handler.save_study_offline(raw_path, patient_data)
                
                if offline_path:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "Guardado Offline",
                        f"El estudio se guardó localmente en:\n\n{offline_path}\n\n"
                        f"Podrás subirlo más tarde cuando tengas conexión."
                    )
            
            # Limpiar archivo temporal RAW
            if os.path.exists(raw_path):
                os.remove(raw_path)
                
        except Exception as e:
            self.statusbar.showMessage(f"Error al guardar: {str(e)}")
            print(f"Error en save_data: {str(e)}")

    @Slot()
    def open_file_dialog(self):
        """Abrir diálogo para seleccionar tipo de archivo a abrir"""
        from PySide6.QtWidgets import QFileDialog
        
        # Desconectar del puerto serial si está conectado
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()
        
        # Abrir diálogo genérico que acepta CSV y JSON
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Abrir Archivo",
            os.path.expanduser("~/Documents"),
            "Estudios Completos (*.json);;Archivos CSV Legacy (*.csv);;Todos los archivos (*.*)"
        )
        
        if not file_path:
            return
        
        # Determinar tipo de archivo por extensión
        if file_path.endswith('.json'):
            # Cargar estudio completo
            self.file_handler.open_complete_study(self)
        elif file_path.endswith('.csv'):
            # Cargar CSV legacy
            self.file_handler.open_data_file(self)
        else:
            self.statusbar.showMessage("Formato de archivo no reconocido")

    @Slot(dict)
    def load_complete_study(self, study_data):
        """
        Cargar estudio completo con múltiples grabaciones
        
        Args:
            study_data (dict): Datos completos del estudio
        """
        try:
            # Limpiar estado actual
            self.graph_handler.clear_data()
            self.list_test.clear()
            self.test_counter = 0
            
            # Cargar grabaciones
            recordings = study_data.get('recordings', [])
            line_positions = study_data.get('line_positions', {})
            
            if not recordings:
                self.statusbar.showMessage("El archivo no contiene grabaciones")
                return
            
            # Restaurar grabaciones en el GraphHandler
            self.graph_handler.stored_recordings = recordings
            self.graph_handler.line_positions = {
                int(k): v for k, v in line_positions.items()
            }
            
            # Recrear curvas permanentes
            for recording in recordings:
                self.graph_handler.add_permanent_curve(recording)
                
                # Agregar a la lista de pruebas
                self.test_counter += 1
                rec_num = recording['recording_number']
                status = recording.get('bronchodilator_status', 'PRE')
                test_name = f"Prueba {rec_num} [{status}]"
                
                from PySide6.QtWidgets import QListWidgetItem
                from PySide6.QtCore import Qt
                item = QListWidgetItem(test_name)
                item.setData(Qt.UserRole, rec_num)
                self.list_test.addItem(item)
            
            # Actualizar contador
            self.graph_handler.recording_count = len(recordings)
            
            # Activar primera grabación
            if recordings:
                first_recording = recordings[0]['recording_number']
                self.graph_handler.set_active_recording(first_recording)
                self.list_test.setCurrentRow(0)
            
            # Mostrar información del paciente en statusbar
            patient = study_data.get('patient', {})
            nombre = patient.get('nombre', 'Desconocido')
            rut = patient.get('rut', '')
            
            self.statusbar.showMessage(
                f"Estudio cargado: {nombre} ({rut}) - {len(recordings)} grabaciones"
            )
            
            # Deshabilitar botones de control serial
            self.is_testing = False
            self.is_calibrated = False
            self.update_button_states()
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al cargar estudio: {str(e)}")
            print(f"Error en load_complete_study: {str(e)}")

    @Slot()
    def clear_data(self):
        """Limpiar el puerto serial y los gráficos"""
        if self.serial_handler and not self.is_testing:
            self.serial_handler.write_data("v")
        
        # Limpiar los gráficos
        self.graph_handler.clear_data()
        
        # Limpiar la lista de pruebas
        self.list_test.clear()
        self.test_counter = 0
        
        # Limpiar info de calidad
        self.current_quality = None

    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        # Detener el timer
        self.port_timer.stop()
        
        # Desconectar si es necesario
        if self.btn_connect.isChecked():
            if self.serial_handler:
                self.serial_handler.stop_reading()
                self.serial_handler.close()
            
        # Aceptar el evento de cierre
        event.accept()

    def get_study_data_for_pdf(self):
        """
        Obtener todos los datos del estudio formateados para generación de PDF
        
        Returns:
            dict: Diccionario completo con todos los datos necesarios para el PDF
        """
        # Obtener todas las grabaciones
        recordings = self.graph_handler.get_stored_recordings()
        
        # Separar por tipo
        pre_recordings = [r for r in recordings if r.get('bronchodilator_status') == 'PRE']
        post_recordings = [r for r in recordings if r.get('bronchodilator_status') == 'POST']
        
        # Calcular promedios
        averages_pre = self.graph_handler.calculate_averages('PRE') if pre_recordings else None
        averages_post = self.graph_handler.calculate_averages('POST') if post_recordings else None
        
        # Calcular calidad
        quality_pre = self.graph_handler.calculate_quality('PRE') if len(pre_recordings) >= 2 else None
        quality_post = self.graph_handler.calculate_quality('POST') if len(post_recordings) >= 2 else None
        
        return {
            'recordings': {
                'all': recordings,
                'pre': pre_recordings,
                'post': post_recordings
            },
            'averages': {
                'pre': averages_pre,
                'post': averages_post
            },
            'quality': {
                'pre': quality_pre,
                'post': quality_post
            },
            'line_positions': self.graph_handler.line_positions
        }