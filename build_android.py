#!/usr/bin/env python3
"""
Script para crear APK de Android
Requiere: Android Studio, Java JDK 8+
Uso: python build_android.py
"""

import subprocess
import sys
import os
from pathlib import Path

def install_android_requirements():
    """Instalar dependencias para Android"""
    print("📱 Instalando dependencias para Android...")
    
    requirements_android = [
        "flet[android]",
        "buildozer",  # Para crear APK
        "cython"      # Dependencia de buildozer
    ]
    
    for req in requirements_android:
        subprocess.run([sys.executable, "-m", "pip", "install", req], check=True)

def create_buildozer_spec():
    """Crear archivo buildozer.spec para Android"""
    
    spec_content = """[app]
# Información de la aplicación
title = PDF Extractor Advanced
package.name = pdfextractor
package.domain = com.pdfextractor.advanced

# Archivos fuente
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,md

# Versión
version = 2.0.0
version.regex = __version__ = ['"]([^'"]*)['"]
version.filename = %(source.dir)s/main.py

# Requisitos Python
requirements = python3,kivy==2.0.0,flet,pypdf,pymupdf,pillow,plyer

# Icono y splash
#icon.filename = %(source.dir)s/assets/icon.png
#presplash.filename = %(source.dir)s/assets/splash.png

# Orientación
orientation = portrait

# Permisos Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# API
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.accept_sdk_license = True

# Arquitecturas
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
# Directorio de build
log_level = 2
warn_on_root = 1
"""
    
    spec_file = Path("buildozer.spec")
    spec_file.write_text(spec_content)
    print(f"✅ Archivo {spec_file} creado")

def build_android_apk():
    """Crear APK de Android usando buildozer"""
    
    print("📱 Creando APK para Android...")
    print("⚠️  NOTA: Esto puede tomar 30-60 minutos en la primera ejecución")
    print()
    
    # Verificar dependencias del sistema
    print("🔍 Verificando dependencias del sistema...")
    
    try:
        # Verificar Java
        result = subprocess.run(["java", "-version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java encontrado")
        else:
            print("❌ Java no encontrado. Instala JDK 8+")
            return
            
    except FileNotFoundError:
        print("❌ Java no encontrado. Instala JDK 8+")
        return
    
    # Crear APK debug
    try:
        cmd = ["buildozer", "android", "debug"]
        subprocess.run(cmd, check=True)
        
        print("✅ APK creado exitosamente!")
        print("📁 Ubicación: bin/pdfextractor-2.0.0-arm64-v8a-debug.apk")
        print("📱 Instala en Android con: adb install bin/*.apk")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando APK: {e}")
        print("💡 Tip: Asegúrate de tener Android Studio y SDK instalados")

def build_flet_android():
    """Alternativa: usar flet build android"""
    
    print("🔄 Intentando con 'flet build android'...")
    
    try:
        cmd = [
            "flet", "build", "apk",
            "--name", "PDF-Extractor-Advanced", 
            "--description", "Extractor de PDF con previsualización",
            "--org", "com.pdfextractor.advanced"
        ]
        
        subprocess.run(cmd, check=True)
        print("✅ APK creado con flet build!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error con flet build: {e}")

def main():
    print("=== BUILD ANDROID APK ===")
    print("🤖 Creando aplicación para Android")
    print()
    
    # Instalar dependencias
    install_android_requirements()
    
    # Crear buildozer.spec
    create_buildozer_spec()
    
    # Intentar build
    if os.name == 'posix':  # Linux/Mac
        build_android_apk()
    else:
        print("⚠️  Buildozer funciona mejor en Linux/Mac")
        print("💡 Para Windows, usa WSL2 o una VM de Linux")
        build_flet_android()  # Intentar alternativa

if __name__ == "__main__":
    main()
