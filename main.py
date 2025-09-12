import flet as ft
from app import AdvancedPDFExtractorApp

def main(page: ft.Page):
    page.title = "PDF Extractor Advanced"
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.DARK
    
    # Centrar ventana en la pantalla
    page.window_center = True
    
    # Configuraciones adicionales de ventana
    page.window_minimizable = True
    page.window_maximizable = True
    page.window_min_width = 800  # Ancho mínimo
    page.window_min_height = 600  # Alto mínimo
    
    # Evitar que la ventana se abra muy pequeña
    page.window_prevent_close = False  # Permitir cerrar
    
    # Configurar scroll global si es necesario
    #page.scroll = ft.ScrollMode.AUTO
    
    AdvancedPDFExtractorApp(page)

if __name__ == "__main__":
    ft.app(target=main)
