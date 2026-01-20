import flet as ft
import json
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
        self.view_mode = "by_pages"  # "by_pages" o "by_source"
        self.current_page_manager = None
        self.drag_start_index = -1
        
        # Toggle para cambiar vista
        self.view_toggle = ft.SegmentedButton(
            selected={"by_pages"},
            allow_empty_selection=False,
            allow_multiple_selection=False,
            segments=[
                ft.Segment(
                    value="by_pages",
                    label=ft.Text("Por hojas"),
                    icon=ft.Icon(ft.Icons.VIEW_MODULE)
                ),
                ft.Segment(
                    value="by_source",
                    label=ft.Text("Por archivo"),
                    icon=ft.Icon(ft.Icons.FOLDER)
                )
            ],
            on_change=self._on_view_change,
            visible=False  # Se muestra solo cuando hay múltiples fuentes
        )
        
        self.preview_content = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )
        
        self.preview_container = ft.Column(
            controls=[
                ft.Container(
                    content=self.view_toggle,
                    padding=ft.padding.only(bottom=10)
                ),
                self.preview_content
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )
        
    def get_control(self):
        """Obtener el control principal del preview"""
        return self.preview_container
    
    def render_pages(self, page_manager: PageManager):
        """Renderizar todas las páginas del manager"""
        self.current_page_manager = page_manager
        self.preview_content.controls.clear()
        
        active_pages = page_manager.get_active_pages()
        
        if not active_pages:
            self.preview_content.controls.append(
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
            # Verificar si hay múltiples fuentes
            unique_sources = page_manager.get_unique_sources()
            has_multiple_sources = len(unique_sources) > 1
            self.view_toggle.visible = has_multiple_sources
            
            # Renderizar según el modo de vista
            if self.view_mode == "by_source" and has_multiple_sources:
                self._render_by_source(page_manager, unique_sources)
            else:
                self._render_by_pages(page_manager, active_pages)
        
        self.page.update()
    
    def _render_by_pages(self, page_manager: PageManager, active_pages: list):
        """Renderizar páginas en vista lineal con arrastrar y soltar"""
        
        pages_row = ft.Row(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=15
        )
        
        # Ordenar páginas por número
        sorted_pages = sorted(active_pages, key=lambda x: x.page_number)
        
        for i, page_info in enumerate(sorted_pages):
            page_preview = self._create_page_preview(page_info, page_manager)
            
            # Hacer que cada página sea un objetivo de soltar
            target = ft.DragTarget(
                group="pages",
                content=page_preview,
                data=page_info.page_number,
                on_accept=self._on_drop,
                on_will_accept=self._on_drag_will_accept,
                on_leave=self._on_drag_leave
            )
            pages_row.controls.append(target)
            
        self.preview_content.controls.append(pages_row)
    
    def _render_by_source(self, page_manager: PageManager, unique_sources: list):
        """Renderizar páginas agrupadas por archivo origen"""
        for source_index, source_name in unique_sources:
            # Obtener páginas de esta fuente
            source_pages = page_manager.get_pages_by_source(source_index)
            if not source_pages:
                continue
            
            # Crear botones de movimiento de archivo
            move_file_up_btn = ft.IconButton(
                icon=ft.Icons.ARROW_UPWARD,
                tooltip="Mover archivo arriba",
                icon_size=18,
                on_click=lambda e, idx=source_index: self._move_source_up(idx, page_manager)
            )
            
            move_file_down_btn = ft.IconButton(
                icon=ft.Icons.ARROW_DOWNWARD,
                tooltip="Mover archivo abajo",
                icon_size=18,
                on_click=lambda e, idx=source_index: self._move_source_down(idx, page_manager)
            )
            
            # Crear encabezado del grupo
            header = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF, size=20, color=ft.Colors.BLUE),
                    ft.Text(
                        source_name,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE,
                        expand=True
                    ),
                    ft.Text(
                        f"({len(source_pages)} páginas)",
                        size=12,
                        color=ft.Colors.GREY_600
                    ),
                    move_file_up_btn,
                    move_file_down_btn
                ], spacing=5),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                border_radius=5
            )
            
            # Crear fila de páginas para esta fuente
            pages_row = ft.Row(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=15
            )
            
            # Ordenar páginas por número
            sorted_pages = sorted(source_pages, key=lambda x: x.page_number)
            
            for page_info in sorted_pages:
                page_preview = self._create_page_preview(page_info, page_manager, show_source=False)
                pages_row.controls.append(page_preview)
            
            # Agregar grupo al contenedor
            group_container = ft.Container(
                content=ft.Column([
                    header,
                    pages_row
                ], spacing=10),
                padding=10,
                margin=ft.margin.only(bottom=15),
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.BLUE)),
                border_radius=10
            )
            
            self.preview_content.controls.append(group_container)
    
    def _on_view_change(self, e):
        """Manejar cambio de vista"""
        if not e.control.selected:
            return
        
        new_mode = list(e.control.selected)[0]
        if new_mode != self.view_mode:
            self.view_mode = new_mode
            if self.current_page_manager:
                self.render_pages(self.current_page_manager)
    
    def _create_page_preview(self, page_info: PageInfo, page_manager: PageManager, show_source: bool = True):
        """Crear el preview de una página individual"""
        # Convertir imagen a base64
        img_base64 = self._image_to_base64(page_info.rotated_image)
        
        # Crear botones de acción
        rotate_button = ft.IconButton(
            icon=ft.Icons.ROTATE_RIGHT,
            tooltip="Rotar 90°",
            icon_size=16,
            on_click=lambda e: self._rotate_page(page_info.page_number, page_manager)
        )
        
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Eliminar página",
            icon_color=ft.Colors.RED,
            icon_size=16,
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
                    # Información de origen (si aplica)
                    ft.Text(
                        f"{page_info.source_pdf}" if page_info.source_pdf and show_source else "",
                        size=9,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ) if page_info.source_pdf and show_source else ft.Container(height=0),
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
        
        # Envolver en un control arrastrable
        draggable_item = ft.Draggable(
            group="pages",
            content=page_container,
            data=page_info.page_number
        )
        
        return draggable_item
    
    def _on_drag_will_accept(self, e: ft.DragTargetEvent):
        """Manejar cuando un arrastrable está sobre un objetivo"""
        e.control.content.border = ft.border.all(2, ft.Colors.BLUE)
        e.control.update()

    def _on_drag_leave(self, e: ft.DragTargetEvent):
        """Manejar cuando un arrastrable sale de un objetivo"""
        e.control.content.border = ft.border.all(2, ft.Colors.GREY_400)
        e.control.update()

    def _on_drop(self, e: ft.DragTargetEvent):
        """Manejar cuando se suelta un arrastrable"""
        page_manager = self.current_page_manager
        if not page_manager:
            return

        # Parse the JSON data from the event to get the source control ID
        try:
            event_data = json.loads(e.data)
            src_id = event_data.get("src_id")
            if not src_id:
                return
        except (json.JSONDecodeError, AttributeError):
            return

        # Get the source draggable control from its ID
        src_control = self.page.get_control(src_id)
        if not src_control:
            return
            
        # Get the page numbers from the control's data properties
        src_page_number = int(src_control.data) # Data from Draggable
        tgt_page_number = int(e.control.data) # Data from DragTarget

        src_page_info = page_manager.get_page_info(src_page_number)
        tgt_page_info = page_manager.get_page_info(tgt_page_number)

        if src_page_info and tgt_page_info and src_page_info.page_number != tgt_page_info.page_number:
            
            active_pages = page_manager.get_active_pages()
            # We need a stable sort before creating the new order
            sorted_pages = sorted(active_pages, key=lambda p: p.page_number)
            
            old_order = [p.page_number for p in sorted_pages]
            
            if src_page_info.page_number in old_order:
                old_order.remove(src_page_info.page_number)

            try:
                # Find insert position
                tgt_index = old_order.index(tgt_page_info.page_number)
                old_order.insert(tgt_index, src_page_info.page_number)
            except ValueError:
                # if target is not in list for some reason, append at the end
                old_order.append(src_page_info.page_number)

            page_manager.reorder_pages(old_order)
            self.render_pages(page_manager)
            
            if self.on_page_change:
                self.on_page_change("Páginas reordenadas")
        else:
            # Si se suelta sobre sí mismo, solo quitar el resaltado
            e.control.content.border = ft.border.all(2, ft.Colors.GREY_400)
            e.control.update()

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
    
    def _move_source_up(self, source_pdf_index: int, page_manager: PageManager):
        """Mover archivo completo hacia arriba"""
        if page_manager.move_source_up(source_pdf_index):
            self.render_pages(page_manager)
            if self.on_page_change:
                self.on_page_change(f"Archivo movido arriba")
    
    def _move_source_down(self, source_pdf_index: int, page_manager: PageManager):
        """Mover archivo completo hacia abajo"""
        if page_manager.move_source_down(source_pdf_index):
            self.render_pages(page_manager)
            if self.on_page_change:
                self.on_page_change(f"Archivo movido abajo")
    
    def clear(self):
        """Limpiar el preview"""
        self.preview_content.controls.clear()
        self.view_toggle.visible = False
        self.current_page_manager = None
        self.page.update()
    
    def show_loading(self, message: str = "Cargando..."):
        """Mostrar indicador de carga"""
        self.preview_content.controls.clear()
        self.view_toggle.visible = False
        self.preview_content.controls.append(
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
        self.preview_content.controls.clear()
        self.view_toggle.visible = False
        self.preview_content.controls.append(
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
