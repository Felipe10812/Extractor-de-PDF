import flet as ft
from typing import List, Optional, Callable
from PIL import Image
import io
import base64


class PDFPreview:
    """Componente para mostrar previsualización de cómo se verán las imágenes en PDF"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.preview_images = []
        self.current_settings = {}
        
        # Controles para la previsualización
        self.preview_title = ft.Text(
            "Previsualización PDF",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE
        )
        
        self.settings_info = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_300
        )
        
        # GridView para mostrar páginas del PDF
        self.preview_grid = ft.GridView(
            expand=True,
            runs_count=3,  # 3 columnas
            max_extent=200,
            child_aspect_ratio=0.7,
            spacing=10,
            run_spacing=10,
        )
        
        self.scroll_container = ft.Container(
            content=self.preview_grid,
            height=400,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREY),
            visible=False  # Inicialmente oculto
        )
        
        # Botón para actualizar previsualización
        self.refresh_button = ft.ElevatedButton(
            "Actualizar Previsualización",
            icon=ft.Icons.REFRESH,
            on_click=self._on_refresh_preview,
            disabled=False,  # Habilitado por defecto
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE,
            visible=True,
            width=250,
            height=40
        )
        
        # Mensaje cuando no hay previsualización
        self.no_preview_message = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.PREVIEW,
                    size=64,
                    color=ft.Colors.GREY_400
                ),
                ft.Text(
                    "Previsualización PDF",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_400
                ),
                ft.Text(
                    "Ajusta la configuración y haz clic en 'Actualizar Previsualización'",
                    size=12,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "(Solo disponible en modo 'Convertir imágenes a PDF')",
                    size=11,
                    color=ft.Colors.BLUE_GREY_400,
                    text_align=ft.TextAlign.CENTER,
                    italic=True
                )
            ]),
            alignment=ft.alignment.center,
            height=400,
            padding=20,
            visible=True  # Siempre visible inicialmente
        )
        
        # Área de contenido principal
        self.content_area = ft.Stack([
            self.no_preview_message,
            self.scroll_container
        ], height=400)
        
        # Container principal
        self.container = ft.Container(
            content=ft.Column([
                self.preview_title,
                self.settings_info,
                ft.Divider(color=ft.Colors.GREY_400),
                self.content_area,
                ft.Container(
                    content=ft.Row([
                        self.refresh_button
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.only(top=10),
                    visible=True
                )
            ]),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
            visible=True
        )
        
        # Callbacks
        self.on_refresh_callback: Optional[Callable] = None
    
    def get_control(self):
        """Obtener el control principal"""
        return self.container
    
    def set_refresh_callback(self, callback: Callable):
        """Establecer callback para actualizar previsualización"""
        self.on_refresh_callback = callback
    
    def enable_refresh(self, enable: bool = True):
        """Habilitar/deshabilitar botón de actualización"""
        self.refresh_button.disabled = not enable
        self.page.update()
    
    def _on_refresh_preview(self, e):
        """Manejar clic en actualizar previsualización"""
        if self.on_refresh_callback:
            self.on_refresh_callback()
    
    def update_settings_info(self, page_size: str, orientation: str, fit_mode: str, image_count: int):
        """Actualizar información de configuración mostrada"""
        orientation_text = "Vertical" if orientation == "portrait" else "Horizontal"
        
        fit_mode_text = {
            "fit": "Ajustar (mantener proporción)",
            "fill": "Llenar página",
            "stretch": "Estirar"
        }.get(fit_mode, fit_mode)
        
        self.settings_info.value = f"📄 {page_size} {orientation_text} • 🎯 {fit_mode_text} • 🖼️ {image_count} imágenes"
        
        self.current_settings = {
            'page_size': page_size,
            'orientation': orientation,
            'fit_mode': fit_mode,
            'image_count': image_count
        }
    
    def update_preview(self, preview_images: List[Image.Image]):
        """Actualizar previsualización con nuevas imágenes"""
        try:
            self.preview_images = preview_images
            self.preview_grid.controls.clear()
            
            if not preview_images:
                # Mostrar mensaje de no hay previsualización
                self.no_preview_message.visible = True
                self.scroll_container.visible = False
                self.page.update()
                return
            
            # Ocultar mensaje y mostrar grid
            self.no_preview_message.visible = False
            self.scroll_container.visible = True
            
            # Convertir imágenes PIL a base64 para mostrar en Flet
            for i, img in enumerate(preview_images):
                # Convertir imagen PIL a base64
                img_bytes = self._pil_to_base64(img)
                
                # Crear container para cada página
                page_container = ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Image(
                                src_base64=img_bytes,
                                width=180,
                                height=240,
                                fit=ft.ImageFit.CONTAIN,
                                border_radius=5
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
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    alignment=ft.alignment.center
                )
                
                self.preview_grid.controls.append(page_container)
            
            self.page.update()
            
        except Exception as e:
            print(f"Error actualizando previsualización: {e}")
            self.show_error("Error generando previsualización")
    
    def _pil_to_base64(self, img: Image.Image) -> str:
        """Convertir imagen PIL a string base64"""
        try:
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            return base64.b64encode(img_bytes).decode()
        except Exception as e:
            print(f"Error convirtiendo imagen a base64: {e}")
            return ""
    
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        self.preview_grid.controls.clear()
        
        error_container = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE,
                    size=64,
                    color=ft.Colors.RED_400
                ),
                ft.Text(
                    "Error en Previsualización",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_400
                ),
                ft.Text(
                    message,
                    size=12,
                    color=ft.Colors.RED_300,
                    text_align=ft.TextAlign.CENTER
                )
            ]),
            alignment=ft.alignment.center,
            height=400,
            padding=20,
            visible=True
        )
        
        # Reemplazar el contenido del stack
        self.content_area.controls.clear()
        self.content_area.controls.append(error_container)
        
        self.page.update()
    
    def show_loading(self):
        """Mostrar indicador de carga"""
        loading_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(
                    width=32,
                    height=32,
                    stroke_width=3,
                    color=ft.Colors.BLUE
                ),
                ft.Text(
                    "Generando Previsualización...",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE
                ),
                ft.Text(
                    "Esto puede tomar unos segundos",
                    size=12,
                    color=ft.Colors.GREY_600
                )
            ]),
            alignment=ft.alignment.center,
            height=400,
            padding=20,
            visible=True
        )
        
        # Guardar controles originales
        original_controls = self.content_area.controls.copy()
        
        # Reemplazar temporalmente el contenido
        self.content_area.controls.clear()
        self.content_area.controls.append(loading_container)
        
        self.page.update()
        
        # Devolver los controles originales para poder restaurarlos
        return original_controls
    
    def set_mode(self, mode: str):
        """Establecer el modo actual (pdf o images)"""
        if mode == "images":
            # En modo imágenes, habilitar funcionalidad
            self.refresh_button.disabled = False
            self.refresh_button.text = "Actualizar Previsualización"
            self.no_preview_message.content.controls[2].value = "Ajusta la configuración de PDF y haz clic en 'Actualizar Previsualización'"
            self.no_preview_message.content.controls[3].visible = False
        else:
            # En modo PDF, deshabilitar funcionalidad
            self.refresh_button.disabled = True
            self.refresh_button.text = "No disponible en modo PDF"
            self.no_preview_message.content.controls[2].value = "Esta función solo está disponible en modo 'Convertir imágenes a PDF'"
            self.no_preview_message.content.controls[3].visible = True
            
        self.page.update()
    
    def clear(self):
        """Limpiar previsualización"""
        self.preview_images.clear()
        self.preview_grid.controls.clear()
        self.current_settings.clear()
        
        # Restaurar estado inicial
        self.content_area.controls.clear()
        self.content_area.controls.extend([self.no_preview_message, self.scroll_container])
        
        self.no_preview_message.visible = True
        self.scroll_container.visible = False
        
        self.settings_info.value = ""
        
        self.page.update()
