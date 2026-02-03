"""
frontend/forms/credit_auto/formulaire.py - Formulaire de crédit automobile
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import uuid
from datetime import datetime, date

from backend.services.calcul import calcul_mensualite, calculer_tableau_amortissement, get_taux_endettement
from backend.services.validations import calculer_age, valider_email, valider_telephone
from backend.services.fichiers import sauvegarder_fichier
from backend.config import DOSSIER_AUTO
from frontend.forms.credit_auto.recapitulatif import generer_pdf_recapitulatif


def run():
    """
    Application principale pour le crédit automobile
    """
    st.title("🚗 Crédit Automobile - Simulation et Demande")

    tab1, tab2 = st.tabs(["📊 Simulateur de crédit", "📝 Formulaire de demande"])

    # Onglet 1: Simulateur de crédit
    with tab1:
        st.header("Simulateur de crédit automobile")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Données du prêt")
            prix_vehicule_sim = st.number_input("💰 Prix du véhicule (DH)", min_value=5000, max_value=2000000, step=1000, value=150000)
            apport_sim = st.number_input("💵 Apport personnel (DH)", min_value=0, max_value=prix_vehicule_sim, step=5000, value=int(prix_vehicule_sim * 0.2))
            montant_sim = prix_vehicule_sim - apport_sim
            st.info(f"Montant à financer: {montant_sim} DH")

            taux_annuel = st.slider("📈 Taux d'intérêt annuel (%)", min_value=0.0, max_value=15.0, step=0.1, value=4.5)
            duree_mois = st.select_slider("📆 Durée de remboursement",
                                         options=[12, 24, 36, 48, 60, 72, 84],
                                         value=48,
                                         format_func=lambda x: f"{x} mois ({x//12} an{'s' if x//12 > 1 else ''})")

        with col2:
            st.subheader("Situation financière")
            revenu_mensuel = st.number_input("💼 Revenu net mensuel (DH)", min_value=0, value=5000)
            charges = st.number_input("📉 Charges mensuelles hors crédit (DH)", min_value=0, value=1500)
            autres_credits = st.number_input("🏦 Mensualités autres crédits (DH)", min_value=0, value=0)

            charges_totales = charges + autres_credits

            # Calcul automatique
            mensualite = calcul_mensualite(montant_sim, taux_annuel, duree_mois)
            cout_total = mensualite * duree_mois
            taux_endettement = get_taux_endettement(revenu_mensuel, charges_totales, mensualite)

            # Affichage des résultats
            st.markdown("### 🔍 Résultats de la simulation")

            res_col1, res_col2, res_col3 = st.columns(3)

            with res_col1:
                st.metric("Mensualité", f"{mensualite:.2f} DH")

            with res_col2:
                st.metric("Coût total du crédit", f"{cout_total - montant_sim:.2f} DH")

            with res_col3:
                color = "green" if taux_endettement <= 33 else "orange" if taux_endettement <= 40 else "red"
                st.markdown(f"<span style='color:{color}; font-size:24px;'>⚖️ {taux_endettement:.1f}%</span> d'endettement", unsafe_allow_html=True)

        # Éligibilité
        st.markdown("---")

        eligibilite_col, graph_col = st.columns([1, 2])

        with eligibilite_col:
            st.subheader("🛡️ Éligibilité au crédit")

            if revenu_mensuel == 0:
                st.error("❌ Aucun revenu renseigné. Simulation invalide.")
                eligibilite = 0
            elif taux_endettement > 40:
                st.error("❌ Taux d'endettement trop élevé. Le prêt est probablement refusé.")
                eligibilite = 0
            elif taux_endettement > 33:
                st.warning("⚠️ Taux d'endettement élevé. L'acceptation du prêt n'est pas garantie.")
                eligibilite = 50
            else:
                st.success("✅ Simulation favorable. Le taux d'endettement est acceptable.")
                eligibilite = 100

            st.progress(eligibilite / 100)

            if st.button("📝 Passer à la demande de crédit", disabled=(eligibilite == 0)):
                st.session_state.prix_vehicule_sim = prix_vehicule_sim
                st.session_state.apport_sim = apport_sim
                st.session_state.montant_sim = montant_sim
                st.session_state.taux_annuel = taux_annuel
                st.session_state.duree_mois = duree_mois
                st.session_state.revenu_mensuel = revenu_mensuel
                st.session_state.go_to_form = True
                st.rerun()

        with graph_col:
            st.subheader("📅 Tableau d'amortissement")

            if montant_sim > 0 and duree_mois > 0:
                tableau = calculer_tableau_amortissement(montant_sim, taux_annuel, duree_mois)
                df_amortissement = pd.DataFrame(tableau)
                df_amortissement = df_amortissement.round(2)

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.fill_between(df_amortissement['mois'], df_amortissement['capital_restant'], alpha=0.3, color='blue')
                ax.plot(df_amortissement['mois'], df_amortissement['capital_restant'], '-', color='blue', label='Capital restant')
                ax.set_title('Évolution du capital restant')
                ax.set_xlabel('Mois')
                ax.set_ylabel('Montant (DH)')
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend()

                st.pyplot(fig)

    # Onglet 2: Formulaire de demande
    with tab2:
        st.header("Formulaire de demande de crédit auto")
        st.markdown("Veuillez remplir soigneusement les informations ci-dessous.")

        if "demande_soumise" in st.session_state and st.session_state.demande_soumise:
            st.success("✅ Votre demande de crédit auto a été soumise avec succès!")
            st.info(f"📋 Référence de votre demande: {st.session_state.reference_demande}")

            if "chemin_pdf" in st.session_state:
                with open(st.session_state.chemin_pdf, "rb") as f:
                    st.download_button(
                        "📥 Télécharger le récapitulatif PDF",
                        data=f,
                        file_name="demande_credit_auto.pdf"
                    )

            if st.button("📝 Nouvelle demande"):
                st.session_state.demande_soumise = False
                st.rerun()

            return

        # Formulaire principal
        with st.form("form_credit_auto", clear_on_submit=False):
            with st.expander("📌 Informations personnelles", expanded=True):
                nom_col, naissance_col = st.columns(2)
                with nom_col:
                    nom = st.text_input("Nom et prénom *")
                with naissance_col:
                    naissance = st.date_input("Date de naissance *", value=date(1980, 1, 1))

                lieu_col, nationalite_col = st.columns(2)
                with lieu_col:
                    lieu_naissance = st.text_input("Lieu de naissance *")
                with nationalite_col:
                    nationalite = st.text_input("Nationalité *", value="Marocaine")

                situation_col, tel_col = st.columns(2)
                with situation_col:
                    situation_familiale = st.selectbox("Situation familiale *",
                                                    ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"])
                with tel_col:
                    telephone = st.text_input("Téléphone *")

                adresse = st.text_area("Adresse postale complète *", height=100)
                email = st.text_input("Email *")

                logement_col, duree_col = st.columns(2)
                with logement_col:
                    logement = st.selectbox("Type de logement *",
                                         ["Locataire", "Propriétaire", "Hébergé à titre gratuit"])
                with duree_col:
                    duree_occupation = st.text_input("Durée d'occupation actuelle *")

            with st.expander("💼 Situation professionnelle", expanded=True):
                prof_col, employeur_col = st.columns(2)
                with prof_col:
                    profession = st.text_input("Profession *")
                with employeur_col:
                    employeur = st.text_input("Employeur *")

                anciennete_col, revenu_col = st.columns(2)
                with anciennete_col:
                    anciennete_pro = st.text_input("Ancienneté professionnelle *")
                with revenu_col:
                    default_revenu = st.session_state.get("revenu_mensuel", 0)
                    revenu_mensuel_form = st.number_input("Revenu net mensuel (DH) *", min_value=0, value=default_revenu)

                revenu_conjoint = st.number_input("Revenu du conjoint (DH)", min_value=0)
                charges_mensuelles = st.number_input("Charges mensuelles (DH)", min_value=0)

            with st.expander("🚘 Informations sur le véhicule", expanded=True):
                marque_col, modele_col = st.columns(2)
                with marque_col:
                    marque = st.text_input("Marque du véhicule *")
                with modele_col:
                    modele = st.text_input("Modèle du véhicule *")

                annee_col, km_col = st.columns(2)
                with annee_col:
                    annee = st.text_input("Année de fabrication *")
                with km_col:
                    kilometrage = st.text_input("Kilométrage actuel", value="0 km (Neuf)")

                default_prix = st.session_state.get("prix_vehicule_sim", 0)
                prix_vehicule = st.number_input("Prix du véhicule (DH) *", min_value=0, value=default_prix)

            with st.expander("💰 Modalités du financement", expanded=True):
                default_apport = st.session_state.get("apport_sim", 0)
                apport = st.number_input("Apport personnel (DH)", min_value=0, value=default_apport)

                montant_max = prix_vehicule - apport if prix_vehicule > apport else 0
                montant = st.number_input("Montant du crédit demandé (DH) *", min_value=0, value=montant_max)

                default_duree = st.session_state.get("duree_mois", 48)
                duree = st.select_slider("Durée de remboursement (mois) *",
                                      options=[12, 24, 36, 48, 60, 72, 84],
                                      value=default_duree)

                default_taux = st.session_state.get("taux_annuel", 4.5)
                taux_estim = st.slider("Taux d'intérêt souhaité (%)", min_value=0.0, max_value=10.0, value=default_taux)

                mensualite_form = calcul_mensualite(montant, taux_estim, duree)
                st.info(f"📌 Mensualité estimée: {mensualite_form:.2f} DH/mois")

            with st.expander("📎 Pièces justificatives", expanded=True):
                carte_id = st.file_uploader("Pièce d'identité (CIN) *", type=["pdf", "png", "jpg", "jpeg"])
                justificatif_domicile = st.file_uploader("Justificatif de domicile *", type=["pdf", "png", "jpg", "jpeg"])
                bulletins = st.file_uploader("Bulletins de salaire *", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
                releves = st.file_uploader("Relevés bancaires *", type=["pdf"], accept_multiple_files=True)
                devis_vehicule = st.file_uploader("Devis du véhicule *", type=["pdf", "jpg", "jpeg", "png"])

            st.markdown("### 📜 Consentements")
            condition1 = st.checkbox("Je certifie l'exactitude des informations fournies *")
            condition2 = st.checkbox("J'accepte le traitement de mes données *")
            condition3 = st.checkbox("J'autorise la vérification de ma situation financière *")
            condition4 = st.checkbox("J'accepte d'être contacté *")

            if st.form_submit_button("📤 Soumettre ma demande"):
                champs_obligatoires = [nom, lieu_naissance, telephone, email, adresse, profession, employeur, anciennete_pro, marque, modele, annee]
                fichiers_obligatoires = [carte_id, justificatif_domicile, devis_vehicule]
                conditions_obligatoires = [condition1, condition2, condition3, condition4]

                if "" in champs_obligatoires or not all(champs_obligatoires):
                    st.error("❌ Veuillez remplir tous les champs obligatoires.")
                    return

                if None in fichiers_obligatoires or not all(fichiers_obligatoires):
                    st.error("❌ Veuillez fournir tous les documents obligatoires.")
                    return

                if not all(conditions_obligatoires):
                    st.error("❌ Veuillez accepter toutes les conditions.")
                    return

                if not valider_email(email):
                    st.error("❌ Format d'email incorrect.")
                    return

                if not valider_telephone(telephone):
                    st.error("❌ Format de téléphone incorrect.")
                    return

                try:
                    reference_demande = f"AUTO-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                    nom_dossier = f"{nom.strip()} - {reference_demande}"

                    os.makedirs(DOSSIER_AUTO, exist_ok=True)
                    chemin_dossier = os.path.join(DOSSIER_AUTO, nom_dossier)
                    os.makedirs(chemin_dossier, exist_ok=True)

                    donnees_formulaire = {
                        "nom": nom,
                        "naissance": naissance,
                        "lieu_naissance": lieu_naissance,
                        "nationalite": nationalite,
                        "situation_familiale": situation_familiale,
                        "adresse": adresse,
                        "telephone": telephone,
                        "email": email,
                        "logement": logement,
                        "duree_occupation": duree_occupation,
                        "profession": profession,
                        "employeur": employeur,
                        "anciennete_pro": anciennete_pro,
                        "revenu_mensuel_form": revenu_mensuel_form,
                        "revenu_conjoint": revenu_conjoint,
                        "marque": marque,
                        "modele": modele,
                        "annee": annee,
                        "kilometrage": kilometrage,
                        "prix_vehicule": prix_vehicule,
                        "montant": montant,
                        "duree": duree,
                        "apport": apport,
                        "taux_estim": taux_estim,
                        "ref_demande": reference_demande,
                        "type_credit": "auto",
                        "statut": "En attente"
                    }

                    pdf = generer_pdf_recapitulatif(donnees_formulaire)
                    chemin_pdf = os.path.join(chemin_dossier, f"{reference_demande}_recapitulatif.pdf")
                    pdf.output(chemin_pdf)

                    sauvegarder_fichier(carte_id, chemin_dossier, "piece_identite.pdf")
                    sauvegarder_fichier(justificatif_domicile, chemin_dossier, "justificatif_domicile.pdf")
                    sauvegarder_fichier(devis_vehicule, chemin_dossier, "devis_vehicule.pdf")

                    for i, fichier in enumerate(bulletins):
                        sauvegarder_fichier(fichier, chemin_dossier, f"bulletin_salaire_{i+1}.pdf")

                    for i, fichier in enumerate(releves):
                        sauvegarder_fichier(fichier, chemin_dossier, f"releve_bancaire_{i+1}.pdf")

                    chemin_json = os.path.join(chemin_dossier, f"{reference_demande}_data.json")
                    with open(chemin_json, "w", encoding='utf-8') as f:
                        json.dump(donnees_formulaire, f, default=str, ensure_ascii=False, indent=2)

                    st.session_state.demande_soumise = True
                    st.session_state.reference_demande = reference_demande
                    st.session_state.chemin_pdf = chemin_pdf

                    st.success("✅ Demande soumise avec succès!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

        st.info("ℹ️ Votre demande sera traitée sous 48h ouvrées.")
