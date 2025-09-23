import flet as ft
from typing import Optional, Callable


class ImageAdjustmentControls:
    """Controles para ajustar configuración de PDF cuando se convierten imágenes"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.on_settings_change: Optional[Callable] = None
        
        # Controles de configuración PDF
        self.page_size_dropdown = ft.Dropdown(
            label="Tamaño de página",
            options=[
                ft.dropdown.Option(key="A4", text="A4"),
                ft.dropdown.Option(key="Letter", text="Carta (Letter)"),
                ft.dropdown.Option(key="Legal", text="Legal"),
                ft.dropdown.Option(key="A3", text="A3"),
                ft.dropdown.Option(key="A5", text="A5")
            ],
            value="A4",
            width=150,
            on_change=self._on_setting_change
        )
        
        self.orientation_dropdown = ft.Dropdown(
            label="Orientación",
            options=[
                ft.dropdown.Option(key="portrait", text="Vertical"),
                ft.dropdown.Option(key="landscape", text="Horizontal")
            ],
            value="portrait",
            width=130,
            on_change=self._on_setting_change
        )
        
        self.fit_mode_dropdown = ft.Dropdown(
            label="Ajuste de imagen",
            options=[
                ft.dropdown.Option(key="fit", text="Ajustar (mantener proporción)"),
                ft.dropdown.Option(key="fill", text="Llenar página"),
                ft.dropdown.Option(key="stretch", text="Estirar")
            ],
            value="fit",
            width=200,
            on_change=self._on_setting_change
        )
        
        # Controles de margen
        self.margin_slider = ft.Slider(
            min=0,
            max=50,
            divisions=50,
            value=10,
            label="Margen: {value}mm",
            width=200,
            on_change=self._on_setting_change
        )
        
        # Botón para previsualizar PDF
        self.preview_pdf_button = ft.ElevatedButton(
            "Vista previa como PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            on_click=self._on_preview_pdf,
            width=200
        )
        
        # Información de configuración actual
        self.config_info = ft.Text(
            "",
            size=11,
            color=ft.Colors.BLUE_GREY_400,
            text_align=ft.TextAlign.CENTER
        )
        
        # Container principal
        self.container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "⚙️ Configuración del PDF", 
                    size=14, 
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                ft.Row([
                    self.page_size_dropdown,
                    self.orientation_dropdown
                ], alignment=ft.MainAxisAlignment.START),
                ft.Row([
                    self.fit_mode_dropdown
                ], alignment=ft.MainAxisAlignment.START),
                ft.Column([
                    ft.Text("Margen:", size=12, color=ft.Colors.WHITE),
                    self.margin_slider
                ]),
                ft.Row([
                    self.preview_pdf_button
                ], alignment=ft.MainAxisAlignment.CENTER),
                self.config_info
            ], spacing=10),
            padding=ft.padding.all(15),
            border=ft.border.all(1, ft.Colors.BLUE_400),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
            visible=False  # Inicialmente oculto
        )
        
        # Actualizar información inicial
        self._update_config_info()
    
    def get_control(self):
        """Obtener el control principal"""
        return self.container
    
    def set_settings_change_callback(self, callback: Callable):
        """Establecer callback para cuando cambian las configuraciones"""
        self.on_settings_change = callback
    
    def set_preview_callback(self, callback: Callable):
        """Establecer callback para previsualización PDF"""
        self.preview_pdf_button.on_click = callback
    
    def show(self, show: bool = True):
        """Mostrar u ocultar los controles"""
        self.container.visible = show
        self.page.update()
    
    def get_settings(self) -> dict:
        """Obtener configuración actual"""
        return {
            'page_size': self.page_size_dropdown.value,
            'orientation': self.orientation_dropdown.value,
            'fit_mode': self.fit_mode_dropdown.value,
            'margin': self.margin_slider.value
        }
    
    def _on_setting_change(self, e):
        """Manejar cambio en configuración"""
        self._update_config_info()
        if self.on_settings_change:
            self.on_settings_change(self.get_settings())
    
    def _on_preview_pdf(self, e):
        """Manejar clic en previsualización PDF"""
        # Este será manejado por el callback establecido externamente
        pass
    
    def _update_config_info(self):
        """Actualizar texto informativo de la configuración"""
        settings = self.get_settings()
        orientation_text = "Vertical" if settings['orientation'] == 'portrait' else 'Horizontal'
        fit_text = {
            'fit': 'Ajustar',
            'fill': 'Llenar',
            'stretch': 'Estirar'
        }.get(settings['fit_mode'], settings['fit_mode'])
        
        self.config_info.value = f"📄 {settings['page_size']} {orientation_text} • 🎯 {fit_text} • 📏 {settings['margin']}mm margen"
        if hasattr(self, 'page'):
            self.page.update()
    
    def reset(self):
        """Resetear controles a valores por defecto"""
        self.page_size_dropdown.value = "A4"
        self.orientation_dropdown.value = "portrait"
        self.fit_mode_dropdown.value = "fit"
        self.margin_slider.value = 10
        self._update_config_info()
        self.show(False)
