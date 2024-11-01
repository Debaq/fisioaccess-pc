from PySide6.QtCore import QObject, Signal, Slot

class SerialDataHandler(QObject):
    # Señal para nuevos datos procesados
    new_data = Signal(dict)
    # Señal para strings no estándar
    other_string = Signal(str)
    
    def __init__(self):
        super().__init__()
    
    @Slot(str)
    def analisis_input_serial(self, data_string):
        """Analizar datos recibidos del puerto serial"""
        print(f"raw {data_string}")
        try:
            
            # Limpiar el string
            data_string = data_string.strip()
            
            # Verificar si es el formato esperado
            values = data_string.split(',')
            
            if len(values) == 4:
                # Convertir valores a float
                t, p, f, v = map(float, values)
                
                # Crear diccionario de datos
                data_dict = {
                    't': t,
                    'p': p,
                    'f': f,
                    'v': v
                }
                
                # Emitir los datos procesados
                self.new_data.emit(data_dict)
            else:
                # Si no es el formato esperado, enviar a otro analizador
                self.analizar_otro_string(data_string)
                
        except Exception as e:
            # Si hay error en el procesamiento, tratar como otro tipo de string
            self.analizar_otro_string(f"Error procesando: {data_string}, {str(e)}")
    
    def analizar_otro_string(self, string):
        """Procesar strings que no coinciden con el formato esperado"""
        print(f"String no estándar recibido: {string}")
        self.other_string.emit(string)