"""
backend/services/validations.py - Fonctions de validation des données
"""
import re
from datetime import date


def calculer_age(date_naissance):
    """
    Calcule l'âge en années à partir de la date de naissance

    Args:
        date_naissance (date): Date de naissance

    Returns:
        int: Âge en années
    """
    aujourd_hui = date.today()
    return aujourd_hui.year - date_naissance.year - ((aujourd_hui.month, aujourd_hui.day) < (date_naissance.month, date_naissance.day))


def valider_email(email):
    """
    Valide le format d'une adresse email

    Args:
        email (str): Adresse email à valider

    Returns:
        bool: True si le format est valide, False sinon
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def valider_telephone(telephone):
    """
    Valide le format d'un numéro de téléphone marocain

    Args:
        telephone (str): Numéro de téléphone à valider

    Returns:
        bool: True si le format est valide, False sinon
    """
    # Format +212XXXXXXXX ou 06XXXXXXXX
    pattern = r'^(\+212[5-7]\d{8}|0[5-7]\d{8})$'
    return re.match(pattern, telephone) is not None


def valider_cin(cin):
    """
    Valide le format d'une Carte Nationale d'Identité marocaine

    Args:
        cin (str): Numéro de CIN à valider

    Returns:
        bool: True si le format est valide, False sinon
    """
    # Format: 1 ou 2 lettres suivies de 5 ou 6 chiffres
    pattern = r'^[A-Za-z]{1,2}\d{5,6}$'
    return re.match(pattern, cin) is not None


def valider_montant(montant, min_val=0, max_val=None):
    """
    Valide un montant numérique dans une plage donnée

    Args:
        montant (float): Montant à valider
        min_val (float): Valeur minimale (défaut: 0)
        max_val (float): Valeur maximale (défaut: None = pas de maximum)

    Returns:
        bool: True si le montant est valide, False sinon
    """
    if montant < min_val:
        return False

    if max_val is not None and montant > max_val:
        return False

    return True


def valider_texte(texte, min_len=1, max_len=None):
    """
    Valide une chaîne de caractères selon sa longueur

    Args:
        texte (str): Texte à valider
        min_len (int): Longueur minimale (défaut: 1)
        max_len (int): Longueur maximale (défaut: None = pas de maximum)

    Returns:
        bool: True si le texte est valide, False sinon
    """
    if not isinstance(texte, str):
        return False

    if len(texte) < min_len:
        return False

    if max_len is not None and len(texte) > max_len:
        return False

    return True


def est_majeur(date_naissance):
    """
    Vérifie si une personne est majeure (18 ans ou plus)

    Args:
        date_naissance (date): Date de naissance

    Returns:
        bool: True si la personne est majeure, False sinon
    """
    age = calculer_age(date_naissance)
    return age >= 18


def nettoyer_texte(texte):
    """
    Nettoie un texte (supprime les espaces inutiles, etc.)

    Args:
        texte (str): Texte à nettoyer

    Returns:
        str: Texte nettoyé
    """
    if not isinstance(texte, str):
        return ""

    # Suppression des espaces en début et fin de chaîne
    texte = texte.strip()

    # Remplacement des espaces multiples par un seul espace
    texte = re.sub(r'\s+', ' ', texte)

    return texte
