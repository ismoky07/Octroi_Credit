"""
run_admin.py - Point d'entrée pour l'application d'administration
Lancer avec: streamlit run run_admin.py
"""
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.admin_main import main

if __name__ == "__main__":
    main()
