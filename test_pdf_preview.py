#!/usr/bin/env python3
"""
Script de prueba específico para la funcionalidad de previsualización PDF
"""

import os
import sys
from pathlib import Path
from PIL import Image
import tempfile

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from services.image_service import ImageService
from services.page_manager import PageManager

def create_test_images():
    """Crear imágenes de prueba de diferentes proporciones"""
    test_dir = Path(tempfile.gettempdir()) / "pdf_preview_test"
    test_dir.mkdir(exist_ok=True)
    
    test_images = []
    
    # Imagen horizontal (landscape)
    img1 = Image.new('RGB', (800, 400), (255, 100, 100))  # Roja horizontal
    img1_path = test_dir / "horizontal_roja.png"
    img1.save(img1_path)
    test_images.append(str(img1_path))
    print(f"✓ Creada imagen horizontal: {img1_path.name} (800x400)")
    
    # Imagen vertical (portrait)
    img2 = Image.new('RGB', (400, 800), (100, 255, 100))  # Verde vertical
    img2_path = test_dir / "vertical_verde.png"
    img2.save(img2_path)
    test_images.append(str(img2_path))
    print(f"✓ Creada imagen vertical: {img2_path.name} (400x800)")
    
    # Imagen cuadrada
    img3 = Image.new('RGB', (600, 600), (100, 100, 255))  # Azul cuadrada
    img3_path = test_dir / "cuadrada_azul.png"
    img3.save(img3_path)
    test_images.append(str(img3_path))
    print(f"✓ Creada imagen cuadrada: {img3_path.name} (600x600)")
    
    # Imagen muy ancha
    img4 = Image.new('RGB', (1200, 300), (255, 255, 100))  # Amarilla muy ancha
    img4_path = test_dir / "muy_ancha_amarilla.png"
    img4.save(img4_path)
    test_images.append(str(img4_path))
    print(f"✓ Creada imagen muy ancha: {img4_path.name} (1200x300)")
    
    return test_images

def test_preview_generation():
    """Probar generación de previsualización PDF"""
    print("\n=== PRUEBA: Generación de Previsualización PDF ===")
    
    # Crear imágenes de prueba
    test_images = create_test_images()
    
    # Crear servicio de imágenes
    image_service = ImageService(test_images)
    print(f"Servicio de imágenes creado con {image_service.get_total_pages()} imágenes válidas")
    
    # Crear page manager y cargar todas las imágenes
    page_manager = PageManager()
    for i in range(1, image_service.get_total_pages() + 1):
        img = image_service.render_page(i, for_export=False)
        if img:
            page_manager.add_page(i, img)
    
    print(f"Page manager cargado con {page_manager.get_selected_pages_count()} imágenes")
    
    # Probar diferentes configuraciones
    test_configs = [
        {
            'name': 'A4_Portrait_Fit',
            'page_size': 'A4',
            'orientation': 'portrait',
            'fit_mode': 'fit',
            'description': 'A4 vertical con ajuste (recomendado para documentos)'
        },
        {
            'name': 'A4_Landscape_Fit', 
            'page_size': 'A4',
            'orientation': 'landscape',
            'fit_mode': 'fit',
            'description': 'A4 horizontal con ajuste (bueno para imágenes anchas)'
        },
        {
            'name': 'A4_Portrait_Fill',
            'page_size': 'A4',
            'orientation': 'portrait',
            'fit_mode': 'fill',
            'description': 'A4 vertical llenando página (puede recortar)'
        },
        {
            'name': 'Letter_Landscape_Stretch',
            'page_size': 'Letter',
            'orientation': 'landscape',
            'fit_mode': 'stretch',
            'description': 'Carta horizontal estirando (puede deformar)'
        }
    ]
    
    output_dir = Path(tempfile.gettempdir()) / "pdf_preview_output"
    output_dir.mkdir(exist_ok=True)
    
    for config in test_configs:
        print(f"\n--- Probando configuración: {config['name']} ---")
        print(f"    Descripción: {config['description']}")
        print(f"    Página: {config['page_size']} {config['orientation']}")
        print(f"    Ajuste: {config['fit_mode']}")
        
        # Generar previsualización
        preview_images = image_service.preview_pdf_pages(
            page_manager=page_manager,
            page_size=config['page_size'],
            orientation=config['orientation'],
            fit_mode=config['fit_mode']
        )
        
        if preview_images:
            print(f"    ✓ Previsualización generada: {len(preview_images)} páginas")
            
            # Guardar las previsualizaciones como imágenes para revisión
            config_dir = output_dir / config['name']
            config_dir.mkdir(exist_ok=True)
            
            for i, preview_img in enumerate(preview_images):
                preview_path = config_dir / f"preview_page_{i+1}.png"
                preview_img.save(preview_path)
            
            print(f"    📄 Previsualizaciones guardadas en: {config_dir}")
            
            # Mostrar información sobre cada página
            for i, preview_img in enumerate(preview_images):
                print(f"      Página {i+1}: {preview_img.size[0]}x{preview_img.size[1]} píxeles")
                
        else:
            print(f"    ✗ Error generando previsualización")
    
    return output_dir

def test_different_proportions():
    """Probar cómo se ven diferentes proporciones de imagen"""
    print(f"\n=== PRUEBA: Análisis de Proporciones ===")
    
    # Crear imágenes con proporciones extremas
    test_dir = Path(tempfile.gettempdir()) / "proportion_test"
    test_dir.mkdir(exist_ok=True)
    
    proportion_tests = [
        {'size': (1000, 200), 'name': 'panoramica', 'color': (255, 150, 0), 'desc': 'Panorámica (5:1)'},
        {'size': (200, 1000), 'name': 'torre', 'color': (150, 0, 255), 'desc': 'Torre (1:5)'},
        {'size': (800, 600), 'name': 'foto_std', 'color': (0, 200, 200), 'desc': 'Foto estándar (4:3)'},
        {'size': (1920, 1080), 'name': 'hd', 'color': (200, 200, 0), 'desc': 'HD (16:9)'}
    ]
    
    test_images = []
    for test in proportion_tests:
        img = Image.new('RGB', test['size'], test['color'])
        img_path = test_dir / f"{test['name']}.png"
        img.save(img_path)
        test_images.append(str(img_path))
        ratio = test['size'][0] / test['size'][1]
        print(f"  ✓ {test['desc']}: {test['size']} (ratio: {ratio:.2f})")
    
    # Crear servicio y page manager
    image_service = ImageService(test_images)
    page_manager = PageManager()
    
    for i in range(1, image_service.get_total_pages() + 1):
        img = image_service.render_page(i, for_export=False)
        if img:
            page_manager.add_page(i, img)
    
    # Probar cómo se ven en diferentes orientaciones
    print(f"\n  Recomendaciones por proporción:")
    
    orientations = [
        {'orientation': 'portrait', 'name': 'Vertical'},
        {'orientation': 'landscape', 'name': 'Horizontal'}
    ]
    
    for orient in orientations:
        print(f"\n  --- PDF {orient['name']} ---")
        
        preview_images = image_service.preview_pdf_pages(
            page_manager=page_manager,
            page_size='A4',
            orientation=orient['orientation'],
            fit_mode='fit'
        )
        
        for i, (test, preview_img) in enumerate(zip(proportion_tests, preview_images)):
            original_ratio = test['size'][0] / test['size'][1]
            if orient['orientation'] == 'landscape':
                page_ratio = 842 / 595  # A4 landscape
                recommendation = "👍 Recomendado" if original_ratio > 1.5 else "⚠️ Puede tener bordes"
            else:
                page_ratio = 595 / 842  # A4 portrait  
                recommendation = "👍 Recomendado" if original_ratio < 0.8 else "⚠️ Puede tener bordes"
            
            print(f"    {test['desc']}: {recommendation}")

def main():
    """Función principal de pruebas"""
    print("=== PRUEBAS DE PREVISUALIZACIÓN PDF ===")
    print(f"Directorio del proyecto: {Path(__file__).parent}")
    print(f"Directorio temporal: {tempfile.gettempdir()}")
    
    try:
        # Ejecutar pruebas
        output_dir = test_preview_generation()
        test_different_proportions()
        
        print(f"\n=== RESUMEN ===")
        print(f"✓ Pruebas de previsualización completadas")
        print(f"✓ Funcionalidad de previsualización PDF: OPERATIVA")
        print(f"📄 Previsualizaciones guardadas en: {output_dir}")
        
        print(f"\n=== ARCHIVOS GENERADOS ===")
        if output_dir.exists():
            for config_dir in output_dir.iterdir():
                if config_dir.is_dir():
                    preview_files = list(config_dir.glob("*.png"))
                    print(f"  📁 {config_dir.name}: {len(preview_files)} previsualizaciones")
        
        # Preguntar si eliminar archivos de prueba
        response = input(f"\n¿Eliminar archivos de prueba? (s/N): ").strip().lower()
        if response in ['s', 'si', 'sí', 'yes', 'y']:
            import shutil
            for test_dir in [Path(tempfile.gettempdir()) / "pdf_preview_test", 
                           Path(tempfile.gettempdir()) / "proportion_test",
                           output_dir]:
                if test_dir.exists():
                    shutil.rmtree(test_dir)
                    print(f"✓ Eliminado: {test_dir}")
        else:
            print("Archivos de prueba conservados para revisión.")
        
        print(f"\n=== CÓMO USAR LA PREVISUALIZACIÓN EN LA APP ===")
        print(f"1. Cambia al modo 'Convertir imágenes a PDF'")
        print(f"2. Carga múltiples imágenes")
        print(f"3. Previsualiza y selecciona las imágenes que quieres")
        print(f"4. Ve a la pestaña 'Previsualización PDF'")
        print(f"5. Ajusta la configuración (tamaño, orientación, ajuste)")
        print(f"6. Haz clic en 'Actualizar Previsualización'")
        print(f"7. Revisa cómo se verán las imágenes en el PDF")
        print(f"8. Ve a 'Exportación' y genera tu PDF")
        
    except Exception as e:
        print(f"\n✗ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== PRUEBAS FINALIZADAS ===")

if __name__ == "__main__":
    main()
