"""
frontend/forms/credit_decouvert/formulaire.py - Formulaire de découvert bancaire
"""
import streamlit as st
import os
import json
import uuid
from datetime import datetime, date

from backend.services.validations import valider_email, valider_telephone
from backend.services.fichiers import sauvegarder_fichier
from backend.config import DOSSIER_DECOUVERT
from frontend.forms.credit_decouvert.recapitulatif import generer_pdf_recapitulatif


def run():
    st.title("💰 Découvert Bancaire - Demande")

    if st.session_state.get("demande_soumise"):
        st.success("✅ Demande soumise!")
        st.info(f"Référence: {st.session_state.reference_demande}")
        if st.button("Nouvelle demande"):
            st.session_state.demande_soumise = False
            st.rerun()
        return

    with st.form("form_decouvert"):
        st.header("📌 Informations personnelles")
        nom = st.text_input("Nom et prénom *")
        naissance = st.date_input("Date de naissance *", value=date(1980, 1, 1))
        telephone = st.text_input("Téléphone *")
        email = st.text_input("Email *")
        adresse = st.text_area("Adresse *")

        st.header("💼 Situation professionnelle")
        profession = st.text_input("Profession *")
        employeur = st.text_input("Employeur *")
        revenu_mensuel_form = st.number_input("Revenu mensuel (DH) *", min_value=0)

        st.header("🏦 Détails du découvert")
        banque = st.selectbox("Banque *", ["Attijariwafa Bank", "BMCE", "Banque Populaire", "CIH", "Crédit du Maroc", "Autre"])
        type_decouvert = st.selectbox("Type de découvert *", ["Découvert autorisé", "Facilité de caisse"])
        montant = st.number_input("Montant demandé (DH) *", 1000, 50000, 5000)
        motif = st.text_area("Motif de la demande *")

        st.header("📎 Documents")
        carte_id = st.file_uploader("Pièce d'identité *", type=["pdf", "png", "jpg"])
        justificatif = st.file_uploader("Justificatif domicile *", type=["pdf", "png", "jpg"])
        bulletins = st.file_uploader("Bulletins de salaire *", type=["pdf"], accept_multiple_files=True)
        releves = st.file_uploader("Relevés bancaires *", type=["pdf"], accept_multiple_files=True)

        condition1 = st.checkbox("Je certifie l'exactitude des informations *")
        condition2 = st.checkbox("J'accepte les conditions *")

        if st.form_submit_button("📤 Soumettre"):
            if not all([nom, telephone, email, adresse, profession, employeur, motif]):
                st.error("❌ Remplissez tous les champs.")
                return
            if not all([carte_id, justificatif]):
                st.error("❌ Documents manquants.")
                return
            if not all([condition1, condition2]):
                st.error("❌ Acceptez les conditions.")
                return
            if not valider_email(email) or not valider_telephone(telephone):
                st.error("❌ Email ou téléphone invalide.")
                return

            try:
                reference = f"DEC-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                nom_dossier = f"{nom.strip()} - {reference}"

                os.makedirs(DOSSIER_DECOUVERT, exist_ok=True)
                chemin_dossier = os.path.join(DOSSIER_DECOUVERT, nom_dossier)
                os.makedirs(chemin_dossier, exist_ok=True)

                donnees = {
                    "nom": nom, "naissance": naissance, "telephone": telephone, "email": email,
                    "adresse": adresse, "profession": profession, "employeur": employeur,
                    "revenu_mensuel_form": revenu_mensuel_form, "banque": banque,
                    "type_decouvert": type_decouvert, "montant": montant, "motif": motif,
                    "ref_demande": reference, "type_credit": "decouvert", "statut": "En attente"
                }

                pdf = generer_pdf_recapitulatif(donnees)
                chemin_pdf = os.path.join(chemin_dossier, f"{reference}_recapitulatif.pdf")
                pdf.output(chemin_pdf)

                sauvegarder_fichier(carte_id, chemin_dossier, "piece_identite.pdf")
                sauvegarder_fichier(justificatif, chemin_dossier, "justificatif_domicile.pdf")
                for i, f in enumerate(bulletins):
                    sauvegarder_fichier(f, chemin_dossier, f"bulletin_{i+1}.pdf")
                for i, f in enumerate(releves):
                    sauvegarder_fichier(f, chemin_dossier, f"releve_{i+1}.pdf")

                with open(os.path.join(chemin_dossier, f"{reference}_data.json"), "w", encoding='utf-8') as f:
                    json.dump(donnees, f, default=str, ensure_ascii=False, indent=2)

                st.session_state.demande_soumise = True
                st.session_state.reference_demande = reference
                st.rerun()

            except Exception as e:
                st.error(f"Erreur: {str(e)}")
