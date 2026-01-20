from pathlib import Path
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Dict, Tuple
from .document_service import DocumentService
from .page_manager import PageManager, PageInfo


class PDFInfo:
    """Información de un PDF individual en el merger"""
    def __init__(self, path: str, index: int):
        self.path = path
        self.index = index
        self.name = Path(path).name
        self.reader = PdfReader(path)
        self.total_pages = len(self.reader.pages)
        self.start_page = 0  # Página global de inicio (se asigna después)
        self.end_page = 0    # Página global de fin (se asigna después)


class PDFMergerService(DocumentService):
    """Servicio para unir múltiples archivos PDF"""
    
    def __init__(self, pdf_paths: List[str]):
        self.pdf_paths = pdf_paths
        self.pdfs: List[PDFInfo] = []
        self.total_pages = 0
        
        # Inicializar información de cada PDF
        current_page = 1
        for i, path in enumerate(pdf_paths):
            pdf_info = PDFInfo(path, i)
            pdf_info.start_page = current_page
            pdf_info.end_page = current_page + pdf_info.total_pages - 1
            self.pdfs.append(pdf_info)
            current_page = pdf_info.end_page + 1
        
        self.total_pages = current_page - 1
    
    def get_total_pages(self) -> int:
        """Retorna el total de páginas de todos los PDFs"""
        return self.total_pages
    
    def get_pdf_count(self) -> int:
        """Retorna la cantidad de PDFs cargados"""
        return len(self.pdfs)
    
    def get_pdf_info(self, index: int) -> PDFInfo:
        """Obtiene información de un PDF específico"""
        if 0 <= index < len(self.pdfs):
            return self.pdfs[index]
        return None
    
    def get_all_pdf_info(self) -> List[PDFInfo]:
        """Obtiene información de todos los PDFs"""
        return self.pdfs
    
    def _find_pdf_for_page(self, global_page_num: int) -> Tuple[PDFInfo, int]:
        """
        Encuentra el PDF que contiene la página global y retorna el PDF y el número de página local
        Returns: (PDFInfo, local_page_number) o (None, 0) si no se encuentra
        """
        for pdf_info in self.pdfs:
            if pdf_info.start_page <= global_page_num <= pdf_info.end_page:
                local_page = global_page_num - pdf_info.start_page + 1
                return pdf_info, local_page
        return None, 0
    
    def extract(self, pages: list[int], output_path: str) -> int:
        """Extrae páginas específicas y las guarda en un nuevo PDF"""
        try:
            writer = PdfWriter()
            pages_found = 0
            
            for page_num in pages:
                pdf_info, local_page = self._find_pdf_for_page(page_num)
                if pdf_info and 1 <= local_page <= pdf_info.total_pages:
                    try:
                        writer.add_page(pdf_info.reader.pages[local_page - 1])
                        pages_found += 1
                    except Exception as e:
                        print(f"Error al añadir página {page_num}: {e}")
            
            if pages_found > 0:
                output_dir = Path(output_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, "wb") as f:
                    writer.write(f)
            
            return pages_found
            
        except Exception as e:
            print(f"Error en extract(): {e}")
            raise e
    
    def render_page(self, page_num: int, scale: float = 1.0, for_export: bool = False):
        """Renderiza una página específica como imagen PIL"""
        try:
            pdf_info, local_page = self._find_pdf_for_page(page_num)
            if not pdf_info:
                return None
            
            # Abrir el documento con PyMuPDF
            doc = fitz.open(pdf_info.path)
            
            # Verificar que la página existe
            if local_page < 1 or local_page > len(doc):
                doc.close()
                return None
            
            # Obtener la página (convertir a índice basado en 0)
            page = doc[local_page - 1]
            
            # Determinar escalado según el propósito
            if for_export:
                target_scale = 4.17  # 300 DPI / 72 DPI
            else:
                target_scale = 2.0 if scale == 1.0 else scale
            
            # Crear matriz de transformación
            mat = fitz.Matrix(target_scale, target_scale)
            
            # Renderizar la página
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
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
    
    def export_combined_pdf(self, page_manager: PageManager, output_path: str, progress_callback=None) -> bool:
        """Exporta páginas seleccionadas como un solo PDF combinado"""
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
                
                # Encontrar el PDF y página local
                pdf_info, local_page = self._find_pdf_for_page(page_info.page_number)
                
                if pdf_info and 1 <= local_page <= pdf_info.total_pages:
                    page = pdf_info.reader.pages[local_page - 1]
                    
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
    
    def export_as_images_zip(self, page_manager: PageManager, output_path: str, 
                            image_format: str = "PNG", progress_callback=None) -> bool:
        """Exporta páginas como imágenes en un archivo ZIP"""
        try:
            import zipfile
            
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            base_name = "merged_pdfs"
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                total_pages = len(active_pages)
                
                for i, page_info in enumerate(active_pages):
                    if progress_callback:
                        progress_callback(i, total_pages, f"Procesando página {page_info.page_number}")
                    
                    # Renderizar página en alta calidad
                    high_quality_img = self.render_page(page_info.page_number, for_export=True)
                    
                    if high_quality_img:
                        # Aplicar rotación si es necesaria
                        if page_info.rotation != 0:
                            high_quality_img = high_quality_img.rotate(-page_info.rotation, expand=True)
                        
                        # Crear nombre de archivo
                        img_filename = f"{base_name}_pagina_{page_info.page_number:03d}.{image_format.lower()}"
                        
                        # Guardar imagen en memoria
                        from io import BytesIO
                        img_buffer = BytesIO()
                        
                        if image_format.upper() == 'JPEG':
                            high_quality_img.save(img_buffer, format=image_format, quality=95, optimize=True)
                        elif image_format.upper() == 'PNG':
                            high_quality_img.save(img_buffer, format=image_format, optimize=True, compress_level=6)
                        else:  # TIFF
                            high_quality_img.save(img_buffer, format=image_format, compression='lzw')
                        
                        # Agregar al ZIP
                        zip_file.writestr(img_filename, img_buffer.getvalue())
                
                if progress_callback:
                    progress_callback(total_pages, total_pages, "Guardando archivo ZIP...")
            
            if progress_callback:
                progress_callback(total_pages, total_pages, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando como ZIP: {e}")
            return False
    
    def export_as_images_folder(self, page_manager: PageManager, output_folder: str, 
                               image_format: str = "PNG", progress_callback=None) -> bool:
        """Exporta páginas como imágenes en una carpeta"""
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            # Crear carpeta si no existe
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            base_name = "merged_pdfs"
            total_pages = len(active_pages)
            
            for i, page_info in enumerate(active_pages):
                if progress_callback:
                    progress_callback(i, total_pages, f"Procesando página {page_info.page_number}")
                
                # Renderizar página en alta calidad
                high_quality_img = self.render_page(page_info.page_number, for_export=True)
                
                if high_quality_img:
                    # Aplicar rotación si es necesaria
                    if page_info.rotation != 0:
                        high_quality_img = high_quality_img.rotate(-page_info.rotation, expand=True)
                    
                    # Crear nombre de archivo
                    img_filename = f"{base_name}_pagina_{page_info.page_number:03d}.{image_format.lower()}"
                    img_path = Path(output_folder) / img_filename
                    
                    # Guardar imagen
                    if image_format.upper() == 'JPEG':
                        high_quality_img.save(img_path, format=image_format, quality=95, optimize=True)
                    elif image_format.upper() == 'PNG':
                        high_quality_img.save(img_path, format=image_format, optimize=True, compress_level=6)
                    else:  # TIFF
                        high_quality_img.save(img_path, format=image_format, compression='lzw')
                    
                    if progress_callback:
                        progress_callback(i + 1, total_pages, f"Guardada: {img_filename}")
            
            if progress_callback:
                progress_callback(total_pages, total_pages, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando a carpeta: {e}")
            return False
