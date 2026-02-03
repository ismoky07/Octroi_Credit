"""
backend/agent_OCR/extraction.py - Extraction OCR avec OpenAI
"""
from typing import Dict, List, Tuple, Optional
import os
import base64
import re

from backend.agent_OCR.models import DocumentInfo
from backend.agent_OCR.utils import safe_print, safe_text_handling

from openai import OpenAI
from dotenv import load_dotenv


def init_client():
    """
    Initialise le client OpenAI avec la cle API
    Retourne un client OpenAI natif (pas LangChain)
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("La cle API OpenAI n'est pas definie dans le fichier .env ou l'environnement")

    client = OpenAI(api_key=api_key)
    return client


def encode_image_to_base64(image_path):
    """Encode une image en base64 pour l'API"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        safe_print(f"Erreur lors de l'encodage de l'image {image_path}: {str(e)}")
        return None


def construire_prompt_ocr() -> dict:
    """Construit le prompt OCR optimise"""
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": """Tu es un expert en extraction d'informations de documents administratifs marocains.

**ETAPE 1 - CLASSIFICATION DU DOCUMENT**
Identifie le type de document parmi :
- CIN (Carte d'Identite Nationale)
- PASSEPORT
- FACTURE_ELECTRICITE (ONE, REDAL, AMENDIS, etc.)
- BULLETIN_SALAIRE
- RELEVE_BANCAIRE
- JUSTIFICATIF_DOMICILE (autre que facture electricite)
- AUTRE (specifie lequel)

**ETAPE 2 - EXTRACTION CIBLEE PAR TYPE**

Si CIN :
- numero_cin: [numero]
- nom_complet: [nom]
- prenom: [prenom]
- date_naissance: [JJ/MM/AAAA]
- lieu_naissance: [ville]
- adresse_complete: [adresse]
- date_emission: [JJ/MM/AAAA]
- date_expiration: [JJ/MM/AAAA]

Si PASSEPORT :
- numero_passeport: [numero]
- nom_complet: [nom]
- prenom: [prenom]
- date_naissance: [JJ/MM/AAAA]
- lieu_naissance: [ville]
- nationalite: [nationalite]
- date_emission: [JJ/MM/AAAA]
- date_expiration: [JJ/MM/AAAA]

Si FACTURE_ELECTRICITE :
- fournisseur: [ONE, REDAL, etc.]
- numero_client: [numero abonne]
- nom_titulaire: [nom]
- adresse_facturation: [adresse]
- periode_facturation: [periode]
- montant_a_payer: [montant en DH]
- date_emission: [JJ/MM/AAAA]
- date_limite_paiement: [JJ/MM/AAAA]

Si BULLETIN_SALAIRE :
- nom_employe: [nom]
- prenom_employe: [prenom]
- entreprise: [nom employeur]
- numero_cnss: [numero]
- poste: [fonction]
- salaire_brut: [montant en DH]
- salaire_net: [montant en DH]
- periode: [MM/AAAA]
- date_emission: [JJ/MM/AAAA]

Si RELEVE_BANCAIRE :
- banque: [nom banque]
- nom_titulaire: [nom]
- numero_compte: [RIB/numero]
- periode_releve: [du JJ/MM/AAAA au JJ/MM/AAAA]
- solde_initial: [montant en DH]
- solde_final: [montant en DH]
- date_emission: [JJ/MM/AAAA]

**ETAPE 3 - GESTION DES CAS DIFFICILES**
- Si un champ est illisible : marque "ILLISIBLE"
- Si un champ est partiellement visible : marque "PARTIEL: [ce qui est visible]"
- Si incertain sur une valeur : marque "INCERTAIN: [valeur probable]"

**FORMAT DE REPONSE OBLIGATOIRE :**
```
TYPE_DOCUMENT: [type identifie]
CONFIANCE_CLASSIFICATION: [HAUTE/MOYENNE/FAIBLE]
QUALITE_IMAGE: [BONNE/MOYENNE/FAIBLE]

INFORMATIONS_EXTRAITES:
- nom_complet: [valeur]
- prenom: [valeur]
- [autres champs selon le type...]

OBSERVATIONS:
- [Notes sur la qualite, problemes detectes]
```

**REGLES IMPORTANTES :**
1. Privilegie la precision sur la quantite - mieux vaut marquer ILLISIBLE que deviner
2. Normalise les formats de date en JJ/MM/AAAA
3. Pour les montants, indique l'unite (DH, MAD)
4. Pour les adresses, extrais l'adresse complete
5. Attention aux variations d'ecriture (manuscrit vs imprime)

Analyse maintenant ce document :"""}
        ]
    }


def construire_prompt_recuperation() -> dict:
    """Prompt specialise pour documents de mauvaise qualite"""
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": """Ce document semble de mauvaise qualite. Mode recuperation active :

1. Identifie les zones de texte les plus lisibles
2. Concentre-toi sur les informations critiques : nom, prenom, numeros
3. Utilise le contexte visuel (logos, mise en page) pour le type de document

**FORMAT DE REPONSE :**
```
TYPE_DOCUMENT: [type probable]
CONFIANCE_CLASSIFICATION: FAIBLE
QUALITE_IMAGE: FAIBLE

INFORMATIONS_EXTRAITES:
- nom_complet: [valeur si lisible sinon ILLISIBLE]
- prenom: [valeur si lisible sinon ILLISIBLE]
- [autres champs critiques...]

OBSERVATIONS:
- Document de tres mauvaise qualite
- [suggestions d'amelioration]
```"""}
        ]
    }


def extraire_infos_documents(client, chemins_images: list) -> Dict[str, dict]:
    """
    Extrait les informations des documents avec validation de qualite
    Retourne un dictionnaire avec analyses completes
    """
    if not chemins_images:
        raise ValueError("Aucun chemin d'image fourni")

    resultats = {}

    for chemin in chemins_images:
        try:
            # Verifications prealables
            if not os.path.exists(chemin):
                safe_print(f"L'image n'existe pas: {chemin}")
                resultats[chemin] = {
                    "extraction_brute": "ERREUR: Fichier introuvable",
                    "qualite": "ERREUR",
                    "parsed_info": None
                }
                continue

            # Encoder l'image
            base64_image = encode_image_to_base64(chemin)
            if not base64_image:
                safe_print(f"Echec de l'encodage: {chemin}")
                resultats[chemin] = {
                    "extraction_brute": "ERREUR: Probleme d'encodage",
                    "qualite": "ERREUR",
                    "parsed_info": None
                }
                continue

            safe_print(f"Traitement de: {os.path.basename(chemin)}")

            # Tentative d'extraction normale
            resultat_extraction = _extraire_avec_gestion_qualite(client, base64_image, chemin)
            resultats[chemin] = resultat_extraction

        except Exception as e:
            safe_print(f"Erreur generale pour {chemin}: {str(e)}")
            resultats[chemin] = {
                "extraction_brute": f"ERREUR: {str(e)}",
                "qualite": "ERREUR",
                "parsed_info": _creer_document_info_erreur(str(e))
            }

    return resultats


def _extraire_avec_gestion_qualite(client, base64_image: str, chemin: str) -> dict:
    """Extrait avec gestion intelligente de la qualite"""

    # Premiere tentative avec prompt normal
    try:
        prompt = construire_prompt_ocr()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                prompt,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1200,
            temperature=0.1  # Plus deterministe pour l'extraction
        )

        texte_extrait = response.choices[0].message.content
        parsed_result = parser_informations_ameliore(texte_extrait)
        qualite = evaluer_qualite_extraction(parsed_result)

        # Si qualite tres faible, essayer le mode recuperation
        if qualite["niveau"] == "FAIBLE":
            safe_print(f"Qualite faible detectee pour {chemin}, tentative mode recuperation...")
            return _tentative_recuperation(client, base64_image, texte_extrait, parsed_result)

        return {
            "extraction_brute": texte_extrait,
            "parsed_info": parsed_result,
            "qualite": qualite,
            "mode": "NORMAL"
        }

    except Exception as api_error:
        safe_print(f"Erreur API pour {chemin}: {str(api_error)}")
        return {
            "extraction_brute": f"ERREUR API: {str(api_error)}",
            "parsed_info": _creer_document_info_erreur(str(api_error)),
            "qualite": {"niveau": "ERREUR", "score_qualite": 0},
            "mode": "ERREUR"
        }


def _tentative_recuperation(client, base64_image: str, extraction_normale: str, parsed_normal: dict) -> dict:
    """Tentative de recuperation pour documents difficiles"""
    try:
        prompt_recuperation = construire_prompt_recuperation()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                prompt_recuperation,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800,
            temperature=0.2
        )

        texte_recuperation = response.choices[0].message.content
        parsed_recuperation = parser_informations_ameliore(texte_recuperation)

        # Fusionner les informations des deux tentatives
        info_fusionnee = _fusionner_extractions(parsed_normal, parsed_recuperation)

        return {
            "extraction_brute": extraction_normale,
            "extraction_recuperation": texte_recuperation,
            "parsed_info": info_fusionnee,
            "qualite": {"niveau": "RECUPERATION", "score_qualite": 30},
            "mode": "RECUPERATION"
        }

    except Exception as e:
        safe_print(f"Erreur mode recuperation: {e}")
        return {
            "extraction_brute": extraction_normale,
            "parsed_info": parsed_normal,
            "qualite": {"niveau": "FAIBLE", "score_qualite": 20},
            "mode": "ECHEC_RECUPERATION"
        }


def parser_informations_ameliore(texte_document: str) -> dict:
    """
    Parse le nouveau format structure de reponse
    """
    try:
        texte_document = safe_text_handling(texte_document)

        result = {
            "type_document": "INCONNU",
            "confiance_classification": "FAIBLE",
            "qualite_image": "INCONNUE",
            "informations": {},
            "observations": []
        }

        lines = texte_document.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith('TYPE_DOCUMENT:'):
                result["type_document"] = line.split(':', 1)[1].strip()
            elif line.startswith('CONFIANCE_CLASSIFICATION:'):
                result["confiance_classification"] = line.split(':', 1)[1].strip()
            elif line.startswith('QUALITE_IMAGE:'):
                result["qualite_image"] = line.split(':', 1)[1].strip()
            elif line == 'INFORMATIONS_EXTRAITES:':
                current_section = 'info'
            elif line == 'OBSERVATIONS:':
                current_section = 'obs'
            elif line.startswith('- ') and current_section == 'info':
                if ':' in line:
                    champ, valeur = line[2:].split(':', 1)
                    champ_clean = safe_text_handling(champ.strip())
                    valeur_clean = safe_text_handling(valeur.strip())
                    result["informations"][champ_clean] = valeur_clean
            elif line.startswith('- ') and current_section == 'obs':
                result["observations"].append(line[2:])

        return result

    except Exception as e:
        safe_print(f"Erreur parsing ameliore: {str(e)}")
        return {
            "type_document": "ERREUR",
            "confiance_classification": "FAIBLE",
            "qualite_image": "INCONNUE",
            "informations": {"erreur": str(e)},
            "observations": ["Erreur de parsing"]
        }


def convertir_vers_document_info(parsed_data: dict) -> DocumentInfo:
    """Convertit le dictionnaire parse vers DocumentInfo"""
    try:
        info = DocumentInfo(type_document=parsed_data.get("type_document", "INCONNU"))

        # Mapping des champs standards
        informations = parsed_data.get("informations", {})

        # Nom et prenom
        info.nom = informations.get("nom_complet") or informations.get("nom_employe") or informations.get("nom_titulaire")
        info.prenom = informations.get("prenom") or informations.get("prenom_employe")

        # Dates
        info.date_naissance = informations.get("date_naissance")
        info.date_emission = informations.get("date_emission")
        info.date_expiration = informations.get("date_expiration")

        # Adresse
        info.adresse = informations.get("adresse_complete") or informations.get("adresse_facturation")

        # Numeros specifiques
        info.numero_document = (informations.get("numero_cin") or
                              informations.get("numero_passeport") or
                              informations.get("numero_client") or
                              informations.get("numero_compte"))

        # Informations supplementaires dans autres_infos
        for cle, valeur in informations.items():
            if cle not in ["nom_complet", "prenom", "date_naissance", "date_emission",
                          "date_expiration", "adresse_complete", "numero_cin"]:
                info.autres_infos[cle] = valeur

        # Metadonnees
        info.autres_infos["confiance_classification"] = parsed_data.get("confiance_classification")
        info.autres_infos["qualite_image"] = parsed_data.get("qualite_image")
        info.autres_infos["observations"] = parsed_data.get("observations", [])

        return info

    except Exception as e:
        safe_print(f"Erreur conversion DocumentInfo: {e}")
        return _creer_document_info_erreur(str(e))


def evaluer_qualite_extraction(parsed_result: dict) -> dict:
    """Evalue la qualite de l'extraction OCR"""
    score = 100
    recommandations = []

    # Penalites selon la qualite d'image
    qualite_image = parsed_result.get("qualite_image", "INCONNUE").upper()
    if qualite_image == "FAIBLE":
        score -= 30
        recommandations.append("Ameliorer la qualite de l'image")
    elif qualite_image == "MOYENNE":
        score -= 15

    # Penalites selon la confiance de classification
    confiance = parsed_result.get("confiance_classification", "FAIBLE").upper()
    if confiance == "FAIBLE":
        score -= 25
        recommandations.append("Verifier le type de document")
    elif confiance == "MOYENNE":
        score -= 10

    # Compter les champs problematiques
    informations = parsed_result.get("informations", {})
    champs_problematiques = 0

    for valeur in informations.values():
        valeur_str = str(valeur).upper()
        if any(keyword in valeur_str for keyword in ["ILLISIBLE", "PARTIEL", "INCERTAIN"]):
            champs_problematiques += 1

    if champs_problematiques > 0:
        score -= champs_problematiques * 12
        recommandations.append(f"{champs_problematiques} champ(s) problematique(s)")

    # Verifier la completude des informations essentielles
    champs_essentiels = ["nom_complet", "prenom"]
    champs_manquants = [c for c in champs_essentiels if not informations.get(c)]

    if champs_manquants:
        score -= len(champs_manquants) * 15
        recommandations.append(f"Champs essentiels manquants: {', '.join(champs_manquants)}")

    score = max(0, score)

    niveau = ("EXCELLENT" if score >= 90 else
             "BON" if score >= 70 else
             "MOYEN" if score >= 50 else
             "FAIBLE")

    return {
        "score_qualite": score,
        "niveau": niveau,
        "recommandations": recommandations,
        "champs_problematiques": champs_problematiques,
        "confiance_classification": confiance
    }


def _fusionner_extractions(normale: dict, recuperation: dict) -> dict:
    """Fusionne les informations de deux extractions"""
    fusion = normale.copy()

    # Prendre les meilleures informations de chaque extraction
    info_normale = normale.get("informations", {})
    info_recuperation = recuperation.get("informations", {})

    for cle, valeur_recup in info_recuperation.items():
        valeur_normale = info_normale.get(cle, "")

        # Si la valeur normale est problematique et la recuperation est claire
        if (any(kw in str(valeur_normale).upper() for kw in ["ILLISIBLE", "PARTIEL"]) and
            not any(kw in str(valeur_recup).upper() for kw in ["ILLISIBLE", "PARTIEL"])):
            fusion["informations"][cle] = valeur_recup

    return fusion


def _creer_document_info_erreur(message_erreur: str) -> DocumentInfo:
    """Cree un DocumentInfo pour les cas d'erreur"""
    return DocumentInfo(
        type_document="ERREUR",
        autres_infos={"erreur": message_erreur}
    )


def analyser_nom_fichier_ameliore(chemin_fichier: str) -> DocumentInfo:
    """Version amelioree de l'analyse du nom de fichier"""
    nom_fichier = os.path.basename(chemin_fichier).lower()
    info_doc = DocumentInfo(type_document="INCONNU")

    # Mapping ameliore des types
    types_mapping = {
        "cin": "CIN",
        "identite": "CIN",
        "piece": "CIN",
        "passeport": "PASSEPORT",
        "domicile": "JUSTIFICATIF_DOMICILE",
        "justificatif": "JUSTIFICATIF_DOMICILE",
        "electricite": "FACTURE_ELECTRICITE",
        "one": "FACTURE_ELECTRICITE",
        "redal": "FACTURE_ELECTRICITE",
        "amendis": "FACTURE_ELECTRICITE",
        "bancaire": "RELEVE_BANCAIRE",
        "releve": "RELEVE_BANCAIRE",
        "salaire": "BULLETIN_SALAIRE",
        "bulletin": "BULLETIN_SALAIRE",
        "paie": "BULLETIN_SALAIRE"
    }

    for mot_cle, type_doc in types_mapping.items():
        if mot_cle in nom_fichier:
            info_doc.type_document = type_doc
            break

    # Extraction amelioree d'informations du nom
    # Patterns pour nom/prenom
    patterns_nom = [
        r'([A-Za-z]+)_([A-Za-z]+)_',  # NOM_PRENOM_
        r'_([A-Za-z]+)_([A-Za-z]+)',  # _NOM_PRENOM
        r'([A-Za-z]+)-([A-Za-z]+)',   # NOM-PRENOM
    ]

    for pattern in patterns_nom:
        match = re.search(pattern, nom_fichier)
        if match:
            info_doc.nom = match.group(1).upper()
            info_doc.prenom = match.group(2).capitalize()
            break

    return info_doc


# Fonction principale d'extraction OCR uniquement
def traiter_documents_ocr(client, chemins_images: list) -> Dict[str, any]:
    """
    Traitement OCR uniquement - se concentre sur l'extraction
    """
    # 1. Extraction OCR
    resultats_ocr = extraire_infos_documents(client, chemins_images)

    # 2. Conversion vers DocumentInfo
    infos_documents = {}
    for chemin, resultat in resultats_ocr.items():
        if resultat.get("parsed_info"):
            info_doc = convertir_vers_document_info(resultat["parsed_info"])
            infos_documents[chemin] = info_doc
        else:
            # Fallback sur l'analyse du nom de fichier
            info_doc = analyser_nom_fichier_ameliore(chemin)
            infos_documents[chemin] = info_doc

    return {
        "resultats_ocr": resultats_ocr,
        "infos_documents": infos_documents,
        "resume_extraction": _generer_resume_extraction(resultats_ocr)
    }


def _generer_resume_extraction(resultats_ocr: Dict) -> Dict:
    """Genere un resume de l'extraction OCR uniquement"""
    total_docs = len(resultats_ocr)
    docs_ok = sum(1 for r in resultats_ocr.values() if r.get("qualite", {}).get("niveau") not in ["ERREUR", "FAIBLE"])
    docs_excellents = sum(1 for r in resultats_ocr.values() if r.get("qualite", {}).get("niveau") == "EXCELLENT")
    docs_recuperation = sum(1 for r in resultats_ocr.values() if r.get("mode") == "RECUPERATION")

    return {
        "total_documents": total_docs,
        "documents_traites_ok": docs_ok,
        "documents_excellents": docs_excellents,
        "documents_en_recuperation": docs_recuperation,
        "taux_succes_global": f"{(docs_ok/total_docs*100):.1f}%" if total_docs > 0 else "0%",
        "taux_excellence": f"{(docs_excellents/total_docs*100):.1f}%" if total_docs > 0 else "0%",
        "recommandations_extraction": _generer_recommandations_extraction(resultats_ocr)
    }


def _generer_recommandations_extraction(resultats_ocr: Dict) -> List[str]:
    """Genere des recommandations specifiques a l'extraction"""
    recommandations = []

    docs_faible_qualite = [k for k, v in resultats_ocr.items()
                          if v.get("qualite", {}).get("niveau") == "FAIBLE"]

    if docs_faible_qualite:
        recommandations.append(f"{len(docs_faible_qualite)} document(s) de faible qualite detecte(s)")
        recommandations.append("Conseil: Ameliorer l'eclairage et la resolution des images")

    docs_erreur = [k for k, v in resultats_ocr.items()
                  if v.get("qualite", {}).get("niveau") == "ERREUR"]

    if docs_erreur:
        recommandations.append(f"{len(docs_erreur)} document(s) en erreur")
        recommandations.append("Conseil: Verifier le format et l'accessibilite des fichiers")

    return recommandations
