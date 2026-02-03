"""
frontend/forms/credit_conso/formulaire.py - Formulaire de crédit consommation
"""
import streamlit as st
import os
import json
import uuid
from datetime import datetime, date

from backend.services.calcul import calcul_mensualite, get_taux_endettement
from backend.services.validations import valider_email, valider_telephone
from backend.services.fichiers import sauvegarder_fichier
from backend.config import DOSSIER_CONSO
from frontend.forms.credit_conso.recapitulatif import generer_pdf_recapitulatif


def run():
    st.title("🛒 Crédit Consommation - Simulation et Demande")

    tab1, tab2 = st.tabs(["📊 Simulateur", "📝 Formulaire"])

    with tab1:
        st.header("Simulateur")
        col1, col2 = st.columns(2)

        with col1:
            montant_sim = st.number_input("💰 Montant (DH)", 5000, 300000, 50000)
            taux_annuel = st.slider("📈 Taux (%)", 0.0, 15.0, 6.5)
            duree_mois = st.select_slider("📆 Durée", [6, 12, 24, 36, 48, 60], 24,
                                         format_func=lambda x: f"{x} mois")

        with col2:
            revenu_mensuel = st.number_input("💼 Revenu (DH)", 0, value=8000)
            charges = st.number_input("📉 Charges (DH)", 0, value=2000)

            mensualite = calcul_mensualite(montant_sim, taux_annuel, duree_mois)
            taux_endettement = get_taux_endettement(revenu_mensuel, charges, mensualite)

            st.metric("Mensualité", f"{mensualite:.2f} DH")
            st.metric("Endettement", f"{taux_endettement:.1f}%")

    with tab2:
        st.header("Formulaire")

        if st.session_state.get("demande_soumise"):
            st.success("✅ Demande soumise!")
            st.info(f"Référence: {st.session_state.reference_demande}")
            if st.button("Nouvelle demande"):
                st.session_state.demande_soumise = False
                st.rerun()
            return

        with st.form("form_conso"):
            nom = st.text_input("Nom et prénom *")
            naissance = st.date_input("Date de naissance *", value=date(1980, 1, 1))
            telephone = st.text_input("Téléphone *")
            email = st.text_input("Email *")
            adresse = st.text_area("Adresse *")

            profession = st.text_input("Profession *")
            employeur = st.text_input("Employeur *")
            revenu_mensuel_form = st.number_input("Revenu mensuel (DH) *", min_value=0)

            type_projet = st.selectbox("Objet du crédit *",
                                      ["Équipement maison", "Travaux", "Voyage", "Événement", "Autre"])
            description_projet = st.text_area("Description du projet")

            montant = st.number_input("Montant (DH) *", 5000, 300000, 50000)
            duree = st.select_slider("Durée (mois) *", [6, 12, 24, 36, 48, 60], 24)
            taux_estim = st.slider("Taux (%)", 0.0, 15.0, 6.5)

            carte_id = st.file_uploader("Pièce d'identité *", type=["pdf", "png", "jpg"])
            justificatif = st.file_uploader("Justificatif domicile *", type=["pdf", "png", "jpg"])
            bulletins = st.file_uploader("Bulletins de salaire *", type=["pdf"], accept_multiple_files=True)

            condition1 = st.checkbox("Je certifie l'exactitude des informations *")
            condition2 = st.checkbox("J'accepte les conditions *")

            if st.form_submit_button("📤 Soumettre"):
                if not all([nom, telephone, email, adresse, profession, employeur]):
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
                    reference = f"CONSO-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                    nom_dossier = f"{nom.strip()} - {reference}"

                    os.makedirs(DOSSIER_CONSO, exist_ok=True)
                    chemin_dossier = os.path.join(DOSSIER_CONSO, nom_dossier)
                    os.makedirs(chemin_dossier, exist_ok=True)

                    donnees = {
                        "nom": nom, "naissance": naissance, "telephone": telephone, "email": email,
                        "adresse": adresse, "profession": profession, "employeur": employeur,
                        "revenu_mensuel_form": revenu_mensuel_form, "type_projet": type_projet,
                        "description_projet": description_projet, "montant": montant,
                        "duree": duree, "taux_estim": taux_estim, "ref_demande": reference,
                        "type_credit": "conso", "statut": "En attente"
                    }

                    pdf = generer_pdf_recapitulatif(donnees)
                    chemin_pdf = os.path.join(chemin_dossier, f"{reference}_recapitulatif.pdf")
                    pdf.output(chemin_pdf)

                    sauvegarder_fichier(carte_id, chemin_dossier, "piece_identite.pdf")
                    sauvegarder_fichier(justificatif, chemin_dossier, "justificatif_domicile.pdf")
                    for i, f in enumerate(bulletins):
                        sauvegarder_fichier(f, chemin_dossier, f"bulletin_{i+1}.pdf")

                    with open(os.path.join(chemin_dossier, f"{reference}_data.json"), "w", encoding='utf-8') as f:
                        json.dump(donnees, f, default=str, ensure_ascii=False, indent=2)

                    st.session_state.demande_soumise = True
                    st.session_state.reference_demande = reference
                    st.rerun()

                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
