import os
import threading
from pathlib import Path
import flet as ft
from services.page_parser import PageParser
from services.pdf_service import PDFService
from services.page_manager import PageManager
from ui.message_handler import MessageHandler
from ui.interactive_preview import InteractivePreview
from ui.export_options import ExportOptions
from ui.progress_dialog import ProgressDialog, InlineProgressBar
from ui.notification_system import NotificationSystem, CompletionDialog
from ui.credits_dialog import CreditsDialog

class AdvancedPDFExtractorApp:
    """Aplicación avanzada de extracción de PDF con funcionalidades interactivas"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PDF Extractor Advanced"
        
        # Servicios y managers
        self.service: PDFService = None
        self.page_manager = PageManager()
        
        # Componentes UI
        self.msg = MessageHandler(page)
        self.preview = InteractivePreview(page, self._on_page_change)
        self.export_options = ExportOptions(page, self._on_export)
        self.progress_dialog = ProgressDialog(page)
        self.loading_bar = InlineProgressBar(page)
        self.completion_dialog = CompletionDialog(page)
        self.credits_dialog = CreditsDialog(page)
        
        # Estado
        self.current_pdf_path = ""
        self.is_processing = False
        
        self._setup_controls()
        self._setup_layout()
    
    def _setup_controls(self):
        """Configurar controles de la interfaz"""
        # Campo de archivo PDF (solo mostrar nombre)
        self.file_name_text = ft.TextField(
            label="Archivo PDF",
            read_only=True,
            expand=True,
            hint_text="Selecciona un archivo PDF..."
        )
        
        # Campo de páginas
        self.pages_input = ft.TextField(
            label="Páginas (ej: 1,3,5-7)",
            hint_text="Deja vacío para todas las páginas",
            expand=True
        )
        
        # Botones principales
        self.load_button = ft.ElevatedButton(
            "Cargar PDF",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self._load_pdf
        )
        
        self.preview_button = ft.OutlinedButton(
            "Previsualizar",
            icon=ft.Icons.PREVIEW,
            on_click=self._preview_pages,
            disabled=True
        )
        
        self.clear_button = ft.OutlinedButton(
            "Limpiar",
            icon=ft.Icons.CLEAR,
            on_click=self._clear_all
        )
        
        self.credits_button = ft.IconButton(
            icon=ft.Icons.INFO_OUTLINE,
            tooltip="Acerca de",
            on_click=self._show_credits,
            icon_size=20
        )
        
        # Información de estado
        self.status_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_700
        )
        
        # File picker
        self.file_picker = ft.FilePicker(on_result=self._handle_file_selection)
        self.page.overlay.append(self.file_picker)
        
        # Tabs para organizar contenido
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Previsualización",
                    icon=ft.Icons.PREVIEW,
                    content=ft.Container(
                        content=ft.Column([
                            self.preview.get_control()
                        ]),
                        padding=10
                    )
                ),
                ft.Tab(
                    text="Exportación",
                    icon=ft.Icons.DOWNLOAD,
                    content=ft.Container(
                        content=self.export_options.get_control(),
                        padding=10
                    )
                )
            ]
        )
    
    def _setup_layout(self):
        """Configurar el layout de la aplicación"""
        # Header con controles principales
        header = ft.Container(
            content=ft.Column([
                # Título con botón de créditos
                ft.Row([
                    ft.Container(expand=1),  # Espaciador izquierdo
                    ft.Text(
                        "PDF Extractor Advanced",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(
                        content=self.credits_button,
                        expand=1,
                        alignment=ft.alignment.center_right
                    )  # Botón de créditos a la derecha
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                
                # Controles de archivo
                ft.Row([
                    self.file_name_text,
                    self.load_button
                ]),
                
                # Controles de páginas
                ft.Row([
                    self.pages_input,
                    self.preview_button,
                    self.clear_button
                ]),
                
                # Barra de progreso inline
                self.loading_bar.get_control(),
                
                # Estado
                self.status_text,
                
                ft.Divider()
            ]),
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
            border_radius=10,
            margin=10
        )
        
        # Layout principal
        main_layout = ft.Column([
            header,
            ft.Container(
                content=self.tabs,
                expand=True,
                margin=10,
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                border_radius=10
            )
        ], expand=True)
        
        self.page.add(main_layout)
    
    def _load_pdf(self, e):
        """Cargar archivo PDF"""
        self.file_picker.pick_files(
            dialog_title="Seleccionar archivo PDF",
            allowed_extensions=["pdf"],
            allow_multiple=False
        )
    
    def _handle_file_selection(self, e: ft.FilePickerResultEvent):
        """Manejar selección de archivo PDF"""
        if not e.files:
            return
        
        file_path = e.files[0].path
        self._load_pdf_file(file_path)
    
    def _load_pdf_file(self, file_path: str):
        """Cargar archivo PDF específico"""
        try:
            self.loading_bar.show("Cargando PDF...")
            
            # Crear servicio PDF
            self.service = PDFService(file_path)
            self.current_pdf_path = file_path
            
            # Mostrar solo el nombre del archivo
            file_name = Path(file_path).name
            self.file_name_text.value = file_name
            
            # Limpiar estado previo
            self.page_manager.clear()
            self.preview.clear()
            self.export_options.reset()
            
            # Actualizar estado
            total_pages = self.service.get_total_pages()
            self.status_text.value = f"PDF cargado: {total_pages} páginas"
            self.preview_button.disabled = False
            
            # Ocultar barra de carga
            self.loading_bar.hide()
            
            self.msg.show(f"PDF cargado exitosamente ({total_pages} páginas)", ft.Colors.GREEN)
            self.page.update()
            
        except Exception as ex:
            self.loading_bar.hide()
            self.msg.show(f"Error cargando PDF: {ex}", ft.Colors.RED, ft.Icons.ERROR)
            self._reset_state()
    
    def _preview_pages(self, e):
        """Previsualizar páginas seleccionadas"""
        if not self.service:
            self.msg.show("Primero carga un PDF", ft.Colors.RED)
            return
        
        if self.is_processing:
            return
        
        try:
            self.is_processing = True
            self.loading_bar.show("Procesando páginas...")
            
            # Notificación de inicio
            pages_str = self.pages_input.value.strip() or "todas las páginas"
            NotificationSystem.show_start_notification(
                "Previsualización", 
                f"Procesando {pages_str}"
            )
            
            # Parsear páginas
            pages_str = self.pages_input.value.strip()
            if not pages_str:
                # Si no hay páginas especificadas, usar todas
                pages = list(range(1, self.service.get_total_pages() + 1))
            else:
                pages = PageParser.parse(pages_str)
            
            # Limpiar manager previo
            self.page_manager.clear()
            
            # Procesar páginas en hilo separado para no bloquear UI
            def process_pages():
                try:
                    total = len(pages)
                    for i, page_num in enumerate(pages):
                        self.loading_bar.update_progress(i, total, f"Renderizando página {page_num}")
                        
                        if page_num <= self.service.get_total_pages():
                            img = self.service.render_page(page_num)
                            if img:
                                self.page_manager.add_page(page_num, img)
                    
                    # Actualizar preview en hilo principal
                    def update_ui():
                        self.preview.render_pages(self.page_manager)
                        self.export_options.enable_export(self.page_manager.get_selected_pages_count() > 0)
                        self.status_text.value = f"Páginas seleccionadas: {self.page_manager.get_selected_pages_count()}"
                        self.loading_bar.hide()
                        self.is_processing = False
                        self.tabs.selected_index = 0  # Cambiar a tab de previsualización
                        self.page.update()
                    
                    self.page.add(ft.Container())  # Trigger para ejecutar update_ui
                    update_ui()
                    
                except Exception as ex:
                    def show_error():
                        self.loading_bar.hide()
                        self.msg.show(f"Error en previsualización: {ex}", ft.Colors.RED)
                        self.is_processing = False
                        self.page.update()
                    
                    show_error()
            
            # Ejecutar en hilo separado
            threading.Thread(target=process_pages, daemon=True).start()
            
        except Exception as ex:
            self.loading_bar.hide()
            self.is_processing = False
            self.msg.show(f"Error parseando páginas: {ex}", ft.Colors.RED)
    
    def _on_page_change(self, message: str):
        """Callback para cambios en páginas"""
        self.msg.show(message, ft.Colors.BLUE)
        self.status_text.value = f"Páginas seleccionadas: {self.page_manager.get_selected_pages_count()}"
        self.export_options.enable_export(self.page_manager.get_selected_pages_count() > 0)
        self.page.update()
    
    def _on_export(self, export_config: dict):
        """Manejar exportación"""
        if not self.service or self.page_manager.get_selected_pages_count() == 0:
            self.msg.show("No hay páginas para exportar", ft.Colors.RED)
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        export_format = export_config['format']
        output_path = export_config['output_path']
        image_format = export_config.get('image_format', 'PNG')
        
        # Mostrar progreso tanto inline como en diálogo para máxima visibilidad
        self.loading_bar.show(f"Exportando ({export_format})...")
        self.progress_dialog.show(f"Exportando ({export_format})...")
        
        # Notificación de inicio de exportación
        format_names = {
            "pdf_combined": "PDF único",
            "pdf_individual": "PDFs individuales",
            "images_zip": f"Imágenes {image_format} (ZIP)",
            "images_folder": f"Imágenes {image_format} (Carpeta)"
        }
        format_display = format_names.get(export_format, export_format)
        NotificationSystem.show_start_notification(
            "Exportación",
            f"Generando {format_display}"
        )
        
        def progress_callback(current, total, status):
            try:
                # Actualizar ambas barras de progreso
                self.loading_bar.update_progress(current, total, status)
                dialog_success = self.progress_dialog.update_progress(current, total, status)
                return dialog_success  # Si el diálogo fue cancelado, detener
            except Exception as e:
                print(f"Error en callback de progreso: {e}")
                return False
        
        def export_worker():
            try:
                success = False
                
                if export_format == "pdf_combined":
                    success = self.service.export_combined_pdf(
                        self.page_manager, output_path, progress_callback
                    )
                elif export_format == "pdf_individual":
                    success = self.service.export_individual_pdfs(
                        self.page_manager, output_path, progress_callback
                    )
                elif export_format == "images_zip":
                    success = self.service.export_as_images_zip(
                        self.page_manager, output_path, image_format, progress_callback
                    )
                elif export_format == "images_folder":
                    success = self.service.export_as_images_folder(
                        self.page_manager, output_path, image_format, progress_callback
                    )
                
                def finish_export():
                    # Ocultar ambos indicadores de progreso
                    self.loading_bar.hide()
                    self.progress_dialog.hide()
                    self.is_processing = False
                    
                    if success:
                        # Calcular número de archivos según el formato
                        active_pages = self.page_manager.get_active_pages()
                        count = len(active_pages)
                        
                        # Mensaje de éxito en la interfaz
                        self.msg.show(f"Exportación completada: {Path(output_path).name}", ft.Colors.GREEN)
                        
                        # Notificación del sistema
                        NotificationSystem.show_completion_notification(
                            "Exportación", 
                            output_path, 
                            count if export_format in ["pdf_individual", "images_folder"] else 0
                        )
                        
                        # Diálogo de completación con opción de abrir carpeta
                        self.completion_dialog.show_completion_dialog(
                            "Exportación",
                            output_path,
                            count if export_format in ["pdf_individual", "images_folder"] else 0
                        )
                        
                        # Limpiar path de salida para evitar corrupción en futuras exportaciones
                        self.export_options.clear_output_path()
                    else:
                        # Notificación de error
                        error_msg = "No se pudieron exportar los archivos"
                        self.msg.show("Error en la exportación", ft.Colors.RED)
                        NotificationSystem.show_error_notification("Exportación", error_msg)
                    
                    self.page.update()
                
                finish_export()
                
            except Exception as ex:
                def show_error():
                    # Ocultar ambos indicadores de progreso
                    self.loading_bar.hide()
                    self.progress_dialog.hide()
                    self.is_processing = False
                    error_msg = f"Error durante la exportación: {str(ex)[:50]}..."
                    self.msg.show(f"Error exportando: {ex}", ft.Colors.RED)
                    NotificationSystem.show_error_notification("Exportación", error_msg)
                    self.page.update()
                
                show_error()
        
        # Ejecutar exportación en hilo separado
        threading.Thread(target=export_worker, daemon=True).start()
    
    def _clear_all(self, e):
        """Limpiar todo"""
        self._reset_state()
        self.msg.show("Aplicación reiniciada", ft.Colors.BLUE)
    
    def _show_credits(self, e):
        """Mostrar diálogo de créditos"""
        self.credits_dialog.show_credits()
    
    def _reset_state(self):
        """Resetear estado de la aplicación"""
        self.service = None
        self.current_pdf_path = ""
        self.is_processing = False
        
        self.file_name_text.value = ""
        self.pages_input.value = ""
        self.status_text.value = ""
        self.preview_button.disabled = True
        
        self.page_manager.clear()
        self.preview.clear()
        self.export_options.reset()
        self.loading_bar.hide()
        
        self.tabs.selected_index = 0
        self.page.update()
