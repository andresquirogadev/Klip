# core/manager.py

import json
import os
from typing import Dict, List, Tuple

SNIPPETS_FILE = "sql_snippets.json"

# Version limits
MAX_SNIPPETS_FREE = 3
MAX_SNIPPETS_PREMIUM = 50  # For future premium version


def load_snippets() -> Dict[str, str]:
    """Carga los snippets desde el archivo JSON."""
    if os.path.exists(SNIPPETS_FILE):
        with open(SNIPPETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    return {}


def save_snippets(snippets: Dict[str, str]):
    """Guarda los snippets en el archivo JSON."""
    with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
        json.dump(snippets, f, indent=4, ensure_ascii=False)


def add_snippet(name: str, code: str):
    """Agrega un nuevo snippet y lo asigna automáticamente al siguiente número disponible."""
    snippets = load_snippets()
    
    # Check snippet limit for FREE version
    if len(snippets) >= MAX_SNIPPETS_FREE:
        raise ValueError(f"Snippet limit reached ({MAX_SNIPPETS_FREE}/{MAX_SNIPPETS_FREE}). Upgrade to Premium for unlimited snippets!")
    
    if name in snippets:
        raise ValueError(f"El snippet '{name}' ya existe.")
    snippets[name] = code
    save_snippets(snippets)
    
    # Auto-assign to next available number (1-9, 0)
    _auto_assign_hotkey(name)


def update_snippet(old_name: str, new_name: str, new_code: str):
    """Actualiza un snippet existente."""
    snippets = load_snippets()
    if old_name not in snippets:
        raise ValueError(f"El snippet '{old_name}' no existe.")
    if new_name != old_name and new_name in snippets:
        raise ValueError(f"El snippet '{new_name}' ya existe.")
    del snippets[old_name]
    snippets[new_name] = new_code
    save_snippets(snippets)


def delete_snippet(name: str):
    """Elimina un snippet y quita su asignación de hotkey."""
    snippets = load_snippets()
    if name not in snippets:
        raise ValueError(f"El snippet '{name}' no existe.")
    del snippets[name]
    save_snippets(snippets)
    
    # Quitar asignación de hotkey
    _remove_hotkey_assignment(name)


def search_snippets(query: str) -> List[Tuple[str, str]]:
    """
    Devuelve una lista de (nombre, código) que coinciden con el query
    en nombre o contenido.
    """
    snippets = load_snippets()
    if not query:
        # Si no hay query, devolvemos todos (ordenados por nombre).
        return sorted(snippets.items(), key=lambda x: x[0].lower())

    q = query.lower()
    results = []
    for name, code in snippets.items():
        if q in name.lower() or q in code.lower():
            results.append((name, code))
    return sorted(results, key=lambda x: x[0].lower())


def get_snippet_count() -> int:
    """Returns the current number of snippets."""
    snippets = load_snippets()
    return len(snippets)


def get_snippets_limit_info() -> str:
    """Returns info about snippet limits (e.g., '2/3')."""
    count = get_snippet_count()
    return f"{count}/{MAX_SNIPPETS_FREE}"


def can_add_more_snippets() -> bool:
    """Check if user can add more snippets."""
    return get_snippet_count() < MAX_SNIPPETS_FREE


def _auto_assign_hotkey(snippet_name: str):
    """Asigna automáticamente el snippet al siguiente número disponible (1-9, 0)."""
    import json
    
    # Cargar config actual
    config_file = "config.json"
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except:
        config = {}
    
    # Asegurar que existe la sección de hotkeys
    if "hotkeys" not in config:
        config["hotkeys"] = {}
    
    # Orden de números: 1, 2, 3, 4, 5, 6, 7, 8, 9, 0
    number_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    
    # Buscar el primer número disponible
    for num in number_order:
        key = f"shift_{num}"
        current_value = config["hotkeys"].get(key, "None")
        
        # Si está vacío o es "None", asignar aquí
        if current_value == "None" or not current_value:
            config["hotkeys"][key] = snippet_name
            
            # Guardar config
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Snippet '{snippet_name}' auto-asignado a número {num}")
            return
    
    # Si no hay espacio disponible, no hacer nada
    print(f"⚠️ No hay números disponibles para asignar '{snippet_name}'")


def _remove_hotkey_assignment(snippet_name: str):
    """Quita la asignación de hotkey de un snippet eliminado."""
    import json
    
    # Cargar config actual
    config_file = "config.json"
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except:
        return  # No hay config, no hacer nada
    
    # Buscar y quitar la asignación
    if "hotkeys" in config:
        for key, value in config["hotkeys"].items():
            # Comparación case-insensitive
            if value and value.lower() == snippet_name.lower():
                config["hotkeys"][key] = "None"
                
                # Guardar config
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Asignación de '{snippet_name}' removida")
                return


def sync_hotkeys_with_snippets():
    """Sincroniza el config.json para que solo contenga snippets que existen."""
    import json
    
    # Cargar snippets existentes
    snippets = load_snippets()
    snippet_names = [name.lower() for name in snippets.keys()]
    
    # Cargar config actual
    config_file = "config.json"
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except:
        return  # No hay config, no hacer nada
    
    if "hotkeys" not in config:
        return
    
    # Verificar cada asignación
    changed = False
    for key, value in config["hotkeys"].items():
        if value and value != "None":
            # Si el snippet no existe, quitar la asignación
            if value.lower() not in snippet_names:
                config["hotkeys"][key] = "None"
                changed = True
                print(f"⚠️ Quitando asignación obsoleta: '{value}'")
    
    # Guardar si hubo cambios
    if changed:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"✅ Config sincronizado con snippets existentes")
