import flet as ft
from PIL import Image
import io

class PreviewRenderer:
    def __init__(self, page: ft.Page):
        self.page = page
        self.preview_area = ft.Row(scroll=ft.ScrollMode.AUTO, expand=True)

    def get_control(self):
        return self.preview_area

    def render_previews(self, images: list[Image.Image]):
        self.preview_area.controls.clear()
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            import base64
            img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            self.preview_area.controls.append(
                ft.Image(src_base64=img_base64, width=200)
            )
        self.page.update()
        if not images:
            self.preview_area.controls.append(ft.Text("No hay páginas para previsualizar."))
            self.page.update()