"""
frontend/pages/gestion_credits.py - Gestion des demandes de crédit
"""
import streamlit as st
from typing import List, Dict

from backend.utils import (
    get_statut_couleur,
    formater_montant,
    sauvegarder_statut_demande
)
from frontend.pages.traitement_documents import afficher_section_documents


def afficher_gestion_credit(titre: str, demandes: List[Dict], type_credit: str):
    """
    Affiche la gestion des demandes pour un type de crédit spécifique

    Args:
        titre (str): Titre de la section
        demandes (List[Dict]): Liste des demandes
        type_credit (str): Type de crédit
    """
    st.header(titre)

    if not demandes:
        st.info(f"Aucune demande de type {type_credit} pour le moment.")
        return

    # Statistiques spécifiques au type de crédit
    afficher_statistiques_credit(demandes)

    st.markdown("---")

    # Filtres
    demandes_filtrees = afficher_filtres_credit(demandes, type_credit)

    # Affichage des demandes sous forme de cartes
    if demandes_filtrees:
        st.subheader(f"📋 Demandes ({len(demandes_filtrees)})")

        for i, demande in enumerate(demandes_filtrees):
            afficher_demande_avec_colonnes(demande, type_credit, i)
    else:
        st.info("Aucune demande ne correspond aux critères de filtrage.")


def afficher_demande_avec_colonnes(demande: Dict, type_credit: str, index: int):
    """
    Affiche une demande avec une structure en colonnes

    Args:
        demande (Dict): Données de la demande
        type_credit (str): Type de crédit
        index (int): Index pour les clés uniques
    """
    # Déterminer la couleur selon le statut
    statut = demande.get("statut", "En attente")
    couleur_statut = get_statut_couleur(statut)

    # En-tête de la demande
    st.markdown(f"### {couleur_statut} {demande.get('nom', 'Client inconnu')} - {demande.get('ref_demande', 'REF')}")
    st.markdown(f"**Statut:** {statut}")

    # Container principal
    with st.container():
        # Section 1: Informations de base
        with st.expander("📋 Informations détaillées", expanded=False):
            afficher_informations_demande(demande, type_credit)
            afficher_actions_demande(demande, type_credit, index)

        # Section 2: Documents
        with st.expander("📂 Documents & Traitement OCR", expanded=False):
            afficher_section_documents(demande, type_credit, index)

    st.markdown("---")


def afficher_statistiques_credit(demandes: List[Dict]):
    """
    Affiche les statistiques pour un type de crédit

    Args:
        demandes (List[Dict]): Liste des demandes
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📋 Total", len(demandes))

    with col2:
        en_attente = sum(1 for d in demandes if d.get("statut", "En attente") == "En attente")
        st.metric("⏳ En attente", en_attente)

    with col3:
        montant_total = sum(d.get("montant", 0) for d in demandes)
        st.metric("💰 Montant total", formater_montant(montant_total))

    with col4:
        montant_moyen = montant_total / len(demandes) if demandes else 0
        st.metric("📊 Montant moyen", formater_montant(montant_moyen))


def afficher_filtres_credit(demandes: List[Dict], type_credit: str) -> List[Dict]:
    """
    Affiche les filtres et retourne les demandes filtrées

    Args:
        demandes (List[Dict]): Liste des demandes
        type_credit (str): Type de crédit

    Returns:
        List[Dict]: Demandes filtrées
    """
    col1, col2 = st.columns(2)

    with col1:
        statut_filtre = st.selectbox(
            "📌 Filtrer par statut",
            ["Tous", "En attente", "En cours d'analyse", "En cours de traitement",
             "Traitement terminé", "Accepté", "Refusé", "Annulé"],
            key=f"statut_{type_credit}"
        )

    with col2:
        recherche_nom = st.text_input(
            "🔍 Rechercher par nom",
            placeholder="Nom du client...",
            key=f"recherche_{type_credit}"
        )

    # Appliquer les filtres
    demandes_filtrees = demandes

    if statut_filtre != "Tous":
        demandes_filtrees = [d for d in demandes_filtrees if d.get("statut", "En attente") == statut_filtre]

    if recherche_nom:
        demandes_filtrees = [d for d in demandes_filtrees
                           if recherche_nom.lower() in d.get("nom", "").lower()]

    return demandes_filtrees


def afficher_informations_demande(demande: Dict, type_credit: str):
    """
    Affiche les informations détaillées d'une demande

    Args:
        demande (Dict): Données de la demande
        type_credit (str): Type de crédit
    """
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👤 Informations client**")
        st.write(f"**Nom:** {demande.get('nom', 'N/A')}")
        st.write(f"**Email:** {demande.get('email', 'N/A')}")
        st.write(f"**Téléphone:** {demande.get('telephone', 'N/A')}")
        st.write(f"**Profession:** {demande.get('profession', 'N/A')}")
        revenu = demande.get('revenu_mensuel_form', 0)
        st.write(f"**Revenu:** {formater_montant(revenu)}/mois")

    with col2:
        st.markdown("**💰 Détails du crédit**")
        montant = demande.get('montant', 0)
        st.write(f"**Montant:** {formater_montant(montant)}")

        if "duree" in demande:
            st.write(f"**Durée:** {demande.get('duree', 0)} mois")

        # Détails spécifiques selon le type
        afficher_details_specifiques_credit(demande, type_credit)


def afficher_details_specifiques_credit(demande: Dict, type_credit: str):
    """
    Affiche les détails spécifiques selon le type de crédit

    Args:
        demande (Dict): Données de la demande
        type_credit (str): Type de crédit
    """
    if type_credit == "auto" and "marque" in demande:
        st.write(f"**Véhicule:** {demande.get('marque', '')} {demande.get('modele', '')}")
        prix_vehicule = demande.get('prix_vehicule', 0)
        st.write(f"**Prix véhicule:** {formater_montant(prix_vehicule)}")
        if "apport" in demande:
            apport = demande.get('apport', 0)
            st.write(f"**Apport:** {formater_montant(apport)}")

    elif type_credit == "immo" and "type_bien" in demande:
        st.write(f"**Type de bien:** {demande.get('type_bien', '')}")
        prix_bien = demande.get('prix_bien', 0)
        st.write(f"**Prix bien:** {formater_montant(prix_bien)}")
        if "adresse_bien" in demande:
            st.write(f"**Adresse:** {demande.get('adresse_bien', '')}")

    elif type_credit == "conso" and "type_projet" in demande:
        st.write(f"**Projet:** {demande.get('type_projet', '')}")
        if "description_projet" in demande:
            description = demande.get('description_projet', '')
            st.write(f"**Description:** {description[:100]}{'...' if len(description) > 100 else ''}")

    elif type_credit == "decouvert" and "type_decouvert" in demande:
        st.write(f"**Type:** {demande.get('type_decouvert', '')}")
        st.write(f"**Motif:** {demande.get('motif', '')}")
        st.write(f"**Banque:** {demande.get('banque', '')}")


def afficher_actions_demande(demande: Dict, type_credit: str, index: int):
    """
    Affiche les actions possibles sur une demande

    Args:
        demande (Dict): Données de la demande
        type_credit (str): Type de crédit
        index (int): Index pour les clés uniques
    """
    st.markdown("### ⚙️ Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔄 Gestion du statut**")

        statut_actuel = demande.get("statut", "En attente")
        statuts_disponibles = [
            "En attente",
            "En cours d'analyse",
            "En cours de traitement",
            "Traitement terminé",
            "Demande de documents complémentaires",
            "Accepté",
            "Refusé",
            "Annulé"
        ]

        nouveau_statut = st.selectbox(
            "Nouveau statut",
            statuts_disponibles,
            index=statuts_disponibles.index(statut_actuel) if statut_actuel in statuts_disponibles else 0,
            key=f"statut_{demande.get('ref_demande', '')}_{index}"
        )

        commentaire = st.text_area(
            "Commentaire",
            value=demande.get("commentaire", ""),
            height=100,
            key=f"comment_{demande.get('ref_demande', '')}_{index}"
        )

        if st.button("💾 Sauvegarder", key=f"save_{demande.get('ref_demande', '')}_{index}"):
            # Ajouter le commentaire aux données
            demande["commentaire"] = commentaire

            if sauvegarder_statut_demande(demande, nouveau_statut, type_credit):
                st.success("✅ Statut mis à jour!")
                st.rerun()

    with col2:
        st.markdown("**👤 Conseiller assigné**")

        conseiller_actuel = demande.get("conseiller", "Non assigné")
        conseillers = [
            "Non assigné",
            "Karim BENANI",
            "Amina TAZI",
            "Hassan LAKHDAR",
            "Fatima ZOUHRI"
        ]

        if conseiller_actuel not in conseillers and conseiller_actuel != "Non assigné":
            conseillers.append(conseiller_actuel)

        conseiller = st.selectbox(
            "Conseiller",
            conseillers,
            index=conseillers.index(conseiller_actuel) if conseiller_actuel in conseillers else 0,
            key=f"conseiller_{demande.get('ref_demande', '')}_{index}"
        )

        if conseiller != conseiller_actuel:
            demande["conseiller"] = conseiller
            if sauvegarder_statut_demande(demande, demande.get("statut", "En attente"), type_credit):
                st.success(f"✅ Conseiller assigné: {conseiller}")

        # Actions rapides
        st.markdown("**⚡ Actions rapides**")

        if st.button("📧 Contacter client", key=f"contact_{demande.get('ref_demande', '')}_{index}"):
            st.info("📤 Fonctionnalité email en développement")

        if st.button("📊 Générer rapport", key=f"report_{demande.get('ref_demande', '')}_{index}"):
            st.info("📋 Génération de rapport en développement")
