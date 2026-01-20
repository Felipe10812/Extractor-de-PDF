from dataclasses import dataclass
from typing import Dict, List
from PIL import Image

@dataclass
class PageInfo:
    """Información de una página específica"""
    page_number: int
    rotation: int = 0  # 0, 90, 180, 270 grados
    is_deleted: bool = False
    original_image: Image.Image = None
    rotated_image: Image.Image = None
    source_pdf: str = None  # Nombre del archivo PDF origen
    source_pdf_index: int = 0  # Índice del PDF en la lista de PDFs
    original_page_number: int = None  # Número de página dentro del PDF origen

class PageManager:
    """Gestor de páginas con funcionalidades de rotación y eliminación"""
    
    def __init__(self):
        self.pages: Dict[int, PageInfo] = {}
        self.selected_pages: List[int] = []
    
    def add_page(self, page_number: int, image: Image.Image, source_pdf: str = None, 
                 source_pdf_index: int = 0, original_page_number: int = None):
        """Agregar una página al gestor"""
        self.pages[page_number] = PageInfo(
            page_number=page_number,
            original_image=image,
            rotated_image=image.copy(),
            source_pdf=source_pdf,
            source_pdf_index=source_pdf_index,
            original_page_number=original_page_number if original_page_number is not None else page_number
        )
        if page_number not in self.selected_pages:
            self.selected_pages.append(page_number)
    
    def rotate_page(self, page_number: int, degrees: int = 90):
        """Rotar una página específica"""
        if page_number not in self.pages:
            return False
        
        page_info = self.pages[page_number]
        page_info.rotation = (page_info.rotation + degrees) % 360
        
        # Aplicar rotación a la imagen
        if page_info.original_image:
            if page_info.rotation == 0:
                page_info.rotated_image = page_info.original_image.copy()
            else:
                page_info.rotated_image = page_info.original_image.rotate(
                    -page_info.rotation, expand=True
                )
        
        return True
    
    def delete_page(self, page_number: int):
        """Marcar una página como eliminada"""
        if page_number in self.pages:
            self.pages[page_number].is_deleted = True
            if page_number in self.selected_pages:
                self.selected_pages.remove(page_number)
            return True
        return False
    
    def restore_page(self, page_number: int):
        """Restaurar una página eliminada"""
        if page_number in self.pages:
            self.pages[page_number].is_deleted = False
            if page_number not in self.selected_pages:
                self.selected_pages.append(page_number)
                self.selected_pages.sort()
            return True
        return False
    
    def get_active_pages(self) -> List[PageInfo]:
        """Obtener páginas activas (no eliminadas)"""
        return [
            page_info for page_info in self.pages.values()
            if not page_info.is_deleted
        ]
    
    def get_page_image(self, page_number: int) -> Image.Image:
        """Obtener imagen de una página (con rotaciones aplicadas)"""
        if page_number in self.pages and not self.pages[page_number].is_deleted:
            return self.pages[page_number].rotated_image
        return None
    
    def get_page_info(self, page_number: int) -> PageInfo:
        """Obtener información de una página"""
        return self.pages.get(page_number)
    
    def clear(self):
        """Limpiar todas las páginas"""
        self.pages.clear()
        self.selected_pages.clear()
    
    def get_selected_pages_count(self) -> int:
        """Obtener cantidad de páginas seleccionadas"""
        return len([p for p in self.pages.values() if not p.is_deleted])
    
    def get_pages_by_source(self, source_pdf_index: int) -> List[PageInfo]:
        """Obtener páginas de un PDF específico"""
        return [
            page_info for page_info in self.pages.values()
            if page_info.source_pdf_index == source_pdf_index and not page_info.is_deleted
        ]
    
    def get_unique_sources(self) -> List[tuple]:
        """Obtener lista única de PDFs fuente (índice, nombre)"""
        sources = {}
        for page_info in self.pages.values():
            if page_info.source_pdf and not page_info.is_deleted:
                sources[page_info.source_pdf_index] = page_info.source_pdf
        return sorted(sources.items())
    
    def move_page_up(self, page_number: int) -> bool:
        """Mover una página hacia arriba en el orden"""
        active_pages = self.get_active_pages()
        sorted_pages = sorted(active_pages, key=lambda x: x.page_number)
        
        # Encontrar índice de la página
        current_index = -1
        for i, page_info in enumerate(sorted_pages):
            if page_info.page_number == page_number:
                current_index = i
                break
        
        # Si está primera o no se encontró, no se puede mover
        if current_index <= 0:
            return False
        
        # Intercambiar números de página con la anterior
        current_page = sorted_pages[current_index]
        previous_page = sorted_pages[current_index - 1]
        
        temp_page_num = current_page.page_number
        current_page.page_number = previous_page.page_number
        previous_page.page_number = temp_page_num
        
        # Actualizar diccionario
        self.pages[current_page.page_number] = current_page
        self.pages[previous_page.page_number] = previous_page
        
        return True
    
    def move_page_down(self, page_number: int) -> bool:
        """Mover una página hacia abajo en el orden"""
        active_pages = self.get_active_pages()
        sorted_pages = sorted(active_pages, key=lambda x: x.page_number)
        
        # Encontrar índice de la página
        current_index = -1
        for i, page_info in enumerate(sorted_pages):
            if page_info.page_number == page_number:
                current_index = i
                break
        
        # Si está última o no se encontró, no se puede mover
        if current_index == -1 or current_index >= len(sorted_pages) - 1:
            return False
        
        # Intercambiar números de página con la siguiente
        current_page = sorted_pages[current_index]
        next_page = sorted_pages[current_index + 1]
        
        temp_page_num = current_page.page_number
        current_page.page_number = next_page.page_number
        next_page.page_number = temp_page_num
        
        # Actualizar diccionario
        self.pages[current_page.page_number] = current_page
        self.pages[next_page.page_number] = next_page
        
        return True
    
    def move_source_up(self, source_pdf_index: int) -> bool:
        """Mover todas las páginas de un PDF hacia arriba"""
        sources = self.get_unique_sources()
        if len(sources) < 2:
            return False
        
        # Encontrar posición de la fuente
        source_position = -1
        for i, (idx, _) in enumerate(sources):
            if idx == source_pdf_index:
                source_position = i
                break
        
        # Si está primera o no se encontró, no se puede mover
        if source_position <= 0:
            return False
        
        # Obtener páginas de ambas fuentes
        current_source_pages = self.get_pages_by_source(sources[source_position][0])
        previous_source_pages = self.get_pages_by_source(sources[source_position - 1][0])
        
        # Intercambiar rangos de números de página
        # Guardar números originales
        current_nums = [p.page_number for p in sorted(current_source_pages, key=lambda x: x.page_number)]
        previous_nums = [p.page_number for p in sorted(previous_source_pages, key=lambda x: x.page_number)]
        
        # Reasignar números
        sorted_current = sorted(current_source_pages, key=lambda x: x.page_number)
        sorted_previous = sorted(previous_source_pages, key=lambda x: x.page_number)
        
        # Eliminar del diccionario
        for p in sorted_current + sorted_previous:
            del self.pages[p.page_number]
        
        # Reasignar con nuevos números
        for i, page in enumerate(sorted_current):
            page.page_number = previous_nums[i] if i < len(previous_nums) else previous_nums[-1] + i - len(previous_nums) + 1
            self.pages[page.page_number] = page
        
        for i, page in enumerate(sorted_previous):
            page.page_number = current_nums[i] if i < len(current_nums) else current_nums[-1] + i - len(current_nums) + 1
            self.pages[page.page_number] = page
        
        return True
    
    def reorder_pages(self, new_order: List[int]):
        """Reordenar las páginas según una lista de números de página"""
        active_pages = self.get_active_pages()
        
        # Crear un mapa del número de página actual a la información de la página
        page_map = {p.page_number: p for p in active_pages}
        
        # Crear una nueva lista de páginas en el orden correcto
        ordered_pages = [page_map[p_num] for p_num in new_order if p_num in page_map]
        
        # Crear un nuevo diccionario de páginas con los números de página actualizados
        new_pages_dict = {}
        
        # Obtener todos los números de página para reasignar
        all_page_numbers = sorted(self.pages.keys())
        
        # Reasignar la información de la página a los nuevos números de página
        for i, page_info in enumerate(ordered_pages):
            new_page_number = all_page_numbers[i]
            
            # Actualizar el número de página
            page_info.page_number = new_page_number
            new_pages_dict[new_page_number] = page_info
            
        # Reemplazar el diccionario de páginas con el nuevo
        # Mantener las páginas eliminadas
        for page_num, page_info in self.pages.items():
            if page_info.is_deleted:
                new_pages_dict[page_num] = page_info
                
        self.pages = new_pages_dict
        
        # Actualizar la lista de páginas seleccionadas
        self.selected_pages = [p.page_number for p in self.get_active_pages()]
        self.selected_pages.sort()

    def move_source_down(self, source_pdf_index: int) -> bool:
        """Mover todas las páginas de un PDF hacia abajo"""
        sources = self.get_unique_sources()
        if len(sources) < 2:
            return False
        
        # Encontrar posición de la fuente
        source_position = -1
        for i, (idx, _) in enumerate(sources):
            if idx == source_pdf_index:
                source_position = i
                break
        
        # Si está última o no se encontró, no se puede mover
        if source_position == -1 or source_position >= len(sources) - 1:
            return False
        
        # Obtener páginas de ambas fuentes
        current_source_pages = self.get_pages_by_source(sources[source_position][0])
        next_source_pages = self.get_pages_by_source(sources[source_position + 1][0])
        
        # Intercambiar rangos de números de página
        current_nums = [p.page_number for p in sorted(current_source_pages, key=lambda x: x.page_number)]
        next_nums = [p.page_number for p in sorted(next_source_pages, key=lambda x: x.page_number)]
        
        # Reasignar números
        sorted_current = sorted(current_source_pages, key=lambda x: x.page_number)
        sorted_next = sorted(next_source_pages, key=lambda x: x.page_number)
        
        # Eliminar del diccionario
        for p in sorted_current + sorted_next:
            del self.pages[p.page_number]
        
        # Reasignar con nuevos números
        for i, page in enumerate(sorted_current):
            page.page_number = next_nums[i] if i < len(next_nums) else next_nums[-1] + i - len(next_nums) + 1
            self.pages[page.page_number] = page
        
        for i, page in enumerate(sorted_next):
            page.page_number = current_nums[i] if i < len(current_nums) else current_nums[-1] + i - len(current_nums) + 1
            self.pages[page.page_number] = page
        
        return True
