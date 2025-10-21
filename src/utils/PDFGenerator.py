from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from PySide6.QtCore import QObject, Signal
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import tempfile
import os
from datetime import datetime


class PDFGenerator(QObject):
    """Generador de reportes PDF para espirometría"""
    
    # Señales
    pdf_generated = Signal(str)  # Emite la ruta del PDF generado
    error_occurred = Signal(str)  # Emite mensaje de error
    
    def __init__(self):
        super().__init__()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para sección
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=6,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_JUSTIFY
        ))
        
        # Estilo para datos del paciente
        self.styles.add(ParagraphStyle(
            name='PatientData',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            leftIndent=0
        ))
    
    def generate_graph_from_data(self, recordings, graph_type='vt'):
        """
        Generar gráfico desde datos de grabaciones usando matplotlib
        
        Args:
            recordings: Lista de grabaciones a graficar
            graph_type: 'vt' para Volumen vs Tiempo, 'fv' para Flujo vs Volumen
            
        Returns:
            str: Ruta del archivo temporal de imagen
        """
        try:
            # Crear figura
            fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
            
            # Colores para las curvas
            colors_list = ['b', 'r', 'g', 'm', 'c', 'y', 'orange', 'purple', 'brown']
            
            # Graficar cada grabación
            for idx, recording in enumerate(recordings):
                data = recording['data']
                rec_num = recording['recording_number']
                color = colors_list[idx % len(colors_list)]
                
                if graph_type == 'vt':
                    # Volumen vs Tiempo
                    ax.plot(data['t'], data['v'], 
                           color=color, 
                           linewidth=2, 
                           label=f'Prueba {rec_num}')
                    ax.set_xlabel('Tiempo (s)', fontsize=11)
                    ax.set_ylabel('Volumen (L)', fontsize=11)
                    ax.set_xlim(0, 17)
                    ax.set_ylim(-4, 6)
                    
                elif graph_type == 'fv':
                    # Flujo vs Volumen
                    ax.plot(data['v'], data['f'], 
                           color=color, 
                           linewidth=2, 
                           label=f'Prueba {rec_num}')
                    ax.set_xlabel('Volumen (L)', fontsize=11)
                    ax.set_ylabel('Flujo (L/s)', fontsize=11)
                    ax.set_xlim(-1, 8)
                    ax.set_ylim(-10, 10)
            
            # Configurar grilla y leyenda
            ax.grid(True, alpha=0.3)
            if len(recordings) > 1:
                ax.legend(fontsize=8, loc='best')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar en archivo temporal
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.png',
                delete=False
            )
            temp_file.close()
            
            plt.savefig(temp_file.name, bbox_inches='tight', dpi=150)
            plt.close(fig)
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generando gráfico: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def export_graph_to_image(self, graph_widget, width=800, height=400):
        """
        Método legacy mantenido por compatibilidad
        DEPRECADO: Usar generate_graph_from_data en su lugar
        """
        print("Warning: export_graph_to_image está deprecado")
        return None
    
    def create_patient_info_table(self, patient_data):
        """
        Crear tabla con información del paciente
        
        Args:
            patient_data: Diccionario con datos del paciente
            
        Returns:
            Table: Tabla de ReportLab
        """
        data = [
            ['Datos del Paciente', 'Datos Antropométricos'],
            [
                f"Nombre: {patient_data.get('nombre', 'N/A')}",
                f"Estatura: {patient_data.get('estatura_cm', 'N/A')} cm"
            ],
            [
                f"RUT: {patient_data.get('rut', 'N/A')}",
                f"Peso: {patient_data.get('peso_kg', 'N/A')} kg"
            ],
            [
                f"Sexo: {patient_data.get('sexo', 'N/A')}",
                ''
            ],
            [
                f"F. Nacimiento: {patient_data.get('fecha_nacimiento', 'N/A')}",
                ''
            ],
            [
                f"Edad: {patient_data.get('edad', 'N/A')} años",
                ''
            ],
            [
                f"Etnia: {patient_data.get('etnia', 'N/A')}",
                ''
            ]
        ]
        
        table = Table(data, colWidths=[9*cm, 9*cm])
        table.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Cuerpo
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        return table
    
    def create_results_table(self, averages_pre, averages_post):
        """
        Crear tabla de resultados con métricas PRE, POST y % cambio
        
        Args:
            averages_pre: Diccionario con promedios PRE
            averages_post: Diccionario con promedios POST
            
        Returns:
            Table: Tabla de ReportLab
        """
        # Encabezados
        data = [
            ['Parámetro', 'PRE-Broncodilatador', 'POST-Broncodilatador', '% Cambio']
        ]
        
        # Definir métricas a mostrar
        metrics = [
            ('FEV1 (L)', 'fev1', 3),
            ('FVC (L)', 'fvc', 3),
            ('FEV1/FVC (%)', 'fev1_fvc_ratio', 1),
            ('PEF (L/s)', 'pef', 3),
            ('FEF25 (L/s)', 'fef25', 3),
            ('FEF50 (L/s)', 'fef50', 3),
            ('FEF75 (L/s)', 'fef75', 3),
            ('FIF25 (L/s)', 'fif25', 3),
            ('FIF50 (L/s)', 'fif50', 3),
            ('FIF75 (L/s)', 'fif75', 3),
        ]
        
        for metric_name, metric_key, decimals in metrics:
            pre_val = averages_pre.get(metric_key) if averages_pre else None
            post_val = averages_post.get(metric_key) if averages_post else None
            
            # Formatear valores
            if pre_val is not None:
                pre_str = f"{pre_val:.{decimals}f}"
            else:
                pre_str = 'N/A'
            
            if post_val is not None:
                post_str = f"{post_val:.{decimals}f}"
            else:
                post_str = 'N/A'
            
            # Calcular % cambio
            if pre_val is not None and post_val is not None and pre_val != 0:
                change = ((post_val - pre_val) / pre_val) * 100
                change_str = f"{change:+.1f}%"
            else:
                change_str = 'N/A'
            
            data.append([metric_name, pre_str, post_str, change_str])
        
        table = Table(data, colWidths=[4*cm, 4*cm, 4*cm, 3*cm])
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Primera columna (nombres)
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            
            # Columnas de datos
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 9),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return table
    
    def generate_pdf(self, study_data, output_path=None):
        """
        Generar PDF completo del estudio de espirometría
        
        Args:
            study_data: Diccionario con todos los datos del estudio
                Debe incluir:
                - patient: datos del paciente
                - recordings: lista de grabaciones con 'all', 'pre', 'post'
                - averages: promedios 'pre' y 'post'
                - quality: calidad 'pre' y 'post'
                - analysis: interpretación y conclusión
            output_path: Ruta donde guardar el PDF (si es None, crea uno temporal)
            
        Returns:
            str: Ruta del PDF generado, o None si hay error
        """
        try:
            # Crear archivo de salida
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix='.pdf',
                    delete=False
                )
                output_path = temp_file.name
                temp_file.close()
            
            # Crear documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Elementos del documento
            elements = []
            
            # TÍTULO PRINCIPAL
            title = Paragraph(
                "REPORTE DE ESPIROMETRÍA",
                self.styles['CustomTitle']
            )
            elements.append(title)
            elements.append(Spacer(1, 0.3*cm))
            
            # Fecha del estudio
            timestamp = study_data.get('timestamp', datetime.now().isoformat())
            try:
                date_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')
            except:
                date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            date_para = Paragraph(
                f"Fecha del estudio: {date_str}",
                self.styles['CustomNormal']
            )
            elements.append(date_para)
            elements.append(Spacer(1, 0.5*cm))
            
            # SECCIÓN 1 - INFORMACIÓN DEL PACIENTE
            patient_table = self.create_patient_info_table(study_data.get('patient', {}))
            elements.append(patient_table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Obtener datos de recordings, promedios y calidad
            recordings = study_data.get('recordings', {})
            pre_recordings = recordings.get('pre', [])
            post_recordings = recordings.get('post', [])
            
            averages = study_data.get('averages', {})
            averages_pre = averages.get('pre')
            averages_post = averages.get('post')
            
            quality = study_data.get('quality', {})
            quality_pre = quality.get('pre')
            quality_post = quality.get('post')
            
            # Limpiar archivos temporales al final
            temp_images = []
            
            # SECCIÓN 2 - GRÁFICOS PRE-BRONCODILATADOR
            if pre_recordings:
                elements.append(Paragraph(
                    "PRE - Broncodilatador",
                    self.styles['CustomSubtitle']
                ))
                elements.append(Spacer(1, 0.3*cm))
                
                # Generar gráficos PRE
                graph_row = []
                
                # V/t
                img_path_vt = self.generate_graph_from_data(pre_recordings, 'vt')
                if img_path_vt:
                    temp_images.append(img_path_vt)
                    img = Image(img_path_vt, width=8*cm, height=5*cm)
                    graph_row.append(img)
                
                # F/V
                img_path_fv = self.generate_graph_from_data(pre_recordings, 'fv')
                if img_path_fv:
                    temp_images.append(img_path_fv)
                    img = Image(img_path_fv, width=8*cm, height=5*cm)
                    graph_row.append(img)
                
                if graph_row:
                    graph_table = Table([graph_row], colWidths=[9*cm, 9*cm])
                    graph_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    elements.append(graph_table)
                    elements.append(Spacer(1, 0.5*cm))
            
            # SECCIÓN 3 - GRÁFICOS POST-BRONCODILATADOR
            if post_recordings:
                elements.append(Paragraph(
                    "POST - Broncodilatador",
                    self.styles['CustomSubtitle']
                ))
                elements.append(Spacer(1, 0.3*cm))
                
                # Generar gráficos POST
                graph_row = []
                
                # V/t
                img_path_vt = self.generate_graph_from_data(post_recordings, 'vt')
                if img_path_vt:
                    temp_images.append(img_path_vt)
                    img = Image(img_path_vt, width=8*cm, height=5*cm)
                    graph_row.append(img)
                
                # F/V
                img_path_fv = self.generate_graph_from_data(post_recordings, 'fv')
                if img_path_fv:
                    temp_images.append(img_path_fv)
                    img = Image(img_path_fv, width=8*cm, height=5*cm)
                    graph_row.append(img)
                
                if graph_row:
                    graph_table = Table([graph_row], colWidths=[9*cm, 9*cm])
                    graph_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    elements.append(graph_table)
                    elements.append(Spacer(1, 0.5*cm))
            
            # SECCIÓN 4 - RESULTADOS
            elements.append(Paragraph(
                "Resultados",
                self.styles['SectionTitle']
            ))
            elements.append(Spacer(1, 0.2*cm))
            
            # Tabla de resultados
            results_table = self.create_results_table(averages_pre, averages_post)
            elements.append(results_table)
            elements.append(Spacer(1, 0.3*cm))
            
            # SECCIÓN 5 - CALIDAD
            quality_text = "Calidad: "
            if quality_pre and quality_pre.get('grade'):
                quality_text += f"PRE: {quality_pre['grade']}"
                if quality_pre.get('repeatability_ml'):
                    quality_text += f" (Rep: {quality_pre['repeatability_ml']:.0f} ml)"
            
            if quality_post and quality_post.get('grade'):
                if quality_pre and quality_pre.get('grade'):
                    quality_text += " | "
                quality_text += f"POST: {quality_post['grade']}"
                if quality_post.get('repeatability_ml'):
                    quality_text += f" (Rep: {quality_post['repeatability_ml']:.0f} ml)"
            
            if quality_text != "Calidad: ":
                quality_para = Paragraph(quality_text, self.styles['CustomNormal'])
                elements.append(quality_para)
                elements.append(Spacer(1, 0.5*cm))
            
            # SECCIÓN 6 - INTERPRETACIÓN
            analysis = study_data.get('analysis', {})
            interpretacion = analysis.get('interpretacion', '')
            
            if interpretacion:
                elements.append(Paragraph(
                    "Interpretación",
                    self.styles['SectionTitle']
                ))
                elements.append(Spacer(1, 0.2*cm))
                
                interp_para = Paragraph(interpretacion, self.styles['CustomNormal'])
                elements.append(interp_para)
                elements.append(Spacer(1, 0.4*cm))
            
            # SECCIÓN 7 - CONCLUSIÓN
            conclusion = analysis.get('conclusion', '')
            
            if conclusion:
                elements.append(Paragraph(
                    "Conclusión",
                    self.styles['SectionTitle']
                ))
                elements.append(Spacer(1, 0.2*cm))
                
                concl_para = Paragraph(conclusion, self.styles['CustomNormal'])
                elements.append(concl_para)
            
            # Generar PDF
            doc.build(elements)
            
            # Limpiar archivos temporales de imágenes
            for temp_img in temp_images:
                try:
                    if os.path.exists(temp_img):
                        os.remove(temp_img)
                except:
                    pass
            
            self.pdf_generated.emit(output_path)
            return output_path
            
        except Exception as e:
            error_msg = f"Error generando PDF: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            return None