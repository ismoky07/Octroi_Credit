"""
frontend/pages/traitement_documents.py - Module de traitement des documents avec OCR
"""
import streamlit as st
import os
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional

from backend.utils import (
    obtenir_chemin_dossier,
    lister_fichiers_dossier,
    formater_taille_fichier,
    sauvegarder_statut_demande,
    get_value_safe
)

# Import du module OCR (optionnel - si les dependances sont installees)
try:
    from backend.agent_OCR import traiter_dossier_documents
    OCR_DISPONIBLE = True
except ImportError:
    OCR_DISPONIBLE = False


def afficher_section_documents(demande: Dict, type_credit: str, index: int):
    """
    Affiche la section des documents avec traitement OCR
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

    # Aperçu du rapport OCR
    afficher_apercu_rapport_ocr(demande, type_credit)
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

    # Section de traitement
    afficher_section_traitement(demande, type_credit, chemin_dossier, index)


def afficher_bouton_telecharger_rapport_ocr(demande: Dict, type_credit: str, key_suffix: str = ""):
    """
    Bouton de téléchargement du rapport OCR
    """
    ref_demande = demande.get('ref_demande', 'demande')
    rapport_data = recuperer_rapport_ocr(demande, type_credit)

    if rapport_data is None:
        st.info("📋 Aucun rapport OCR généré")
        st.caption("Lancez d'abord le traitement OCR pour générer un rapport")
        return

    source = rapport_data.get('source', 'inconnue')
    score_confiance = rapport_data.get('score_confiance', 0)

    if score_confiance > 0:
        st.info(f"📊 Rapport OCR disponible (score: {score_confiance:.1f}/100)")
    else:
        st.info(f"📊 Rapport OCR disponible (source: {source})")

    if st.button(f"📊 Télécharger rapport OCR", key=f"rapport_ocr_{ref_demande}_{key_suffix}", type="primary"):
        try:
            chemin_dossier = obtenir_chemin_dossier(demande, type_credit)

            # Essayer le PDF existant
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

            # Générer un rapport basique
            rapport_basique = generer_rapport_texte(rapport_data, demande, type_credit)
            nom_fichier = f"Rapport_OCR_{ref_demande}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            st.download_button(
                label="⬇️ Télécharger le rapport OCR (TXT)",
                data=rapport_basique.encode('utf-8'),
                file_name=nom_fichier,
                mime="text/plain",
                key=f"dl_rapport_basique_{ref_demande}_{key_suffix}"
            )

        except Exception as e:
            st.error(f"❌ Erreur lors du téléchargement: {str(e)}")


def recuperer_rapport_ocr(demande: Dict, type_credit: str) -> Optional[Dict]:
    """
    Récupère le rapport OCR
    """
    chemin_dossier = obtenir_chemin_dossier(demande, type_credit)
    if not chemin_dossier or not os.path.exists(chemin_dossier):
        return None

    fichiers_rapport = [
        "rapport_analyse.json",
        "traitement_status.json",
        "rapport_ocr.json"
    ]

    rapport_data = {}

    for nom_fichier in fichiers_rapport:
        chemin_rapport = os.path.join(chemin_dossier, nom_fichier)
        if os.path.exists(chemin_rapport):
            try:
                with open(chemin_rapport, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    rapport_data.update(data)
                    rapport_data["source"] = nom_fichier
                    break
            except Exception:
                continue

    return rapport_data if rapport_data else None


def generer_rapport_texte(rapport_data: Dict, demande: Dict, type_credit: str) -> str:
    """
    Génère un rapport texte
    """
    ref_demande = demande.get('ref_demande', 'N/A')

    rapport = f"""RAPPORT D'ANALYSE OCR
=====================

Référence: {ref_demande}
Type de crédit: {type_credit.upper()}
Date: {datetime.now().strftime('%d/%m/%Y à %H:%M')}

RÉSUMÉ
------
"""

    if "resume" in rapport_data:
        resume = rapport_data["resume"]
        rapport += f"""
Documents analysés: {resume.get('nombre_documents', 0)}
Concordance: {'OUI' if resume.get('concordance') else 'NON'}
Score de confiance: {resume.get('score_confiance', 0):.1f}/100
"""

    rapport += """

=====================
Rapport généré automatiquement
"""

    return rapport


def afficher_apercu_rapport_ocr(demande: Dict, type_credit: str):
    """
    Affiche un aperçu du rapport OCR
    """
    rapport_data = recuperer_rapport_ocr(demande, type_credit)
    if not rapport_data:
        st.info("📋 Aucun rapport OCR disponible")
        return

    st.markdown("### 📊 Aperçu du rapport OCR")

    if "resume" in rapport_data:
        resume = rapport_data["resume"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Documents", resume.get('nombre_documents', 0))
        with col2:
            concordance = resume.get('concordance')
            st.metric("✅ Concordance", "OK" if concordance else "Problèmes")
        with col3:
            score = resume.get('score_confiance', 0)
            st.metric("🎯 Score", f"{score:.1f}/100")


def afficher_fichiers_par_categorie(fichiers: List[Dict], ref_demande: str, index: int):
    """
    Affiche les fichiers organisés par catégorie
    """
    fichiers_par_type = {}
    for fichier in fichiers:
        type_fichier = fichier["type"]
        if type_fichier not in fichiers_par_type:
            fichiers_par_type[type_fichier] = []
        fichiers_par_type[type_fichier].append(fichier)

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
        try:
            with open(fichier["chemin"], "rb") as f:
                st.download_button(
                    "⬇️",
                    data=f.read(),
                    file_name=fichier["nom"],
                    key=f"dl_{key_suffix}"
                )
        except Exception as e:
            st.error(f"Erreur: {str(e)}")


def afficher_visualiseur_documents_complet(demande: Dict, type_credit: str):
    """
    Visualiseur complet de documents
    """
    st.markdown("### 📂 Visualiseur de documents")

    chemin_dossier = obtenir_chemin_dossier(demande, type_credit)
    if not chemin_dossier or not os.path.exists(chemin_dossier):
        st.warning("📁 Dossier non trouvé")
        return

    fichiers = lister_fichiers_dossier(chemin_dossier)
    fichiers_documents = [f for f in fichiers if not f["nom"].endswith('.json')]

    if not fichiers_documents:
        st.info("📄 Aucun document trouvé")
        return

    noms_fichiers = [f["nom"] for f in fichiers_documents]
    fichier_selectionne = st.selectbox(
        "Choisir un document:",
        noms_fichiers,
        key=f"select_doc_{demande.get('ref_demande', 'default')}"
    )

    fichier_actuel = next((f for f in fichiers_documents if f["nom"] == fichier_selectionne), None)

    if fichier_actuel:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{get_icone_fichier(fichier_actuel['extension'])} {fichier_actuel['nom']}**")
        with col2:
            st.write(f"Taille: {formater_taille_fichier(fichier_actuel['taille'])}")
        with col3:
            st.write(f"Modifié: {fichier_actuel['date_modification']}")

        st.markdown("---")

        extension = fichier_actuel["extension"].lower()
        try:
            if extension in ['.jpg', '.jpeg', '.png', '.gif']:
                st.image(fichier_actuel["chemin"], caption=fichier_actuel['nom'], use_container_width=True)
            elif extension == '.pdf':
                with open(fichier_actuel["chemin"], "rb") as f:
                    pdf_data = f.read()
                pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="500"></iframe>', unsafe_allow_html=True)
            else:
                st.info("📎 Prévisualisation non disponible pour ce type de fichier")
        except Exception as e:
            st.error(f"❌ Erreur de prévisualisation: {str(e)}")


def afficher_section_traitement(demande: Dict, type_credit: str, chemin_dossier: str, index: int):
    """
    Section de traitement OCR
    """
    st.markdown("---")
    st.markdown("### 🔬 Traitement des documents")

    statut_traitement = get_statut_traitement(chemin_dossier)

    col1, col2 = st.columns([2, 1])

    with col1:
        if statut_traitement:
            status = statut_traitement.get("status", "unknown")
            if status == "completed":
                st.success("✅ Traitement termine")
            elif status == "processing":
                st.warning("⏳ Traitement en cours...")
            else:
                st.info("📋 Aucun traitement effectue")
        else:
            st.info("📋 Aucun traitement effectue")

    with col2:
        if not OCR_DISPONIBLE:
            st.warning("⚠️ Module OCR non disponible")
            st.caption("Installez les dependances: langgraph, openai, fitz")
        elif st.button("🚀 LANCER TRAITEMENT", key=f"process_{index}", type="primary"):
            lancer_traitement_ocr(demande, type_credit, chemin_dossier, index)


def lancer_traitement_ocr(demande: Dict, type_credit: str, chemin_dossier: str, index: int):
    """
    Lance le traitement OCR sur le dossier
    """
    if not OCR_DISPONIBLE:
        st.error("❌ Module OCR non disponible")
        return

    ref_demande = demande.get('ref_demande', 'N/A')

    try:
        # Sauvegarder le statut en cours
        statut = {
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "ref_demande": ref_demande
        }
        chemin_statut = os.path.join(chemin_dossier, "traitement_status.json")
        with open(chemin_statut, "w", encoding='utf-8') as f:
            json.dump(statut, f, ensure_ascii=False, indent=2)

        with st.spinner("🔬 Traitement OCR en cours..."):
            # Lancer le traitement
            resultat = traiter_dossier_documents(chemin_dossier)

            if resultat:
                # Mettre a jour le statut
                statut["status"] = "completed"
                statut["end_time"] = datetime.now().isoformat()
                statut["concordance"] = resultat.concordance
                statut["nb_documents"] = resultat.nb_documents_analyses

                with open(chemin_statut, "w", encoding='utf-8') as f:
                    json.dump(statut, f, ensure_ascii=False, indent=2)

                st.success(f"✅ Traitement termine - {resultat.nb_documents_analyses} documents analyses")
                if resultat.concordance:
                    st.info("✅ Toutes les informations concordent")
                else:
                    st.warning(f"⚠️ {len(resultat.problemes_concordance)} probleme(s) detecte(s)")
            else:
                statut["status"] = "error"
                statut["error"] = "Echec du traitement"
                with open(chemin_statut, "w", encoding='utf-8') as f:
                    json.dump(statut, f, ensure_ascii=False, indent=2)
                st.error("❌ Echec du traitement OCR")

        st.rerun()

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


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
