import flet as ft
from app import PDFExtractorApp

def main(page: ft.Page):
    page.title = "PDF Extractor (SOLID)"
    PDFExtractorApp(page)

if __name__ == "__main__":
    ft.app(target=main)
