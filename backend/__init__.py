"""
backend/__init__.py - Package backend pour l'octroi de crédit

Ce package contient toute la logique métier, les services et utilitaires.
"""

__version__ = "1.0.0"
__author__ = "Équipe Octroi de Crédit"

# Imports principaux pour faciliter l'accès
from backend.config import *
from backend.auth import (
    gerer_authentification,
    valider_credentials,
    afficher_info_utilisateur,
    deconnecter_utilisateur,
    verifier_permissions
)
from backend.utils import (
    charger_toutes_demandes,
    formater_montant,
    get_statut_couleur,
    sauvegarder_statut_demande,
    obtenir_chemin_dossier,
    lister_fichiers_dossier,
    formater_taille_fichier
)
