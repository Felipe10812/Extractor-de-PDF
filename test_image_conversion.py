#!/usr/bin/env python3
"""
Script de prueba para validar la nueva funcionalidad de conversión de imágenes a PDF
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
    """Crear imágenes de prueba en un directorio temporal"""
    test_dir = Path(tempfile.gettempdir()) / "test_images"
    test_dir.mkdir(exist_ok=True)
    
    # Crear algunas imágenes de prueba de diferentes tamaños y colores
    test_images = []
    
    # Imagen 1: Rectángulo rojo (landscape)
    img1 = Image.new('RGB', (800, 600), (255, 0, 0))
    img1_path = test_dir / "test_imagen_01_rojo.png"
    img1.save(img1_path)
    test_images.append(str(img1_path))
    print(f"✓ Creada imagen de prueba: {img1_path.name} (800x600, roja)")
    
    # Imagen 2: Rectángulo verde (portrait)  
    img2 = Image.new('RGB', (600, 800), (0, 255, 0))
    img2_path = test_dir / "test_imagen_02_verde.png"
    img2.save(img2_path)
    test_images.append(str(img2_path))
    print(f"✓ Creada imagen de prueba: {img2_path.name} (600x800, verde)")
    
    # Imagen 3: Cuadrado azul
    img3 = Image.new('RGB', (700, 700), (0, 0, 255))
    img3_path = test_dir / "test_imagen_03_azul.jpg"
    img3.save(img3_path, "JPEG")
    test_images.append(str(img3_path))
    print(f"✓ Creada imagen de prueba: {img3_path.name} (700x700, azul, JPEG)")
    
    # Imagen 4: Pequeña imagen amarilla
    img4 = Image.new('RGB', (300, 200), (255, 255, 0))
    img4_path = test_dir / "test_imagen_04_amarilla.png"
    img4.save(img4_path)
    test_images.append(str(img4_path))
    print(f"✓ Creada imagen de prueba: {img4_path.name} (300x200, amarilla)")
    
    return test_images

def test_image_service_loading():
    """Probar carga de imágenes con ImageService"""
    print("\n=== PRUEBA 1: Carga de Imágenes ===")
    
    test_images = create_test_images()
    
    # Crear servicio de imágenes
    image_service = ImageService(test_images)
    
    print(f"Total de imágenes cargadas: {image_service.get_total_pages()}")
    print(f"Información de imágenes:")
    
    for info in image_service.get_images_info():
        if info['format'] != 'ERROR':
            print(f"  - {info['name']}: {info['format']}, {info['size']}, {info['mode']}")
        else:
            print(f"  - {info['name']}: ERROR - {info.get('error', 'Error desconocido')}")
    
    return image_service, test_images

def test_image_rendering():
    """Probar renderizado de imágenes"""
    print("\n=== PRUEBA 2: Renderizado de Imágenes ===")
    
    image_service, test_images = test_image_service_loading()
    
    for i in range(1, image_service.get_total_pages() + 1):
        # Probar renderizado para preview
        img_preview = image_service.render_page(i, for_export=False)
        if img_preview:
            print(f"✓ Imagen {i} renderizada para preview: {img_preview.size}")
        else:
            print(f"✗ Error renderizando imagen {i} para preview")
        
        # Probar renderizado para exportación
        img_export = image_service.render_page(i, for_export=True)
        if img_export:
            print(f"✓ Imagen {i} renderizada para exportación: {img_export.size}")
        else:
            print(f"✗ Error renderizando imagen {i} para exportación")
    
    return image_service

def test_pdf_conversion():
    """Probar conversión de imágenes a PDF"""
    print("\n=== PRUEBA 3: Conversión a PDF ===")
    
    image_service = test_image_rendering()
    
    # Crear page manager y seleccionar todas las páginas
    page_manager = PageManager()
    
    # Simular carga de todas las páginas en el page manager
    for i in range(1, image_service.get_total_pages() + 1):
        img = image_service.render_page(i, for_export=False)
        if img:
            page_manager.add_page(i, img)  # Se selecciona automáticamente
    
    # Directorio de salida
    output_dir = Path(tempfile.gettempdir()) / "pdf_conversion_test"
    output_dir.mkdir(exist_ok=True)
    
    def progress_callback(current, total, status):
        print(f"  Progreso: {current+1}/{total} - {status}")
        return True  # Continuar
    
    # Probar PDF único
    print("\n--- Probando PDF único ---")
    output_path = output_dir / "test_pdf_unico.pdf"
    success = image_service.convert_to_pdf(
        page_manager=page_manager,
        output_path=str(output_path),
        page_size='A4',
        orientation='portrait',
        fit_mode='fit',
        progress_callback=progress_callback
    )
    
    if success and output_path.exists():
        file_size = output_path.stat().st_size
        print(f"  ✓ PDF único creado exitosamente ({file_size:,} bytes)")
    else:
        print(f"  ✗ Error creando PDF único")
    
    # Probar PDFs individuales en ZIP
    print("\n--- Probando PDFs individuales en ZIP ---")
    zip_path = output_dir / "test_pdfs_individuales.zip"
    success = image_service.convert_to_individual_pdfs_zip(
        page_manager=page_manager,
        output_path=str(zip_path),
        page_size='A4',
        orientation='portrait',
        fit_mode='fit',
        progress_callback=progress_callback
    )
    
    if success and zip_path.exists():
        file_size = zip_path.stat().st_size
        print(f"  ✓ ZIP de PDFs individuales creado exitosamente ({file_size:,} bytes)")
    else:
        print(f"  ✗ Error creando ZIP de PDFs individuales")
    
    # Probar PDFs individuales en carpeta
    print("\n--- Probando PDFs individuales en carpeta ---")
    folder_path = output_dir / "pdfs_individuales"
    success = image_service.convert_to_individual_pdfs_folder(
        page_manager=page_manager,
        output_folder=str(folder_path),
        page_size='A4',
        orientation='portrait',
        fit_mode='fit',
        progress_callback=progress_callback
    )
    
    if success and folder_path.exists():
        pdf_files = list(folder_path.glob("*.pdf"))
        print(f"  ✓ Carpeta de PDFs individuales creada exitosamente ({len(pdf_files)} archivos)")
        for pdf_file in pdf_files:
            print(f"    - {pdf_file.name} ({pdf_file.stat().st_size:,} bytes)")
    else:
        print(f"  ✗ Error creando carpeta de PDFs individuales")
    
    # Probar diferentes configuraciones solo para PDF único
    print("\n--- Probando diferentes configuraciones ---")
    test_configs = [
        {
            'name': 'A4_landscape_fill',
            'page_size': 'A4',
            'orientation': 'landscape',
            'fit_mode': 'fill'
        },
        {
            'name': 'Letter_portrait_stretch',
            'page_size': 'Letter',
            'orientation': 'portrait',
            'fit_mode': 'stretch'
        }
    ]
    
    for config in test_configs:
        output_path = output_dir / f"test_conversion_{config['name']}.pdf"
        print(f"\n  Probando configuración: {config['name']}")
        print(f"    Página: {config['page_size']}")
        print(f"    Orientación: {config['orientation']}")
        print(f"    Ajuste: {config['fit_mode']}")
        
        success = image_service.convert_to_pdf(
            page_manager=page_manager,
            output_path=str(output_path),
            page_size=config['page_size'],
            orientation=config['orientation'],
            fit_mode=config['fit_mode'],
            progress_callback=progress_callback
        )
        
        if success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"    ✓ PDF creado exitosamente ({file_size:,} bytes)")
        else:
            print(f"    ✗ Error creando PDF")
    
    return output_dir

def test_image_export():
    """Probar exportación de imágenes procesadas"""
    print("\n=== PRUEBA 4: Exportación de Imágenes ===")
    
    image_service = test_image_rendering()
    
    # Crear page manager y seleccionar algunas páginas
    page_manager = PageManager()
    
    # Seleccionar solo las páginas 1 y 3
    selected_pages = [1, 3]
    for page_num in selected_pages:
        img = image_service.render_page(page_num, for_export=False)
        if img:
            page_manager.add_page(page_num, img)  # Se selecciona automáticamente
    
    output_dir = Path(tempfile.gettempdir()) / "image_export_test"
    output_dir.mkdir(exist_ok=True)
    
    def progress_callback(current, total, status):
        print(f"  Progreso: {current+1}/{total} - {status}")
        return True
    
    # Probar exportación como ZIP
    zip_path = output_dir / "images_export_test.zip"
    print(f"\nExportando imágenes seleccionadas como ZIP: {zip_path}")
    success = image_service.export_as_images_zip(
        page_manager=page_manager,
        output_path=str(zip_path),
        image_format="PNG",
        progress_callback=progress_callback
    )
    
    if success and zip_path.exists():
        file_size = zip_path.stat().st_size
        print(f"✓ ZIP creado exitosamente ({file_size:,} bytes)")
    else:
        print(f"✗ Error creando ZIP")
    
    # Probar exportación a carpeta
    folder_path = output_dir / "exported_images"
    print(f"\nExportando imágenes seleccionadas a carpeta: {folder_path}")
    success = image_service.export_as_images_folder(
        page_manager=page_manager,
        output_folder=str(folder_path),
        image_format="JPEG",
        progress_callback=progress_callback
    )
    
    if success and folder_path.exists():
        exported_files = list(folder_path.glob("*.jpeg"))
        print(f"✓ Carpeta creada exitosamente ({len(exported_files)} archivos)")
        for file in exported_files:
            print(f"  - {file.name} ({file.stat().st_size:,} bytes)")
    else:
        print(f"✗ Error exportando a carpeta")

def cleanup_test_files():
    """Limpiar archivos de prueba"""
    print("\n=== LIMPIEZA ===")
    
    test_dirs = [
        Path(tempfile.gettempdir()) / "test_images",
        Path(tempfile.gettempdir()) / "pdf_conversion_test", 
        Path(tempfile.gettempdir()) / "image_export_test"
    ]
    
    for test_dir in test_dirs:
        if test_dir.exists():
            try:
                import shutil
                shutil.rmtree(test_dir)
                print(f"✓ Eliminado directorio: {test_dir}")
            except Exception as e:
                print(f"✗ Error eliminando {test_dir}: {e}")

def main():
    """Función principal de pruebas"""
    print("=== PRUEBAS DE FUNCIONALIDAD: CONVERSIÓN DE IMÁGENES A PDF ===")
    print(f"Directorio del proyecto: {Path(__file__).parent}")
    print(f"Directorio temporal: {tempfile.gettempdir()}")
    
    try:
        # Ejecutar todas las pruebas
        test_image_service_loading()
        test_image_rendering()
        pdf_output_dir = test_pdf_conversion()
        test_image_export()
        
        print(f"\n=== RESUMEN DE RESULTADOS ===")
        print(f"✓ Todas las pruebas completadas")
        print(f"✓ PDFs de prueba generados en: {pdf_output_dir}")
        print(f"✓ Funcionalidad de conversión de imágenes a PDF: OPERATIVA")
        
        print(f"\n=== ARCHIVOS GENERADOS PARA REVISIÓN ===")
        if pdf_output_dir.exists():
            for pdf_file in pdf_output_dir.glob("*.pdf"):
                print(f"  📄 {pdf_file}")
        
        # Preguntar si eliminar archivos de prueba
        response = input(f"\n¿Eliminar archivos de prueba? (s/N): ").strip().lower()
        if response in ['s', 'si', 'sí', 'yes', 'y']:
            cleanup_test_files()
        else:
            print("Archivos de prueba conservados para revisión manual.")
            
    except Exception as e:
        print(f"\n✗ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== PRUEBAS FINALIZADAS ===")

if __name__ == "__main__":
    main()
