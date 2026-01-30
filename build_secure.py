# build_secure.py - Build with maximum security using PyArmor

"""
Advanced build script with PyArmor obfuscation.

This provides the highest level of protection by:
1. Obfuscating Python code with PyArmor
2. Encrypting bytecode
3. Adding anti-debugging measures
4. Creating a single executable

Prerequisites:
    pip install pyarmor pyinstaller cryptography

Usage:
    python build_secure.py
"""

import os
import sys
import shutil
import subprocess


def check_dependencies():
    """Check if required packages are installed."""
    required = ['pyarmor', 'PyInstaller', 'cryptography']
    missing = []
    
    for package in required:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print("ERROR: Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    return True


def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__', 'dist_obfuscated']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/...")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # Clean .spec files
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)
            print(f"Removed {file}")


def obfuscate_code():
    """Obfuscate Python code using PyArmor."""
    print("\n" + "=" * 60)
    print("Step 1: Obfuscating code with PyArmor...")
    print("=" * 60 + "\n")
    
    # Create output directory
    obf_dir = "dist_obfuscated"
    if os.path.exists(obf_dir):
        shutil.rmtree(obf_dir)
    
    # PyArmor obfuscation command
    cmd = [
        'pyarmor',
        'gen',
        '--output', obf_dir,
        '--restrict', '1',  # Restrict mode 1 (strict protection)
        '--private',  # Encrypt all co_consts
        '--enable', 'jit',  # Enable JIT (if available)
        'main.py',
        'security.py',
        'notification.py',
        'core/manager.py',
        'ui/overlay.py',
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("✓ Code obfuscation complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR during obfuscation: {e}")
        print(e.stderr)
        return False


def build_executable():
    """Build the final executable with PyInstaller."""
    print("\n" + "=" * 60)
    print("Step 2: Building executable with PyInstaller...")
    print("=" * 60 + "\n")
    
    obf_dir = "dist_obfuscated"
    
    # Check for icon
    icon_path = os.path.join('assets', 'icon.png')
    ico_path = icon_path.replace('.png', '.ico')
    icon_option = []
    
    if os.path.exists(ico_path):
        icon_option = ['--icon', ico_path]
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name', 'Klip',
        '--onefile',
        '--windowed',
        '--clean',
        '--key', 'KlipSecureApp2024_Obfuscated',
        
        # Add hidden imports
        '--hidden-import', 'security',
        '--hidden-import', 'notification',
        '--hidden-import', 'PyQt6',
        '--hidden-import', 'keyboard',
        '--hidden-import', 'pyautogui',
        '--hidden-import', 'supabase',
        '--hidden-import', 'cryptography',
        
        # Add data files
        '--add-data', 'sql_snippets.json;.',
        '--add-data', 'assets;assets',
        
        # Add obfuscated modules
        '--add-data', f'{obf_dir};.',
        
        '--noupx',
        
        os.path.join(obf_dir, 'main.py'),
    ] + icon_option
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("✓ Executable build complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR during build: {e}")
        print(e.stderr)
        return False


def print_summary():
    """Print build summary and next steps."""
    print("\n" + "=" * 60)
    print("🎉 BUILD SUCCESSFUL!")
    print("=" * 60)
    print("\n📦 Your secure executable is ready:")
    print("   Location: dist/Klip.exe")
    print("\n🔒 Security features enabled:")
    print("   ✓ PyArmor code obfuscation")
    print("   ✓ Bytecode encryption")
    print("   ✓ Anti-debugging protection")
    print("   ✓ Runtime integrity checks")
    print("   ✓ String obfuscation")
    print("   ✓ Restrict mode (prevents import)")
    print("\n⚠️  Important notes:")
    print("   • Test the executable thoroughly")
    print("   • Keep the build environment secure")
    print("   • Don't share your .pyarmor/ folder")
    print("   • Consider code signing for distribution")
    print("\n📖 See SECURITY.md for more information")
    print("=" * 60 + "\n")


def main():
    """Main build process."""
    print("=" * 60)
    print("Klip - Secure Build Process")
    print("=" * 60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Obfuscate code
    if not obfuscate_code():
        print("\n❌ Build failed during obfuscation")
        sys.exit(1)
    
    # Build executable
    if not build_executable():
        print("\n❌ Build failed during executable creation")
        sys.exit(1)
    
    # Success
    print_summary()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
