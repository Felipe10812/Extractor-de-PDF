import flet as ft
from typing import Callable, Optional

class ProgressDialog:
    """Diálogo de progreso para operaciones largas"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.progress_bar = ft.ProgressBar(width=300, value=0)
        self.status_text = ft.Text("Iniciando...", size=14, text_align=ft.TextAlign.CENTER)
        self.cancel_callback: Optional[Callable] = None
        self._is_cancelled = False
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Procesando"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.progress_bar,
                        self.status_text
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    tight=True
                ),
                width=350,
                height=80
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self._on_cancel
                )
            ]
        )
    
    def show(self, title: str = "Procesando"):
        """Mostrar el diálogo de progreso"""
        self.dialog.title.value = title
        self.progress_bar.value = 0
        self.status_text.value = "Iniciando..."
        self._is_cancelled = False
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Actualizar el progreso"""
        if self._is_cancelled:
            return False
        
        try:
            progress = current / total if total > 0 else 0
            self.progress_bar.value = progress
            
            if status:
                self.status_text.value = status
            else:
                self.status_text.value = f"{current}/{total}"
            
            # Forzar actualización inmediata
            self.page.update()
            
            # Pequeña pausa para asegurar que la UI se actualice
            import time
            time.sleep(0.01)
            
            return True
        except Exception as e:
            print(f"Error actualizando progreso: {e}")
            return False
    
    def hide(self):
        """Ocultar el diálogo"""
        if self.page.dialog:
            self.dialog.open = False
            self.page.dialog = None
            self.page.update()
    
    def set_cancel_callback(self, callback: Callable):
        """Establecer callback para cancelación"""
        self.cancel_callback = callback
    
    def _on_cancel(self, e):
        """Manejar cancelación"""
        self._is_cancelled = True
        if self.cancel_callback:
            self.cancel_callback()
        self.hide()
    
    def is_cancelled(self) -> bool:
        """Verificar si fue cancelado"""
        return self._is_cancelled

class InlineProgressBar:
    """Barra de progreso inline para mostrar en la interfaz"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.progress_bar = ft.ProgressBar(
            width=500,
            height=8,
            visible=False,
            color=ft.Colors.BLUE,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE)
        )
        self.status_text = ft.Text(
            "", 
            size=13, 
            visible=False, 
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_SURFACE
        )
        
        # Container con fondo para mejor visibilidad
        self.container = ft.Container(
            content=ft.Column(
                controls=[self.progress_bar, self.status_text],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
            visible=False
        )
    
    def get_control(self):
        """Obtener el control de progreso"""
        return self.container
    
    def show(self, status: str = "Cargando..."):
        """Mostrar barra de progreso"""
        self.progress_bar.value = None  # Indeterminado
        self.progress_bar.visible = True
        self.status_text.value = status
        self.status_text.visible = True
        self.container.visible = True
        self.page.update()
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Actualizar progreso"""
        try:
            if total > 0:
                self.progress_bar.value = current / total
            
            if status:
                self.status_text.value = status
            else:
                self.status_text.value = f"Procesando {current}/{total}"
            
            # Asegurar que esté visible
            self.progress_bar.visible = True
            self.status_text.visible = True
            
            self.page.update()
        except Exception as e:
            print(f"Error actualizando progreso inline: {e}")
    
    def hide(self):
        """Ocultar barra de progreso"""
        self.progress_bar.visible = False
        self.status_text.visible = False
        self.container.visible = False
        self.page.update()
