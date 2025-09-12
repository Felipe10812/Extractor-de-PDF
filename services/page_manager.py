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

class PageManager:
    """Gestor de páginas con funcionalidades de rotación y eliminación"""
    
    def __init__(self):
        self.pages: Dict[int, PageInfo] = {}
        self.selected_pages: List[int] = []
    
    def add_page(self, page_number: int, image: Image.Image):
        """Agregar una página al gestor"""
        self.pages[page_number] = PageInfo(
            page_number=page_number,
            original_image=image,
            rotated_image=image.copy()
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
