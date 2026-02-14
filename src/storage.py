import json
import os
import streamlit as st

STORAGE_FILE = "favorites.json"

def ensure_storage():
    """Checks if the storage file is writable. Returns True if server-side storage is available."""
    try:
        if not os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        else:
            # Test write access
            with open(STORAGE_FILE, 'a', encoding='utf-8') as f:
                pass
        return True
    except Exception:
        return False

def load_favorites():
    """Loads favorites from the local JSON file."""
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_favorite(name, selected_schools, selected_fields):
    """Saves a selection to the local JSON file."""
    data = load_favorites()
    data[name] = {
        "schools": selected_schools,
        "fields": selected_fields
    }
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def delete_favorite(name):
    """Deletes a favorite from the local JSON file."""
    data = load_favorites()
    if name in data:
        del data[name]
        try:
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False
    return False

def get_export_json(name, selected_schools, selected_fields):
    """Generates a JSON string for client-side download."""
    obj = {
        "name": name,
        "schools": selected_schools,
        "fields": selected_fields
    }
    return json.dumps(obj, ensure_ascii=False, indent=4)
