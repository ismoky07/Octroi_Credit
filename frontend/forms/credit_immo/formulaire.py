"""
frontend/forms/credit_immo/formulaire.py - Formulaire de crédit immobilier
"""
import streamlit as st
import os
import json
import uuid
from datetime import datetime, date

from backend.services.calcul import calcul_mensualite, get_taux_endettement
from backend.services.validations import valider_email, valider_telephone
from backend.services.fichiers import sauvegarder_fichier
from backend.config import DOSSIER_IMMO
from frontend.forms.credit_immo.recapitulatif import generer_pdf_recapitulatif


def run():
    st.title("🏠 Crédit Immobilier - Simulation et Demande")

    tab1, tab2 = st.tabs(["📊 Simulateur", "📝 Formulaire"])

    with tab1:
        st.header("Simulateur de crédit immobilier")

        col1, col2 = st.columns(2)

        with col1:
            prix_bien_sim = st.number_input("💰 Prix du bien (DH)", min_value=100000, max_value=10000000, value=1000000)
            apport_sim = st.number_input("💵 Apport personnel (DH)", min_value=0, max_value=prix_bien_sim, value=int(prix_bien_sim * 0.2))
            montant_sim = prix_bien_sim - apport_sim
            st.info(f"Montant à financer: {montant_sim} DH")

            taux_annuel = st.slider("📈 Taux (%)", 0.0, 10.0, 3.5)
            duree_mois = st.select_slider("📆 Durée", [60, 120, 180, 240, 300, 360], 240,
                                         format_func=lambda x: f"{x} mois ({x//12} ans)")

        with col2:
            revenu_mensuel = st.number_input("💼 Revenu mensuel (DH)", min_value=0, value=15000)
            charges = st.number_input("📉 Charges mensuelles (DH)", min_value=0, value=3500)

            mensualite = calcul_mensualite(montant_sim, taux_annuel, duree_mois)
            taux_endettement = get_taux_endettement(revenu_mensuel, charges, mensualite)

            st.metric("Mensualité", f"{mensualite:.2f} DH")
            st.metric("Taux d'endettement", f"{taux_endettement:.1f}%")

            if taux_endettement <= 33:
                st.success("✅ Éligible")
            elif taux_endettement <= 40:
                st.warning("⚠️ Éligibilité incertaine")
            else:
                st.error("❌ Non éligible")

    with tab2:
        st.header("Formulaire de demande")

        if st.session_state.get("demande_soumise"):
            st.success("✅ Demande soumise!")
            st.info(f"Référence: {st.session_state.reference_demande}")
            if st.button("Nouvelle demande"):
                st.session_state.demande_soumise = False
                st.rerun()
            return

        with st.form("form_credit_immo"):
            with st.expander("📌 Informations personnelles", expanded=True):
                nom = st.text_input("Nom et prénom *")
                naissance = st.date_input("Date de naissance *", value=date(1980, 1, 1))
                lieu_naissance = st.text_input("Lieu de naissance *")
                nationalite = st.text_input("Nationalité *", value="Marocaine")
                situation_familiale = st.selectbox("Situation familiale *", ["Célibataire", "Marié(e)", "Divorcé(e)"])
                telephone = st.text_input("Téléphone *")
                email = st.text_input("Email *")
                adresse = st.text_area("Adresse *")
                logement = st.selectbox("Type de logement *", ["Locataire", "Propriétaire", "Hébergé"])
                duree_occupation = st.text_input("Durée d'occupation *")

            with st.expander("💼 Situation professionnelle", expanded=True):
                profession = st.text_input("Profession *")
                employeur = st.text_input("Employeur *")
                anciennete_pro = st.text_input("Ancienneté *")
                revenu_mensuel_form = st.number_input("Revenu mensuel (DH) *", min_value=0)
                revenu_conjoint = st.number_input("Revenu conjoint (DH)", min_value=0)
                charges_mensuelles = st.number_input("Charges mensuelles (DH)", min_value=0)

            with st.expander("🏠 Bien immobilier", expanded=True):
                type_bien = st.selectbox("Type de bien *", ["Appartement", "Villa", "Maison", "Terrain"])
                surface = st.number_input("Surface (m²) *", min_value=0, value=100)
                adresse_bien = st.text_area("Adresse du bien *")
                ville = st.text_input("Ville *")
                quartier = st.text_input("Quartier *")
                prix_bien = st.number_input("Prix du bien (DH) *", min_value=0)

            with st.expander("💰 Financement", expanded=True):
                apport = st.number_input("Apport personnel (DH)", min_value=0)
                montant = st.number_input("Montant demandé (DH) *", min_value=0, value=max(0, prix_bien - apport))
                duree = st.select_slider("Durée (mois) *", [60, 120, 180, 240, 300, 360], 240)
                taux_estim = st.slider("Taux souhaité (%)", 0.0, 10.0, 3.5)
                st.info(f"Mensualité estimée: {calcul_mensualite(montant, taux_estim, duree):.2f} DH")

            with st.expander("📎 Documents", expanded=True):
                carte_id = st.file_uploader("Pièce d'identité *", type=["pdf", "png", "jpg"])
                justificatif_domicile = st.file_uploader("Justificatif domicile *", type=["pdf", "png", "jpg"])
                bulletins = st.file_uploader("Bulletins de salaire *", type=["pdf"], accept_multiple_files=True)
                releves = st.file_uploader("Relevés bancaires *", type=["pdf"], accept_multiple_files=True)
                compromis = st.file_uploader("Compromis de vente *", type=["pdf", "png", "jpg"])

            condition1 = st.checkbox("Je certifie l'exactitude des informations *")
            condition2 = st.checkbox("J'accepte le traitement de mes données *")

            if st.form_submit_button("📤 Soumettre"):
                if not all([nom, lieu_naissance, telephone, email, adresse, profession, employeur, adresse_bien, ville, quartier]):
                    st.error("❌ Remplissez tous les champs obligatoires.")
                    return
                if not all([carte_id, justificatif_domicile, compromis]):
                    st.error("❌ Fournissez tous les documents obligatoires.")
                    return
                if not all([condition1, condition2]):
                    st.error("❌ Acceptez les conditions.")
                    return
                if not valider_email(email):
                    st.error("❌ Email invalide.")
                    return
                if not valider_telephone(telephone):
                    st.error("❌ Téléphone invalide.")
                    return

                try:
                    reference_demande = f"IMMO-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                    nom_dossier = f"{nom.strip()} - {reference_demande}"

                    os.makedirs(DOSSIER_IMMO, exist_ok=True)
                    chemin_dossier = os.path.join(DOSSIER_IMMO, nom_dossier)
                    os.makedirs(chemin_dossier, exist_ok=True)

                    donnees = {
                        "nom": nom, "naissance": naissance, "lieu_naissance": lieu_naissance,
                        "nationalite": nationalite, "situation_familiale": situation_familiale,
                        "adresse": adresse, "telephone": telephone, "email": email,
                        "logement": logement, "duree_occupation": duree_occupation,
                        "profession": profession, "employeur": employeur, "anciennete_pro": anciennete_pro,
                        "revenu_mensuel_form": revenu_mensuel_form, "revenu_conjoint": revenu_conjoint,
                        "type_bien": type_bien, "surface": surface, "adresse_bien": adresse_bien,
                        "ville": ville, "quartier": quartier, "prix_bien": prix_bien,
                        "montant": montant, "duree": duree, "apport": apport, "taux_estim": taux_estim,
                        "ref_demande": reference_demande, "type_credit": "immo", "statut": "En attente"
                    }

                    pdf = generer_pdf_recapitulatif(donnees)
                    chemin_pdf = os.path.join(chemin_dossier, f"{reference_demande}_recapitulatif.pdf")
                    pdf.output(chemin_pdf)

                    sauvegarder_fichier(carte_id, chemin_dossier, "piece_identite.pdf")
                    sauvegarder_fichier(justificatif_domicile, chemin_dossier, "justificatif_domicile.pdf")
                    sauvegarder_fichier(compromis, chemin_dossier, "compromis_vente.pdf")
                    for i, f in enumerate(bulletins):
                        sauvegarder_fichier(f, chemin_dossier, f"bulletin_{i+1}.pdf")
                    for i, f in enumerate(releves):
                        sauvegarder_fichier(f, chemin_dossier, f"releve_{i+1}.pdf")

                    with open(os.path.join(chemin_dossier, f"{reference_demande}_data.json"), "w", encoding='utf-8') as f:
                        json.dump(donnees, f, default=str, ensure_ascii=False, indent=2)

                    st.session_state.demande_soumise = True
                    st.session_state.reference_demande = reference_demande
                    st.session_state.chemin_pdf = chemin_pdf
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
