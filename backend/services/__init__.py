"""
backend/services/__init__.py - Package des services métier
"""

from backend.services.calcul import (
    calcul_mensualite,
    calculer_tableau_amortissement,
    get_taux_endettement,
    calculer_capacite_emprunt,
    calculer_frais_dossier
)

from backend.services.validations import (
    calculer_age,
    valider_email,
    valider_telephone,
    valider_cin,
    valider_montant,
    valider_texte,
    est_majeur,
    nettoyer_texte
)

from backend.services.fichiers import (
    sauvegarder_fichier,
    get_binary_file_downloader_html,
    get_extension_fichier,
    verifier_taille_fichier,
    lister_fichiers_dossier as lister_fichiers,
    detecter_type_fichier
)
