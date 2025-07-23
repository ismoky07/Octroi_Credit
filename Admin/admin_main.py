"""
app_admin.py - Orchestrateur principal des modules d'administration
"""
import streamlit as st

# Import de toutes les fonctions d'interface des modules admin
from auth import gerer_authentification, afficher_info_utilisateur, deconnecter_utilisateur
from dashboard import afficher_tableau_bord_general
from gestion_credits import afficher_gestion_credit
from gestion_clients import afficher_gestion_clients
from utilsAdmin import charger_toutes_demandes

def main():
    """Fonction principale d'orchestration de l'interface admin"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="🏦 Administration Crédit",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Vérifier l'authentification
    if not gerer_authentification():
        return
    
    # Charger les données une seule fois
    demandes_toutes = charger_toutes_demandes()
    
    # Sidebar de navigation
    with st.sidebar:
        afficher_info_utilisateur()
        st.markdown("---")
        
        # Menu de navigation principal
        page = st.selectbox(
            "📋 Navigation",
            [
                "📊 Dashboard",
                "💳 Gestion des Crédits",
                "👥 Gestion des Clients",
                "🔓 Déconnexion"
            ]
        )
    
    # Orchestration des pages
    if page == "📊 Dashboard":
        # Interface dashboard complète
        afficher_tableau_bord_general(demandes_toutes)
        
    elif page == "💳 Gestion des Crédits":
        # Interface gestion des crédits avec navigation par type
        orchestrer_gestion_credits(demandes_toutes)
        
    elif page == "👥 Gestion des Clients":
        # Interface gestion des clients
        afficher_gestion_clients(demandes_toutes)
        
    elif page == "🔓 Déconnexion":
        deconnecter_utilisateur()
        st.rerun()

def orchestrer_gestion_credits(demandes_toutes):
    """Orchestre l'interface de gestion des crédits par type"""
    
    st.title("💳 Gestion des Demandes de Crédit")
    
    if not demandes_toutes:
        st.info("📋 Aucune demande de crédit pour le moment.")
        return
    
    # Navigation par type de crédit dans la sidebar
    with st.sidebar:
        st.markdown("### 🎯 Type de crédit")
        type_choisi = st.radio(
            "Choisir le type :",
            [
                "🚗 Crédit Auto",
                "🏠 Crédit Immobilier", 
                "🛒 Crédit Consommation",
                "💰 Découvert Bancaire",
                "📊 Vue globale"
            ]
        )
    
    # Mapping des choix vers les types de crédit
    mapping = {
        "🚗 Crédit Auto": ("auto", "🚗 Crédit Automobile"),
        "🏠 Crédit Immobilier": ("immo", "🏠 Crédit Immobilier"),
        "🛒 Crédit Consommation": ("conso", "🛒 Crédit à la Consommation"),
        "💰 Découvert Bancaire": ("decouvert", "💰 Découvert Bancaire")
    }
    
    if type_choisi == "📊 Vue globale":
        # Afficher toutes les demandes avec statistiques par type
        afficher_vue_globale_credits(demandes_toutes)
    else:
        # Afficher les demandes filtrées par type
        type_credit, titre = mapping[type_choisi]
        demandes_filtrees = filtrer_par_type(demandes_toutes, type_credit)
        afficher_gestion_credit(titre, demandes_filtrees, type_credit)

def filtrer_par_type(demandes_toutes, type_credit):
    """Filtre les demandes par type de crédit"""
    return [
        demande for demande in demandes_toutes 
        if demande.get("type_credit") == type_credit
    ]

def afficher_vue_globale_credits(demandes_toutes):
    """Affiche une vue globale avec statistiques par type"""
    
    st.header("📊 Vue d'ensemble des demandes")
    
    # Compter par type
    stats_types = {
        "auto": 0,
        "immo": 0, 
        "conso": 0,
        "decouvert": 0
    }
    
    for demande in demandes_toutes:
        type_credit = demande.get("type_credit", "")
        if type_credit in stats_types:
            stats_types[type_credit] += 1
    
    # Afficher les métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚗 Crédit Auto", stats_types["auto"])
    with col2:
        st.metric("🏠 Crédit Immo", stats_types["immo"])
    with col3:
        st.metric("🛒 Crédit Conso", stats_types["conso"])
    with col4:
        st.metric("💰 Découvert", stats_types["decouvert"])
    
    # Tableau récapitulatif
    st.markdown("### 📋 Dernières demandes par type")
    
    for type_credit, count in stats_types.items():
        if count > 0:
            with st.expander(f"Détails {type_credit.upper()} ({count} demandes)"):
                demandes_type = filtrer_par_type(demandes_toutes, type_credit)
                
                # Afficher les 5 dernières demandes
                for demande in demandes_type[-5:]:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{demande.get('nom', 'N/A')}**")
                    with col2:
                        from utilsAdmin import formater_montant
                        st.write(formater_montant(demande.get('montant', 0)))
                    with col3:
                        from utilsAdmin import get_statut_couleur
                        statut = demande.get('statut', 'En attente')
                        st.write(f"{get_statut_couleur(statut)} {statut}")

# Point d'entrée
if __name__ == "__main__":
    main()