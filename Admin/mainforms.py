""" Fichier principal de l'application de crédit - VERSION SIMPLE """
import streamlit as st

# Import des formulaires
from forms.credit_auto import auto as credit_auto_app
from forms.credit_immo import immo as credit_immo_app
from forms.credit_conso import conso as credit_conso_app
from forms.credit_decouvert import decouvert as credit_decouvert_app

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

# Section principale - Afficher l'application correspondante au type de crédit sélectionné
if credit_type == "Crédit Automobile":
    credit_auto_app.run()
elif credit_type == "Crédit Immobilier":
    credit_immo_app.run()
elif credit_type == "Crédit Consommation":
    credit_conso_app.run()
elif credit_type == "Découvert Bancaire":
    credit_decouvert_app.run()