import flet as ft
import os
import subprocess
from pathlib import Path
from typing import Optional

class NotificationSystem:
    """Sistema de notificaciones del sistema operativo"""
    
    @staticmethod
    def show_notification(title: str, message: str, icon: str = "info"):
        """
        Mostrar notificación del sistema
        
        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            icon: Tipo de icono (info, success, error, warning)
        """
        try:
            # Usar plyer para notificaciones multiplataforma
            from plyer import notification
            
            # Determinar ícono según el tipo
            app_icon = None  # Por defecto sin ícono personalizado
            
            notification.notify(
                title=title,
                message=message,
                timeout=5,  # 5 segundos
                app_name="PDF Extractor Advanced",
                app_icon=app_icon
            )
        except Exception as e:
            print(f"Error mostrando notificación: {e}")
            # Fallback: usar notificación nativa de Windows si plyer falla
            NotificationSystem._windows_native_notification(title, message)
    
    @staticmethod
    def _windows_native_notification(title: str, message: str):
        """Notificación nativa de Windows como fallback"""
        try:
            # Usar PowerShell para mostrar notificación toast en Windows
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{title}</text>
                        <text id="2">{message}</text>
                    </binding>
                </visual>
            </toast>
"@
            
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            $toast.Tag = "PDF-Extractor"
            $toast.Group = "PDF-Extractor"
            
            $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("PDF Extractor Advanced")
            $notifier.Show($toast)
            '''
            
            # CRÍTICO: Usar CREATE_NO_WINDOW para evitar que la ventana de PowerShell aparezca
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NO_WINDOW

            subprocess.run([
                "powershell", "-Command", ps_script
            ], capture_output=True, text=True, timeout=5,
            creationflags=creation_flags)
            
        except Exception as e:
            print(f"Error en notificación Windows nativa: {e}")
    
    @staticmethod
    def show_completion_notification(operation: str, output_path: str, count: int = 0):
        """
        Mostrar notificación de operación completada con opción de abrir carpeta
        
        Args:
            operation: Tipo de operación (ej: "Exportación", "Extracción")
            output_path: Ruta donde se guardaron los archivos
            count: Número de elementos procesados
        """
        try:
            path_obj = Path(output_path)
            
            if path_obj.is_file():
                # Si es un archivo, mostrar el nombre del archivo
                file_name = path_obj.name
                folder_path = str(path_obj.parent)
                message = f"Archivo guardado: {file_name}"
            else:
                # Si es una carpeta, mostrar el nombre de la carpeta
                folder_name = path_obj.name
                folder_path = str(path_obj)
                if count > 0:
                    message = f"{count} archivos guardados en: {folder_name}"
                else:
                    message = f"Archivos guardados en: {folder_name}"
            
            # Mostrar notificación
            NotificationSystem.show_notification(
                title=f"✅ {operation} Completada",
                message=message,
                icon="success"
            )
            
        except Exception as e:
            print(f"Error en notificación de completación: {e}")
            # Fallback básico
            NotificationSystem.show_notification(
                title=f"✅ {operation} Completada",
                message="Los archivos se han guardado exitosamente",
                icon="success"
            )
    
    @staticmethod
    def show_error_notification(operation: str, error_message: str):
        """
        Mostrar notificación de error
        
        Args:
            operation: Tipo de operación que falló
            error_message: Mensaje de error
        """
        NotificationSystem.show_notification(
            title=f"❌ Error en {operation}",
            message=error_message,
            icon="error"
        )
    
    @staticmethod
    def show_start_notification(operation: str, details: str = ""):
        """
        Mostrar notificación de inicio de operación
        
        Args:
            operation: Tipo de operación que inicia
            details: Detalles adicionales
        """
        message = f"Iniciando {operation.lower()}..."
        if details:
            message += f"\n{details}"
            
        NotificationSystem.show_notification(
            title=f"🚀 {operation} Iniciada",
            message=message,
            icon="info"
        )

class CompletionDialog:
    """Diálogo de completación con opción de abrir carpeta"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.output_path = ""
        
    def show_completion_dialog(self, operation: str, output_path: str, count: int = 0):
        """Mostrar diálogo de operación completada"""
        self.output_path = output_path
        path_obj = Path(output_path)
        
        if path_obj.is_file():
            file_name = path_obj.name
            folder_path = str(path_obj.parent)
            content_text = f"Archivo guardado:\n{file_name}"
            button_text = "Abrir Carpeta"
            self.open_path = folder_path
        else:
            folder_name = path_obj.name
            if count > 0:
                content_text = f"{count} archivos guardados en:\n{folder_name}"
            else:
                content_text = f"Archivos guardados en:\n{folder_name}"
            button_text = "Abrir Carpeta"
            self.open_path = output_path
        
        # Crear diálogo
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=24),
                ft.Text(f"{operation} Completada", size=18, weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(content_text, text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    ft.Text("¿Qué deseas hacer ahora?", size=12, color=ft.Colors.GREY_600)
                ], tight=True),
                width=350
            ),
            actions=[
                ft.TextButton(
                    button_text,
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=self._open_folder
                ),
                ft.ElevatedButton(
                    "Cerrar",
                    on_click=self._close_dialog
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _open_folder(self, e):
        """Abrir carpeta en el explorador"""
        try:
            import subprocess
            import platform
            import os
            
            # CRÍTICO: Usar CREATE_NO_WINDOW para evitar que la ventana de consola aparezca
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NO_WINDOW

            system = platform.system()
            if system == "Windows":
                subprocess.run(['explorer', self.open_path], creationflags=creation_flags)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", self.open_path], creationflags=creation_flags)
            elif system == "Linux":
                subprocess.run(["xdg-open", self.open_path], creationflags=creation_flags)
        except Exception as ex:
            print(f"Error abriendo carpeta: {ex}")
        
        self._close_dialog(e)
    
    def _close_dialog(self, e):
        """Cerrar diálogo"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.dialog = None
            self.page.update()
