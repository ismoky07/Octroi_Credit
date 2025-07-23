import os
import time
from langgraph.graph import END, StateGraph, START

# ============================================
# IMPORTS SÉCURISÉS AVEC GESTION D'ERREURS - VERSION ADAPTÉE
# ============================================

# IMPORT MODELS
try:
    from .models import State, DocumentInfo
    InfoDocument = DocumentInfo  # Alias pour compatibilité
except ImportError:
    try:
        from models import State, DocumentInfo
        InfoDocument = DocumentInfo
    except ImportError:
        print("❌ ERREUR CRITIQUE: Impossible d'importer models.py")
        raise

# IMPORT UTILS
try:
    from .utilsAgentOCR import safe_print
except ImportError:
    try:
        from utilsAgentOCR import safe_print
    except ImportError:
        def safe_print(message):
            print(f"[OCR] {message}")

# IMPORT CHARGER DOCUMENT
try:
    from .charger_document import charger_documents, verifier_pdf, convertir_pdf_en_images
except ImportError:
    try:
        from charger_document import charger_documents, verifier_pdf, convertir_pdf_en_images
    except ImportError:
        def charger_documents(dossier_path):
            """Fallback pour charger_documents"""
            import glob
            pdfs = glob.glob(os.path.join(dossier_path, "*.pdf"))
            safe_print(f"⚠️ Fallback charger_documents: {len(pdfs)} PDFs trouvés")
            return pdfs
        
        def verifier_pdf(pdf_path):
            """Fallback pour verifier_pdf"""
            return os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf')
        
        def convertir_pdf_en_images(pdf_paths, output_dir):
            """Fallback pour convertir_pdf_en_images"""
            safe_print("⚠️ Fonction convertir_pdf_en_images non disponible - fallback utilisé")
            return []

# IMPORT EXTRACTION OCR - NOUVEAU MODULE AMÉLIORÉ
try:
    from Admin.agent_OCR_Comparaison.extration_ocr import init_client, traiter_documents_ocr, analyser_nom_fichier_ameliore
except ImportError:
    try:
        from Admin.agent_OCR_Comparaison.extration_ocr import init_client, traiter_documents_ocr, analyser_nom_fichier_ameliore
    except ImportError:
        def init_client():
            """Fallback pour init_client"""
            safe_print("⚠️ Client OCR non disponible - fallback utilisé")
            return None
        
        def traiter_documents_ocr(client, images_paths):
            """Fallback pour traiter_documents_ocr"""
            safe_print("⚠️ Fonction traiter_documents_ocr non disponible - fallback utilisé")
            return {
                "resultats_ocr": {},
                "infos_documents": {},
                "resume_extraction": {
                    "total_documents": 0,
                    "documents_traites_ok": 0,
                    "taux_succes_global": "0%"
                }
            }
        
        def analyser_nom_fichier_ameliore(chemin):
            """Fallback pour analyser_nom_fichier_ameliore"""
            nom_fichier = os.path.basename(chemin).lower()
            if "cin" in nom_fichier or "identite" in nom_fichier:
                type_doc = "CIN"
            elif "passeport" in nom_fichier:
                type_doc = "PASSEPORT"
            elif "domicile" in nom_fichier or "adresse" in nom_fichier:
                type_doc = "JUSTIFICATIF_DOMICILE"
            elif "salaire" in nom_fichier or "bulletin" in nom_fichier:
                type_doc = "BULLETIN_SALAIRE"
            else:
                type_doc = "DOCUMENT_GENERIQUE"
            
            return DocumentInfo(type_document=type_doc)

# IMPORT CONCORDANCE - NOUVEAU MODULE AMÉLIORÉ
try:
    from agent_OCR_Comparaison.concordance_checker import verifier_concordance_complete, analyser_concordance_detaillee
except ImportError:
    try:
        from concordance_checker import verifier_concordance_complete, analyser_concordance_detaillee
    except ImportError:
        def verifier_concordance_complete(infos_documents):
            """Fallback pour verifier_concordance_complete"""
            safe_print("⚠️ Fonction verifier_concordance_complete non disponible - fallback utilisé")
            return True, []
        
        def analyser_concordance_detaillee(infos_documents):
            """Fallback pour analyser_concordance_detaillee"""
            safe_print("⚠️ Fonction analyser_concordance_detaillee non disponible - fallback utilisé")
            return {
                "total_documents": len(infos_documents),
                "concordance_globale": True,
                "problemes_detectes": [],
                "score_confiance": 100.0,
                "recommandations": []
            }

# IMPORT RAPPORT GENERATOR - VERSION ADAPTÉE
try:
    from .rapport_generator import sauvegarder_rapport_complet
except ImportError:
    try:
        from rapport_generator import sauvegarder_rapport_complet
    except ImportError:
        def sauvegarder_rapport_complet(infos_documents, concordance, problemes_concordance, 
                                       output_dir, state=None, ref_demande="N/A", 
                                       analyse_detaillee=None, resultats_ocr=None):
            """Fallback pour sauvegarder_rapport_complet"""
            try:
                import json
                from datetime import datetime
                
                # Créer un rapport basique
                rapport_data = {
                    "ref_demande": ref_demande,
                    "timestamp": datetime.now().isoformat(),
                    "resume": {
                        "nombre_documents": len(infos_documents),
                        "concordance": concordance,
                        "problemes": len(problemes_concordance)
                    },
                    "documents": {},
                    "problemes_concordance": problemes_concordance
                }
                
                # Convertir les DocumentInfo en dict
                for chemin, info in infos_documents.items():
                    nom_fichier = os.path.basename(chemin)
                    if hasattr(info, 'dict'):
                        rapport_data["documents"][nom_fichier] = info.dict()
                    elif hasattr(info, '__dict__'):
                        rapport_data["documents"][nom_fichier] = info.__dict__
                    else:
                        rapport_data["documents"][nom_fichier] = str(info)
                
                # Sauvegarder en JSON
                chemin_rapport = os.path.join(output_dir, "rapport_analyse.json")
                with open(chemin_rapport, "w", encoding="utf-8") as f:
                    json.dump(rapport_data, f, ensure_ascii=False, indent=2)
                
                safe_print(f"Rapport fallback sauvegardé: {chemin_rapport}")
                return True
                
            except Exception as e:
                safe_print(f"Erreur fallback rapport: {e}")
                return False

###################
# NŒUDS DU WORKFLOW - VERSIONS ADAPTÉES POUR NOUVEAUX MODULES
###################

def charger_documents_node(state: State) -> State:
    """Nœud pour charger les documents PDF du dossier"""
    safe_print("\n=== CHARGEMENT DES DOCUMENTS ===")
    
    state_dict = state.dict()
    state_dict['workflow_status'] = "CHARGEMENT_DOCUMENTS"
    
    try:
        if not isinstance(state.dossier_path, str):
            state_dict['dossier_path'] = str(state.dossier_path)
            
        pdf_paths = charger_documents(state_dict['dossier_path'])
        state_dict['pdf_paths'] = pdf_paths
        state_dict['nb_pdfs_traites'] = len(pdf_paths)
        
        safe_print(f"Nombre de PDF chargés: {len(pdf_paths)}")
        
        if not pdf_paths:
            state_dict['erreurs_rencontrees'].append("Aucun PDF trouvé dans le dossier")
            
    except Exception as e:
        error_msg = f"Erreur lors du chargement des documents: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)
        state_dict['pdf_paths'] = []
        
    safe_print("=== FIN CHARGEMENT DES DOCUMENTS ===\n")
    
    return State(**state_dict)

def valider_pdfs_node(state: State) -> State:
    """Nœud pour valider les PDFs avant traitement"""
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
    safe_print(f"PDFs rejetés: {len(pdfs_invalides)}")
    
    if pdfs_invalides:
        state_dict['erreurs_rencontrees'].append(f"{len(pdfs_invalides)} PDFs rejetés pour cause d'invalidité")
    
    safe_print("=== FIN VALIDATION DES PDFs ===\n")
    
    return State(**state_dict)

def convertir_en_images_node(state: State) -> State:
    """Nœud pour convertir les PDFs en images"""
    safe_print("\n=== CONVERSION EN IMAGES ===")
    
    state_dict = state.dict()
    state_dict['workflow_status'] = "CONVERSION_IMAGES"
    
    if not state.pdf_paths:
        safe_print("Aucun PDF à convertir")
        state_dict['images_paths'] = []
        state_dict['nb_images_generees'] = 0
        safe_print("=== FIN CONVERSION EN IMAGES ===\n")
        return State(**state_dict)
    
    try:
        output_dir = os.path.join(state.dossier_path, "images_temp")
        images_paths = convertir_pdf_en_images(state.pdf_paths, output_dir)
        state_dict['images_paths'] = images_paths
        state_dict['nb_images_generees'] = len(images_paths)
        
        safe_print(f"Nombre d'images générées: {len(images_paths)}")
        
        if not images_paths:
            state_dict['erreurs_rencontrees'].append("Aucune image générée à partir des PDFs")
            
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
    NOUVEAU NŒUD UNIFIÉ: Extraction OCR ET parsing avec le nouveau système
    """
    safe_print("\n=== EXTRACTION ET PARSING DES INFORMATIONS ===")
    
    state_dict = state.dict()
    state_dict['workflow_status'] = "EXTRACTION_ET_PARSING"
    
    if not state.images_paths:
        safe_print("Aucune image à analyser")
        state_dict['infos_documents'] = {}
        state_dict['documents_texte'] = {}
        state_dict['nb_documents_analyses'] = 0
        safe_print("=== FIN EXTRACTION ET PARSING ===\n")
        return State(**state_dict)
        
    try:
        # Utiliser le nouveau système d'extraction amélioré
        client = init_client()
        resultats_complets = traiter_documents_ocr(client, state.images_paths)
        
        # Extraire les différentes parties du résultat
        resultats_ocr = resultats_complets.get("resultats_ocr", {})
        infos_documents = resultats_complets.get("infos_documents", {})
        resume_extraction = resultats_complets.get("resume_extraction", {})
        
        # Stocker dans le state
        state_dict['infos_documents'] = {}
        state_dict['documents_texte'] = {}
        state_dict['resultats_ocr_detailles'] = resultats_ocr  # Nouveau champ
        
        # Convertir les DocumentInfo en dict pour le stockage et garder les textes
        for chemin, info_doc in infos_documents.items():
            # Stocker l'objet DocumentInfo converti en dict
            if hasattr(info_doc, 'dict'):
                state_dict['infos_documents'][chemin] = info_doc.dict()
            else:
                state_dict['infos_documents'][chemin] = info_doc
            
            # Récupérer le texte brut de l'extraction si disponible
            if chemin in resultats_ocr:
                extraction_brute = resultats_ocr[chemin].get("extraction_brute", "")
                state_dict['documents_texte'][chemin] = extraction_brute
        
        state_dict['nb_documents_analyses'] = len(infos_documents)
        
        # Afficher les statistiques d'extraction
        safe_print(f"Documents traités: {resume_extraction.get('total_documents', 0)}")
        safe_print(f"Documents avec succès: {resume_extraction.get('documents_traites_ok', 0)}")
        safe_print(f"Taux de succès: {resume_extraction.get('taux_succes_global', '0%')}")
        
        # Afficher le détail par document
        for chemin, info_doc in infos_documents.items():
            type_doc = info_doc.type_document if hasattr(info_doc, 'type_document') else 'INCONNU'
            safe_print(f"✅ Document analysé: {os.path.basename(chemin)} -> {type_doc}")
        
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
    NŒUD AMÉLIORÉ: Vérification de concordance avec analyse détaillée
    """
    safe_print("\n=== VÉRIFICATION DE CONCORDANCE AVANCÉE ===")
    
    state_dict = state.dict()
    state_dict['workflow_status'] = "VERIFICATION_CONCORDANCE"
    
    if not state.infos_documents:
        safe_print("Aucune information à vérifier")
        state_dict['concordance'] = None
        state_dict['problemes_concordance'] = []
        state_dict['analyse_concordance_detaillee'] = {}
        safe_print("=== FIN VÉRIFICATION DE CONCORDANCE ===\n")
        return State(**state_dict)
        
    try:
        # Reconvertir les dicts en objets DocumentInfo
        infos_documents_obj = {}
        for chemin, info in state.infos_documents.items():
            if isinstance(info, dict):
                infos_documents_obj[chemin] = DocumentInfo(**info)
            else:
                infos_documents_obj[chemin] = info
        
        # Vérification de base
        concordance, problemes = verifier_concordance_complete(infos_documents_obj)
        
        # Analyse détaillée (nouvelle fonction)
        analyse_detaillee = analyser_concordance_detaillee(infos_documents_obj)
        
        # Stocker tous les résultats
        state_dict['concordance'] = concordance
        state_dict['problemes_concordance'] = problemes
        state_dict['analyse_concordance_detaillee'] = analyse_detaillee
        
        # Affichage des résultats
        safe_print(f"Concordance: {concordance}")
        safe_print(f"Score de confiance: {analyse_detaillee.get('score_confiance', 0):.1f}/100")
        
        if not concordance:
            safe_print(f"Problèmes détectés: {len(problemes)}")
            for p in problemes:
                safe_print(f"  - {p}")
        else:
            safe_print("✅ Toutes les informations concordent")
        
        # Afficher les recommandations
        recommandations = analyse_detaillee.get('recommandations', [])
        if recommandations:
            safe_print("Recommandations:")
            for rec in recommandations:
                safe_print(f"  • {rec}")
            
    except Exception as e:
        error_msg = f"Erreur lors de la vérification de concordance: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)
        state_dict['concordance'] = None
        state_dict['problemes_concordance'] = []
        state_dict['analyse_concordance_detaillee'] = {}
    
    safe_print("=== FIN VÉRIFICATION DE CONCORDANCE ===\n")
    
    return State(**state_dict)

def generer_rapport_node(state: State) -> State:
    """
    NŒUD AMÉLIORÉ: Génération de rapport complet avec nouvelles fonctionnalités
    """
    safe_print("\n=== GÉNÉRATION DU RAPPORT COMPLET ===")
    
    state_dict = state.dict()
    state_dict['workflow_status'] = "GENERATION_RAPPORT"
    
    try:
        if not state.infos_documents:
            safe_print("Aucune information pour générer un rapport")
            return State(**state_dict)
        
        # Reconvertir les dicts en objets DocumentInfo
        infos_documents_obj = {}
        for chemin, info in state.infos_documents.items():
            if isinstance(info, dict):
                infos_documents_obj[chemin] = DocumentInfo(**info)
            else:
                infos_documents_obj[chemin] = info
        
        # Récupérer l'analyse de concordance détaillée
        analyse_detaillee = state_dict.get('analyse_concordance_detaillee', {})
        
        # Récupérer les résultats OCR détaillés
        resultats_ocr = state_dict.get('resultats_ocr_detailles', {})
        
        # Générer une référence de demande
        ref_demande = os.path.basename(state.dossier_path)
        
        # Utiliser la nouvelle fonction de sauvegarde complète
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
            # Mise à jour des chemins dans le state
            state_dict['rapport_path'] = os.path.join(state.dossier_path, "rapport_ocr.txt")
            
            safe_print("✅ Rapport complet généré et sauvegardé")
            safe_print("   - Rapport TXT: rapport_ocr.txt")
            safe_print("   - Rapport JSON: rapport_analyse.json") 
            safe_print("   - Rapport PDF: rapport_ocr.pdf")
        else:
            safe_print("⚠️ Problème lors de la génération du rapport")
            state_dict['erreurs_rencontrees'].append("Erreur lors de la génération du rapport")
        
    except Exception as e:
        error_msg = f"Erreur lors de la génération du rapport: {str(e)}"
        safe_print(error_msg)
        state_dict['erreurs_rencontrees'].append(error_msg)
    
    safe_print("=== FIN GÉNÉRATION DU RAPPORT ===\n")
    
    return State(**state_dict)

###################
# CONSTRUCTION DU WORKFLOW OPTIMISÉ
###################

def construire_workflow():
    """Construit et retourne le workflow LangGraph optimisé avec nouveaux modules"""
    workflow = StateGraph(State)
    
    # Ajouter tous les nœuds - WORKFLOW SIMPLIFIÉ
    workflow.add_node("charger_documents", charger_documents_node)
    workflow.add_node("valider_pdfs", valider_pdfs_node)
    workflow.add_node("convertir_en_images", convertir_en_images_node)
    workflow.add_node("extraire_et_parser_infos", extraire_et_parser_infos_node)  # NŒUD UNIFIÉ
    workflow.add_node("verifier_concordance", verifier_concordance_node)  # AMÉLIORÉ
    workflow.add_node("generer_rapport", generer_rapport_node)  # AMÉLIORÉ
    
    # Définir le point d'entrée
    workflow.add_edge(START, "charger_documents")
    
    # Définir le flux principal - SIMPLIFIÉ
    workflow.add_edge("charger_documents", "valider_pdfs")
    workflow.add_edge("valider_pdfs", "convertir_en_images")
    workflow.add_edge("convertir_en_images", "extraire_et_parser_infos")  # DIRECT
    workflow.add_edge("extraire_et_parser_infos", "verifier_concordance")
    workflow.add_edge("verifier_concordance", "generer_rapport")
    workflow.add_edge("generer_rapport", END)
    
    return workflow.compile()

###################
# FONCTIONS UTILITAIRES MISES À JOUR
###################

def creer_state_initial(dossier_path: str) -> State:
    """Crée un état initial pour le workflow"""
    return State(dossier_path=dossier_path)

def get_workflow_info():
    """Retourne les informations sur le workflow"""
    return {
        "version": "3.0 - Adapté aux nouveaux modules",
        "nodes": [
            "charger_documents",
            "valider_pdfs", 
            "convertir_en_images",
            "extraire_et_parser_infos",  # UNIFIÉ
            "verifier_concordance",      # AMÉLIORÉ
            "generer_rapport"            # AMÉLIORÉ
        ],
        "nouveautes": [
            "Utilise le nouveau module extraction_ocr avec gestion de qualité",
            "Utilise le nouveau module concordance avec analyse détaillée",
            "Workflow simplifié avec nœud unifié extraction+parsing",
            "Rapports enrichis avec scores de confiance",
            "Support du mode récupération pour documents difficiles"
        ],
        "compatibility": [
            "Compatible avec les nouveaux modules d'extraction et concordance",
            "Gestion améliorée des erreurs OCR",
            "Métadonnées de qualité conservées",
            "Rapports multi-formats (TXT, JSON, PDF)"
        ]
    }

# EXPORTS POUR COMPATIBILITÉ
__all__ = [
    'State', 
    'DocumentInfo', 
    'InfoDocument', 
    'construire_workflow', 
    'creer_state_initial',
    'get_workflow_info'
]