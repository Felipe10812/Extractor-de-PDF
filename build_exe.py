#!/usr/bin/env python3
"""
Script para crear ejecutable de Windows optimizado
para PDF Extractor Advanced
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def clean_build_dirs():
    """Limpiar directorios de build anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"🧹 Limpiado: {dir_name}")
            except Exception as e:
                print(f"⚠️ No se pudo limpiar {dir_name}: {e}")

def create_optimized_spec():
    """Crear archivo .spec personalizado para mejor control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import sys

# Recopilar datos de paquetes necesarios
datas = []
binaries = []
hiddenimports = [
    'flet',
    'pypdf', 
    'fitz',
    'PIL',
    'pillow',
    'plyer',
    'threading',
    'subprocess',
    'asyncio',
    'concurrent.futures'
]

# Recopilar automáticamente dependencias
tmp_ret = collect_all('flet')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('pypdf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('fitz')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'tkinter', 'numpy.testing', 'pytest',
        'unittest', 'test', 'tests', 'setuptools',
        'pkg_resources', 'distutils'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDF-Extractor-Advanced',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Desactivar UPX completamente
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # CRÍTICO: Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    # Configuraciones adicionales para Windows
    uac_admin=False,
    uac_uiaccess=False,
)
'''
    
    spec_file = Path("PDF-Extractor-Advanced.spec")
    spec_file.write_text(spec_content)
    return str(spec_file)

def create_version_info():
    """Crear archivo de información de versión"""
    version_info = '''# UTF-8
#
# Información de versión para PDF Extractor Advanced
#

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2,0,0,0),
    prodvers=(2,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'PDF Extractor Advanced'),
        StringStruct('FileDescription', 'Extractor de PDF con Previsualización Interactiva'),
        StringStruct('FileVersion', '2.0.0'),
        StringStruct('InternalName', 'PDF-Extractor-Advanced'),
        StringStruct('LegalCopyright', '© 2025 PDF Extractor Advanced'),
        StringStruct('OriginalFilename', 'PDF-Extractor-Advanced.exe'),
        StringStruct('ProductName', 'PDF Extractor Advanced'),
        StringStruct('ProductVersion', '2.0.0')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
'''
    
    version_file = Path("version_info.txt")
    version_file.write_text(version_info, encoding='utf-8')
    print("✅ Archivo de versión creado")

def build_executable():
    """Crear el ejecutable final"""
    
    print("🚀 CREANDO EJECUTABLE PDF EXTRACTOR ADVANCED")
    print("=" * 50)
    
    # Paso 1: Limpiar
    print("\n1️⃣ Limpiando archivos anteriores...")
    clean_build_dirs()
    
    # Paso 2: Crear información de versión
    print("\n2️⃣ Creando información de versión...")
    create_version_info()
    
    # Paso 3: Crear archivo .spec personalizado
    print("\n3️⃣ Creando archivo .spec personalizado...")
    spec_file = create_optimized_spec()
    print(f"✅ Archivo .spec creado: {spec_file}")
    
    # Paso 4: Compilar usando archivo .spec para mejor control
    print("\n4️⃣ Compilando ejecutable...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--distpath", "release",  # Carpeta final
        "--workpath", "build",    # Carpeta temporal
        "--clean",                # Limpiar cache
        "--noconfirm",           # No pedir confirmación
        spec_file                  # Usar archivo .spec personalizado
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Compilación exitosa!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en compilación: {e}")
        print("Salida:", e.stdout)
        print("Errores:", e.stderr)
        return False
    
        # Paso 5: Verificar resultado
        exe_path = Path("release/PDF-Extractor-Advanced.exe")
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"\n✅ EJECUTABLE CREADO EXITOSAMENTE!")
            print(f"📁 Ubicación: {exe_path}")
            print(f"📊 Tamaño: {file_size:.1f} MB")
            print(f"✨ Configuración: SIN VENTANA DE CONSOLA")
            
            # Paso 6: Limpiar archivos temporales
            print("\n5️⃣ Limpiando archivos temporales...")
            temp_files = ['PDF-Extractor-Advanced.spec', 'version_info.txt']
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"🧹 {temp_file} eliminado")
                except:
                    pass
            
            print(f"\n🎉 ¡LISTO! Ejecutable en: release/PDF-Extractor-Advanced.exe")
            print(f"✅ NO DEBERÍA APARECER VENTANA POWERSHELL")
            return True
        else:
            print("❌ No se pudo crear el ejecutable")
            return False

def test_executable():
    """Probar el ejecutable creado"""
    exe_path = Path("release/PDF-Extractor-Advanced.exe")
    
    if exe_path.exists():
        print(f"\n🧪 Probando ejecutable...")
        try:
            # Solo iniciar el proceso, no esperar
            subprocess.Popen([str(exe_path)])
            print("✅ Ejecutable iniciado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error probando ejecutable: {e}")
            return False
    else:
        print("❌ Ejecutable no encontrado")
        return False

if __name__ == "__main__":
    print("🛠️ BUILDER - PDF EXTRACTOR ADVANCED")
    print("Creando ejecutable optimizado para Windows...")
    print()
    
    success = build_executable()
    
    if success:
        print("\n" + "="*50)
        print("📦 RESUMEN:")
        print("✅ Ejecutable creado: release/PDF-Extractor-Advanced.exe")
        print("✅ Listo para distribuir")
        print("✅ No requiere Python instalado")
        print("✅ Ejecutar directamente haciendo doble clic")
        print()
        
        test_choice = input("¿Probar el ejecutable ahora? (s/n): ").lower()
        if test_choice in ['s', 'si', 'y', 'yes']:
            test_executable()
    else:
        print("❌ Hubo errores en la creación del ejecutable")
