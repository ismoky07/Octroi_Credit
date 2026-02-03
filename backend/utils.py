"""
backend/utils.py - Fonctions utilitaires pour l'application
"""
import os
import json
import streamlit as st
from datetime import date
from typing import List, Dict, Optional

from backend.config import DOSSIER_DEMANDES


def charger_toutes_demandes() -> List[Dict]:
    """
    Charge toutes les demandes de crédit depuis les dossiers

    Returns:
        List[Dict]: Liste de dictionnaires contenant les données des demandes
    """
    demandes = []

    # Types de crédit et leurs dossiers
    types_credit = {
        "auto": "auto",
        "immo": "immo",
        "conso": "conso",
        "decouvert": "decouvert"
    }

    if not os.path.exists(DOSSIER_DEMANDES):
        return demandes

    for type_credit, dossier in types_credit.items():
        chemin_base = os.path.join(DOSSIER_DEMANDES, dossier)

        if not os.path.exists(chemin_base):
            continue

        for nom_dossier in os.listdir(chemin_base):
            chemin_dossier = os.path.join(chemin_base, nom_dossier)

            if not os.path.isdir(chemin_dossier):
                continue

            # Chercher le fichier JSON de données
            for fichier in os.listdir(chemin_dossier):
                if fichier.endswith("_data.json"):
                    chemin_json = os.path.join(chemin_dossier, fichier)

                    try:
                        with open(chemin_json, "r", encoding='utf-8') as f:
                            donnees = json.load(f)

                            if "type_credit" not in donnees:
                                donnees["type_credit"] = type_credit

                            if "statut" not in donnees:
                                donnees["statut"] = "En attente"

                            donnees["chemin_dossier"] = chemin_dossier
                            donnees["nom_dossier"] = nom_dossier

                            demandes.append(donnees)
                            break
                    except:
                        continue

    return demandes


def obtenir_chemin_dossier(demande: Dict, type_credit: str) -> Optional[str]:
    """
    Obtient le chemin du dossier d'une demande avec format Nom Prenom - REF

    Args:
        demande (Dict): Données de la demande
        type_credit (str): Type de crédit

    Returns:
        Optional[str]: Chemin du dossier ou None si non trouvé
    """
    if "chemin_dossier" in demande and os.path.exists(demande["chemin_dossier"]):
        return demande["chemin_dossier"]

    chemin_base = os.path.join(DOSSIER_DEMANDES, type_credit)
    ref_demande = demande.get('ref_demande', '')
    nom = demande.get('nom', '')

    if os.path.exists(chemin_base):
        for dossier in os.listdir(chemin_base):
            if ref_demande and f" - {ref_demande}" in dossier:
                return os.path.join(chemin_base, dossier)
            elif nom and nom.lower() in dossier.lower():
                return os.path.join(chemin_base, dossier)
            elif ref_demande and ref_demande in dossier:
                return os.path.join(chemin_base, dossier)

    return None


def generer_nom_dossier(nom_complet: str, ref_demande: str) -> str:
    """
    Génère le nom du dossier selon le format Nom Prenom - REF

    Args:
        nom_complet (str): Nom complet du client
        ref_demande (str): Référence de la demande

    Returns:
        str: Nom du dossier formaté
    """
    if not nom_complet or not ref_demande:
        return f"Client - {ref_demande}" if ref_demande else "Client"

    # Format final : Nom Prenom - REF
    return f"{nom_complet.strip()} - {ref_demande}"


def sauvegarder_statut_demande(demande: Dict, nouveau_statut: str, type_credit: str) -> bool:
    """
    Sauvegarde le nouveau statut d'une demande

    Args:
        demande (Dict): Données de la demande
        nouveau_statut (str): Nouveau statut à appliquer
        type_credit (str): Type de crédit

    Returns:
        bool: True si succès, False sinon
    """
    chemin_dossier = obtenir_chemin_dossier(demande, type_credit)
    if not chemin_dossier:
        return False

    ref_demande = demande.get('ref_demande', 'demande')
    chemin_json = os.path.join(chemin_dossier, f"{ref_demande}_data.json")

    demande["statut"] = nouveau_statut
    demande["date_mise_a_jour"] = date.today().isoformat()

    if "admin_user" in st.session_state:
        demande["modifie_par"] = st.session_state.admin_user

    try:
        with open(chemin_json, "w", encoding='utf-8') as f:
            json.dump(demande, f, default=str, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def get_statut_couleur(statut: str) -> str:
    """
    Retourne l'emoji couleur correspondant au statut

    Args:
        statut (str): Statut de la demande

    Returns:
        str: Emoji couleur
    """
    couleurs_statut = {
        "En attente": "🟡",
        "En cours d'analyse": "🔵",
        "En cours de traitement": "🟠",
        "Accepté": "🟢",
        "Refusé": "🔴",
        "Annulé": "⚫",
        "Traitement terminé": "🟢",
        "Demande de documents complémentaires": "🟣",
        "Prêt pour décision": "🟢"
    }
    return couleurs_statut.get(statut, "⚪")


def formater_montant(montant: float) -> str:
    """
    Formate un montant avec séparateurs de milliers

    Args:
        montant (float): Montant à formater

    Returns:
        str: Montant formaté
    """
    if montant == 0:
        return "0 DH"
    return f"{montant:,.0f} DH".replace(",", " ")


def get_type_credit_depuis_demande(demande: Dict) -> str:
    """
    Détermine le type de crédit depuis les données de la demande

    Args:
        demande (Dict): Données de la demande

    Returns:
        str: Type de crédit détecté
    """
    if "marque" in demande or demande.get("type_credit") == "auto":
        return "Auto"
    elif "type_bien" in demande or demande.get("type_credit") == "immo":
        return "Immobilier"
    elif "type_projet" in demande or demande.get("type_credit") == "conso":
        return "Consommation"
    elif "type_decouvert" in demande or demande.get("type_credit") == "decouvert":
        return "Découvert"
    else:
        return demande.get("type_credit", "Inconnu")


def lister_fichiers_dossier(chemin_dossier: str) -> List[Dict]:
    """
    Liste tous les fichiers d'un dossier avec leurs informations

    Args:
        chemin_dossier (str): Chemin du dossier

    Returns:
        List[Dict]: Liste des fichiers avec leurs métadonnées
    """
    fichiers = []

    if not os.path.exists(chemin_dossier):
        return fichiers

    for nom_fichier in os.listdir(chemin_dossier):
        chemin_fichier = os.path.join(chemin_dossier, nom_fichier)

        if os.path.isfile(chemin_fichier):
            stat_fichier = os.stat(chemin_fichier)

            fichier_info = {
                "nom": nom_fichier,
                "chemin": chemin_fichier,
                "taille": stat_fichier.st_size,
                "date_modification": date.fromtimestamp(stat_fichier.st_mtime),
                "extension": os.path.splitext(nom_fichier)[1].lower(),
                "type": determiner_type_fichier(nom_fichier)
            }

            fichiers.append(fichier_info)

    return fichiers


def determiner_type_fichier(nom_fichier: str) -> str:
    """
    Détermine le type d'un fichier selon son nom

    Args:
        nom_fichier (str): Nom du fichier

    Returns:
        str: Type de fichier
    """
    nom_lower = nom_fichier.lower()

    if "piece_identite" in nom_lower or "cin" in nom_lower:
        return "Pièce d'identité"
    elif "justificatif_domicile" in nom_lower:
        return "Justificatif de domicile"
    elif "bulletin_salaire" in nom_lower:
        return "Bulletin de salaire"
    elif "releve_bancaire" in nom_lower:
        return "Relevé bancaire"
    elif "devis" in nom_lower:
        return "Devis"
    elif "carte_grise" in nom_lower:
        return "Carte grise"
    elif "recapitulatif" in nom_lower:
        return "Récapitulatif"
    elif nom_lower.endswith("_data.json"):
        return "Données JSON"
    else:
        return "Document complémentaire"


def get_value_safe(state, key, default=None):
    """
    Récupère une valeur de manière sécurisée depuis un état
    qui peut être un objet State ou un AddableValuesDict

    Args:
        state: Objet ou dictionnaire contenant les données
        key (str): Clé à récupérer
        default: Valeur par défaut si la clé n'existe pas

    Returns:
        Valeur trouvée ou valeur par défaut
    """
    if hasattr(state, key):
        # Si c'est un objet avec attributs
        return getattr(state, key, default)
    else:
        # Si c'est un dictionnaire
        return state.get(key, default)


def formater_taille_fichier(taille_bytes: int) -> str:
    """
    Formate la taille d'un fichier en format lisible

    Args:
        taille_bytes (int): Taille en bytes

    Returns:
        str: Taille formatée
    """
    if taille_bytes < 1024:
        return f"{taille_bytes} B"
    elif taille_bytes < 1024 * 1024:
        return f"{taille_bytes / 1024:.1f} KB"
    else:
        return f"{taille_bytes / (1024 * 1024):.1f} MB"
