"""
admin/__init__.py - Package d'administration modulaire pour l'octroi de crédit

Ce package contient tous les modules nécessaires pour l'interface d'administration.
"""

__version__ = "1.0.0"
__author__ = "Équipe Octroi de Crédit"

# Configuration par défaut
CONFIG_ADMIN = {
    "MAX_FICHIERS_UPLOAD": 50,
    "TAILLE_MAX_FICHIER": 10 * 1024 * 1024,  # 10 MB
    "FORMATS_AUTORISES": [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"],
    "TIMEOUT_SESSION": 3600,  # 1 heure
    "NIVEAU_LOG": "INFO"
}

def get_config(cle: str = None):
    """
    Récupère la configuration d'administration
    
    Args:
        cle (str, optional): Clé de configuration spécifique
        
    Returns:
        dict or any: Configuration complète ou valeur spécifique
    """
    if cle:
        return CONFIG_ADMIN.get(cle)
    return CONFIG_ADMIN.copy()

def verifier_sante_systeme():
    """
    Vérifie la santé du système d'administration
    
    Returns:
        dict: État de santé du système
    """
    import os
    
    sante = {
        "status": "OK",
        "checks": {},
        "warnings": [],
        "errors": []
    }
    
    # Vérifier l'existence des dossiers principaux
    dossiers_requis = [
        "data/demandes_clients",
        "data/demandes_clients/auto",
        "data/demandes_clients/immo", 
        "data/demandes_clients/conso",
        "data/demandes_clients/decouvert"
    ]
    
    for dossier in dossiers_requis:
        if os.path.exists(dossier):
            sante["checks"][f"dossier_{dossier}"] = "✅ Présent"
        else:
            sante["checks"][f"dossier_{dossier}"] = "❌ Manquant"
            sante["warnings"].append(f"Dossier manquant: {dossier}")
    
    # Vérifier les permissions d'écriture
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(dir=".", delete=True):
            pass
        sante["checks"]["permissions_ecriture"] = "✅ OK"
    except Exception as e:
        sante["checks"]["permissions_ecriture"] = "❌ Erreur"
        sante["errors"].append(f"Permissions d'écriture: {str(e)}")
    
    # Déterminer le statut global
    if sante["errors"]:
        sante["status"] = "ERREUR"
    elif sante["warnings"]:
        sante["status"] = "AVERTISSEMENT"
    
    return sante

# ============================================================================
# IMPORTS PRINCIPAUX - Ajout nécessaire pour le fonctionnement
# ============================================================================

# Import principal pour permettre 'from admin import admin_dashboard'
try:
    from Admin.dashboard import admin_dashboard
    
    # Imports optionnels des fonctions utiliStaires
    from Admin.auth import gerer_authentification, valider_credentials
    from Admin.utilsAdmin import (
        charger_toutes_demandes,
        formater_montant,
        get_statut_couleur,
        sauvegarder_statut_demande
    )
    
    # Marquer comme disponible
    ADMIN_AVAILABLE = True
    
except ImportError as e:
    # En cas d'erreur d'import, créer une fonction de fallback
    import streamlit as st
    
    def admin_dashboard():
        st.error("🚨 Erreur de chargement du module admin")
        st.error(f"Détails: {str(e)}")
        st.info("Vérifiez que tous les fichiers admin sont présents et corrects")
    
    ADMIN_AVAILABLE = False

# Exports publics du package
__all__ = [
    'admin_dashboard',
    'get_config', 
    'verifier_sante_systeme',
    'CONFIG_ADMIN',
    'ADMIN_AVAILABLE'
]