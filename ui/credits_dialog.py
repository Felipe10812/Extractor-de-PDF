import flet as ft
from pathlib import Path

class CreditsDialog:
    """Diálogo de créditos y acerca de la aplicación"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.dialog = None
    
    def show_credits(self):
        """Mostrar diálogo de créditos"""
        
        # Información de la aplicación
        app_info = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(
                        name=ft.Icons.PICTURE_AS_PDF,
                        size=48,
                        color=ft.Colors.BLUE_500
                    ),
                    ft.Column([
                        ft.Text(
                            "PDF Extractor Advanced",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            "Versión 2.0.0",
                            size=14,
                            color=ft.Colors.GREY_700
                        ),
                    ], spacing=2)
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=10
            ),
            
            ft.Divider(),
            
            # Descripción
            ft.Text(
                "Extractor de PDF con Previsualización Interactiva",
                size=16,
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.GREY_800
            ),
            
            ft.Container(height=10),
            
            # Características principales
            ft.Text(
                "✨ Características:",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY
            ),
            
            ft.Column([
                self._create_feature_item("🔍", "Previsualización interactiva de páginas"),
                self._create_feature_item("🔄", "Rotar y eliminar páginas individuales"),
                self._create_feature_item("📁", "Múltiples formatos de exportación"),
                self._create_feature_item("📊", "Barras de progreso en tiempo real"),
                self._create_feature_item("🔔", "Notificaciones del sistema"),
                self._create_feature_item("🌙", "Tema oscuro moderno"),
                self._create_feature_item("🖼️", "Imágenes de alta calidad (300 DPI)"),
            ], spacing=5),
            
            ft.Container(height=10),
            
            ft.Divider(),
            
            # Desarrolladores
            ft.Text(
                "👨‍💻 Desarrolladores:",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY
            ),
            
            # Desarrollador principal actual
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Felipe Acosta Coronado",
                        size=16,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.GREY_800
                    ),
                    ft.Text(
                        "Desarrollo y mejoras de la versión avanzada",
                        size=11,
                        color=ft.Colors.GREY_600
                    ),
                    ft.TextButton(
                        "🔗 github.com/Felipe10812",
                        url="https://github.com/Felipe10812",
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_600,
                            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                        )
                    ),
                ], spacing=2),
                padding=ft.Padding(left=20, top=5, right=20, bottom=10)
            ),
            
            # Desarrollador original
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "andromux",
                        size=16,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.GREY_800
                    ),
                    ft.Text(
                        "Desarrollador del proyecto original • Creador del código base",
                        size=11,
                        color=ft.Colors.GREY_600
                    ),
                    ft.TextButton(
                        "🔗 github.com/andromux",
                        url="https://github.com/andromux",
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_600,
                            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                        )
                    ),
                ], spacing=2),
                padding=ft.Padding(left=20, top=0, right=20, bottom=5)
            ),
            
            ft.Divider(),
            
            # Reconocimientos
            ft.Text(
                "🙏 Reconocimientos:",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY
            ),
            
            ft.Container(
                content=ft.Text(
                    "Esta aplicación está basada en el trabajo original de andromux. "
                    "Agradecemos su contribución al código abierto y su inspiración "
                    "para crear herramientas accesibles para la comunidad.",
                    size=11,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.JUSTIFY
                ),
                padding=ft.Padding(left=20, top=5, right=20, bottom=10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
                border_radius=8
            ),
            
            ft.Divider(),
            
            # Librerías utilizadas
            ft.Text(
                "📚 Librerías utilizadas:",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY
            ),
            
            ft.Column([
                self._create_library_item("Flet", "Framework multiplataforma para interfaces de usuario"),
                self._create_library_item("PyMuPDF", "Procesamiento y renderizado de documentos PDF"),
                self._create_library_item("Pillow", "Manipulación y procesamiento de imágenes"),
                self._create_library_item("Plyer", "Notificaciones del sistema multiplataforma"),
                self._create_library_item("PyPDF", "Manipulación de documentos PDF"),
            ], spacing=8),
            
            ft.Container(height=15),
            
            # Copyright
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "© 2025 PDF Extractor Advanced",
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Basado en el trabajo original de andromux • Mejorado por Felipe Acosta",
                        size=9,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Distribuido bajo la Licencia MIT",
                        size=9,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                        italic=True
                    )
                ], spacing=2),
                padding=15,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREY),
                border_radius=8
            )
        ], 
        spacing=5,
        scroll=ft.ScrollMode.AUTO
        )
        
        # Botones del diálogo
        actions = [
            ft.TextButton(
                "Cerrar",
                on_click=self._close_dialog,
                icon=ft.Icons.CLOSE
            )
        ]
        
        # Crear diálogo
        self.dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE_500),
                ft.Text("Acerca de la aplicación")
            ]),
            content=ft.Container(
                content=app_info,
                width=520,
                height=680
            ),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.CENTER,
            modal=True,
            bgcolor=ft.Colors.BLACK87,
        )
        
        # Mostrar diálogo
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()
    
    def _create_feature_item(self, icon: str, text: str) -> ft.Container:
        """Crear elemento de característica"""
        return ft.Container(
            content=ft.Row([
                ft.Text(icon, size=14),
                ft.Text(text, size=12, color=ft.Colors.GREY_700)
            ]),
            padding=ft.Padding(left=10, top=2, right=10, bottom=2)
        )
    
    def _create_library_item(self, name: str, description: str) -> ft.Container:
        """Crear elemento de librería"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    f"• {name}",
                    size=12,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.BLUE_600
                ),
                ft.Text(
                    description,
                    size=10,
                    color=ft.Colors.GREY_600
                )
            ], spacing=1),
            padding=ft.Padding(left=15, top=0, right=10, bottom=0)
        )
    
    def _close_dialog(self, e):
        """Cerrar el diálogo"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
