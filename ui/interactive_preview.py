import flet as ft
from PIL import Image
import io
import base64
from typing import Callable, Optional
from services.page_manager import PageManager, PageInfo

class InteractivePreview:
    """Componente de preview interactivo con funcionalidades de rotación y eliminación"""
    
    def __init__(self, page: ft.Page, on_page_change: Optional[Callable] = None):
        self.page = page
        self.on_page_change = on_page_change
        self.preview_container = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )
        
    def get_control(self):
        """Obtener el control principal del preview"""
        return self.preview_container
    
    def render_pages(self, page_manager: PageManager):
        """Renderizar todas las páginas del manager"""
        self.preview_container.controls.clear()
        
        active_pages = page_manager.get_active_pages()
        
        if not active_pages:
            self.preview_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay páginas para mostrar",
                        size=16,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            # Crear una fila para las páginas con scroll horizontal
            pages_row = ft.Row(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=15
            )
            
            # Ordenar páginas por número
            sorted_pages = sorted(active_pages, key=lambda x: x.page_number)
            
            for page_info in sorted_pages:
                page_preview = self._create_page_preview(page_info, page_manager)
                pages_row.controls.append(page_preview)
            
            self.preview_container.controls.append(pages_row)
        
        self.page.update()
    
    def _create_page_preview(self, page_info: PageInfo, page_manager: PageManager):
        """Crear el preview de una página individual"""
        # Convertir imagen a base64
        img_base64 = self._image_to_base64(page_info.rotated_image)
        
        # Crear botones de acción
        rotate_button = ft.IconButton(
            icon=ft.Icons.ROTATE_RIGHT,
            tooltip="Rotar 90°",
            on_click=lambda e: self._rotate_page(page_info.page_number, page_manager)
        )
        
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Eliminar página",
            icon_color=ft.Colors.RED,
            on_click=lambda e: self._delete_page(page_info.page_number, page_manager)
        )
        
        # Crear indicador de rotación
        rotation_text = f"{page_info.rotation}°" if page_info.rotation > 0 else ""
        
        # Container principal de la página
        page_container = ft.Container(
            content=ft.Column(
                controls=[
                    # Imagen de la página
                    ft.Container(
                        content=ft.Image(
                            src_base64=img_base64,
                            width=200,
                            height=250,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        border=ft.border.all(2, ft.Colors.GREY_400),
                        border_radius=5,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE),
                        padding=5
                    ),
                    # Información de la página
                    ft.Text(
                        f"Página {page_info.page_number}",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    # Indicador de rotación
                    ft.Text(
                        rotation_text,
                        size=10,
                        color=ft.Colors.BLUE,
                        text_align=ft.TextAlign.CENTER
                    ) if rotation_text else ft.Container(height=14),
                    # Botones de acción
                    ft.Row(
                        controls=[rotate_button, delete_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=10,
            margin=5,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY)
        )
        
        return page_container
    
    def _image_to_base64(self, img: Image.Image) -> str:
        """Convertir imagen PIL a base64"""
        if not img:
            return ""
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return img_base64
    
    def _rotate_page(self, page_number: int, page_manager: PageManager):
        """Rotar una página específica"""
        page_manager.rotate_page(page_number, 90)
        self.render_pages(page_manager)
        
        if self.on_page_change:
            self.on_page_change(f"Página {page_number} rotada 90°")
    
    def _delete_page(self, page_number: int, page_manager: PageManager):
        """Eliminar una página específica"""
        page_manager.delete_page(page_number)
        self.render_pages(page_manager)
        
        if self.on_page_change:
            self.on_page_change(f"Página {page_number} eliminada")
    
    def clear(self):
        """Limpiar el preview"""
        self.preview_container.controls.clear()
        self.page.update()
    
    def show_loading(self, message: str = "Cargando..."):
        """Mostrar indicador de carga"""
        self.preview_container.controls.clear()
        self.preview_container.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ProgressRing(),
                        ft.Text(message, text_align=ft.TextAlign.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                padding=20
            )
        )
        self.page.update()
    
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        self.preview_container.controls.clear()
        self.preview_container.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=48),
                        ft.Text(
                            message,
                            color=ft.Colors.RED,
                            text_align=ft.TextAlign.CENTER
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                padding=20
            )
        )
        self.page.update()
