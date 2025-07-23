"""
admin/traitement_documents.py - Module de traitement des documents avec OCR - VERSION ADAPTÉE
Compatible avec les nouveaux modules d'extraction et concordance améliorés
"""
import streamlit as st
import os
import json
import sys
import base64
from datetime import datetime
from typing import Dict, List, Optional

from utilsAdmin import (
    obtenir_chemin_dossier, 
    lister_fichiers_dossier, 
    formater_taille_fichier,
    sauvegarder_statut_demande,
    get_value_safe
)

# ============================================
# FONCTIONS PRINCIPALES
# ============================================

def afficher_section_documents(demande: Dict, type_credit: str, index: int):
    """
    Affiche la section des documents avec traitement OCR - VERSION ADAPTÉE
    """
    chemin_dossier = obtenir_chemin_dossier(demande, type_credit)
    ref_demande = demande.get('ref_demande', 'N/A')
    
    if not chemin_dossier or not os.path.exists(chemin_dossier):
        st.warning(f"📁 Dossier non trouvé pour {ref_demande}")
        return
    
    # Récupérer la liste des fichiers
    fichiers = lister_fichiers_dossier(chemin_dossier)
    fichiers_documents = [f for f in fichiers if not f["nom"].endswith('.json')]
    
    if not fichiers_documents:
        st.info("📄 Aucun document trouvé dans ce dossier")
        return
    
    st.markdown(f"### 📂 Documents du dossier ({len(fichiers_documents)})")
    
    # Boutons d'action principaux
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        afficher_bouton_telecharger_rapport_ocr(demande, type_credit, str(index))
    
    with col2:
        if st.button("👁️ Visualiseur documents", key=f"visualiseur_{index}"):
            st.session_state[f"show_viewer_{index}"] = True
    
    with col3:
        if st.button("📋 Liste détaillée", key=f"toggle_details_{index}"):
            show_details_key = f"show_details_{index}"
            st.session_state[show_details_key] = not st.session_state.get(show_details_key, True)
    
    st.markdown("---")
    
    # Aperçu du rapport OCR - AMÉLIORÉ
    afficher_apercu_rapport_ocr_ameliore(demande, type_credit)
    st.markdown("---")
    
    # Visualiseur complet (si activé)
    if st.session_state.get(f"show_viewer_{index}", False):
        afficher_visualiseur_documents_complet(demande, type_credit)
        if st.button("❌ Fermer le visualiseur", key=f"close_viewer_{index}"):
            st.session_state[f"show_viewer_{index}"] = False
            st.rerun()
        st.markdown("---")
    
    # Liste des fichiers (si détails activés)
    if st.session_state.get(f"show_details_{index}", True):
        afficher_fichiers_par_categorie(fichiers_documents, ref_demande, index)
    
    # Section de traitement - AMÉLIORÉE
    afficher_section_traitement_amelioree(demande, type_credit, chemin_dossier, index)

# ============================================
# GESTION DES RAPPORTS OCR - VERSION AMÉLIORÉE
# ============================================

def afficher_bouton_telecharger_rapport_ocr(demande: Dict, type_credit: str, key_suffix: str = ""):
    """
    Bouton de téléchargement du rapport OCR - COMPATIBLE NOUVEAUX FORMATS
    """
    ref_demande = demande.get('ref_demande', 'demande')
    rapport_data = recuperer_rapport_ocr_ameliore(demande, type_credit)
    
    if rapport_data is None:
        st.info("📋 Aucun rapport OCR généré")
        st.caption("Lancez d'abord le traitement OCR pour générer un rapport")
        return
    
    source = rapport_data.get('source', 'inconnue')
    score_confiance = rapport_data.get('score_confiance', 0)
    
    # Affichage enrichi
    if score_confiance > 0:
        st.info(f"📊 Rapport OCR disponible (score: {score_confiance:.1f}/100)")
    else:
        st.info(f"📊 Rapport OCR disponible (source: {source})")
    
    if st.button(f"📊 Télécharger rapport OCR", key=f"rapport_ocr_{ref_demande}_{key_suffix}", type="primary"):
        try:
            chemin_dossier = obtenir_chemin_dossier(demande, type_credit)
            
            # Essayer le PDF existant (priorité)
            chemin_pdf = os.path.join(chemin_dossier, "rapport_ocr.pdf")
            if os.path.exists(chemin_pdf):
                with open(chemin_pdf, "rb") as f:
                    pdf_data = f.read()
                nom_fichier = f"Rapport_OCR_{ref_demande}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="⬇️ Télécharger le rapport OCR (PDF)",
                    data=pdf_data,
                    file_name=nom_fichier,
                    mime="application/pdf",
                    key=f"dl_rapport_pdf_{ref_demande}_{key_suffix}"
                )
                return
            
            # Essayer le rapport texte
            chemin_txt = os.path.join(chemin_dossier, "rapport_ocr.txt")
            if os.path.exists(chemin_txt):
                with open(chemin_txt, "r", encoding='utf-8') as f:
                    rapport_texte = f.read()
                nom_fichier = f"Rapport_OCR_{ref_demande}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                st.download_button(
                    label="⬇️ Télécharger le rapport OCR (TXT)",
                    data=rapport_texte.encode('utf-8'),
                    file_name=nom_fichier,
                    mime="text/plain",
                    key=f"dl_rapport_txt_{ref_demande}_{key_suffix}"
                )
                return
            
            # Générer un rapport basique amélioré
            rapport_basique = generer_rapport_texte_ameliore(rapport_data, demande, type_credit)
            nom_fichier = f"Rapport_OCR_{ref_demande}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            st.download_button(
                label="⬇️ Télécharger le rapport OCR (TXT)",
                data=rapport_basique.encode('utf-8'),
                file_name=nom_fichier,
                mime="text/plain",
                key=f"dl_rapport_basique_{ref_demande}_{key_suffix}"
            )
            st.success("✅ Rapport amélioré généré avec succès !")
            
        except Exception as e:
            st.error(f"❌ Erreur lors du téléchargement: {str(e)}")

def recuperer_rapport_ocr_ameliore(demande: Dict, type_credit: str) -> Optional[Dict]:
    """
    Récupère le rapport OCR avec support des nouveaux formats - VERSION AMÉLIORÉE
    """
    chemin_dossier = obtenir_chemin_dossier(demande, type_credit)
    if not chemin_dossier or not os.path.exists(chemin_dossier):
        return None
    
    # Chercher les fichiers de rapport dans l'ordre de priorité
    fichiers_rapport = [
        "rapport_analyse.json",     # Nouveau format avec analyse détaillée
        "traitement_status.json",   # Format de workflow
        "rapport_ocr.json"          # Format legacy
    ]
    
    rapport_data = {}
    
    for nom_fichier in fichiers_rapport:
        chemin_rapport = os.path.join(chemin_dossier, nom_fichier)
        if os.path.exists(chemin_rapport):
            try:
                with open(chemin_rapport, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if nom_fichier == "rapport_analyse.json":
                        # Nouveau format avec analyse détaillée
                        rapport_data.update(data)
                        rapport_data["source"] = "rapport_analyse_avance"
                        
                        # Extraire le score de confiance si disponible
                        if "analyse_detaillee" in data:
                            score = data["analyse_detaillee"].get("score_confiance", 0)
                            rapport_data["score_confiance"] = score
                        
                        break  # Priorité au nouveau format
                        
                    elif nom_fichier == "traitement_status.json":
                        if data.get("status") == "completed" and "results" in data:
                            rapport_data["resultats"] = data["results"]
                            rapport_data["source"] = "traitement_status"
                            
                            # Extraire les métriques du workflow
                            results = data["results"]
                            rapport_data["workflow_metrics"] = {
                                "nb_pdfs_traites": results.get("nb_pdfs_traites", 0),
                                "nb_images_generees": results.get("nb_images_generees", 0),
                                "nb_documents_analyses": results.get("nb_documents_analyses", 0)
                            }
                    else:
                        # Format legacy
                        rapport_data.update(data)
                        rapport_data["source"] = nom_fichier
                    
                    break
                    
            except Exception as e:
                continue
    
    # Chercher le rapport texte
    for nom_fichier in ["rapport_ocr.txt", "rapport_analyse.txt"]:
        chemin_texte = os.path.join(chemin_dossier, nom_fichier)
        if os.path.exists(chemin_texte):
            try:
                with open(chemin_texte, "r", encoding='utf-8') as f:
                    rapport_data["rapport_texte"] = f.read()
                    break
            except:
                continue
    
    return rapport_data if rapport_data else None

def generer_rapport_texte_ameliore(rapport_data: Dict, demande: Dict, type_credit: str) -> str:
    """
    Génère un rapport texte amélioré avec nouvelles métriques
    """
    ref_demande = demande.get('ref_demande', 'N/A')
    
    rapport = f"""RAPPORT D'ANALYSE OCR AVANCÉ
============================

Référence: {ref_demande}
Type de crédit: {type_credit.upper()}
Date: {datetime.now().strftime('%d/%m/%Y à %H:%M')}

RÉSUMÉ EXÉCUTIF
--------------
"""
    
    # Informations selon le nouveau format
    if rapport_data.get("source") == "rapport_analyse_avance":
        resume = rapport_data.get("resume", {})
        analyse_detaillee = rapport_data.get("analyse_detaillee", {})
        
        rapport += f"""
Documents analysés: {resume.get('nombre_documents', 0)}
Concordance: {'✅ OUI' if resume.get('concordance') else '❌ NON'}
Score de confiance: {resume.get('score_confiance', 0):.1f}/100
Problèmes détectés: {resume.get('nombre_problemes', 0)}

STATISTIQUES D'EXTRACTION:
• Documents avec nom: {analyse_detaillee.get('documents_avec_nom', 0)}
• Documents avec prénom: {analyse_detaillee.get('documents_avec_prenom', 0)}
• Documents avec adresse: {analyse_detaillee.get('documents_avec_adresse', 0)}
• Documents avec CIN: {analyse_detaillee.get('documents_avec_cin', 0)}
"""
        
        # Recommandations
        recommandations = analyse_detaillee.get('recommandations', [])
        if recommandations:
            rapport += f"\nRECOMMANDATIONS:\n"
            for rec in recommandations:
                rapport += f"• {rec}\n"
                
    elif rapport_data.get("source") == "traitement_status":
        # Format workflow
        resultats = rapport_data.get("resultats", {})
        workflow_metrics = rapport_data.get("workflow_metrics", {})
        
        rapport += f"""
PDFs traités: {workflow_metrics.get('nb_pdfs_traites', 0)}
Images générées: {workflow_metrics.get('nb_images_generees', 0)}
Documents analysés: {workflow_metrics.get('nb_documents_analyses', 0)}
Concordance: {'✅ OUI' if resultats.get('concordance') else '❌ NON'}
"""
        
        problemes = resultats.get('problemes_concordance', [])
        if problemes:
            rapport += f"\nPROBLÈMES DÉTECTÉS:\n"
            for i, probleme in enumerate(problemes, 1):
                rapport += f"{i}. {probleme}\n"
    
    # Contenu du rapport texte détaillé
    if rapport_data.get("rapport_texte"):
        rapport += f"\n\nDÉTAILS COMPLETS:\n{rapport_data['rapport_texte']}"
    
    # Documents analysés
    if "documents" in rapport_data:
        rapport += f"\n\nDOCUMENTS ANALYSÉS:\n"
        for nom_doc, infos in rapport_data["documents"].items():
            type_doc = infos.get("type_document", "INCONNU")
            nom = infos.get("nom", "N/A")
            prenom = infos.get("prenom", "N/A")
            rapport += f"• {nom_doc}: {type_doc} - {nom} {prenom}\n"
    
    rapport += f"""

RECOMMANDATIONS FINALES
----------------------
✓ Vérifiez les résultats du traitement OCR
✓ Contrôlez manuellement si problèmes détectés
✓ Contactez le demandeur si documents illisibles
✓ Score de confiance recommandé: > 70/100

============================
Rapport généré automatiquement
Système OCR v2.0 avec analyse avancée
"""
    
    return rapport

def afficher_apercu_rapport_ocr_ameliore(demande: Dict, type_credit: str):
    """
    Affiche un aperçu enrichi du rapport OCR avec nouvelles métriques
    """
    rapport_data = recuperer_rapport_ocr_ameliore(demande, type_credit)
    if not rapport_data:
        st.info("📋 Aucun rapport OCR disponible")
        return
    
    st.markdown("### 📊 Aperçu du rapport OCR")
    
    source = rapport_data.get("source", "inconnue")
    
    # Affichage selon le type de rapport
    if source == "rapport_analyse_avance":
        # Nouveau format avec analyse détaillée
        resume = rapport_data.get("resume", {})
        analyse_detaillee = rapport_data.get("analyse_detaillee", {})
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 Documents", resume.get('nombre_documents', 0))
        with col2:
            concordance = resume.get('concordance')
            st.metric("✅ Concordance", "OK" if concordance else "Problèmes")
        with col3:
            score = resume.get('score_confiance', 0)
            st.metric("🎯 Score confiance", f"{score:.1f}/100")
        with col4:
            problemes = resume.get('nombre_problemes', 0)
            st.metric("⚠️ Problèmes", problemes)
        
        # Détails d'extraction
        if analyse_detaillee:
            st.markdown("**Qualité d'extraction:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"• Noms extraits: {analyse_detaillee.get('documents_avec_nom', 0)}")
                st.write(f"• Prénoms extraits: {analyse_detaillee.get('documents_avec_prenom', 0)}")
            with col2:
                st.write(f"• Adresses extraites: {analyse_detaillee.get('documents_avec_adresse', 0)}")
                st.write(f"• Numéros CIN: {analyse_detaillee.get('documents_avec_cin', 0)}")
        
        # Recommandations
        recommandations = analyse_detaillee.get('recommandations', [])
        if recommandations:
            st.markdown("**Recommandations:**")
            for rec in recommandations:
                st.write(f"• {rec}")
                
    elif source == "traitement_status":
        # Format workflow
        resultats = rapport_data.get("resultats", {})
        workflow_metrics = rapport_data.get("workflow_metrics", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 PDFs traités", workflow_metrics.get('nb_pdfs_traites', 0))
        with col2:
            st.metric("🖼️ Images générées", workflow_metrics.get('nb_images_generees', 0))
        with col3:
            concordance = resultats.get('concordance')
            if concordance is not None:
                st.metric("✅ Concordance", "OK" if concordance else "Problèmes")
        
        problemes = resultats.get('problemes_concordance', [])
        if problemes:
            st.warning("⚠️ Problèmes détectés:")
            for probleme in problemes:
                st.write(f"• {probleme}")
    
    # Badge de qualité
    score_confiance = rapport_data.get('score_confiance', 0)
    if score_confiance >= 90:
        st.success("🏆 Excellente qualité d'extraction")
    elif score_confiance >= 70:
        st.info("✅ Bonne qualité d'extraction")
    elif score_confiance >= 50:
        st.warning("⚠️ Qualité moyenne - vérification recommandée")
    elif score_confiance > 0:
        st.error("❌ Faible qualité - traitement manuel requis")

# ============================================
# AFFICHAGE DES FICHIERS (INCHANGÉ)
# ============================================

def afficher_fichiers_par_categorie(fichiers: List[Dict], ref_demande: str, index: int):
    """
    Affiche les fichiers organisés par catégorie
    """
    # Organiser par type
    fichiers_par_type = {}
    for fichier in fichiers:
        type_fichier = fichier["type"]
        if type_fichier not in fichiers_par_type:
            fichiers_par_type[type_fichier] = []
        fichiers_par_type[type_fichier].append(fichier)
    
    # Ordre d'affichage
    ordre_types = [
        "Pièce d'identité", "Justificatif de domicile", "Bulletin de salaire",
        "Relevé bancaire", "Devis", "Carte grise", "Récapitulatif", "Document complémentaire"
    ]
    
    for type_fichier in ordre_types:
        if type_fichier in fichiers_par_type:
            st.markdown(f"**📋 {type_fichier} ({len(fichiers_par_type[type_fichier])})**")
            
            for i, fichier in enumerate(fichiers_par_type[type_fichier]):
                afficher_carte_fichier(fichier, ref_demande, f"{index}_{type_fichier}_{i}")
            
            st.markdown("---")

def afficher_carte_fichier(fichier: Dict, ref_demande: str, key_suffix: str):
    """
    Affiche une carte pour un fichier individuel
    """
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        icone = get_icone_fichier(fichier["extension"])
        st.markdown(f"{icone} **{fichier['nom']}**")
        st.caption(f"Type: {fichier['type']}")
    
    with col2:
        st.write(f"📊 {formater_taille_fichier(fichier['taille'])}")
        st.write(f"📅 {fichier['date_modification']}")
    
    with col3:
        # Téléchargement
        try:
            with open(fichier["chemin"], "rb") as f:
                st.download_button(
                    "⬇️ Télécharger",
                    data=f.read(),
                    file_name=fichier["nom"],
                    key=f"dl_{key_suffix}"
                )
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
        
        # Prévisualisation
        if peut_previsualiser(fichier["extension"]):
            if st.button("👁️ Prévisualiser", key=f"view_{key_suffix}"):
                afficher_previsualisation_document(fichier, key_suffix)

def peut_previsualiser(extension: str) -> bool:
    """
    Vérifie si un fichier peut être prévisualisé
    """
    extensions_exclues = ['.exe', '.dll', '.so', '.bin']
    return extension.lower() not in extensions_exclues

def afficher_previsualisation_document(fichier: Dict, key_suffix: str):
    """
    Prévisualisation de document
    """
    extension = fichier["extension"].lower()
    st.markdown(f"### 👁️ Prévisualisation : {fichier['nom']}")
    
    try:
        # Images
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            st.image(fichier["chemin"], caption=fichier['nom'], use_column_width=True)
            
        # PDF
        elif extension == '.pdf':
            with open(fichier["chemin"], "rb") as f:
                pdf_data = f.read()
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            pdf_html = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="500"></iframe>'
            st.markdown(pdf_html, unsafe_allow_html=True)
            
        # Fichiers texte
        elif extension in ['.txt', '.json', '.csv', '.xml']:
            encodings = ['utf-8', 'latin-1', 'cp1252']
            contenu = None
            
            for encoding in encodings:
                try:
                    with open(fichier["chemin"], "r", encoding=encoding) as f:
                        contenu = f.read(5000)  # Max 5000 caractères
                    break
                except UnicodeDecodeError:
                    continue
            
            if contenu:
                if extension == '.json':
                    try:
                        data = json.loads(contenu)
                        st.json(data)
                    except:
                        st.code(contenu, language='json')
                else:
                    st.text_area("Contenu:", contenu, height=400, disabled=True)
            else:
                st.error("❌ Impossible de lire le fichier")
        
        # Autres fichiers
        else:
            st.info(f"📎 Fichier {extension.upper()}")
            try:
                with open(fichier["chemin"], "rb") as f:
                    sample = f.read(1024)
                try:
                    text_content = sample.decode('utf-8')
                    st.text_area("Aperçu:", text_content[:1000], height=300, disabled=True)
                except UnicodeDecodeError:
                    st.info("Fichier binaire non prévisualisable")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
        
        # Informations du fichier
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**📁 Nom:** {fichier['nom']}")
            st.write(f"**📏 Taille:** {formater_taille_fichier(fichier['taille'])}")
        with col2:
            st.write(f"**📅 Modifié:** {fichier['date_modification']}")
            st.write(f"**🏷️ Type:** {fichier['type']}")
            
    except Exception as e:
        st.error(f"❌ Erreur de prévisualisation: {str(e)}")

def afficher_visualiseur_documents_complet(demande: Dict, type_credit: str):
    """
    Visualiseur complet de documents
    """
    st.markdown("### 📂 Visualiseur de documents complet")
    
    chemin_dossier = obtenir_chemin_dossier(demande, type_credit)
    if not chemin_dossier or not os.path.exists(chemin_dossier):
        st.warning("📁 Dossier non trouvé")
        return
    
    fichiers = lister_fichiers_dossier(chemin_dossier)
    fichiers_documents = [f for f in fichiers if not f["nom"].endswith('.json')]
    
    if not fichiers_documents:
        st.info("📄 Aucun document trouvé")
        return
    
    # Sélecteur de document
    noms_fichiers = [f["nom"] for f in fichiers_documents]
    fichier_selectionne = st.selectbox(
        "Choisir un document:",
        noms_fichiers,
        key=f"select_doc_{demande.get('ref_demande', 'default')}"
    )
    
    # Trouver le fichier sélectionné
    fichier_actuel = next((f for f in fichiers_documents if f["nom"] == fichier_selectionne), None)
    
    if fichier_actuel:
        # Afficher les infos
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{get_icone_fichier(fichier_actuel['extension'])} {fichier_actuel['nom']}**")
        with col2:
            st.write(f"Taille: {formater_taille_fichier(fichier_actuel['taille'])}")
        with col3:
            st.write(f"Modifié: {fichier_actuel['date_modification']}")
        
        st.markdown("---")
        
        # Prévisualisation
        if peut_previsualiser(fichier_actuel["extension"]):
            afficher_previsualisation_document(fichier_actuel, f"viewer_{demande.get('ref_demande', 'default')}")
        else:
            st.info("📎 Prévisualisation non disponible")

# ============================================
# TRAITEMENT OCR - VERSION ADAPTÉE AUX NOUVEAUX MODULES
# ============================================

def afficher_section_traitement_amelioree(demande: Dict, type_credit: str, chemin_dossier: str, index: int):
    """
    Section de traitement OCR avec nouvelles fonctionnalités
    """
    st.markdown("---")
    st.markdown("### 🔬 Traitement avancé des documents")
    
    # Vérifier le statut
    statut_traitement = get_statut_traitement(chemin_dossier)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if statut_traitement:
            afficher_statut_traitement_ameliore(statut_traitement)
        else:
            st.info("📋 Aucun traitement effectué")
            st.caption("Le nouveau système OCR offre une extraction plus précise et une analyse de concordance avancée")
    
    with col2:
        if statut_traitement and statut_traitement.get("status") == "completed":
            if st.button("🔄 Relancer", key=f"reprocess_{index}"):
                lancer_traitement_ocr_ameliore(demande, type_credit, chemin_dossier)
        else:
            if st.button("🚀 LANCER TRAITEMENT AVANCÉ", key=f"process_{index}", type="primary"):
                lancer_traitement_ocr_ameliore(demande, type_credit, chemin_dossier)
    
    # Résultats améliorés
    if statut_traitement and statut_traitement.get("status") == "completed":
        afficher_resultats_traitement_ameliore(statut_traitement, demande, type_credit, index)

def lancer_traitement_ocr_ameliore(demande: Dict, type_credit: str, chemin_dossier: str):
    """
    Lance le traitement OCR avec les nouveaux modules améliorés
    """
    ref_demande = demande.get('ref_demande', 'N/A')
    
    try:
        # Mettre à jour le statut
        if sauvegarder_statut_demande(demande, "En cours de traitement avancé", type_credit):
            st.success("📝 Statut mis à jour")
        
        # Créer le statut de traitement
        statut_traitement = {
            "status": "processing",
            "started_at": datetime.now().isoformat(),
            "ref_demande": ref_demande,
            "version": "2.0_modules_ameliores"
        }
        
        chemin_statut = os.path.join(chemin_dossier, "traitement_status.json")
        with open(chemin_statut, "w", encoding='utf-8') as f:
            json.dump(statut_traitement, f, ensure_ascii=False, indent=2)
        
        # Lancer le traitement amélioré
        with st.spinner("🔬 Traitement OCR avancé en cours..."):
            resultat_traitement = executer_traitement_ocr_ameliore(chemin_dossier, ref_demande)
        
        # Mettre à jour le statut final
        if resultat_traitement:
            statut_traitement.update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "results": resultat_traitement,
                "version": "2.0_modules_ameliores"
            })
            sauvegarder_statut_demande(demande, "Traitement avancé terminé", type_credit)
            st.success("✅ Traitement avancé terminé!")
        else:
            statut_traitement.update({
                "status": "error",
                "error_message": "Erreur lors du traitement OCR avancé",
                "version": "2.0_modules_ameliores"
            })
            st.error("❌ Erreur lors du traitement")
        
        # Sauvegarder le statut final
        with open(chemin_statut, "w", encoding='utf-8') as f:
            json.dump(statut_traitement, f, ensure_ascii=False, indent=2)
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")

def executer_traitement_ocr_ameliore(chemin_dossier: str, ref_demande: str = "N/A") -> Optional[Dict]:
    """
    Exécute le traitement OCR avec les nouveaux modules améliorés
    """
    try:
        st.info("🤖 Démarrage du traitement OCR avancé...")
        
        # Configuration des chemins
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        agents_dir = os.path.join(parent_dir, "Admin")
        ocr_dir = os.path.join(agents_dir, "agent_OCR_Comparaison")
        
        # Vérifier que les dossiers existent
        if not os.path.exists(agents_dir):
            st.error(f"❌ Dossier Admin non trouvé: {agents_dir}")
            return None
            
        if not os.path.exists(ocr_dir):
            st.error(f"❌ Dossier OCR non trouvé: {ocr_dir}")
            return None
        
        # Ajouter aux chemins
        chemins_a_ajouter = [parent_dir, agents_dir, ocr_dir]
        for chemin in chemins_a_ajouter:
            if chemin not in sys.path:
                sys.path.insert(0, chemin)
        
        # Import du workflow amélioré
        try:
            from agent_OCR_Comparaison import workflowAgentOCR
            st.success("✅ Workflow OCR amélioré importé")
        except ImportError as e:
            st.error(f"❌ Import workflowAgentOCR échoué: {e}")
            return None
        
        # Vérifier les attributs disponibles
        if not hasattr(workflowAgentOCR, 'construire_workflow'):
            st.error("❌ Fonction 'construire_workflow' non trouvée")
            return None
        
        if not hasattr(workflowAgentOCR, 'State'):
            st.error("❌ Classe 'State' non trouvée")
            return None
        
        # Utiliser le workflow amélioré
        try:
            workflow = workflowAgentOCR.construire_workflow()
            st.success("✅ Workflow amélioré créé")
            
            # Créer l'état initial
            if hasattr(workflowAgentOCR, 'creer_state_initial'):
                state = workflowAgentOCR.creer_state_initial(chemin_dossier)
            else:
                state = workflowAgentOCR.State(dossier_path=chemin_dossier)
            st.success("✅ État initial créé")
            
            # Exécuter le workflow amélioré
            with st.spinner("⚙️ Exécution du workflow amélioré..."):
                resultat_agent = workflow.invoke(state)
            st.success("✅ Workflow amélioré exécuté")
            
        except Exception as e:
            st.error(f"❌ Erreur lors de l'exécution du workflow: {e}")
            return None
        
        # Sauvegarder le rapport avec les nouveaux modules
        try:
            from agent_OCR_Comparaison.rapport_generator import sauvegarder_rapport_complet
            
            # Extraire les informations avec la nouvelle structure
            infos_docs = get_value_safe(resultat_agent, 'infos_documents', {})
            concordance = get_value_safe(resultat_agent, 'concordance', True)
            problemes = get_value_safe(resultat_agent, 'problemes_concordance', [])
            analyse_detaillee = get_value_safe(resultat_agent, 'analyse_concordance_detaillee', {})
            resultats_ocr = get_value_safe(resultat_agent, 'resultats_ocr_detailles', {})
            
            # Reconvertir les objets DocumentInfo si nécessaire
            if infos_docs and isinstance(list(infos_docs.values())[0], dict):
                # Les objets sont stockés en dict, les reconvertir
                from agent_OCR_Comparaison.models import DocumentInfo
                infos_docs_obj = {}
                for chemin, info_dict in infos_docs.items():
                    infos_docs_obj[chemin] = DocumentInfo(**info_dict)
                infos_docs = infos_docs_obj
            
            # Sauvegarder avec la nouvelle signature
            sauvegarder_rapport_complet(
                infos_docs, 
                concordance, 
                problemes, 
                chemin_dossier, 
                state=resultat_agent,
                ref_demande=ref_demande,
                analyse_detaillee=analyse_detaillee,
                resultats_ocr=resultats_ocr
            )
            st.success("✅ Rapport amélioré sauvegardé")
            
        except Exception as e:
            st.warning(f"⚠️ Rapport non sauvegardé: {str(e)}")
        
        # Formater les résultats avec les nouvelles métriques
        def extraire_valeur_securisee(obj, attr, default=None):
            try:
                if hasattr(obj, attr):
                    return getattr(obj, attr)
                elif hasattr(obj, 'dict') and isinstance(obj.dict(), dict) and attr in obj.dict():
                    return obj.dict()[attr]
                elif isinstance(obj, dict) and attr in obj:
                    return obj[attr]
                else:
                    return default
            except:
                return default
        
        # Extraire l'analyse de concordance détaillée
        analyse_detaillee = extraire_valeur_securisee(resultat_agent, 'analyse_concordance_detaillee', {})
        
        resultats = {
            "fonction_utilisee": "construire_workflow_ameliore",
            "version": "2.0_modules_ameliores",
            "nb_pdfs_traites": extraire_valeur_securisee(resultat_agent, 'nb_pdfs_traites', 0),
            "nb_images_generees": extraire_valeur_securisee(resultat_agent, 'nb_images_generees', 0),
            "nb_documents_analyses": extraire_valeur_securisee(resultat_agent, 'nb_documents_analyses', 0),
            "concordance": extraire_valeur_securisee(resultat_agent, 'concordance', None),
            "problemes_concordance": extraire_valeur_securisee(resultat_agent, 'problemes_concordance', []),
            "dossier_path": chemin_dossier,
            "workflow_status": extraire_valeur_securisee(resultat_agent, 'workflow_status', 'COMPLETED'),
            # Nouvelles métriques
            "score_confiance": analyse_detaillee.get('score_confiance', 0),
            "documents_avec_nom": analyse_detaillee.get('documents_avec_nom', 0),
            "documents_avec_prenom": analyse_detaillee.get('documents_avec_prenom', 0),
            "documents_avec_adresse": analyse_detaillee.get('documents_avec_adresse', 0),
            "documents_avec_cin": analyse_detaillee.get('documents_avec_cin', 0),
            "recommandations": analyse_detaillee.get('recommandations', [])
        }
        
        st.success("✅ Traitement OCR avancé terminé avec succès!")
        return resultats
        
    except Exception as e:
        st.error(f"❌ Erreur générale OCR: {str(e)}")
        return None

def get_statut_traitement(chemin_dossier: str) -> Optional[Dict]:
    """
    Récupère le statut du traitement
    """
    chemin_statut = os.path.join(chemin_dossier, "traitement_status.json")
    if not os.path.exists(chemin_statut):
        return None
    
    try:
        with open(chemin_statut, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def afficher_statut_traitement_ameliore(statut_traitement: Dict):
    """
    Affiche le statut du traitement avec nouvelles informations
    """
    status = statut_traitement.get("status", "unknown")
    version = statut_traitement.get("version", "1.0")
    
    if status == "processing":
        st.warning("⏳ Traitement en cours...")
        if version.startswith("2.0"):
            st.caption("🚀 Utilisation des modules améliorés")
    elif status == "completed":
        st.success("✅ Traitement terminé")
        if version.startswith("2.0"):
            st.caption("🎯 Traitement avec modules améliorés")
        if "completed_at" in statut_traitement:
            st.caption(f"Terminé le {statut_traitement['completed_at']}")
    elif status == "error":
        st.error("❌ Erreur lors du traitement")
    else:
        st.info("📋 Statut inconnu")

def afficher_resultats_traitement_ameliore(statut_traitement: Dict, demande: Dict, type_credit: str, index: int):
    """
    Affiche les résultats du traitement OCR avec nouvelles métriques
    """
    resultats = statut_traitement.get("results", {})
    if not resultats:
        st.warning("⚠️ Aucun résultat disponible")
        return
    
    st.markdown("### 📊 Résultats du traitement OCR avancé")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 PDFs traités", get_value_safe(resultats, 'nb_pdfs_traites', 0))
    with col2:
        st.metric("🖼️ Images générées", get_value_safe(resultats, 'nb_images_generees', 0))
    with col3:
        st.metric("📋 Documents analysés", get_value_safe(resultats, 'nb_documents_analyses', 0))
    with col4:
        concordance = get_value_safe(resultats, 'concordance', None)
        if concordance is not None:
            st.metric("✅ Concordance", "OK" if concordance else "Problèmes")
    
    # Nouvelles métriques de qualité
    score_confiance = get_value_safe(resultats, 'score_confiance', 0)
    if score_confiance > 0:
        st.markdown("### 🎯 Qualité d'extraction")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Score confiance", f"{score_confiance:.1f}/100")
        with col2:
            st.metric("👤 Noms extraits", get_value_safe(resultats, 'documents_avec_nom', 0))
        with col3:
            st.metric("📝 Prénoms extraits", get_value_safe(resultats, 'documents_avec_prenom', 0))
        with col4:
            st.metric("🆔 CIN extraits", get_value_safe(resultats, 'documents_avec_cin', 0))
        
        # Badge de qualité
        if score_confiance >= 90:
            st.success("🏆 Excellente qualité d'extraction")
        elif score_confiance >= 70:
            st.info("✅ Bonne qualité d'extraction")
        elif score_confiance >= 50:
            st.warning("⚠️ Qualité moyenne - vérification recommandée")
        else:
            st.error("❌ Faible qualité - traitement manuel requis")
    
    # Problèmes de concordance
    problemes = get_value_safe(resultats, 'problemes_concordance', [])
    if problemes:
        st.error("❌ Problèmes de concordance:")
        for probleme in problemes:
            st.warning(f"⚠️ {probleme}")
    
    # Recommandations
    recommandations = get_value_safe(resultats, 'recommandations', [])
    if recommandations:
        st.markdown("### 💡 Recommandations")
        for rec in recommandations:
            st.info(f"• {rec}")
    
    # Actions
    st.markdown("#### ⚡ Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        afficher_bouton_telecharger_rapport_ocr(demande, type_credit, "results")
    
    with col2:
        if st.button("📧 Notifier client", key=f"notify_client_{index}"):
            st.info("📤 Fonctionnalité en développement")
    
    with col3:
        # Décision intelligente basée sur le score
        if score_confiance >= 70 and concordance:
            if st.button("✅ Marquer validé", key=f"mark_validated_{index}"):
                if sauvegarder_statut_demande(demande, "Validé automatiquement", type_credit):
                    st.success("✅ Dossier validé automatiquement")
                    st.rerun()
        else:
            if st.button("⚠️ Marquer pour révision", key=f"mark_review_{index}"):
                if sauvegarder_statut_demande(demande, "Révision manuelle requise", type_credit):
                    st.success("✅ Marqué pour révision manuelle")
                    st.rerun()

# ============================================
# FONCTIONS UTILITAIRES (INCHANGÉES)
# ============================================

def get_icone_fichier(extension: str) -> str:
    """
    Retourne l'icône pour un type de fichier
    """
    icones = {
        '.pdf': '📄', '.doc': '📝', '.docx': '📝', '.txt': '📝',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
        '.json': '📊', '.csv': '📊', '.xlsx': '📊', '.xml': '📊'
    }
    return icones.get(extension.lower(), '📎')