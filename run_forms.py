"""
run_forms.py - Point d'entrée pour l'application de formulaires clients
Lancer avec: streamlit run run_forms.py
"""
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from frontend.forms.credit_auto import formulaire as credit_auto_app
from frontend.forms.credit_immo import formulaire as credit_immo_app
from frontend.forms.credit_conso import formulaire as credit_conso_app
from frontend.forms.credit_decouvert import formulaire as credit_decouvert_app

# Configuration de la page
st.set_page_config(
    page_title="Formulaire de Crédit",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar avec menu de navigation
with st.sidebar:
    st.title("💰 Crédit Banque")

    # Sélection de langue
    st.selectbox("🌐 Langue", ["Français", "العربية", "English"])

    # Menu principal
    st.header("Menu")
    credit_type = st.radio(
        "Type de crédit",
        ["Crédit Automobile", "Crédit Immobilier", "Crédit Consommation", "Découvert Bancaire"]
    )

# Section principale
if credit_type == "Crédit Automobile":
    credit_auto_app.run()
elif credit_type == "Crédit Immobilier":
    credit_immo_app.run()
elif credit_type == "Crédit Consommation":
    credit_conso_app.run()
elif credit_type == "Découvert Bancaire":
    credit_decouvert_app.run()
