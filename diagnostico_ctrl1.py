# diagnostico_ctrl1.py - Diagnóstico completo de Ctrl+1

"""
Script de diagnóstico para verificar que Ctrl+1 funciona correctamente.
"""

import sys
import os

print("=" * 70)
print("DIAGNÓSTICO CTRL+1 - KLIP V1.0")
print("=" * 70)

# 1. Verificar que main.py tiene el código correcto
print("\n[1/4] Verificando código en main.py...")
try:
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    checks = {
        "Ctrl+1 en setup_keyboard_hotkeys": "keyboard.add_hotkey('ctrl+1'" in content,
        "Función on_save_selection existe": "def on_save_selection(overlay: SnippetOverlay):" in content,
        "Verificación de límites": "can_add_more_snippets()" in content and "on_save_selection" in content,
        "SignalEmitter configurado": "emitter.save_selection_signal.connect" in content,
        "Lambda emite señal": "lambda: emitter.save_selection_signal.emit()" in content,
    }
    
    all_ok = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"     {status} {check}")
        if not result:
            all_ok = False
    
    if all_ok:
        print("     ✅ Todo el código está correctamente implementado")
    else:
        print("     ⚠️ Hay problemas en la implementación")
        
except Exception as e:
    print(f"     ❌ Error leyendo main.py: {e}")
    all_ok = False

# 2. Verificar orden de ejecución
print("\n[2/4] Verificando orden de registro de hotkeys...")
try:
    # Buscar la línea donde se registra ctrl+1
    lines = content.split('\n')
    ctrl1_line = None
    unhook_line = None
    
    for i, line in enumerate(lines, 1):
        if "keyboard.add_hotkey('ctrl+1'" in line and "setup_keyboard_hotkeys" in '\n'.join(lines[max(0,i-20):i]):
            ctrl1_line = i
        if "keyboard.unhook_all_hotkeys()" in line:
            unhook_line = i
    
    if ctrl1_line and unhook_line:
        if ctrl1_line > unhook_line:
            print(f"     ✅ Ctrl+1 se registra DESPUÉS de unhook (correcto)")
            print(f"        unhook en línea {unhook_line}, ctrl+1 en línea {ctrl1_line}")
        else:
            print(f"     ❌ Ctrl+1 se registra ANTES de unhook (incorrecto)")
            print(f"        Esto causaría que se borre el hotkey")
    else:
        print(f"     ⚠️ No se pudo determinar el orden")
        print(f"        ctrl+1 línea: {ctrl1_line}, unhook línea: {unhook_line}")
        
except Exception as e:
    print(f"     ⚠️ Error en análisis: {e}")

# 3. Verificar dependencias
print("\n[3/4] Verificando dependencias...")
deps_ok = True
try:
    import keyboard
    print("     ✅ keyboard module disponible")
except ImportError:
    print("     ❌ keyboard module NO disponible")
    deps_ok = False

try:
    import pyperclip
    print("     ✅ pyperclip disponible")
except ImportError:
    print("     ❌ pyperclip NO disponible")
    deps_ok = False

try:
    from PyQt6.QtWidgets import QApplication
    print("     ✅ PyQt6 disponible")
except ImportError:
    print("     ❌ PyQt6 NO disponible")
    deps_ok = False

# 4. Estado de snippets
print("\n[4/4] Estado actual de snippets...")
try:
    from core.manager import get_snippet_count, get_snippets_limit_info, can_add_more_snippets
    
    count = get_snippet_count()
    limit_info = get_snippets_limit_info()
    can_add = can_add_more_snippets()
    
    print(f"     📊 Snippets: {limit_info}")
    print(f"     {'✅' if can_add else '⚠️'} Puede agregar más: {can_add}")
    
    if not can_add:
        print(f"     ⚠️ LÍMITE ALCANZADO - Ctrl+1 mostrará mensaje de upgrade")
    else:
        print(f"     ✅ Hay espacio para {3 - count} snippet(s) más")
        
except Exception as e:
    print(f"     ❌ Error: {e}")

# Resumen final
print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)

if all_ok and deps_ok:
    print("\n✅ TODO ESTÁ CORRECTO")
    print("\nCómo probar:")
    print("1. Asegúrate que main.py esté corriendo")
    print("2. Abre Notepad")
    print("3. Escribe y selecciona texto")
    print("4. Presiona Ctrl+1")
    print("5. Debería aparecer diálogo para guardar")
else:
    print("\n⚠️ HAY PROBLEMAS")
    if not all_ok:
        print("   - Código en main.py tiene issues")
    if not deps_ok:
        print("   - Faltan dependencias")
    print("\nRevisa los detalles arriba")

print("\n" + "=" * 70)

# Instrucciones de prueba
print("\nINSTRUCCIONES DE PRUEBA MANUAL:")
print("-" * 70)
print("""
1. INICIAR APP:
   python main.py
   
2. VERIFICAR MENSAJE:
   Busca: "✅ Global hotkeys configured in separate thread (F12, Ctrl+Shift+S, Ctrl+1)"
   
3. PROBAR F12 PRIMERO:
   - Presiona F12
   - ¿Se abre selector? → Sí = hotkeys funcionan
   
4. PROBAR CTRL+1:
   - Abre Notepad
   - Escribe: SELECT * FROM test
   - Selecciona todo (Ctrl+A)
   - Presiona Ctrl+1
   - ¿Aparece diálogo? → Sí = FUNCIONA! 🎉
   
5. SI NO FUNCIONA:
   - Cierra TODAS las instancias de main.py
   - Reinicia: python main.py
   - Prueba de nuevo
""")

print("=" * 70)
