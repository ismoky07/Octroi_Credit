"""
backend/services/fichiers.py - Module pour la gestion des fichiers
"""
import os
import base64


def sauvegarder_fichier(fichier, chemin_dossier, nom_fichier):
    """
    Sauvegarde un fichier téléchargé dans le dossier spécifié

    Args:
        fichier: Objet fichier de Streamlit (st.file_uploader)
        chemin_dossier (str): Chemin du dossier de destination
        nom_fichier (str): Nom du fichier de destination

    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    if fichier is None:
        return False

    # Créer le chemin si nécessaire
    os.makedirs(chemin_dossier, exist_ok=True)

    # Chemin complet
    chemin_complet = os.path.join(chemin_dossier, nom_fichier)

    # Sauvegarde du fichier
    with open(chemin_complet, "wb") as f:
        f.write(fichier.getbuffer())

    return True


def get_binary_file_downloader_html(bin_file, file_label='Fichier'):
    """
    Génère un lien HTML pour télécharger un fichier binaire

    Args:
        bin_file (str): Chemin du fichier binaire
        file_label (str): Libellé du lien de téléchargement

    Returns:
        str: Code HTML pour télécharger le fichier
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href


def get_extension_fichier(fichier):
    """
    Récupère l'extension d'un fichier téléchargé par Streamlit

    Args:
        fichier: Objet fichier de Streamlit (st.file_uploader)

    Returns:
        str: Extension du fichier (sans le point)
    """
    if fichier is None:
        return ""

    # Récupérer le nom du fichier
    filename = fichier.name

    # Extraire l'extension
    extension = os.path.splitext(filename)[1]

    # Supprimer le point et convertir en minuscules
    extension = extension.lower().lstrip('.')

    return extension


def verifier_taille_fichier(fichier, taille_max_mb=10):
    """
    Vérifie si la taille d'un fichier est inférieure à la limite

    Args:
        fichier: Objet fichier de Streamlit (st.file_uploader)
        taille_max_mb (float): Taille maximale en mégaoctets

    Returns:
        bool: True si la taille est acceptable, False sinon
    """
    if fichier is None:
        return True

    # Calculer la taille en Mo
    taille_mo = len(fichier.getbuffer()) / (1024 * 1024)

    # Vérifier par rapport à la limite
    return taille_mo <= taille_max_mb


def lister_fichiers_dossier(chemin_dossier, extensions=None):
    """
    Liste les fichiers d'un dossier, éventuellement filtrés par extension

    Args:
        chemin_dossier (str): Chemin du dossier à parcourir
        extensions (list): Liste des extensions à inclure (sans le point)

    Returns:
        list: Liste des chemins complets des fichiers
    """
    if not os.path.exists(chemin_dossier):
        return []

    fichiers = []

    for fichier in os.listdir(chemin_dossier):
        chemin_complet = os.path.join(chemin_dossier, fichier)

        # Vérifier que c'est un fichier (pas un dossier)
        if not os.path.isfile(chemin_complet):
            continue

        # Filtrer par extension si demandé
        if extensions:
            ext = os.path.splitext(fichier)[1].lower().lstrip('.')
            if ext not in extensions:
                continue

        fichiers.append(chemin_complet)

    return fichiers


def detecter_type_fichier(chemin_fichier):
    """
    Détecte le type d'un fichier (PDF, image, etc.)

    Args:
        chemin_fichier: Chemin du fichier à analyser

    Returns:
        str: Type du fichier (PDF, Image, Autre)
    """
    extension = os.path.splitext(chemin_fichier)[1].lower()

    if extension in ['.pdf']:
        return "PDF"
    elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return "Image"
    elif extension in ['.doc', '.docx']:
        return "Document Word"
    elif extension in ['.xls', '.xlsx']:
        return "Feuille de calcul Excel"
    elif extension in ['.json']:
        return "Données JSON"
    else:
        return "Autre"
