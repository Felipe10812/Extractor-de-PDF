import flet as ft
from typing import Callable, Optional
from pathlib import Path
from datetime import datetime

class ExportOptions:
    """Componente para opciones de exportación"""
    
    def __init__(self, page: ft.Page, on_export: Optional[Callable] = None):
        self.page = page
        self.on_export = on_export
        self.base_filename = "archivo" # Nombre por defecto
        
        # Controles para opciones de exportación
        self.export_format = ft.Dropdown(
            label="Formato de exportación",
            options=[
                ft.dropdown.Option(key="pdf_combined", text="PDF único"),
                ft.dropdown.Option(key="pdf_individual", text="PDFs individuales"),
                ft.dropdown.Option(key="images_zip", text="Imágenes (ZIP)"),
                ft.dropdown.Option(key="images_folder", text="Imágenes (Carpeta)")
            ],
            value="pdf_combined",
            width=200
        )
        
        self.image_format = ft.Dropdown(
            label="Formato de imagen",
            options=[
                ft.dropdown.Option(key="PNG", text="PNG"),
                ft.dropdown.Option(key="JPEG", text="JPEG"),
                ft.dropdown.Option(key="TIFF", text="TIFF")
            ],
            value="PNG",
            width=150,
            visible=False  # Solo visible para exportación de imágenes
        )
        
        self.output_path = ft.TextField(
            label="Ruta de salida",
            read_only=True,
            expand=True
        )
        
        self.browse_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Seleccionar carpeta",
            on_click=self._on_browse
        )
        
        self.export_button = ft.ElevatedButton(
            "Exportar",
            icon=ft.Icons.DOWNLOAD,
            on_click=self._on_export_click,
            disabled=True
        )
        
        # Folder picker
        self.folder_picker = ft.FilePicker(on_result=self._on_folder_selected)
        self.page.overlay.append(self.folder_picker)
        
        # Container principal
        self.container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Opciones de Exportación", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([self.export_format, self.image_format]),
                    ft.Row([
                        self.output_path,
                        self.browse_button
                    ]),
                    ft.Row([
                        self.export_button
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ],
                spacing=15
            ),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY)
        )
        
        # Setup event handlers
        self.export_format.on_change = self._on_format_change
    
    def get_control(self):
        """Obtener el control principal"""
        return self.container
    
    def _on_format_change(self, e):
        """Manejar cambio de formato de exportación"""
        format_key = self.export_format.value
        
        # IMPORTANTE: Limpiar path anterior para evitar corrupción de archivos
        self.output_path.value = ""
        self.export_button.disabled = True
        
        # Mostrar/ocultar opciones de imagen según el formato
        is_image_format = format_key in ["images_zip", "images_folder"]
        self.image_format.visible = is_image_format
        
        # Actualizar texto del botón de navegación
        if format_key in ["pdf_combined"]:
            self.output_path.label = "Archivo de salida"
            self.output_path.hint_text = "Selecciona dónde guardar el PDF"
        elif format_key == "images_zip":
            self.output_path.label = "Archivo ZIP de salida"
            self.output_path.hint_text = "Selecciona dónde guardar el ZIP"
        else:
            self.output_path.label = "Carpeta de salida"
            self.output_path.hint_text = "Selecciona carpeta de destino"
        
        self.page.update()
    
    def _on_browse(self, e):
        """Manejar clic en botón de navegación"""
        format_key = self.export_format.value
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_key == "pdf_combined":
            # Para PDF único, mostrar diálogo de guardar archivo
            suggested_name = f"{self.base_filename}_{timestamp}.pdf"
            self.folder_picker.save_file(
                dialog_title="Guardar PDF como...",
                file_name=suggested_name,
                allowed_extensions=["pdf"]
            )
        elif format_key in ["images_zip"]:
            # Para ZIP de imágenes, mostrar diálogo de guardar archivo
            suggested_name = f"{self.base_filename}_imagenes_{timestamp}.zip"
            self.folder_picker.save_file(
                dialog_title="Guardar como...",
                file_name=suggested_name,
                allowed_extensions=["zip"]
            )
        else:
            # Para otros formatos, seleccionar carpeta
            self.folder_picker.get_directory_path(dialog_title="Seleccionar carpeta de destino")
    
    def _on_folder_selected(self, e: ft.FilePickerResultEvent):
        """Manejar selección de carpeta o archivo"""
        if e.path:
            self.output_path.value = e.path
            self.export_button.disabled = False
        elif hasattr(e, 'files') and e.files:
            # Para save_file
            self.output_path.value = e.files[0].path
            self.export_button.disabled = False
        else:
            self.export_button.disabled = True
        
        self.page.update()
    
    def _on_export_click(self, e):
        """Manejar clic en botón de exportación"""
        if not self.on_export:
            return
        
        # Validar y corregir la extensión del archivo de salida
        output_path = self.output_path.value
        format_key = self.export_format.value
        
        if format_key == "pdf_combined":
            if not output_path.lower().endswith(".pdf"):
                output_path += ".pdf"
        elif format_key == "images_zip":
            if not output_path.lower().endswith(".zip"):
                output_path += ".zip"
        
        # Actualizar el campo de texto con la ruta corregida
        self.output_path.value = output_path
        self.page.update()
        
        # Crear la configuración de exportación
        export_config = {
            'format': format_key,
            'output_path': output_path,
            'image_format': self.image_format.value if self.image_format.visible else 'PNG'
        }
        
        self.on_export(export_config)
    
    def enable_export(self, enable: bool = True):
        """Habilitar/deshabilitar exportación"""
        self.export_button.disabled = not enable or not self.output_path.value
        self.page.update()
    
    def set_base_filename(self, name: str):
        """Establecer el nombre base del archivo PDF cargado."""
        self.base_filename = name

    def reset(self):
        """Resetear controles"""
        self.output_path.value = ""
        self.export_button.disabled = True
        self.export_format.value = "pdf_combined"
        self.image_format.value = "PNG"
        self.image_format.visible = False
        self.output_path.hint_text = "Selecciona dónde guardar el PDF"
        self.page.update()
    
    def clear_output_path(self):
        """Limpiar solo el path de salida después de exportación exitosa"""
        self.output_path.value = ""
        self.export_button.disabled = True
        # Actualizar hint text según el formato actual
        format_key = self.export_format.value
        if format_key == "pdf_combined":
            self.output_path.hint_text = "Selecciona dónde guardar el PDF"
        elif format_key == "images_zip":
            self.output_path.hint_text = "Selecciona dónde guardar el ZIP"
        else:
            self.output_path.hint_text = "Selecciona carpeta de destino"
        self.page.update()
