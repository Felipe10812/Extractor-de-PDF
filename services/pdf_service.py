from pathlib import Path
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
from PIL import Image
from .document_service import DocumentService

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

    def render_page(self, page_num: int, scale: float = 1.0):
        """Convierte página en imagen PIL para preview."""
        try:
            # Abrir el documento con PyMuPDF
            doc = fitz.open(self.pdf_path)
            
            # Verificar que la página existe (PyMuPDF usa índice basado en 0)
            if page_num < 1 or page_num > len(doc):
                doc.close()
                return None
            
            # Obtener la página (convertir a índice basado en 0)
            page = doc[page_num - 1]
            
            # Crear una matriz de transformación para el escalado
            mat = fitz.Matrix(scale, scale)
            
            # Renderizar la página como imagen
            pix = page.get_pixmap(matrix=mat)
            
            # Convertir a bytes PNG
            img_data = pix.tobytes("png")
            
            # Convertir a PIL Image
            from io import BytesIO
            img = Image.open(BytesIO(img_data))
            
            # Redimensionar para preview (ancho máximo 300px)
            if img.width > 300:
                ratio = 300 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((300, new_height), Image.Resampling.LANCZOS)
            
            doc.close()
            return img
            
        except Exception as e:
            print(f"Error renderizando página {page_num}: {e}")
            return None
