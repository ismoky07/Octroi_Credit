# Configuration de l'application
# Ce fichier contient les constantes et paramètres de configuration de l'application

import os

# Configuration générale
APP_TITLE = "Crédit Banque"
APP_ICON = "💰"

# Configuration des chemins - Utiliser des chemins relatifs à la racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Configuration des dossiers de données
DOSSIER_DEMANDES = os.path.join(DATA_DIR, "demandes_clients")
DOSSIER_AUTO = os.path.join(DOSSIER_DEMANDES, "auto")
DOSSIER_IMMO = os.path.join(DOSSIER_DEMANDES, "immo")
DOSSIER_CONSO = os.path.join(DOSSIER_DEMANDES, "conso")
DOSSIER_DECOUVERT = os.path.join(DOSSIER_DEMANDES, "decouvert")

# Configuration des crédits auto
AUTO_MONTANT_MIN = 5000
AUTO_MONTANT_MAX = 2000000
AUTO_DUREE_OPTIONS = [12, 24, 36, 48, 60, 72, 84]
AUTO_TAUX_MIN = 0.0
AUTO_TAUX_MAX = 15.0
AUTO_TAUX_DEFAUT = 4.5

# Configuration des crédits immobiliers
IMMO_MONTANT_MIN = 100000
IMMO_MONTANT_MAX = 10000000
IMMO_DUREE_OPTIONS = [60, 120, 180, 240, 300, 360]
IMMO_TAUX_MIN = 0.0
IMMO_TAUX_MAX = 10.0
IMMO_TAUX_DEFAUT = 3.5

# Configuration des crédits à la consommation
CONSO_MONTANT_MIN = 5000
CONSO_MONTANT_MAX = 300000
CONSO_DUREE_OPTIONS = [6, 12, 24, 36, 48, 60]
CONSO_TAUX_MIN = 0.0
CONSO_TAUX_MAX = 15.0
CONSO_TAUX_DEFAUT = 6.5

# Configuration des découverts bancaires
DECOUVERT_MONTANT_MIN = 1000
DECOUVERT_MONTANT_MAX = 50000
DECOUVERT_TAUX_DEFAUT = 12.0

# Configuration des documents
DOCUMENTS_EXTENSIONS = ["pdf", "png", "jpg", "jpeg"]
TAILLE_MAX_DOCUMENT_MB = 10

# Configuration de l'administration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpass"  # À remplacer par un système sécurisé en production

# Limites d'endettement
ENDETTEMENT_MAX_AUTO = 40  # Pourcentage maximal pour l'éligibilité
ENDETTEMENT_RECOMMANDE_AUTO = 33  # Pourcentage recommandé pour l'éligibilité

ENDETTEMENT_MAX_IMMO = 40
ENDETTEMENT_RECOMMANDE_IMMO = 33

ENDETTEMENT_MAX_CONSO = 40
ENDETTEMENT_RECOMMANDE_CONSO = 33

ENDETTEMENT_MAX_DECOUVERT = 40
ENDETTEMENT_RECOMMANDE_DECOUVERT = 33

# Statuts des demandes
STATUTS_DEMANDES = [
    "En attente",
    "En cours d'analyse",
    "Demande de documents complémentaires",
    "Accepté",
    "Refusé",
    "Annulé"
]

# Frais de dossier selon le type de crédit
FRAIS_DOSSIER_AUTO = 1000
FRAIS_DOSSIER_IMMO = 5000
FRAIS_DOSSIER_CONSO = 500
FRAIS_DOSSIER_DECOUVERT = 100

# Assurance crédit (taux annuel en %)
TAUX_ASSURANCE_AUTO = 0.5
TAUX_ASSURANCE_IMMO = 0.4
TAUX_ASSURANCE_CONSO = 0.7

# Configuration admin
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
