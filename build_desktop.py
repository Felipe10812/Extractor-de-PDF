#!/usr/bin/env python3
"""
Script para crear ejecutables de escritorio multiplataforma
Uso: python build_desktop.py [windows|linux|mac]
"""

import subprocess
import sys
import platform
import os

def install_requirements():
    """Instalar dependencias para build"""
    print("📦 Instalando dependencias para build...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flet[desktop]"], check=True)

def build_desktop(target_platform=None):
    """Crear ejecutable de escritorio"""
    
    if not target_platform:
        target_platform = platform.system().lower()
        if target_platform == "darwin":
            target_platform = "mac"
    
    print(f"🔨 Creando ejecutable para {target_platform}...")
    
    # Comando base de flet pack
    cmd = [
        "flet", "pack", "main.py",
        "--name", "PDFExtractorAdvanced",
        "--description", "Extractor de PDF Avanzado con Previsualización Interactiva",
        "--product-name", "PDF Extractor Advanced",
        "--product-version", "2.0.0",
        "--copyright", "© 2025 PDF Extractor Advanced"
    ]
    
    # Configuraciones específicas por plataforma
    if target_platform == "windows":
        cmd.extend([
            "--icon", "assets/icon.ico",  # Si tienes icono
            "--add-data", "requirements.txt;.",
            "--distpath", "dist/windows"
        ])
    elif target_platform == "linux":
        cmd.extend([
            "--icon", "assets/icon.png",  # Si tienes icono
            "--add-data", "requirements.txt:.",
            "--distpath", "dist/linux"
        ])
    elif target_platform == "mac":
        cmd.extend([
            "--icon", "assets/icon.icns",  # Si tienes icono
            "--add-data", "requirements.txt:.",
            "--distpath", "dist/mac"
        ])
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Ejecutable creado exitosamente en dist/{target_platform}/")
        print(f"📁 Tamaño estimado: ~50-80 MB")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando ejecutable: {e}")
        
        # Comando alternativo usando PyInstaller
        print("🔄 Intentando con PyInstaller...")
        create_pyinstaller_spec(target_platform)

def create_pyinstaller_spec(target_platform):
    """Crear ejecutable usando PyInstaller como alternativa"""
    
    # Instalar PyInstaller
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "PDFExtractorAdvanced",
        "--distpath", f"dist/{target_platform}",
        "main.py"
    ]
    
    if target_platform == "windows":
        cmd.append("--console")  # Para debug en Windows
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Ejecutable PyInstaller creado en dist/{target_platform}/")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error con PyInstaller: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("=== BUILD DESKTOP ===")
    print("Plataformas soportadas: windows, linux, mac")
    print()
    
    install_requirements()
    build_desktop(target)
