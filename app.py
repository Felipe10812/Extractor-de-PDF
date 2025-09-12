import os
from pathlib import Path
import flet as ft
from services.page_parser import PageParser
from services.pdf_service import PDFService
from ui.message_handler import MessageHandler
from ui.preview_renderer import PreviewRenderer

class PDFExtractorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.service: PDFService | None = None
        self.msg = MessageHandler(page)
        self.preview = PreviewRenderer(page)

        self._setup_controls()
        self._setup_layout()

    def _setup_controls(self):
        self.file_path_text = ft.TextField(label="Archivo PDF", read_only=True)
        self.pages_input = ft.TextField(label="Páginas (ej: 1,3,5-7)")
        self.folder_text = ft.TextField(label="Carpeta destino", read_only=True)
        self.extract_button = ft.ElevatedButton("Extraer", on_click=lambda e: self.extract())
        self.preview_button = ft.OutlinedButton("Previsualizar", on_click=lambda e: self.preview_pages())

        self.file_picker = ft.FilePicker(on_result=self.handle_file)
        self.folder_picker = ft.FilePicker(on_result=self.handle_folder)
        self.page.overlay.extend([self.file_picker, self.folder_picker])

    def _setup_layout(self):
        self.page.add(
            ft.Column([
                ft.Row([self.file_path_text, ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=lambda e: self.file_picker.pick_files(file_type="application/pdf"))]),
                ft.Row([self.folder_text, ft.IconButton(icon=ft.Icons.CREATE_NEW_FOLDER, on_click=lambda e: self.folder_picker.get_directory_path())]),
                self.pages_input,
                ft.Row([self.extract_button, self.preview_button]),
                ft.Divider(),
                ft.Text("Previsualización", size=20, weight=ft.FontWeight.BOLD),
                self.preview.get_control()
            ], scroll=ft.ScrollMode.AUTO)
        )

    def handle_file(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.file_path_text.value = e.files[0].path
            try:
                self.service = PDFService(self.file_path_text.value)
                self.msg.show(f"PDF cargado. Total páginas: {self.service.get_total_pages()}", ft.Colors.GREEN)
            except Exception as ex:
                self.msg.show(f"Error: {ex}", ft.Colors.RED, ft.Icons.ERROR)
        self.page.update()

    def handle_folder(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.folder_text.value = e.path
            self.page.update()

    def preview_pages(self):
        if not self.service:
            self.msg.show("Primero selecciona un PDF", ft.Colors.RED)
            return
        try:
            pages = PageParser.parse(self.pages_input.value)
            imgs = [self.service.render_page(p) for p in pages if p <= self.service.get_total_pages()]
            self.preview.render_previews(imgs)
        except Exception as ex:
            self.msg.show(f"Error en previsualización: {ex}", ft.Colors.RED)

    def extract(self):
        if not self.service:
            self.msg.show("Primero selecciona un PDF", ft.Colors.RED)
            return
        if not self.folder_text.value:
            self.msg.show("Selecciona carpeta de destino", ft.Colors.RED)
            return
        try:
            pages = PageParser.parse(self.pages_input.value)
            output_file = os.path.join(self.folder_text.value, f"{Path(self.file_path_text.value).stem}_extraidas.pdf")
            count = self.service.extract(pages, output_file)
            if count:
                self.msg.show(f"Guardado en {output_file}", ft.Colors.GREEN)
            else:
                self.msg.show("No se extrajeron páginas válidas", ft.Colors.RED)
        except Exception as ex:
            self.msg.show(f"Error: {ex}", ft.Colors.RED)
