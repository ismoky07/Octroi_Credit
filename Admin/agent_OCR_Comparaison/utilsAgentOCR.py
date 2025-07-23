import os
import sys
import io

# Configuration de l'encodage pour éviter les problèmes
try:
    if not hasattr(sys.stdout, 'buffer') or not sys.stdout.__class__.__name__ == 'OutStream':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='backslashreplace')
except Exception:
    pass

def safe_print(text):
    """Version silencieuse pour Streamlit"""
    # Ne rien faire - Streamlit bloque les prints
    # Les logs seront visibles dans l'interface Streamlit directement
    pass

def safe_text_handling(text):
    """Assure que le texte est correctement encodé en UTF-8"""
    if text is None:
        return ""
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='backslashreplace')
    if isinstance(text, str):
        return text
    return str(text)