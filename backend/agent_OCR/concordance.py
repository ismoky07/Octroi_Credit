"""
backend/agent_OCR/concordance.py - Verification de concordance des documents
"""
import re
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

from backend.agent_OCR.models import DocumentInfo
from backend.agent_OCR.utils import safe_print


def normaliser_texte_ocr(texte: str) -> str:
    """
    Normalise le texte pour gerer les variations typiques de l'OCR
    """
    if not texte:
        return ""

    # Convertir en minuscules
    texte = texte.lower()

    # Enlever les accents
    replacements = {
        'a': 'a', 'a': 'a', 'a': 'a', 'a': 'a', 'a': 'a', 'a': 'a',
        'e': 'e', 'e': 'e', 'e': 'e', 'e': 'e',
        'i': 'i', 'i': 'i', 'i': 'i', 'i': 'i',
        'o': 'o', 'o': 'o', 'o': 'o', 'o': 'o', 'o': 'o',
        'u': 'u', 'u': 'u', 'u': 'u', 'u': 'u',
        'c': 'c', 'n': 'n'
    }
    for ancien, nouveau in replacements.items():
        texte = texte.replace(ancien, nouveau)

    # Enlever ponctuation et espaces multiples
    texte = re.sub(r'[^\w\s]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte)

    return texte.strip()


def normaliser_numero(numero: str) -> str:
    """
    Normalise les numeros en enlevant espaces, tirets, points
    """
    if not numero:
        return ""
    return re.sub(r'[\s\-\.]', '', numero)


def comparer_textes_normalises(texte1: str, texte2: str, tolerance: float = 0.8) -> bool:
    """
    Compare deux textes normalises avec tolerance pour erreurs OCR
    """
    if not texte1 or not texte2:
        return False

    norm1 = normaliser_texte_ocr(texte1)
    norm2 = normaliser_texte_ocr(texte2)

    # Comparaison exacte apres normalisation
    if norm1 == norm2:
        return True

    # Calcul de similarite basique (optionnel pour tolerance OCR)
    mots1 = set(norm1.split())
    mots2 = set(norm2.split())

    if not mots1 or not mots2:
        return False

    intersection = len(mots1.intersection(mots2))
    union = len(mots1.union(mots2))

    similarite = intersection / union if union > 0 else 0
    return similarite >= tolerance


def verifier_concordance_complete(infos_documents: Dict[str, DocumentInfo]) -> Tuple[bool, List[str]]:
    """
    Verification complete de concordance entre documents
    """
    if len(infos_documents) < 2:
        safe_print("Moins de 2 documents a comparer")
        return True, []

    problemes = []

    # 1. INFORMATIONS D'IDENTITE PERSONNELLE
    problemes.extend(_verifier_identite_personnelle(infos_documents))

    # 2. IDENTIFIANTS OFFICIELS
    problemes.extend(_verifier_identifiants_officiels(infos_documents))

    # 3. INFORMATIONS DE DOMICILE ET CONTACT
    problemes.extend(_verifier_domicile_contact(infos_documents))

    # 4. INFORMATIONS FINANCIERES
    problemes.extend(_verifier_coherence_financiere(infos_documents))

    # 5. COHERENCE TEMPORELLE
    problemes.extend(_verifier_coherence_temporelle(infos_documents))

    # 6. VERIFICATIONS CROISEES SPECIALISEES
    problemes.extend(_verifier_croisements_specifiques(infos_documents))

    return len(problemes) == 0, problemes


def _verifier_identite_personnelle(infos_documents: Dict[str, DocumentInfo]) -> List[str]:
    """Verifie la coherence des informations d'identite"""
    problemes = []

    # Collecter les informations
    noms = [(chemin, info.nom) for chemin, info in infos_documents.items() if info.nom]
    prenoms = [(chemin, info.prenom) for chemin, info in infos_documents.items() if info.prenom]
    dates_naissance = [(chemin, info.date_naissance) for chemin, info in infos_documents.items() if info.date_naissance]

    # Verifier les noms
    if len(noms) >= 2:
        noms_normalises = {normaliser_texte_ocr(nom) for _, nom in noms}
        if len(noms_normalises) > 1:
            problemes.append(f"Discordance des noms: {', '.join(f'{nom} ({os.path.basename(chemin)})' for chemin, nom in noms)}")

    # Verifier les prenoms
    if len(prenoms) >= 2:
        prenoms_normalises = {normaliser_texte_ocr(prenom) for _, prenom in prenoms}
        if len(prenoms_normalises) > 1:
            problemes.append(f"Discordance des prenoms: {', '.join(f'{prenom} ({os.path.basename(chemin)})' for chemin, prenom in prenoms)}")

    # Verifier les dates de naissance
    if len(dates_naissance) >= 2:
        dates_normalisees = {normaliser_numero(date) for _, date in dates_naissance}
        if len(dates_normalisees) > 1:
            problemes.append(f"Discordance des dates de naissance: {', '.join(f'{date} ({os.path.basename(chemin)})' for chemin, date in dates_naissance)}")

    return problemes


def _verifier_identifiants_officiels(infos_documents: Dict[str, DocumentInfo]) -> List[str]:
    """Verifie la coherence des identifiants officiels"""
    problemes = []

    # Numeros CIN
    nums_cin = [(chemin, getattr(info, 'numero_cin', None)) for chemin, info in infos_documents.items() if getattr(info, 'numero_cin', None)]
    if len(nums_cin) >= 2:
        cin_normalises = {normaliser_numero(num) for _, num in nums_cin}
        if len(cin_normalises) > 1:
            problemes.append(f"Discordance des numeros CIN: {', '.join(f'{num} ({os.path.basename(chemin)})' for chemin, num in nums_cin)}")

    # Numeros de securite sociale (si disponible)
    nums_secu = [(chemin, getattr(info, 'numero_securite_sociale', None)) for chemin, info in infos_documents.items() if getattr(info, 'numero_securite_sociale', None)]
    if len(nums_secu) >= 2:
        secu_normalises = {normaliser_numero(num) for _, num in nums_secu}
        if len(secu_normalises) > 1:
            problemes.append(f"Discordance des numeros de securite sociale: {', '.join(f'{num} ({os.path.basename(chemin)})' for chemin, num in nums_secu)}")

    return problemes


def _verifier_domicile_contact(infos_documents: Dict[str, DocumentInfo]) -> List[str]:
    """Verifie la coherence des informations de domicile et contact"""
    problemes = []

    # Adresses
    adresses = [(chemin, info.adresse) for chemin, info in infos_documents.items() if info.adresse]
    if len(adresses) >= 2:
        # Grouper les adresses similaires
        groupes_adresses = {}
        for chemin, adresse in adresses:
            adresse_norm = normaliser_texte_ocr(adresse)
            groupe_trouve = False

            for adresse_existante in groupes_adresses:
                if comparer_textes_normalises(adresse_norm, adresse_existante, tolerance=0.7):
                    groupes_adresses[adresse_existante].append((chemin, adresse))
                    groupe_trouve = True
                    break

            if not groupe_trouve:
                groupes_adresses[adresse_norm] = [(chemin, adresse)]

        if len(groupes_adresses) > 1:
            problemes.append(f"Possible discordance des adresses detectee entre {len(groupes_adresses)} groupes differents")

    # Numeros de telephone
    telephones = [(chemin, getattr(info, 'telephone', None)) for chemin, info in infos_documents.items() if getattr(info, 'telephone', None)]
    if len(telephones) >= 2:
        tel_normalises = {normaliser_numero(tel) for _, tel in telephones}
        if len(tel_normalises) > 1:
            problemes.append(f"Discordance des numeros de telephone: {', '.join(f'{tel} ({os.path.basename(chemin)})' for chemin, tel in telephones)}")

    return problemes


def _verifier_coherence_financiere(infos_documents: Dict[str, DocumentInfo]) -> List[str]:
    """Verifie la coherence des informations financieres"""
    problemes = []

    # RIB/IBAN
    ribs = [(chemin, getattr(info, 'rib', None)) for chemin, info in infos_documents.items() if getattr(info, 'rib', None)]
    if len(ribs) >= 2:
        rib_normalises = {normaliser_numero(rib) for _, rib in ribs}
        if len(rib_normalises) > 1:
            problemes.append(f"Discordance des RIB/IBAN: {', '.join(f'{rib} ({os.path.basename(chemin)})' for chemin, rib in ribs)}")

    # Employeur (nom de l'entreprise)
    employeurs = [(chemin, getattr(info, 'employeur', None)) for chemin, info in infos_documents.items() if getattr(info, 'employeur', None)]
    if len(employeurs) >= 2:
        employeurs_normalises = {normaliser_texte_ocr(emp) for _, emp in employeurs}
        if len(employeurs_normalises) > 1:
            problemes.append(f"Discordance des employeurs: {', '.join(f'{emp} ({os.path.basename(chemin)})' for chemin, emp in employeurs)}")

    # Verification salaire vs virements (logique metier specifique)
    salaires = [(chemin, getattr(info, 'salaire_net', None)) for chemin, info in infos_documents.items() if getattr(info, 'salaire_net', None)]
    virements = [(chemin, getattr(info, 'montant_virement', None)) for chemin, info in infos_documents.items() if getattr(info, 'montant_virement', None)]

    if salaires and virements:
        # Logique de comparaison salaire/virement a implementer selon besoins
        pass

    return problemes


def _verifier_coherence_temporelle(infos_documents: Dict[str, DocumentInfo]) -> List[str]:
    """Verifie la coherence temporelle des documents"""
    problemes = []

    # Dates d'emission des documents
    dates_emission = [(chemin, getattr(info, 'date_emission', None)) for chemin, info in infos_documents.items() if getattr(info, 'date_emission', None)]

    if len(dates_emission) >= 2:
        # Verifier que les dates ne sont pas trop eloignees (ex: plus de 6 mois)
        try:
            dates_parsed = []
            for chemin, date_str in dates_emission:
                # Tentative de parsing de differents formats de date
                date_obj = _parser_date_flexible(date_str)
                if date_obj:
                    dates_parsed.append((chemin, date_obj))

            if len(dates_parsed) >= 2:
                dates_only = [date for _, date in dates_parsed]
                ecart_max = max(dates_only) - min(dates_only)

                if ecart_max.days > 180:  # Plus de 6 mois
                    problemes.append(f"Ecart important entre les dates d'emission des documents: {ecart_max.days} jours")

        except Exception as e:
            safe_print(f"Erreur lors de la verification temporelle: {e}")

    return problemes


def _verifier_croisements_specifiques(infos_documents: Dict[str, DocumentInfo]) -> List[str]:
    """Verifications croisees specialisees selon le type de document"""
    problemes = []

    # Identifier les types de documents disponibles
    types_docs = {info.type_document for info in infos_documents.values()}

    # Verifications specifiques CIN + Facture electricite
    if 'cin' in types_docs and 'facture_electricite' in types_docs:
        # L'adresse doit correspondre
        # (deja verifie dans _verifier_domicile_contact mais on peut ajouter des regles specifiques)
        pass

    # Verifications specifiques Bulletin salaire + Releve bancaire
    if 'bulletin_salaire' in types_docs and 'releve_bancaire' in types_docs:
        # Les dates de paie doivent correspondre aux virements
        # Les montants doivent etre coherents
        pass

    return problemes


def _parser_date_flexible(date_str: str) -> Optional[datetime]:
    """Parse une date avec plusieurs formats possibles"""
    if not date_str:
        return None

    formats = [
        '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
        '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
        '%d/%m/%y', '%d-%m-%y', '%d.%m.%y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    return None


def analyser_concordance_detaillee(infos_documents: Dict[str, DocumentInfo]) -> Dict[str, any]:
    """
    Analyse detaillee de la concordance avec statistiques completes
    """
    if not infos_documents:
        return {"analyse": "Aucun document a analyser"}

    stats = {
        "total_documents": len(infos_documents),
        "documents_avec_nom": 0,
        "documents_avec_prenom": 0,
        "documents_avec_date_naissance": 0,
        "documents_avec_adresse": 0,
        "documents_avec_cin": 0,
        "documents_avec_telephone": 0,
        "documents_avec_rib": 0,
        "types_documents": {},
        "concordance_globale": True,
        "problemes_detectes": [],
        "score_confiance": 0.0,
        "recommandations": []
    }

    # Compter les documents avec chaque type d'information
    for chemin, info in infos_documents.items():
        if info.nom:
            stats["documents_avec_nom"] += 1
        if info.prenom:
            stats["documents_avec_prenom"] += 1
        if info.date_naissance:
            stats["documents_avec_date_naissance"] += 1
        if info.adresse:
            stats["documents_avec_adresse"] += 1
        if getattr(info, 'numero_cin', None):
            stats["documents_avec_cin"] += 1
        if getattr(info, 'telephone', None):
            stats["documents_avec_telephone"] += 1
        if getattr(info, 'rib', None):
            stats["documents_avec_rib"] += 1

        # Compter les types de documents
        type_doc = info.type_document
        if type_doc not in stats["types_documents"]:
            stats["types_documents"][type_doc] = 0
        stats["types_documents"][type_doc] += 1

    # Verifier la concordance
    concordance, problemes = verifier_concordance_complete(infos_documents)
    stats["concordance_globale"] = concordance
    stats["problemes_detectes"] = problemes

    # Calculer un score de confiance
    score = _calculer_score_confiance(stats, problemes)
    stats["score_confiance"] = score

    # Generer des recommandations
    stats["recommandations"] = _generer_recommandations(stats)

    return stats


def _calculer_score_confiance(stats: Dict, problemes: List[str]) -> float:
    """Calcule un score de confiance base sur la concordance et la completude"""
    score_base = 100.0

    # Penalites pour les problemes detectes
    score_base -= len(problemes) * 15

    # Bonus pour la completude des informations
    if stats["documents_avec_nom"] >= 2:
        score_base += 5
    if stats["documents_avec_cin"] >= 1:
        score_base += 10
    if stats["documents_avec_adresse"] >= 2:
        score_base += 5

    return max(0.0, min(100.0, score_base))


def _generer_recommandations(stats: Dict) -> List[str]:
    """Genere des recommandations basees sur l'analyse"""
    recommandations = []

    if stats["documents_avec_cin"] == 0:
        recommandations.append("Aucun numero CIN detecte - verifier la qualite de l'OCR sur la CIN")

    if stats["documents_avec_nom"] < 2:
        recommandations.append("Peu de documents contiennent le nom - ameliorer l'extraction")

    if not stats["concordance_globale"]:
        recommandations.append("Discordances detectees - verification manuelle recommandee")

    if stats["score_confiance"] < 50:
        recommandations.append("Score de confiance faible - revalider les documents")

    return recommandations
