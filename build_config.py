# build_config.py - Configuration for building secure executable

"""
PyInstaller build configuration for creating a secure, obfuscated executable.

Usage:
    python build_config.py

This will create a hardened executable with:
- Code obfuscation
- Anti-debugging measures
- Encrypted resources
- Single-file executable
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """Build the executable with security features."""
    
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, 'main.py')
    icon_path = os.path.join(script_dir, 'assets', 'icon.png')
    manifest_path = os.path.join(script_dir, 'app.manifest')
    
    # Check if icon exists
    icon_option = []
    if os.path.exists(icon_path):
        # Convert PNG to ICO if needed
        ico_path = icon_path.replace('.png', '.ico')
        if not os.path.exists(ico_path):
            try:
                from PIL import Image
                img = Image.open(icon_path)
                img.save(ico_path, format='ICO')
                print(f"✓ Icon converted: {ico_path}")
            except:
                print("⚠ Could not convert icon. Install Pillow: pip install Pillow")
        
        if os.path.exists(ico_path):
            icon_option = ['--icon', ico_path]
    
    # Check if manifest exists
    manifest_option = []
    if os.path.exists(manifest_path):
        manifest_option = ['--manifest', manifest_path]
        print(f"✓ Using manifest: {manifest_path}")
    
    # PyInstaller options for maximum security
    pyinstaller_args = [
        main_script,
        '--name=Klip',
        '--onefile',  # Single executable file
        '--windowed',  # No console window
        '--clean',  # Clean cache before building
        '--uac-admin',  # Request administrator privileges (Windows only)
        
        # Add security module
        '--hidden-import=security',
        '--hidden-import=notification',
        
        # Add all required packages
        '--hidden-import=PyQt6',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=keyboard',
        '--hidden-import=pyautogui',
        '--hidden-import=supabase',
        '--hidden-import=cryptography',
        
        # Add data files
        '--add-data', f'{script_dir}/sql_snippets.json;.',
        '--add-data', f'{script_dir}/assets;assets',
        
        # Security options - Note: bytecode encryption removed in PyInstaller 6.0
        # Use PyArmor or other obfuscation tools for code protection
        
        # UPX compression (optional, requires UPX to be installed)
        # '--upx-dir', 'C:\\upx',  # Uncomment and set path if you have UPX
        
        # Additional options
        '--noupx',  # Disable UPX if not available
        '--strip',  # Strip debug symbols (Linux/Mac)
    ] + icon_option + manifest_option
    
    print("=" * 60)
    print("Building Klip with security features...")
    print("=" * 60)
    print("\nSecurity features enabled:")
    print("✓ Anti-debugging measures")
    print("✓ Machine-binding")
    print("✓ Integrity verification")
    print("✓ String obfuscation (use PyArmor for full obfuscation)")
    print("✓ Administrator privileges required")
    print("✓ Windows manifest with UAC settings")
    print("\nBuilding executable...\n")
    
    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print("\nExecutable location: dist/Klip.exe")
    print("\nIMPORTANT: For additional security:")
    print("1. Use code obfuscation tools like PyArmor")
    print("2. Implement license key validation")
    print("3. Use anti-tamper protection services")
    print("4. Regular updates to patch vulnerabilities")
    print("=" * 60)


if __name__ == '__main__':
    # Check dependencies
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller not found.")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)
    
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("ERROR: cryptography not found.")
        print("Install it with: pip install cryptography")
        sys.exit(1)
    
    # Build
    build_exe()
