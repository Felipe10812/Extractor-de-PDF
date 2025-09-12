from abc import ABC, abstractmethod
from PIL import Image

class DocumentService(ABC):
    @abstractmethod
    def get_total_pages(self) -> int:
        pass

    @abstractmethod
    def extract(self, pages: list[int], output_path: str) -> int:
        pass

    @abstractmethod
    def render_page(self, page_num: int, scale: float = 1.0) -> "Image.Image":
        """Devuelve un objeto PIL.Image para previsualización."""
        pass
