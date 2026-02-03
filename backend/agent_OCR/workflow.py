"""
backend/agent_OCR/workflow.py - Workflow LangGraph pour l'OCR
"""
import os
import time
from langgraph.graph import END, StateGraph, START

from backend.agent_OCR.models import State, DocumentInfo
from backend.agent_OCR.utils import safe_print
from backend.agent_OCR.charger_document import charger_documents, verifier_pdf, convertir_pdf_en_images
from backend.agent_OCR.extraction import init_client, traiter_documents_ocr, analyser_nom_fichier_ameliore
from backend.agent_OCR.concordance import verifier_concordance_complete, analyser_concordance_detaillee
from backend.agent_OCR.rapport import sauvegarder_rapport_complet


###################
# NOEUDS DU WORKFLOW
###################

def charger_documents_node(state: State) -> State:
    """Noeud pour charger les documents PDF du dossier"""
    safe_print("\n=== CHARGEMENT DES DOCUMENTS ===")

    state_dict = state.dict()
    state_dict['workflow_status'] = "CHARGEMENT_DOCUMENTS"

    try:
        if not isinstance(state.dossier_path, str):
            state_dict['dossier_path'] = str(state.dossier_path)

        pdf_paths = charger_documents(state_dict['dossier_path'])
        state_dict['pdf_paths'] = pdf_paths
        state_dict['nb_pdfs_traites'] = len(pdf_paths)

        safe_print(f"Nombre de PDF charges: {len(pdf_paths)}")

        if not pdf_paths:
            state_dict['erreurs_rencontrees'].append("Aucun PDF trouve dans le dossier")

    except Exception as e:
        error_msg = f"Erreur lors du chargement des documents: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)
        state_dict['pdf_paths'] = []

    safe_print("=== FIN CHARGEMENT DES DOCUMENTS ===\n")

    return State(**state_dict)


def valider_pdfs_node(state: State) -> State:
    """Noeud pour valider les PDFs avant traitement"""
    safe_print("\n=== VALIDATION DES PDFs ===")

    state_dict = state.dict()
    state_dict['workflow_status'] = "VALIDATION_PDFS"

    pdfs_valides = []
    pdfs_invalides = []

    for pdf_path in state.pdf_paths:
        if verifier_pdf(pdf_path):
            pdfs_valides.append(pdf_path)
        else:
            pdfs_invalides.append(pdf_path)

    state_dict['pdf_paths'] = pdfs_valides
    state_dict['pdfs_rejetes'] = pdfs_invalides
    state_dict['nb_pdfs_rejetes'] = len(pdfs_invalides)

    safe_print(f"PDFs valides: {len(pdfs_valides)}")
    safe_print(f"PDFs rejetes: {len(pdfs_invalides)}")

    if pdfs_invalides:
        state_dict['erreurs_rencontrees'].append(f"{len(pdfs_invalides)} PDFs rejetes pour cause d'invalidite")

    safe_print("=== FIN VALIDATION DES PDFs ===\n")

    return State(**state_dict)


def convertir_en_images_node(state: State) -> State:
    """Noeud pour convertir les PDFs en images"""
    safe_print("\n=== CONVERSION EN IMAGES ===")

    state_dict = state.dict()
    state_dict['workflow_status'] = "CONVERSION_IMAGES"

    if not state.pdf_paths:
        safe_print("Aucun PDF a convertir")
        state_dict['images_paths'] = []
        state_dict['nb_images_generees'] = 0
        safe_print("=== FIN CONVERSION EN IMAGES ===\n")
        return State(**state_dict)

    try:
        output_dir = os.path.join(state.dossier_path, "images_temp")
        images_paths = convertir_pdf_en_images(state.pdf_paths, output_dir)
        state_dict['images_paths'] = images_paths
        state_dict['nb_images_generees'] = len(images_paths)

        safe_print(f"Nombre d'images generees: {len(images_paths)}")

        if not images_paths:
            state_dict['erreurs_rencontrees'].append("Aucune image generee a partir des PDFs")

    except Exception as e:
        error_msg = f"Erreur lors de la conversion en images: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)
        state_dict['images_paths'] = []
        state_dict['nb_images_generees'] = 0

    safe_print("=== FIN CONVERSION EN IMAGES ===\n")

    return State(**state_dict)


def extraire_et_parser_infos_node(state: State) -> State:
    """
    NOEUD UNIFIE: Extraction OCR ET parsing avec le nouveau systeme
    """
    safe_print("\n=== EXTRACTION ET PARSING DES INFORMATIONS ===")

    state_dict = state.dict()
    state_dict['workflow_status'] = "EXTRACTION_ET_PARSING"

    if not state.images_paths:
        safe_print("Aucune image a analyser")
        state_dict['infos_documents'] = {}
        state_dict['documents_texte'] = {}
        state_dict['nb_documents_analyses'] = 0
        safe_print("=== FIN EXTRACTION ET PARSING ===\n")
        return State(**state_dict)

    try:
        # Utiliser le nouveau systeme d'extraction ameliore
        client = init_client()
        resultats_complets = traiter_documents_ocr(client, state.images_paths)

        # Extraire les differentes parties du resultat
        resultats_ocr = resultats_complets.get("resultats_ocr", {})
        infos_documents = resultats_complets.get("infos_documents", {})
        resume_extraction = resultats_complets.get("resume_extraction", {})

        # Stocker dans le state
        state_dict['infos_documents'] = {}
        state_dict['documents_texte'] = {}
        state_dict['resultats_ocr_detailles'] = resultats_ocr

        # Convertir les DocumentInfo en dict pour le stockage et garder les textes
        for chemin, info_doc in infos_documents.items():
            # Stocker l'objet DocumentInfo converti en dict
            if hasattr(info_doc, 'dict'):
                state_dict['infos_documents'][chemin] = info_doc.dict()
            else:
                state_dict['infos_documents'][chemin] = info_doc

            # Recuperer le texte brut de l'extraction si disponible
            if chemin in resultats_ocr:
                extraction_brute = resultats_ocr[chemin].get("extraction_brute", "")
                state_dict['documents_texte'][chemin] = extraction_brute

        state_dict['nb_documents_analyses'] = len(infos_documents)

        # Afficher les statistiques d'extraction
        safe_print(f"Documents traites: {resume_extraction.get('total_documents', 0)}")
        safe_print(f"Documents avec succes: {resume_extraction.get('documents_traites_ok', 0)}")
        safe_print(f"Taux de succes: {resume_extraction.get('taux_succes_global', '0%')}")

        # Afficher le detail par document
        for chemin, info_doc in infos_documents.items():
            type_doc = info_doc.type_document if hasattr(info_doc, 'type_document') else 'INCONNU'
            safe_print(f"Document analyse: {os.path.basename(chemin)} -> {type_doc}")

        if not infos_documents:
            state_dict['erreurs_rencontrees'].append("Aucune information extraite des images")

    except Exception as e:
        error_msg = f"Erreur lors de l'extraction et parsing: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)
        state_dict['infos_documents'] = {}
        state_dict['documents_texte'] = {}
        state_dict['nb_documents_analyses'] = 0

    safe_print("=== FIN EXTRACTION ET PARSING ===\n")

    return State(**state_dict)


def verifier_concordance_node(state: State) -> State:
    """
    NOEUD AMELIORE: Verification de concordance avec analyse detaillee
    """
    safe_print("\n=== VERIFICATION DE CONCORDANCE AVANCEE ===")

    state_dict = state.dict()
    state_dict['workflow_status'] = "VERIFICATION_CONCORDANCE"

    if not state.infos_documents:
        safe_print("Aucune information a verifier")
        state_dict['concordance'] = None
        state_dict['problemes_concordance'] = []
        state_dict['analyse_concordance_detaillee'] = {}
        safe_print("=== FIN VERIFICATION DE CONCORDANCE ===\n")
        return State(**state_dict)

    try:
        # Reconvertir les dicts en objets DocumentInfo
        infos_documents_obj = {}
        for chemin, info in state.infos_documents.items():
            if isinstance(info, dict):
                infos_documents_obj[chemin] = DocumentInfo(**info)
            else:
                infos_documents_obj[chemin] = info

        # Verification de base
        concordance, problemes = verifier_concordance_complete(infos_documents_obj)

        # Analyse detaillee (nouvelle fonction)
        analyse_detaillee = analyser_concordance_detaillee(infos_documents_obj)

        # Stocker tous les resultats
        state_dict['concordance'] = concordance
        state_dict['problemes_concordance'] = problemes
        state_dict['analyse_concordance_detaillee'] = analyse_detaillee

        # Affichage des resultats
        safe_print(f"Concordance: {concordance}")
        safe_print(f"Score de confiance: {analyse_detaillee.get('score_confiance', 0):.1f}/100")

        if not concordance:
            safe_print(f"Problemes detectes: {len(problemes)}")
            for p in problemes:
                safe_print(f"  - {p}")
        else:
            safe_print("Toutes les informations concordent")

        # Afficher les recommandations
        recommandations = analyse_detaillee.get('recommandations', [])
        if recommandations:
            safe_print("Recommandations:")
            for rec in recommandations:
                safe_print(f"  - {rec}")

    except Exception as e:
        error_msg = f"Erreur lors de la verification de concordance: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)
        state_dict['concordance'] = None
        state_dict['problemes_concordance'] = []
        state_dict['analyse_concordance_detaillee'] = {}

    safe_print("=== FIN VERIFICATION DE CONCORDANCE ===\n")

    return State(**state_dict)


def generer_rapport_node(state: State) -> State:
    """
    NOEUD AMELIORE: Generation de rapport complet avec nouvelles fonctionnalites
    """
    safe_print("\n=== GENERATION DU RAPPORT COMPLET ===")

    state_dict = state.dict()
    state_dict['workflow_status'] = "GENERATION_RAPPORT"

    try:
        if not state.infos_documents:
            safe_print("Aucune information pour generer un rapport")
            return State(**state_dict)

        # Reconvertir les dicts en objets DocumentInfo
        infos_documents_obj = {}
        for chemin, info in state.infos_documents.items():
            if isinstance(info, dict):
                infos_documents_obj[chemin] = DocumentInfo(**info)
            else:
                infos_documents_obj[chemin] = info

        # Recuperer l'analyse de concordance detaillee
        analyse_detaillee = state_dict.get('analyse_concordance_detaillee', {})

        # Recuperer les resultats OCR detailles
        resultats_ocr = state_dict.get('resultats_ocr_detailles', {})

        # Generer une reference de demande
        ref_demande = os.path.basename(state.dossier_path)

        # Utiliser la nouvelle fonction de sauvegarde complete
        succes = sauvegarder_rapport_complet(
            infos_documents_obj,
            state.concordance,
            state.problemes_concordance,
            state.dossier_path,
            state=state,
            ref_demande=ref_demande,
            analyse_detaillee=analyse_detaillee,
            resultats_ocr=resultats_ocr
        )

        if succes:
            # Mise a jour des chemins dans le state
            state_dict['rapport_path'] = os.path.join(state.dossier_path, "rapport_ocr.txt")

            safe_print("Rapport complet genere et sauvegarde")
            safe_print("   - Rapport TXT: rapport_ocr.txt")
            safe_print("   - Rapport JSON: rapport_analyse.json")
            safe_print("   - Rapport PDF: rapport_ocr.pdf")
        else:
            safe_print("Probleme lors de la generation du rapport")
            state_dict['erreurs_rencontrees'].append("Erreur lors de la generation du rapport")

    except Exception as e:
        error_msg = f"Erreur lors de la generation du rapport: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)

    safe_print("=== FIN GENERATION DU RAPPORT ===\n")

    return State(**state_dict)


###################
# CONSTRUCTION DU WORKFLOW OPTIMISE
###################

def construire_workflow():
    """Construit et retourne le workflow LangGraph optimise avec nouveaux modules"""
    workflow = StateGraph(State)

    # Ajouter tous les noeuds - WORKFLOW SIMPLIFIE
    workflow.add_node("charger_documents", charger_documents_node)
    workflow.add_node("valider_pdfs", valider_pdfs_node)
    workflow.add_node("convertir_en_images", convertir_en_images_node)
    workflow.add_node("extraire_et_parser_infos", extraire_et_parser_infos_node)
    workflow.add_node("verifier_concordance", verifier_concordance_node)
    workflow.add_node("generer_rapport", generer_rapport_node)

    # Definir le point d'entree
    workflow.add_edge(START, "charger_documents")

    # Definir le flux principal - SIMPLIFIE
    workflow.add_edge("charger_documents", "valider_pdfs")
    workflow.add_edge("valider_pdfs", "convertir_en_images")
    workflow.add_edge("convertir_en_images", "extraire_et_parser_infos")
    workflow.add_edge("extraire_et_parser_infos", "verifier_concordance")
    workflow.add_edge("verifier_concordance", "generer_rapport")
    workflow.add_edge("generer_rapport", END)

    return workflow.compile()


###################
# FONCTIONS UTILITAIRES MISES A JOUR
###################

def creer_state_initial(dossier_path: str) -> State:
    """Cree un etat initial pour le workflow"""
    return State(dossier_path=dossier_path)


def get_workflow_info():
    """Retourne les informations sur le workflow"""
    return {
        "version": "3.0 - Adapte aux nouveaux modules",
        "nodes": [
            "charger_documents",
            "valider_pdfs",
            "convertir_en_images",
            "extraire_et_parser_infos",
            "verifier_concordance",
            "generer_rapport"
        ],
        "nouveautes": [
            "Utilise le nouveau module extraction_ocr avec gestion de qualite",
            "Utilise le nouveau module concordance avec analyse detaillee",
            "Workflow simplifie avec noeud unifie extraction+parsing",
            "Rapports enrichis avec scores de confiance",
            "Support du mode recuperation pour documents difficiles"
        ],
        "compatibility": [
            "Compatible avec les nouveaux modules d'extraction et concordance",
            "Gestion amelioree des erreurs OCR",
            "Metadonnees de qualite conservees",
            "Rapports multi-formats (TXT, JSON, PDF)"
        ]
    }


# EXPORTS POUR COMPATIBILITE
__all__ = [
    'State',
    'DocumentInfo',
    'construire_workflow',
    'creer_state_initial',
    'get_workflow_info'
]
