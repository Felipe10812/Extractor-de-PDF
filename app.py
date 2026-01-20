import os
import threading
from pathlib import Path
from typing import List
import flet as ft
from services.page_parser import PageParser
from services.pdf_service import PDFService
from services.pdf_merger_service import PDFMergerService
from services.image_service import ImageService
from services.page_manager import PageManager
from ui.message_handler import MessageHandler
from ui.interactive_preview import InteractivePreview
from ui.export_options import ExportOptions
from ui.progress_dialog import ProgressDialog, InlineProgressBar
from ui.notification_system import NotificationSystem, CompletionDialog
from ui.credits_dialog import CreditsDialog
from ui.image_adjustment_controls import ImageAdjustmentControls

class AdvancedPDFExtractorApp:
    """Aplicación avanzada de extracción de PDF con funcionalidades interactivas"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PDF & Image Converter"
        
        # Servicios y managers
        self.service = None  # Puede ser PDFService, PDFMergerService o ImageService
        self.page_manager = PageManager()
        self.current_mode = "pdf"  # "pdf", "merge_pdfs" o "images"
        
        # Componentes UI
        self.msg = MessageHandler(page)
        self.preview = InteractivePreview(page, self._on_page_change)
        self.export_options = ExportOptions(page, self._on_export)
        self.progress_dialog = ProgressDialog(page)
        self.loading_bar = InlineProgressBar(page)
        self.completion_dialog = CompletionDialog(page)
        self.credits_dialog = CreditsDialog(page)
        self.image_adjustment = ImageAdjustmentControls(page)
        
        # Estado
        self.current_file_paths = []  # Lista de archivos cargados
        self.is_processing = False
        
        self._setup_controls()
        self._setup_layout()
        
        # Configurar callbacks para controles de ajuste de imágenes
        self.image_adjustment.set_preview_callback(self._show_pdf_preview)
        self.image_adjustment.set_settings_change_callback(self._on_pdf_settings_change)
    
    def _setup_controls(self):
        """Configurar controles de la interfaz"""
        
        # Selector de modo
        self.mode_selector = ft.SegmentedButton(
            selected={"pdf"},
            allow_empty_selection=False,
            allow_multiple_selection=False,
            segments=[
                ft.Segment(
                    value="pdf",
                    label=ft.Text("Extraer de PDF"),
                    icon=ft.Icon(ft.Icons.PICTURE_AS_PDF)
                ),
                ft.Segment(
                    value="merge_pdfs",
                    label=ft.Text("Unir PDFs"),
                    icon=ft.Icon(ft.Icons.MERGE_TYPE)
                ),
                ft.Segment(
                    value="images", 
                    label=ft.Text("Convertir imágenes a PDF"),
                    icon=ft.Icon(ft.Icons.IMAGE)
                )
            ],
            on_change=self._on_mode_change
        )
        
        # Campo de archivo (dinámico según el modo)
        self.file_name_text = ft.TextField(
            label="Archivo PDF",
            read_only=True,
            expand=True,
            hint_text="Selecciona un archivo PDF..."
        )
        
        # Campo de páginas/imágenes
        self.pages_input = ft.TextField(
            label="Páginas (ej: 1,3,5-7)",
            hint_text="Deja vacío para todas las páginas",
            expand=True
        )
        
        # Botones principales
        self.load_button = ft.ElevatedButton(
            "Cargar PDF",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self._load_files
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
                            self.image_adjustment.get_control(),  # Controles de ajuste PDF
                            self.preview.get_control()
                        ], spacing=10),
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
                        "PDF & Image Converter",
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
                
                # Selector de modo
                ft.Container(
                    content=ft.Column([
                        ft.Text("Selecciona el tipo de operación:", weight=ft.FontWeight.BOLD, size=14),
                        self.mode_selector
                    ]),
                    margin=ft.margin.only(bottom=10)
                ),
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
    
    def _on_mode_change(self, e):
        """Manejar cambio de modo"""
        if not e.control.selected:
            return
        
        new_mode = list(e.control.selected)[0]
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            self._update_ui_for_mode()
            self._reset_state()
    
    def _update_ui_for_mode(self):
        """Actualizar la interfaz según el modo seleccionado"""
        if self.current_mode == "pdf":
            self.file_name_text.label = "Archivo PDF"
            self.file_name_text.hint_text = "Selecciona un archivo PDF..."
            self.load_button.text = "Cargar PDF"
            self.load_button.icon = ft.Icons.UPLOAD_FILE
            self.pages_input.label = "Páginas (ej: 1,3,5-7)"
            self.pages_input.hint_text = "Deja vacío para todas las páginas"
        elif self.current_mode == "merge_pdfs":
            self.file_name_text.label = "Archivos PDF"
            self.file_name_text.hint_text = "Selecciona múltiples archivos PDF..."
            self.load_button.text = "Cargar PDFs"
            self.load_button.icon = ft.Icons.UPLOAD_FILE
            self.pages_input.label = "Páginas (ej: 1,3,5-7)"
            self.pages_input.hint_text = "Deja vacío para todas las páginas"
        else:  # images
            self.file_name_text.label = "Imágenes seleccionadas"
            self.file_name_text.hint_text = "Selecciona múltiples imágenes..."
            self.load_button.text = "Cargar imágenes"
            self.load_button.icon = ft.Icons.IMAGE
            self.pages_input.label = "Imágenes (ej: 1,3,5-7)"
            self.pages_input.hint_text = "Deja vacío para todas las imágenes"
        
        # Actualizar el modo en los componentes
        self.export_options.set_mode(self.current_mode)
        
        # Mostrar/ocultar controles de ajuste de imagen según el modo
        if self.current_mode == "images":
            self.image_adjustment.show(True)
        else:
            self.image_adjustment.show(False)
        
        self.page.update()
    
    def _load_files(self, e):
        """Cargar archivos según el modo"""
        if self.current_mode == "pdf":
            self.file_picker.pick_files(
                dialog_title="Seleccionar archivo PDF",
                allowed_extensions=["pdf"],
                allow_multiple=False
            )
        elif self.current_mode == "merge_pdfs":
            self.file_picker.pick_files(
                dialog_title="Seleccionar archivos PDF para unir",
                allowed_extensions=["pdf"],
                allow_multiple=True
            )
        else:  # images
            self.file_picker.pick_files(
                dialog_title="Seleccionar imágenes",
                allowed_extensions=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
                allow_multiple=True
            )
    
    def _handle_file_selection(self, e: ft.FilePickerResultEvent):
        """Manejar selección de archivos"""
        if not e.files:
            return
        
        if self.current_mode == "pdf":
            file_path = e.files[0].path
            self._load_pdf_file(file_path)
        elif self.current_mode == "merge_pdfs":
            file_paths = [f.path for f in e.files]
            self._load_merge_pdf_files(file_paths)
        else:  # images
            file_paths = [f.path for f in e.files]
            self._load_image_files(file_paths)
    
    def _load_pdf_file(self, file_path: str):
        """Cargar archivo PDF específico"""
        try:
            self.loading_bar.show("Cargando PDF...")
            
            # Crear servicio PDF
            self.service = PDFService(file_path)
            self.current_file_paths = [file_path]
            
            # Mostrar solo el nombre del archivo
            file_name = Path(file_path).name
            self.file_name_text.value = file_name

            # CRÍTICO: Pasar el nombre base al módulo de exportación para sugerencias
            base_name = Path(file_path).stem
            self.export_options.set_base_filename(base_name)
            
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
    
    def _load_merge_pdf_files(self, file_paths: List[str]):
        """Cargar múltiples archivos PDF para unir"""
        try:
            self.loading_bar.show("Cargando PDFs...")
            
            # Crear servicio de merger de PDFs
            self.service = PDFMergerService(file_paths)
            self.current_file_paths = file_paths
            
            # Mostrar información de PDFs cargados
            total_pdfs = self.service.get_pdf_count()
            total_pages = self.service.get_total_pages()
            
            if total_pdfs == 1:
                self.file_name_text.value = Path(file_paths[0]).name
            else:
                self.file_name_text.value = f"{total_pdfs} archivos PDF seleccionados"
            
            # Usar nombre descriptivo para la base
            base_name = f"merged_{total_pdfs}_pdfs"
            if file_paths:
                first_name = Path(file_paths[0]).stem
                base_name = f"{first_name}_y_{total_pdfs-1}_mas" if total_pdfs > 1 else first_name
            
            self.export_options.set_base_filename(base_name)
            
            # Limpiar estado previo
            self.page_manager.clear()
            self.preview.clear()
            self.export_options.reset()
            
            # Actualizar estado
            self.status_text.value = f"{total_pdfs} PDFs cargados: {total_pages} páginas totales"
            self.preview_button.disabled = False
            
            # Ocultar barra de carga
            self.loading_bar.hide()
            
            self.msg.show(f"PDFs cargados exitosamente ({total_pdfs} archivos, {total_pages} páginas)", ft.Colors.GREEN)
            self.page.update()
            
        except Exception as ex:
            self.loading_bar.hide()
            self.msg.show(f"Error cargando PDFs: {ex}", ft.Colors.RED, ft.Icons.ERROR)
            self._reset_state()
    
    def _load_image_files(self, file_paths: List[str]):
        """Cargar múltiples archivos de imagen"""
        try:
            self.loading_bar.show("Cargando imágenes...")
            
            # Crear servicio de imágenes
            self.service = ImageService(file_paths)
            self.current_file_paths = file_paths
            
            # Mostrar información de imágenes cargadas
            total_images = len(file_paths)
            if total_images == 1:
                self.file_name_text.value = Path(file_paths[0]).name
            else:
                self.file_name_text.value = f"{total_images} imágenes seleccionadas"
            
            # Usar el nombre de la primera imagen como base
            base_name = f"imagenes_{len(file_paths)}_items"
            if file_paths:
                first_name = Path(file_paths[0]).stem
                base_name = f"{first_name}_y_{len(file_paths)-1}_mas" if len(file_paths) > 1 else first_name
            
            self.export_options.set_base_filename(base_name)
            
            # Limpiar estado previo
            self.page_manager.clear()
            self.preview.clear()
            self.export_options.reset()
            self.image_adjustment.reset()
            
            # Actualizar estado
            valid_images = self.service.get_total_pages()
            self.status_text.value = f"Imágenes cargadas: {valid_images} válidas de {total_images} seleccionadas"
            self.preview_button.disabled = False
            
            # Habilitar controles de ajuste de imagen si estamos en modo imágenes
            if self.current_mode == "images":
                self.image_adjustment.show(True)
            
            # Ocultar barra de carga
            self.loading_bar.hide()
            
            self.msg.show(f"Imágenes cargadas exitosamente ({valid_images} válidas)", ft.Colors.GREEN)
            self.page.update()
            
        except Exception as ex:
            self.loading_bar.hide()
            self.msg.show(f"Error cargando imágenes: {ex}", ft.Colors.RED, ft.Icons.ERROR)
            self._reset_state()
    
    def _preview_pages(self, e):
        """Previsualizar páginas/imágenes seleccionadas"""
        if not self.service:
            self.msg.show(f"Primero carga {'un PDF' if self.current_mode == 'pdf' else 'imágenes'}", ft.Colors.RED)
            return
        
        if self.is_processing:
            return
        
        try:
            self.is_processing = True
            self.loading_bar.show("Procesando páginas...")
            
            # Notificación de inicio
            pages_str = self.pages_input.value.strip() or ("todas las páginas" if self.current_mode == "pdf" else "todas las imágenes")
            NotificationSystem.show_start_notification(
                "Previsualización", 
                f"Procesando {pages_str}"
            )
            
            # Parsear páginas/imágenes
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
                        item_type = "página" if self.current_mode in ["pdf", "merge_pdfs"] else "imagen"
                        self.loading_bar.update_progress(i, total, f"Renderizando {item_type} {page_num}")
                        
                        if page_num <= self.service.get_total_pages():
                            img = self.service.render_page(page_num)
                            if img:
                                # Para modo merge_pdfs, agregar metadata de origen
                                if self.current_mode == "merge_pdfs" and isinstance(self.service, PDFMergerService):
                                    pdf_info, local_page = self.service._find_pdf_for_page(page_num)
                                    if pdf_info:
                                        self.page_manager.add_page(
                                            page_num, img, 
                                            source_pdf=pdf_info.name,
                                            source_pdf_index=pdf_info.index,
                                            original_page_number=local_page
                                        )
                                else:
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
            item_type = "páginas" if self.current_mode in ["pdf", "merge_pdfs"] else "imágenes"
            self.msg.show(f"No hay {item_type} para exportar", ft.Colors.RED)
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
            "pdf_individual_zip": "PDFs individuales (ZIP)",
            "pdf_individual_folder": "PDFs individuales (Carpeta)",
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
                    if self.current_mode == "merge_pdfs":
                        # Unión de múltiples PDFs
                        success = self.service.export_combined_pdf(
                            self.page_manager, output_path, progress_callback
                        )
                    elif self.current_mode == "images":
                        # Conversión de imágenes a PDF usando configuraciones de ajuste
                        settings = self.image_adjustment.get_settings()
                        success = self.service.convert_to_pdf(
                            self.page_manager, output_path, settings['page_size'], 
                            settings['orientation'], settings['fit_mode'], progress_callback
                        )
                    else:
                        # Extracción de PDF
                        success = self.service.export_combined_pdf(
                            self.page_manager, output_path, progress_callback
                        )
                elif export_format == "pdf_individual":
                    success = self.service.export_individual_pdfs(
                        self.page_manager, output_path, progress_callback
                    )
                elif export_format == "pdf_individual_zip":
                    if self.current_mode == "images":
                        # Conversión de imágenes a PDFs individuales en ZIP usando configuraciones
                        settings = self.image_adjustment.get_settings()
                        success = self.service.convert_to_individual_pdfs_zip(
                            self.page_manager, output_path, settings['page_size'], 
                            settings['orientation'], settings['fit_mode'], progress_callback
                        )
                    else:
                        # No implementado para modo PDF
                        success = False
                elif export_format == "pdf_individual_folder":
                    if self.current_mode == "images":
                        # Conversión de imágenes a PDFs individuales en carpeta usando configuraciones
                        settings = self.image_adjustment.get_settings()
                        success = self.service.convert_to_individual_pdfs_folder(
                            self.page_manager, output_path, settings['page_size'],
                            settings['orientation'], settings['fit_mode'], progress_callback
                        )
                    else:
                        # No implementado para modo PDF
                        success = False
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
                            count if export_format in ["pdf_individual", "pdf_individual_zip", "pdf_individual_folder", "images_folder"] else 0
                        )
                        
                        # Diálogo de completación con opción de abrir carpeta
                        self.completion_dialog.show_completion_dialog(
                            "Exportación",
                            output_path,
                            count if export_format in ["pdf_individual", "pdf_individual_zip", "pdf_individual_folder", "images_folder"] else 0
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
    
    def _refresh_pdf_preview(self):
        """Actualizar previsualización PDF"""
        if not self.service or self.current_mode != "images":
            return
        
        if self.page_manager.get_selected_pages_count() == 0:
            self.msg.show("No hay imágenes seleccionadas para previsualizar", ft.Colors.RED)
            return
        
        # Obtener configuración actual de exportación
        page_size = self.export_options.pdf_page_size.value
        orientation = self.export_options.pdf_orientation.value
        fit_mode = self.export_options.pdf_fit_mode.value
        
        # Actualizar información de configuración
        image_count = self.page_manager.get_selected_pages_count()
        self.pdf_preview.update_settings_info(page_size, orientation, fit_mode, image_count)
        
        def preview_worker():
            try:
                # Mostrar indicador de carga
                original_content = self.pdf_preview.show_loading()
                
                # Generar previsualización
                preview_images = self.service.preview_pdf_pages(
                    self.page_manager, page_size, orientation, fit_mode
                )
                
                # Actualizar UI en hilo principal
                def update_preview():
                    # Restaurar controles originales
                    self.pdf_preview.content_area.controls.clear()
                    for control in original_content:
                        self.pdf_preview.content_area.controls.append(control)
                    
                    if preview_images:
                        self.pdf_preview.update_preview(preview_images)
                        self.msg.show(f"Previsualización actualizada ({len(preview_images)} páginas)", ft.Colors.GREEN)
                    else:
                        self.pdf_preview.show_error("No se pudo generar la previsualización")
                        self.msg.show("Error generando previsualización PDF", ft.Colors.RED)
                
                update_preview()
                
            except Exception as ex:
                def show_error():
                    self.pdf_preview.show_error(f"Error: {str(ex)[:50]}...")
                    self.msg.show(f"Error en previsualización: {ex}", ft.Colors.RED)
                
                show_error()
        
        # Ejecutar en hilo separado
        threading.Thread(target=preview_worker, daemon=True).start()
    
    def _on_pdf_settings_change(self, settings: dict):
        """Manejar cambio en configuraciones de PDF"""
        # Actualizar configuraciones en export_options para mantener sincronización
        if hasattr(self.export_options, 'pdf_page_size'):
            self.export_options.pdf_page_size.value = settings['page_size']
            self.export_options.pdf_orientation.value = settings['orientation']
            self.export_options.pdf_fit_mode.value = settings['fit_mode']
    
    def _show_pdf_preview(self, e):
        """Mostrar previsualización de cómo se verá el PDF"""
        if not self.service or self.current_mode != "images":
            return
        
        if self.page_manager.get_selected_pages_count() == 0:
            self.msg.show("Selecciona al menos una imagen para previsualizar", ft.Colors.RED)
            return
        
        # Obtener configuración de los controles de ajuste
        settings = self.image_adjustment.get_settings()
        
        def preview_worker():
            try:
                # Generar previsualización usando ImageService
                preview_images = self.service.preview_pdf_pages(
                    page_manager=self.page_manager,
                    page_size=settings['page_size'],
                    orientation=settings['orientation'],
                    fit_mode=settings['fit_mode']
                )
                
                if preview_images:
                    # Crear ventana modal para mostrar la previsualización
                    def show_preview_dialog():
                        self._show_pdf_preview_dialog(preview_images, settings)
                    
                    show_preview_dialog()
                    self.msg.show(f"Previsualización generada ({len(preview_images)} páginas)", ft.Colors.GREEN)
                else:
                    self.msg.show("Error generando previsualización PDF", ft.Colors.RED)
                    
            except Exception as ex:
                self.msg.show(f"Error en previsualización: {ex}", ft.Colors.RED)
        
        # Ejecutar en hilo separado
        threading.Thread(target=preview_worker, daemon=True).start()
    
    def _show_pdf_preview_dialog(self, preview_images, settings):
        """Mostrar diálogo con previsualización PDF"""
        from PIL import Image
        import io
        import base64
        
        # Convertir imágenes a base64 para mostrar en Flet
        preview_controls = []
        
        for i, img in enumerate(preview_images):
            # Convertir PIL a base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Crear control de imagen
            preview_control = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Image(
                            src_base64=img_base64,
                            width=200,
                            height=280,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        border=ft.border.all(2, ft.Colors.GREY_400),
                        border_radius=5,
                        bgcolor=ft.Colors.WHITE,
                        padding=5
                    ),
                    ft.Text(
                        f"Página {i + 1}",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    )
                ]),
                margin=5
            )
            preview_controls.append(preview_control)
        
        # Crear diálogo
        orientation_text = "Vertical" if settings['orientation'] == 'portrait' else 'Horizontal'
        dialog_content = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Vista Previa PDF - {settings['page_size']} {orientation_text}"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"📄 {settings['page_size']} {orientation_text} • 🎯 {settings['fit_mode']} • 📏 {settings['margin']}mm margen",
                        size=12,
                        color=ft.Colors.BLUE_GREY_600
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Row(
                            controls=preview_controls,
                            scroll=ft.ScrollMode.AUTO,
                            alignment=ft.MainAxisAlignment.START
                        ),
                        height=350,
                        width=600
                    )
                ]),
                width=650,
                height=400
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_preview_dialog())
            ]
        )
        
        self.page.overlay.append(dialog_content)
        dialog_content.open = True
        self.page.update()
        
        # Guardar referencia para poder cerrar el diálogo
        self._current_preview_dialog = dialog_content
    
    def _close_preview_dialog(self):
        """Cerrar diálogo de previsualización"""
        if hasattr(self, '_current_preview_dialog'):
            self._current_preview_dialog.open = False
            self.page.overlay.remove(self._current_preview_dialog)
            self.page.update()
    
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
        self.current_file_paths = []
        self.is_processing = False
        
        self.file_name_text.value = ""
        self.pages_input.value = ""
        self.status_text.value = ""
        self.preview_button.disabled = True
        
        self.page_manager.clear()
        self.preview.clear()
        self.export_options.reset()
        self.image_adjustment.reset()
        self.loading_bar.hide()
        
        self.tabs.selected_index = 0
        self.page.update()
