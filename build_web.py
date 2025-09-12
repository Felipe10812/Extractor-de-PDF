#!/usr/bin/env python3
"""
Script para crear Progressive Web App (PWA)
La aplicación funcionará en navegadores web
Uso: python build_web.py
"""

import subprocess
import sys
import os
from pathlib import Path

def install_web_requirements():
    """Instalar dependencias para web"""
    print("🌐 Instalando dependencias para web...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flet[web]"], check=True)

def create_web_app():
    """Crear aplicación web usando flet build web"""
    
    print("🌐 Creando Progressive Web App...")
    
    cmd = [
        "flet", "build", "web",
        "--name", "PDF Extractor Advanced",
        "--description", "Extractor de PDF con previsualización interactiva",
        "--base-url", "/pdfextractor/",  # Para hosting
        "--web-app-meta",
        "--route-url-strategy", "hash"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        print("✅ PWA creada exitosamente!")
        print("📁 Ubicación: build/web/")
        print("🌍 Para probar localmente:")
        print("   cd build/web && python -m http.server 8000")
        print("   Luego abre: http://localhost:8000")
        
        # Crear script de servidor local
        create_local_server_script()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando PWA: {e}")

def create_local_server_script():
    """Crear script para servidor local"""
    
    server_script = """#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import threading
import time

PORT = 8080

def start_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Servidor iniciado en http://localhost:{PORT}")
        httpd.serve_forever()

def open_browser():
    time.sleep(2)  # Esperar a que inicie el servidor
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == "__main__":
    print("=== PDF EXTRACTOR ADVANCED - WEB SERVER ===")
    
    # Iniciar servidor en hilo separado
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Abrir navegador
    open_browser()
    
    try:
        print("Presiona Ctrl+C para detener el servidor")
        server_thread.join()
    except KeyboardInterrupt:
        print("\\n🛑 Servidor detenido")
"""
    
    web_dir = Path("build/web")
    if web_dir.exists():
        server_file = web_dir / "start_server.py"
        server_file.write_text(server_script)
        print(f"✅ Servidor local creado: {server_file}")
        print("💡 Para iniciar: python build/web/start_server.py")

def create_dockerfile():
    """Crear Dockerfile para deployment en contenedor"""
    
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de la aplicación web
COPY build/web/ /app/static/

# Instalar servidor web simple
RUN pip install gunicorn

# Crear servidor simple
COPY <<EOF /app/server.py
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/app/static", **kwargs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), CustomHandler)
    print(f"Starting server on port {port}")
    server.serve_forever()
EOF

EXPOSE 8080

CMD ["python", "server.py"]
"""
    
    dockerfile = Path("Dockerfile")
    dockerfile.write_text(dockerfile_content)
    print(f"✅ {dockerfile} creado para deployment")

def main():
    print("=== BUILD PROGRESSIVE WEB APP ===")
    print("🌐 Creando aplicación web multiplataforma")
    print()
    
    # Instalar dependencias
    install_web_requirements()
    
    # Crear PWA
    create_web_app()
    
    # Crear Dockerfile
    create_dockerfile()
    
    print()
    print("🎉 BUILD COMPLETADO")
    print()
    print("📋 INSTRUCCIONES DE USO:")
    print("1. Prueba local: python build/web/start_server.py")
    print("2. Deploy en servidor: sube la carpeta build/web/")
    print("3. Deploy en Docker: docker build -t pdfextractor .")

if __name__ == "__main__":
    main()
