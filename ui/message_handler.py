import flet as ft

class MessageHandler:
    def __init__(self, page: ft.Page):
        self.page = page

    def show(self, msg, color=ft.Colors.GREEN, icon=ft.Icons.CHECK_CIRCLE_OUTLINED):
        snack = ft.SnackBar(
            content=ft.Row([ft.Icon(icon, color="white"), ft.Text(msg, color="white")]),
            bgcolor=color,
            open=True,
            duration=3000
        )
        self.page.snack_bar = snack
        self.page.update()
