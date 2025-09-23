from pathlib import Path
from PIL import Image, ImageOps
import fitz  # PyMuPDF para crear PDFs
from typing import List, Dict, Tuple
from .document_service import DocumentService
from .page_manager import PageManager, PageInfo


class ImageService(DocumentService):
    """Servicio para manejar múltiples imágenes y convertirlas a PDF"""
    
    def __init__(self, image_paths: List[str]):
        self.image_paths = image_paths
        self.images_info = []
        self.total_pages = len(image_paths)
        
        # Cargar información básica de cada imagen
        self._load_images_info()
    
    def _load_images_info(self):
        """Cargar información básica de todas las imágenes"""
        self.images_info = []
        
        for i, path in enumerate(self.image_paths):
            try:
                with Image.open(path) as img:
                    info = {
                        'path': path,
                        'index': i + 1,  # Usar índice 1-based
                        'name': Path(path).name,
                        'format': img.format,
                        'size': img.size,
                        'mode': img.mode
                    }
                    self.images_info.append(info)
            except Exception as e:
                print(f"Error cargando imagen {path}: {e}")
                # Agregar info de error pero mantener la imagen en la lista
                info = {
                    'path': path,
                    'index': i + 1,
                    'name': Path(path).name,
                    'format': 'ERROR',
                    'size': (0, 0),
                    'mode': 'ERROR',
                    'error': str(e)
                }
                self.images_info.append(info)
        
        # Actualizar total de páginas basado en imágenes válidas
        self.total_pages = len([info for info in self.images_info if info['format'] != 'ERROR'])
    
    def get_total_pages(self) -> int:
        """Retornar número total de imágenes válidas"""
        return self.total_pages
    
    def get_images_info(self) -> List[Dict]:
        """Obtener información de todas las imágenes"""
        return self.images_info
    
    def render_page(self, page_num: int, scale: float = 1.0, for_export: bool = False):
        """Renderizar una imagen específica como PIL Image"""
        try:
            # Verificar que el número de página sea válido
            if page_num < 1 or page_num > len(self.images_info):
                return None
            
            image_info = self.images_info[page_num - 1]
            
            # Verificar que la imagen sea válida
            if image_info['format'] == 'ERROR':
                return None
            
            # Cargar la imagen
            img = Image.open(image_info['path'])
            
            # Convertir a RGB si es necesario (para PDFs)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Crear un fondo blanco para transparencias
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Aplicar escalado si es necesario
            if not for_export and scale != 1.0:
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            elif not for_export and img.width > 300:
                # Para preview: redimensionar para eficiencia
                ratio = 300 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((300, new_height), Image.Resampling.LANCZOS)
            
            return img
            
        except Exception as e:
            print(f"Error renderizando imagen {page_num}: {e}")
            return None
    
    def extract(self, pages: list[int], output_path: str) -> int:
        """Método heredado - no aplicable para imágenes"""
        # Este método no es relevante para imágenes individuales
        # Las imágenes se "extraen" copiándolas o convirtiéndolas
        return 0
    
    def convert_to_pdf(self, page_manager: PageManager, output_path: str, 
                      page_size: str = "A4", orientation: str = "portrait",
                      fit_mode: str = "fit", progress_callback=None) -> bool:
        """
        Convertir imágenes seleccionadas a un PDF
        
        Args:
            page_manager: Manager con páginas seleccionadas
            output_path: Ruta del PDF de salida
            page_size: Tamaño de página ("A4", "Letter", "Legal", "A3", "A5")
            orientation: Orientación ("portrait", "landscape")
            fit_mode: Modo de ajuste ("fit", "fill", "stretch")
            progress_callback: Callback para progreso
        """
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            # Definir tamaños de página en puntos (72 DPI)
            page_sizes = {
                "A4": (595, 842),
                "Letter": (612, 792),
                "Legal": (612, 1008),
                "A3": (842, 1191),
                "A5": (420, 595)
            }
            
            base_size = page_sizes.get(page_size, page_sizes["A4"])
            
            # Aplicar orientación
            if orientation == "landscape":
                page_width, page_height = base_size[1], base_size[0]
            else:
                page_width, page_height = base_size[0], base_size[1]
            
            # Crear documento PDF con PyMuPDF
            pdf_doc = fitz.open()
            
            total_images = len(active_pages)
            
            for i, page_info in enumerate(active_pages):
                if progress_callback:
                    progress_callback(i, total_images, f"Procesando imagen {page_info.page_number}")
                
                # Obtener imagen en alta calidad
                img = self.render_page(page_info.page_number, for_export=True)
                
                if not img:
                    continue
                
                # Aplicar rotación si es necesaria
                if page_info.rotation != 0:
                    img = img.rotate(-page_info.rotation, expand=True)
                
                # Convertir PIL Image a bytes
                from io import BytesIO
                img_buffer = BytesIO()
                img.save(img_buffer, format='JPEG', quality=90)
                img_bytes = img_buffer.getvalue()
                
                # Crear nueva página en el PDF
                page = pdf_doc.new_page(width=page_width, height=page_height)
                
                # Calcular dimensiones para ajustar la imagen
                img_width, img_height = img.size
                
                if fit_mode == "fit":
                    # Ajustar manteniendo proporción (letterbox)
                    scale_x = page_width / img_width
                    scale_y = page_height / img_height
                    scale = min(scale_x, scale_y)
                    
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    # Centrar la imagen
                    x_offset = (page_width - new_width) / 2
                    y_offset = (page_height - new_height) / 2
                    
                elif fit_mode == "fill":
                    # Llenar la página completa (crop si es necesario)
                    scale_x = page_width / img_width
                    scale_y = page_height / img_height
                    scale = max(scale_x, scale_y)
                    
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    # Centrar y recortar
                    x_offset = (page_width - new_width) / 2
                    y_offset = (page_height - new_height) / 2
                    
                else:  # stretch
                    # Estirar para llenar completamente (puede deformar)
                    new_width = page_width
                    new_height = page_height
                    x_offset = 0
                    y_offset = 0
                
                # Definir rectángulo donde insertar la imagen
                img_rect = fitz.Rect(x_offset, y_offset, x_offset + new_width, y_offset + new_height)
                
                # Insertar imagen en la página
                page.insert_image(img_rect, stream=img_bytes)
            
            # Progreso: guardando archivo
            if progress_callback:
                progress_callback(total_images, total_images, "Guardando PDF...")
            
            # Crear directorio si no existe
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar PDF
            pdf_doc.save(output_path)
            pdf_doc.close()
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_images, total_images, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error convirtiendo imágenes a PDF: {e}")
            return False
    
    def convert_to_individual_pdfs_zip(self, page_manager: PageManager, output_path: str, 
                                      page_size: str = "A4", orientation: str = "portrait",
                                      fit_mode: str = "fit", progress_callback=None) -> bool:
        """
        Convertir cada imagen seleccionada en un PDF individual y comprimirlos en ZIP
        
        Args:
            page_manager: Manager con páginas seleccionadas
            output_path: Ruta del archivo ZIP de salida
            page_size: Tamaño de página ("A4", "Letter", "Legal", "A3", "A5")
            orientation: Orientación ("portrait", "landscape")
            fit_mode: Modo de ajuste ("fit", "fill", "stretch")
            progress_callback: Callback para progreso
        """
        import zipfile
        import tempfile
        
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            # Definir tamaños de página en puntos (72 DPI)
            page_sizes = {
                "A4": (595, 842),
                "Letter": (612, 792),
                "Legal": (612, 1008),
                "A3": (842, 1191),
                "A5": (420, 595)
            }
            
            base_size = page_sizes.get(page_size, page_sizes["A4"])
            
            # Aplicar orientación
            if orientation == "landscape":
                page_width, page_height = base_size[1], base_size[0]
            else:
                page_width, page_height = base_size[0], base_size[1]
            
            total_images = len(active_pages)
            
            # Crear ZIP para los PDFs
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, page_info in enumerate(active_pages):
                    if progress_callback:
                        progress_callback(i, total_images, f"Creando PDF de imagen {page_info.page_number}")
                    
                    # Obtener imagen en alta calidad
                    img = self.render_page(page_info.page_number, for_export=True)
                    
                    if not img:
                        continue
                    
                    # Aplicar rotación si es necesaria
                    if page_info.rotation != 0:
                        img = img.rotate(-page_info.rotation, expand=True)
                    
                    # Crear PDF individual con PyMuPDF
                    pdf_doc = fitz.open()
                    page = pdf_doc.new_page(width=page_width, height=page_height)
                    
                    # Convertir PIL Image a bytes
                    from io import BytesIO
                    img_buffer = BytesIO()
                    img.save(img_buffer, format='JPEG', quality=90)
                    img_bytes = img_buffer.getvalue()
                    
                    # Calcular dimensiones para ajustar la imagen
                    img_width, img_height = img.size
                    
                    if fit_mode == "fit":
                        # Ajustar manteniendo proporción (letterbox)
                        scale_x = page_width / img_width
                        scale_y = page_height / img_height
                        scale = min(scale_x, scale_y)
                        
                        new_width = img_width * scale
                        new_height = img_height * scale
                        
                        # Centrar la imagen
                        x_offset = (page_width - new_width) / 2
                        y_offset = (page_height - new_height) / 2
                        
                    elif fit_mode == "fill":
                        # Llenar la página completa (crop si es necesario)
                        scale_x = page_width / img_width
                        scale_y = page_height / img_height
                        scale = max(scale_x, scale_y)
                        
                        new_width = img_width * scale
                        new_height = img_height * scale
                        
                        # Centrar y recortar
                        x_offset = (page_width - new_width) / 2
                        y_offset = (page_height - new_height) / 2
                        
                    else:  # stretch
                        # Estirar para llenar completamente (puede deformar)
                        new_width = page_width
                        new_height = page_height
                        x_offset = 0
                        y_offset = 0
                    
                    # Definir rectángulo donde insertar la imagen
                    img_rect = fitz.Rect(x_offset, y_offset, x_offset + new_width, y_offset + new_height)
                    
                    # Insertar imagen en la página
                    page.insert_image(img_rect, stream=img_bytes)
                    
                    # Crear nombre de archivo PDF
                    if page_info.page_number <= len(self.images_info):
                        img_info = self.images_info[page_info.page_number - 1]
                        original_name = Path(img_info['name']).stem
                        pdf_filename = f"{original_name}_{page_info.page_number:03d}.pdf"
                    else:
                        pdf_filename = f"imagen_{page_info.page_number:03d}.pdf"
                    
                    # Convertir PDF a bytes y agregarlo al ZIP
                    pdf_bytes = pdf_doc.tobytes()
                    zip_file.writestr(pdf_filename, pdf_bytes)
                    
                    # Cerrar documento PDF
                    pdf_doc.close()
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_images, total_images, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error convirtiendo imágenes a PDFs individuales (ZIP): {e}")
            return False
    
    def convert_to_individual_pdfs_folder(self, page_manager: PageManager, output_folder: str, 
                                         page_size: str = "A4", orientation: str = "portrait",
                                         fit_mode: str = "fit", progress_callback=None) -> bool:
        """
        Convertir cada imagen seleccionada en un PDF individual y guardarlos en una carpeta
        
        Args:
            page_manager: Manager con páginas seleccionadas
            output_folder: Carpeta de destino para los PDFs
            page_size: Tamaño de página ("A4", "Letter", "Legal", "A3", "A5")
            orientation: Orientación ("portrait", "landscape")
            fit_mode: Modo de ajuste ("fit", "fill", "stretch")
            progress_callback: Callback para progreso
        """
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            # Crear carpeta si no existe
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            # Definir tamaños de página en puntos (72 DPI)
            page_sizes = {
                "A4": (595, 842),
                "Letter": (612, 792),
                "Legal": (612, 1008),
                "A3": (842, 1191),
                "A5": (420, 595)
            }
            
            base_size = page_sizes.get(page_size, page_sizes["A4"])
            
            # Aplicar orientación
            if orientation == "landscape":
                page_width, page_height = base_size[1], base_size[0]
            else:
                page_width, page_height = base_size[0], base_size[1]
            
            total_images = len(active_pages)
            
            for i, page_info in enumerate(active_pages):
                if progress_callback:
                    progress_callback(i, total_images, f"Creando PDF de imagen {page_info.page_number}")
                
                # Obtener imagen en alta calidad
                img = self.render_page(page_info.page_number, for_export=True)
                
                if not img:
                    continue
                
                # Aplicar rotación si es necesaria
                if page_info.rotation != 0:
                    img = img.rotate(-page_info.rotation, expand=True)
                
                # Crear PDF individual con PyMuPDF
                pdf_doc = fitz.open()
                page = pdf_doc.new_page(width=page_width, height=page_height)
                
                # Convertir PIL Image a bytes
                from io import BytesIO
                img_buffer = BytesIO()
                img.save(img_buffer, format='JPEG', quality=90)
                img_bytes = img_buffer.getvalue()
                
                # Calcular dimensiones para ajustar la imagen
                img_width, img_height = img.size
                
                if fit_mode == "fit":
                    # Ajustar manteniendo proporción (letterbox)
                    scale_x = page_width / img_width
                    scale_y = page_height / img_height
                    scale = min(scale_x, scale_y)
                    
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    # Centrar la imagen
                    x_offset = (page_width - new_width) / 2
                    y_offset = (page_height - new_height) / 2
                    
                elif fit_mode == "fill":
                    # Llenar la página completa (crop si es necesario)
                    scale_x = page_width / img_width
                    scale_y = page_height / img_height
                    scale = max(scale_x, scale_y)
                    
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    # Centrar y recortar
                    x_offset = (page_width - new_width) / 2
                    y_offset = (page_height - new_height) / 2
                    
                else:  # stretch
                    # Estirar para llenar completamente (puede deformar)
                    new_width = page_width
                    new_height = page_height
                    x_offset = 0
                    y_offset = 0
                
                # Definir rectángulo donde insertar la imagen
                img_rect = fitz.Rect(x_offset, y_offset, x_offset + new_width, y_offset + new_height)
                
                # Insertar imagen en la página
                page.insert_image(img_rect, stream=img_bytes)
                
                # Crear nombre de archivo PDF y ruta completa
                if page_info.page_number <= len(self.images_info):
                    img_info = self.images_info[page_info.page_number - 1]
                    original_name = Path(img_info['name']).stem
                    pdf_filename = f"{original_name}_{page_info.page_number:03d}.pdf"
                else:
                    pdf_filename = f"imagen_{page_info.page_number:03d}.pdf"
                
                pdf_path = Path(output_folder) / pdf_filename
                
                # Guardar PDF
                pdf_doc.save(str(pdf_path))
                pdf_doc.close()
                
                # Progreso actualizado
                if progress_callback:
                    progress_callback(i + 1, total_images, f"Guardado: {pdf_filename}")
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_images, total_images, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error convirtiendo imágenes a PDFs individuales (carpeta): {e}")
            return False
    
    def preview_pdf_pages(self, page_manager: PageManager, page_size: str = "A4", 
                         orientation: str = "portrait", fit_mode: str = "fit") -> List[Image.Image]:
        """
        Generar previsualizaciones de cómo se verán las imágenes en el PDF
        
        Args:
            page_manager: Manager con páginas seleccionadas
            page_size: Tamaño de página ("A4", "Letter", "Legal", "A3", "A5")
            orientation: Orientación ("portrait", "landscape")
            fit_mode: Modo de ajuste ("fit", "fill", "stretch")
            
        Returns:
            Lista de imágenes PIL representando cada página del PDF
        """
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return []
            
            # Definir tamaños de página en puntos (72 DPI)
            page_sizes = {
                "A4": (595, 842),
                "Letter": (612, 792),
                "Legal": (612, 1008),
                "A3": (842, 1191),
                "A5": (420, 595)
            }
            
            base_size = page_sizes.get(page_size, page_sizes["A4"])
            
            # Aplicar orientación
            if orientation == "landscape":
                page_width, page_height = base_size[1], base_size[0]
            else:
                page_width, page_height = base_size[0], base_size[1]
            
            # Escalar para preview (reducir el tamaño para mejor rendimiento)
            preview_scale = 0.3  # 30% del tamaño real
            preview_width = int(page_width * preview_scale)
            preview_height = int(page_height * preview_scale)
            
            preview_images = []
            
            for page_info in active_pages:
                # Obtener imagen original
                img = self.render_page(page_info.page_number, for_export=False)
                
                if not img:
                    continue
                
                # Aplicar rotación si es necesaria
                if page_info.rotation != 0:
                    img = img.rotate(-page_info.rotation, expand=True)
                
                # Crear lienzo de página (fondo blanco)
                page_canvas = Image.new('RGB', (preview_width, preview_height), (255, 255, 255))
                
                # Calcular dimensiones para ajustar la imagen
                img_width, img_height = img.size
                
                if fit_mode == "fit":
                    # Ajustar manteniendo proporción (letterbox)
                    scale_x = preview_width / img_width
                    scale_y = preview_height / img_height
                    scale = min(scale_x, scale_y)
                    
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    
                    # Centrar la imagen
                    x_offset = (preview_width - new_width) // 2
                    y_offset = (preview_height - new_height) // 2
                    
                elif fit_mode == "fill":
                    # Llenar la página completa (crop si es necesario)
                    scale_x = preview_width / img_width
                    scale_y = preview_height / img_height
                    scale = max(scale_x, scale_y)
                    
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    
                    # Centrar y recortar
                    x_offset = (preview_width - new_width) // 2
                    y_offset = (preview_height - new_height) // 2
                    
                else:  # stretch
                    # Estirar para llenar completamente (puede deformar)
                    new_width = preview_width
                    new_height = preview_height
                    x_offset = 0
                    y_offset = 0
                
                # Redimensionar imagen
                if fit_mode == "stretch":
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Para modo "fill", puede que necesitemos recortar
                if fit_mode == "fill" and (new_width > preview_width or new_height > preview_height):
                    # Calcular el área de recorte
                    crop_x = max(0, (new_width - preview_width) // 2)
                    crop_y = max(0, (new_height - preview_height) // 2)
                    crop_box = (
                        crop_x,
                        crop_y,
                        crop_x + min(new_width, preview_width),
                        crop_y + min(new_height, preview_height)
                    )
                    resized_img = resized_img.crop(crop_box)
                    new_width = resized_img.width
                    new_height = resized_img.height
                    x_offset = 0
                    y_offset = 0
                
                # Pegar imagen en el lienzo
                if x_offset >= 0 and y_offset >= 0:
                    page_canvas.paste(resized_img, (x_offset, y_offset))
                else:
                    # Si hay offsets negativos, necesitamos ajustar
                    paste_x = max(0, x_offset)
                    paste_y = max(0, y_offset)
                    crop_left = max(0, -x_offset)
                    crop_top = max(0, -y_offset)
                    
                    if crop_left > 0 or crop_top > 0:
                        crop_box = (
                            crop_left,
                            crop_top,
                            min(resized_img.width, crop_left + preview_width - paste_x),
                            min(resized_img.height, crop_top + preview_height - paste_y)
                        )
                        cropped_img = resized_img.crop(crop_box)
                        page_canvas.paste(cropped_img, (paste_x, paste_y))
                    else:
                        page_canvas.paste(resized_img, (paste_x, paste_y))
                
                # Agregar borde para simular página
                from PIL import ImageDraw
                draw = ImageDraw.Draw(page_canvas)
                draw.rectangle([(0, 0), (preview_width-1, preview_height-1)], outline=(200, 200, 200), width=1)
                
                preview_images.append(page_canvas)
            
            return preview_images
            
        except Exception as e:
            print(f"Error generando previsualización PDF: {e}")
            return []
    
    def export_as_images_zip(self, page_manager: PageManager, output_path: str, 
                            image_format: str = "PNG", progress_callback=None) -> bool:
        """Exportar imágenes seleccionadas como ZIP (copia las originales)"""
        import zipfile
        
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                total_images = len(active_pages)
                
                for i, page_info in enumerate(active_pages):
                    if progress_callback:
                        progress_callback(i, total_images, f"Procesando imagen {page_info.page_number}")
                    
                    # Obtener información de la imagen original
                    if page_info.page_number <= len(self.images_info):
                        img_info = self.images_info[page_info.page_number - 1]
                        
                        if img_info['format'] != 'ERROR':
                            # Cargar imagen
                            img = self.render_page(page_info.page_number, for_export=True)
                            
                            if img:
                                # Aplicar rotación si es necesaria
                                if page_info.rotation != 0:
                                    img = img.rotate(-page_info.rotation, expand=True)
                                
                                # Crear nombre de archivo
                                original_name = Path(img_info['name']).stem
                                new_filename = f"{original_name}_{page_info.page_number:03d}.{image_format.lower()}"
                                
                                # Guardar imagen en memoria
                                from io import BytesIO
                                img_buffer = BytesIO()
                                
                                if image_format.upper() == 'JPEG':
                                    img.save(img_buffer, format=image_format, quality=95, optimize=True)
                                elif image_format.upper() == 'PNG':
                                    img.save(img_buffer, format=image_format, optimize=True, compress_level=6)
                                else:  # TIFF
                                    img.save(img_buffer, format=image_format, compression='lzw')
                                
                                # Agregar al ZIP
                                zip_file.writestr(new_filename, img_buffer.getvalue())
                
                # Progreso final
                if progress_callback:
                    progress_callback(total_images, total_images, "Guardando archivo ZIP...")
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_images, total_images, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando imágenes como ZIP: {e}")
            return False
    
    def export_as_images_folder(self, page_manager: PageManager, output_folder: str, 
                               image_format: str = "PNG", progress_callback=None) -> bool:
        """Exportar imágenes seleccionadas a una carpeta"""
        try:
            active_pages = page_manager.get_active_pages()
            if not active_pages:
                return False
            
            # Crear carpeta si no existe
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            total_images = len(active_pages)
            
            for i, page_info in enumerate(active_pages):
                if progress_callback:
                    progress_callback(i, total_images, f"Procesando imagen {page_info.page_number}")
                
                # Obtener información de la imagen original
                if page_info.page_number <= len(self.images_info):
                    img_info = self.images_info[page_info.page_number - 1]
                    
                    if img_info['format'] != 'ERROR':
                        # Cargar imagen
                        img = self.render_page(page_info.page_number, for_export=True)
                        
                        if img:
                            # Aplicar rotación si es necesaria
                            if page_info.rotation != 0:
                                img = img.rotate(-page_info.rotation, expand=True)
                            
                            # Crear nombre de archivo
                            original_name = Path(img_info['name']).stem
                            new_filename = f"{original_name}_{page_info.page_number:03d}.{image_format.lower()}"
                            img_path = Path(output_folder) / new_filename
                            
                            # Guardar imagen
                            if image_format.upper() == 'JPEG':
                                img.save(img_path, format=image_format, quality=95, optimize=True)
                            elif image_format.upper() == 'PNG':
                                img.save(img_path, format=image_format, optimize=True, compress_level=6)
                            else:  # TIFF
                                img.save(img_path, format=image_format, compression='lzw')
                            
                            # Progreso actualizado
                            if progress_callback:
                                progress_callback(i + 1, total_images, f"Guardada: {new_filename}")
            
            # Progreso completado
            if progress_callback:
                progress_callback(total_images, total_images, "Completado")
            
            return True
            
        except Exception as e:
            print(f"Error exportando imágenes a carpeta: {e}")
            return False
