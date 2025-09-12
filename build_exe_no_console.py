#!/usr/bin/env python3
"""
Script ROBUSTO para eliminar completamente la ventana de PowerShell
en el ejecutable de PDF Extractor Advanced
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def create_no_console_spec():
    """Crear archivo .spec ultra-robusto anti-consola"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

# Configuración ultra-robusta para eliminar ventana de consola
block_cipher = None

# Datos y dependencias
datas = []
binaries = []
hiddenimports = [
    'flet', 'flet_core', 'flet_runtime',
    'pypdf', 'pypdf2', 'fitz', 'pymupdf',
    'PIL', 'pillow',
    'plyer', 'plyer.platforms.win.notification',
    'threading', 'concurrent.futures', 'asyncio',
    'subprocess', 'multiprocessing',
    'json', 'base64', 'io', 'tempfile',
    'pathlib', 'shutil', 'zipfile'
]

# Auto-recopilar dependencias críticas
for module in ['flet', 'pypdf', 'fitz', 'PIL', 'plyer']:
    try:
        tmp_ret = collect_all(module)
        datas += tmp_ret[0]
        binaries += tmp_ret[1] 
        hiddenimports += tmp_ret[2]
    except:
        pass

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
        'matplotlib', 'numpy', 'scipy',
        'tkinter', 'turtle', 'test', 'tests',
        'unittest', 'pytest',
        'pkg_resources' # setuptools y distutils a veces son necesarios
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# CONFIGURACIÓN CRÍTICA PARA ELIMINAR CONSOLA
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
    upx=False,                      # NO UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # CRÍTICO 1: Sin consola
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Configuraciones adicionales Windows anti-consola
    uac_admin=False,
    uac_uiaccess=False,
    hide_console='minimize-late'    # CRÍTICO 2: Ocultar consola tardía
)
'''
    
    spec_path = Path("PDF-Extractor-Advanced-NoConsole.spec")
    spec_path.write_text(spec_content)
    return str(spec_path)

def build_no_console():
    """Crear ejecutable SIN ventana de consola garantizado"""
    
    print("🚀 CREANDO EJECUTABLE ANTI-POWERSHELL")
    print("=" * 55)
    
    # 1. Limpiar
    print("\n🧹 Limpiando directorios...")
    for dirname in ['build', 'dist', 'release', '__pycache__']:
        if os.path.exists(dirname):
            try:
                shutil.rmtree(dirname)
                print(f"✅ {dirname} limpiado")
            except:
                pass
    
    # 2. Crear spec ultra-robusto
    print("\n📝 Creando archivo .spec anti-consola...")
    spec_file = create_no_console_spec()
    print(f"✅ Spec creado: {spec_file}")
    
    # 3. Compilar con configuración extrema
    print("\n⚙️ Compilando con configuración anti-consola...")
    
    # Establecer variables de entorno para PyInstaller
    env = os.environ.copy()
    env['PYINSTALLER_COMPILE_BOOTLOADER'] = '0'
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--distpath", "release",
        "--workpath", "build", 
        "--clean",
        "--noconfirm",
        "--log-level", "WARN",  # Menos verbose
        spec_file
    ]
    
    try:
        print("🔨 Ejecutando PyInstaller...")
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        print("✅ Compilación exitosa!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error de compilación: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    # 4. Verificar resultado
    exe_path = Path("release/PDF-Extractor-Advanced.exe")
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n🎉 EJECUTABLE ANTI-POWERSHELL CREADO!")
        print(f"📁 Ubicación: {exe_path}")
        print(f"📊 Tamaño: {file_size:.1f} MB")
        print(f"🛡️ Configuración: ANTI-CONSOLA EXTREMA")
        
        # 5. Limpiar archivos temporales
        print("\n🧹 Limpieza final...")
        try:
            if os.path.exists(spec_file):
                os.remove(spec_file)
                print("✅ Spec temporal eliminado")
        except:
            pass
        
        print("\n" + "="*55)
        print("🚀 RESULTADO:")
        print("✅ Ejecutable creado con configuración ANTI-POWERSHELL")
        print("✅ NO debería aparecer ninguna ventana de consola")
        print("✅ Listo para distribución")
        print("=" * 55)
        
        return True
    else:
        print("❌ No se pudo crear el ejecutable")
        return False

def test_no_console():
    """Probar el ejecutable sin consola"""
    exe_path = Path("release/PDF-Extractor-Advanced.exe")
    
    if exe_path.exists():
        print(f"\n🧪 Probando ejecutable anti-consola...")
        try:
            # Usar subprocess con CREATE_NO_WINDOW para el test también
            subprocess.Popen(
                [str(exe_path)],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            print("✅ Ejecutable iniciado - verificar que NO aparezca PowerShell")
            return True
        except Exception as e:
            print(f"❌ Error ejecutando: {e}")
            return False
    else:
        print("❌ Ejecutable no encontrado")
        return False

if __name__ == "__main__":
    print("🛡️ BUILDER ANTI-POWERSHELL - PDF EXTRACTOR ADVANCED")
    print("Creando ejecutable con configuración extrema anti-consola...")
    print()
    
    success = build_no_console()
    
    if success:
        print()
        test_choice = input("¿Probar el ejecutable anti-consola ahora? (s/n): ").lower()
        if test_choice in ['s', 'si', 'y', 'yes']:
            test_no_console()
            print("\n⚠️ IMPORTANTE: Verifica que NO aparezca ventana de PowerShell")
    else:
        print("❌ Falló la creación del ejecutable anti-consola")
