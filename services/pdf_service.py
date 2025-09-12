from pathlib import Path
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
from PIL import Image
import zipfile
import os
from typing import List
from .document_service import DocumentService
from .page_manager import PageManager, PageInfo

class PDFService(DocumentService):
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        self.total_pages = len(self.reader.pages)

    def get_total_pages(self) -> int:
        return self.total_pages

    def extract(self, pages: list[int], output_path: str) -> int:
        try:
            writer = PdfWriter()
            pages_found = 0
            
            print(f"Intentando extraer páginas: {pages}")
            print(f"Total de páginas en PDF: {self.total_pages}")
            
            for page_num in pages:
                if 1 <= page_num <= self.total_pages:
                    try:
                        writer.add_page(self.reader.pages[page_num - 1])
                        pages_found += 1
                        print(f"Página {page_num} añadida exitosamente")
                    except Exception as e:
                        print(f"Error al añadir página {page_num}: {e}")
                else:
                    print(f"Página {page_num} fuera de rango (1-{self.total_pages})")
            
            if pages_found > 0:
                # Crear el directorio si no existe
                output_dir = Path(output_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)
                print(f"Directorio de salida: {output_dir}")
                
                # Escribir el archivo
                with open(output_path, "wb") as f:
                    writer.write(f)
                print(f"PDF guardado en: {output_path}")
            else:
                print("No se encontraron páginas válidas para extraer")
                
            return pages_found
            
        except Exception as e:
            print(f"Error en extract(): {e}")
            raise e

    def render_page(self, page_num: int, scale: float = 1.0, for_export: bool = False):
        """Convierte página en imagen PIL para preview o exportación."""
        try:
            # Abrir el documento con PyMuPDF
            doc = fitz.open(self.pdf_path)
            
            # Verificar que la página existe (PyMuPDF usa índice basado en 0)
            if page_num < 1 or page_num > len(doc):
                doc.close()
                return None
            
            # Obtener la página (convertir a índice basado en 0)
            page = doc[page_num - 1]
            
            # Determinar escalado según el propósito
            if for_export:
                # Para exportación: alta calidad (300 DPI equivalente)
                target_scale = 4.17  # 300 DPI / 72 DPI
            else:
                # Para preview: calidad moderada pero eficiente
                target_scale = 2.0 if scale == 1.0 else scale
            
            # Crear una matriz de transformación para el escalado
            mat = fitz.Matrix(target_scale, target_scale)
            
            # Renderizar la página como imagen con alta calidad
            pix = page.get_pixmap(matrix=mat, alpha=False)  # Sin canal alfa para mejor compresión
            
            # Convertir a bytes PNG
            img_data = pix.tobytes("png")
            
            # Convertir a PIL Image
            from io import BytesIO
            img = Image.open(BytesIO(img_data))
            
            # Solo redimensionar si es para preview
            if not for_export and img.width > 300:
                ratio = 300 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((300, new_height), Image.Resampling.LANCZOS)
            
            doc.close()
            return img
            
        except Exception as e:
            print(f"Error renderizando página {page_num}: {e}")
            return None
    
    def export_as_images_zip(self, page_manager: PageManager, output_path: str, 
                            image_format: str = "PNG", progress_callback=None) -> bool:
        """Exportar páginas como imágenes en un archivo ZIP"""
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            base_name = Path(self.pdf_path).stem
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                total_pages = len(active_pages)
                
                for i, page_info in enumerate(active_pages):
                    if progress_callback:
                        progress_callback(i, total_pages, f"Procesando página {page_info.page_number}")
                    
                    # Renderizar página en alta calidad para exportación
                    high_quality_img = self.render_page(page_info.page_number, for_export=True)
                    
                    if high_quality_img:
                        # Aplicar rotación si es necesaria
                        if page_info.rotation != 0:
                            high_quality_img = high_quality_img.rotate(-page_info.rotation, expand=True)
                        
                        # Crear nombre de archivo para la imagen
                        img_filename = f"{base_name}_pagina_{page_info.page_number:03d}.{image_format.lower()}"
                        
                        # Guardar imagen en memoria con configuraciones de calidad
                        from io import BytesIO
                        img_buffer = BytesIO()
                        
                        # Configuraciones de calidad por formato
                        if image_format.upper() == 'JPEG':
                            high_quality_img.save(img_buffer, format=image_format, quality=95, optimize=True)
                        elif image_format.upper() == 'PNG':
                            high_quality_img.save(img_buffer, format=image_format, optimize=True, compress_level=6)
                        else:  # TIFF
                            high_quality_img.save(img_buffer, format=image_format, compression='lzw')
                        
                        # Agregar al ZIP
                        zip_file.writestr(img_filename, img_buffer.getvalue())
                
                # Progreso final: guardando archivo
                if progress_callback:
                    progress_callback(total_pages, total_pages, "Guardando archivo ZIP...")
                
            # Progreso completado
            if progress_callback:
                progress_callback(total_pages, total_pages, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando como ZIP: {e}")
            return False
    
    def export_as_images_folder(self, page_manager: PageManager, output_folder: str, 
                               image_format: str = "PNG", progress_callback=None) -> bool:
        """Exportar páginas como imágenes en una carpeta"""
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            # Crear carpeta si no existe
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            base_name = Path(self.pdf_path).stem
            total_pages = len(active_pages)
            
            for i, page_info in enumerate(active_pages):
                if progress_callback:
                    progress_callback(i, total_pages, f"Procesando página {page_info.page_number}")
                
                # Renderizar página en alta calidad para exportación
                high_quality_img = self.render_page(page_info.page_number, for_export=True)
                
                if high_quality_img:
                    # Aplicar rotación si es necesaria
                    if page_info.rotation != 0:
                        high_quality_img = high_quality_img.rotate(-page_info.rotation, expand=True)
                    
                    # Crear nombre de archivo para la imagen
                    img_filename = f"{base_name}_pagina_{page_info.page_number:03d}.{image_format.lower()}"
                    img_path = Path(output_folder) / img_filename
                    
                    # Guardar imagen con configuraciones de calidad
                    if image_format.upper() == 'JPEG':
                        high_quality_img.save(img_path, format=image_format, quality=95, optimize=True)
                    elif image_format.upper() == 'PNG':
                        high_quality_img.save(img_path, format=image_format, optimize=True, compress_level=6)
                    else:  # TIFF
                        high_quality_img.save(img_path, format=image_format, compression='lzw')
                    
                    # Progreso actualizado después de guardar cada imagen
                    if progress_callback:
                        progress_callback(i + 1, total_pages, f"Guardada: {img_filename}")
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_pages, total_pages, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando a carpeta: {e}")
            return False
    
    def export_individual_pdfs(self, page_manager: PageManager, output_folder: str, progress_callback=None) -> bool:
        """Exportar cada página como PDF individual"""
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            # Crear carpeta si no existe
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            base_name = Path(self.pdf_path).stem
            total_pages = len(active_pages)
            
            for i, page_info in enumerate(active_pages):
                if progress_callback:
                    progress_callback(i, total_pages, f"Procesando página {page_info.page_number}")
                
                # Crear un nuevo PDF para esta página
                writer = PdfWriter()
                page = self.reader.pages[page_info.page_number - 1]
                
                # Aplicar rotación si es necesaria
                if page_info.rotation != 0:
                    page.rotate(page_info.rotation)
                
                writer.add_page(page)
                
                # Guardar PDF individual
                pdf_filename = f"{base_name}_pagina_{page_info.page_number:03d}.pdf"
                pdf_path = Path(output_folder) / pdf_filename
                
                with open(pdf_path, "wb") as f:
                    writer.write(f)
                
                # Progreso actualizado después de guardar cada PDF
                if progress_callback:
                    progress_callback(i + 1, total_pages, f"Guardado: {pdf_filename}")
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_pages, total_pages, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando PDFs individuales: {e}")
            return False
    
    def export_combined_pdf(self, page_manager: PageManager, output_path: str, progress_callback=None) -> bool:
        """Exportar páginas seleccionadas como un solo PDF"""
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            writer = PdfWriter()
            total_pages = len(active_pages)
            
            # Ordenar páginas por número
            sorted_pages = sorted(active_pages, key=lambda x: x.page_number)
            
            for i, page_info in enumerate(sorted_pages):
                if progress_callback:
                    progress_callback(i, total_pages, f"Procesando página {page_info.page_number}")
                
                page = self.reader.pages[page_info.page_number - 1]
                
                # Aplicar rotación si es necesaria
                if page_info.rotation != 0:
                    page.rotate(page_info.rotation)
                
                writer.add_page(page)
            
            # Crear directorio si no existe
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar PDF combinado
            if progress_callback:
                progress_callback(total_pages, total_pages, "Guardando PDF combinado...")
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_pages, total_pages, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando PDF combinado: {e}")
            return False
