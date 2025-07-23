import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import uuid
from datetime import datetime, date

from forms.commun.fonction_de_calcul import get_taux_endettement
from forms.commun.champs_validations import calculer_age, valider_email, valider_telephone
from forms.credit_decouvert.recapitulatif import generer_pdf_recapitulatif
from forms.commun.sauvegarder_fichier import sauvegarder_fichier, get_binary_file_downloader_html

def run():
    """
    Application principale pour le découvert bancaire
    """
    # Titre principal
    st.title("💸 Découvert Bancaire - Simulation et Demande")
    
    # Onglets pour séparer simulation et demande
    tab1, tab2 = st.tabs(["📊 Simulateur de découvert", "📝 Formulaire de demande"])
    
    # Onglet 1: Simulateur de découvert
    with tab1:
        st.header("Simulateur de découvert bancaire")
        
        # Affichage du contenu dans des colonnes
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Découvert souhaité")
            
            montant_decouvert = st.number_input("💰 Montant du découvert (DH)", min_value=1000, max_value=50000, step=1000, value=5000)
            
            duree_decouvert = st.radio("⏱️ Type de découvert", [
                "Ponctuel (1 mois)", "Court terme (3 mois)", "Permanent"
            ])
            
            taux_annuel = 12.0  # Taux fixe pour les découverts
            st.info(f"📈 Taux d'intérêt annuel: {taux_annuel}%")
            
            # Commissions et frais
            commission = st.number_input("💲 Commission d'ouverture (DH)", min_value=0, max_value=500, step=50, value=100)
        
        with col2:
            st.subheader("Situation financière")
            revenu_mensuel = st.number_input("💼 Revenu net mensuel (DH)", min_value=0, value=8000)
            charges = st.number_input("📉 Charges mensuelles hors crédit (DH)", min_value=0, value=2000)
            autres_credits = st.number_input("🏦 Mensualités autres crédits (DH)", min_value=0, value=0)
            
            charges_totales = charges + autres_credits
            
            # Calcul du taux d'endettement (pour un découvert, on considère 10% du montant comme charge mensuelle)
            charge_decouvert = montant_decouvert * 0.1
            taux_endettement = get_taux_endettement(revenu_mensuel, charges_totales, charge_decouvert)
            
            # Affichage des résultats
            st.markdown("### 🔍 Résultats de la simulation")
            
            # KPIs en 3 colonnes
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                if duree_decouvert == "Ponctuel (1 mois)":
                    interet_mensuel = montant_decouvert * (taux_annuel / 100 / 12)
                    st.metric("Intérêts par mois", f"{interet_mensuel:.2f} DH")
                elif duree_decouvert == "Court terme (3 mois)":
                    interet_3mois = montant_decouvert * (taux_annuel / 100 / 4)
                    st.metric("Intérêts sur 3 mois", f"{interet_3mois:.2f} DH")
                else:  # Permanent
                    interet_annuel = montant_decouvert * (taux_annuel / 100)
                    st.metric("Intérêts annuels", f"{interet_annuel:.2f} DH")
            
            with res_col2:
                st.metric("Commission d'ouverture", f"{commission:.2f} DH")
            
            with res_col3:
                color = "green" if taux_endettement <= 33 else "orange" if taux_endettement <= 40 else "red"
                st.markdown(f"<span style='color:{color}; font-size:24px;'>⚖️ {taux_endettement:.1f}%</span> d'endettement", unsafe_allow_html=True)
        
        # Éligibilité et fonctionnement
        st.markdown("---")
        
        eligibilite_col, info_col = st.columns([1, 2])
        
        with eligibilite_col:
            st.subheader("🛡️ Éligibilité au découvert")
            
            if revenu_mensuel == 0:
                st.error("❌ Aucun revenu renseigné. Simulation invalide.")
                eligibilite = 0
            elif taux_endettement > 40:
                st.error("❌ Taux d'endettement trop élevé. Le découvert est probablement refusé.")
                eligibilite = 0
            elif taux_endettement > 33:
                st.warning("⚠️ Taux d'endettement élevé. L'acceptation du découvert n'est pas garantie.")
                eligibilite = 50
            else:
                st.success("✅ Simulation favorable. Le taux d'endettement est acceptable.")
                eligibilite = 100
            
            # Jauge d'éligibilité
            st.progress(eligibilite / 100)
            
            # Résumé des coûts
            st.subheader("💰 Récapitulatif des coûts")
            if duree_decouvert == "Ponctuel (1 mois)":
                cout_total = interet_mensuel + commission
                st.info(f"Total à payer: {cout_total:.2f} DH")
                st.markdown(f"- Intérêts (1 mois): {interet_mensuel:.2f} DH")
            elif duree_decouvert == "Court terme (3 mois)":
                cout_total = interet_3mois + commission
                st.info(f"Total à payer: {cout_total:.2f} DH")
                st.markdown(f"- Intérêts (3 mois): {interet_3mois:.2f} DH")
            else:  # Permanent
                cout_total = interet_annuel + commission
                st.info(f"Total à payer sur un an: {cout_total:.2f} DH")
                st.markdown(f"- Intérêts annuels: {interet_annuel:.2f} DH")
            
            st.markdown(f"- Commission: {commission:.2f} DH")
            
            # Bouton pour passer à la demande
            if st.button("📝 Passer à la demande de découvert", disabled=(eligibilite == 0)):
                # Sauvegarde des données de simulation dans session_state
                st.session_state.montant_decouvert = montant_decouvert
                st.session_state.duree_decouvert = duree_decouvert
                st.session_state.taux_annuel = taux_annuel
                st.session_state.revenu_mensuel = revenu_mensuel
                st.session_state.go_to_form = True
                st.rerun()
        
        # Informations sur le découvert
        with info_col:
            st.subheader("ℹ️ Fonctionnement du découvert bancaire")
            
            st.write("""
            Le découvert bancaire est une facilité de caisse qui vous permet de disposer d'un montant 
            supérieur au solde de votre compte courant pendant une période déterminée.
            """)
            
            # Explication selon le type de découvert
            if duree_decouvert == "Ponctuel (1 mois)":
                st.write("""
                **Découvert ponctuel (1 mois):**
                - Solution idéale pour les besoins temporaires de trésorerie
                - Le découvert doit être remboursé dans un délai d'un mois
                - Les intérêts sont calculés sur le montant utilisé et la durée d'utilisation effective
                """)
                
                # Exemple de calendrier
                st.subheader("📅 Exemple d'utilisation")
                
                df_exemple = pd.DataFrame({
                    "Jour": [1, 15, 30],
                    "Opération": [
                        f"Utilisation du découvert: -{montant_decouvert} DH",
                        f"Utilisation partielle: -{montant_decouvert/2} DH",
                        f"Remboursement total: +{montant_decouvert} DH"
                    ],
                    "Coût": [
                        f"Commission: {commission} DH",
                        f"Intérêts mi-parcours: {montant_decouvert * (taux_annuel/100/12/2):.2f} DH",
                        f"Intérêts finaux: {interet_mensuel:.2f} DH"
                    ]
                })
                
                st.dataframe(df_exemple, use_container_width=True)
                
            elif duree_decouvert == "Court terme (3 mois)":
                st.write("""
                **Découvert court terme (3 mois):**
                - Adapté pour les besoins de trésorerie sur plusieurs mois
                - Le découvert doit être remboursé dans un délai de trois mois
                - Possibilité d'échelonner le remboursement sur la période
                - Les intérêts sont calculés sur le montant utilisé et la durée d'utilisation effective
                """)
                
                # Graphique d'utilisation typique
                fig, ax = plt.subplots(figsize=(10, 4))
                x = [0, 30, 60, 90]
                y = [0, montant_decouvert, montant_decouvert*0.7, 0]
                ax.plot(x, y, marker='o')
                ax.fill_between(x, y, alpha=0.3, color='red')
                ax.set_title('Exemple d\'utilisation d\'un découvert court terme')
                ax.set_xlabel('Jours')
                ax.set_ylabel('Montant utilisé (DH)')
                ax.grid(True, linestyle='--', alpha=0.7)
                
                st.pyplot(fig)
                
            else:  # Permanent
                st.write("""
                **Découvert permanent:**
                - Solution pour disposer en permanence d'une réserve de trésorerie
                - Renouvelable automatiquement (sous réserve du respect des conditions)
                - Les intérêts sont calculés uniquement sur les montants utilisés
                - Révision annuelle du montant autorisé en fonction de l'historique du compte
                """)
                
                # Exemple de coûts selon l'utilisation
                st.subheader("💰 Coût selon l'utilisation")
                
                df_cout = pd.DataFrame({
                    "Utilisation moyenne": ["25%", "50%", "75%", "100%"],
                    "Montant moyen": [
                        f"{montant_decouvert*0.25:.2f} DH",
                        f"{montant_decouvert*0.5:.2f} DH",
                        f"{montant_decouvert*0.75:.2f} DH",
                        f"{montant_decouvert:.2f} DH"
                    ],
                    "Intérêts annuels": [
                        f"{montant_decouvert*0.25*(taux_annuel/100):.2f} DH",
                        f"{montant_decouvert*0.5*(taux_annuel/100):.2f} DH",
                        f"{montant_decouvert*0.75*(taux_annuel/100):.2f} DH",
                        f"{interet_annuel:.2f} DH"
                    ]
                })
                
                st.dataframe(df_cout, use_container_width=True)
    
    # Onglet 2: Formulaire de demande
    with tab2:
        st.header("Formulaire de demande de découvert bancaire")
        st.markdown("Veuillez remplir soigneusement les informations ci-dessous pour constituer votre dossier de demande.")
        
        # Si formulaire soumis avec succès, afficher uniquement la confirmation
        if "demande_soumise" in st.session_state and st.session_state.demande_soumise:
            st.success("✅ Votre demande de découvert bancaire a été soumise avec succès!")
            st.info(f"📋 Référence de votre demande: {st.session_state.reference_demande}")
            
            if "chemin_pdf" in st.session_state:
                with open(st.session_state.chemin_pdf, "rb") as f:
                    st.download_button(
                        "📥 Télécharger le récapitulatif PDF",
                        data=f,
                        file_name="demande_decouvert.pdf"
                    )
            
            if st.button("📝 Nouvelle demande"):
                st.session_state.demande_soumise = False
                st.rerun()
            
            return
        
        # Formulaire principal
        with st.form("form_decouvert", clear_on_submit=False):
            # Progression en haut du formulaire
            form_progress = st.progress(0)
            
            # Sections avec expanders pour mieux organiser
            with st.expander("📌 Informations personnelles", expanded=True):
                form_progress.progress(0.1)
                
                nom_col, naissance_col = st.columns(2)
                with nom_col:
                    nom = st.text_input("Nom et prénom *", help="Votre nom et prénom tels qu'ils apparaissent sur vos documents d'identité")
                
                with naissance_col:
                    naissance = st.date_input("Date de naissance *", 
                                              value=date(1980, 1, 1),
                                              min_value=date(1940, 1, 1),
                                              max_value=date.today())
                
                lieu_col, nationalite_col = st.columns(2)
                with lieu_col:
                    lieu_naissance = st.text_input("Lieu de naissance *")
                
                with nationalite_col:
                    nationalite = st.text_input("Nationalité *", value="Marocaine")
                
                situation_col, tel_col = st.columns(2)
                with situation_col:
                    situation_familiale = st.selectbox("Situation familiale *", 
                                                    ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)", "Pacsé(e)"])
                with tel_col:
                    telephone = st.text_input("Téléphone *", help="Format attendu: +212XXXXXXXX ou 06XXXXXXXX")
                
                adresse = st.text_area("Adresse postale complète *", height=100)
                email = st.text_input("Email *")
            
            with st.expander("💼 Situation professionnelle", expanded=True):
                form_progress.progress(0.3)
                
                prof_col, employeur_col = st.columns(2)
                with prof_col:
                    profession = st.text_input("Profession *")
                
                with employeur_col:
                    employeur = st.text_input("Employeur / Activité indépendante *")
                
                anciennete_col, revenu_col = st.columns(2)
                with anciennete_col:
                    anciennete_pro = st.text_input("Ancienneté professionnelle *", help="Ex: 5 ans")
                
                with revenu_col:
                    # Utilisation sécurisée de session_state avec valeur par défaut
                    default_revenu = 0
                    if "revenu_mensuel" in st.session_state:
                        default_revenu = st.session_state.revenu_mensuel
                    
                    revenu_mensuel_form = st.number_input("Revenu net mensuel (DH) *", 
                                                       min_value=0, 
                                                       value=default_revenu)
                
                revenu_conjoint = st.number_input("Revenu du conjoint (si applicable) (DH)", min_value=0)
                
                charges_mensuelles = st.number_input("Charges mensuelles (loyer, factures, etc.) (DH)", min_value=0)
                
                credits_en_cours = st.radio("Avez-vous des crédits en cours ?", ["Non", "Oui"])
                if credits_en_cours == "Oui":
                    nb_credits = st.number_input("Nombre de crédits en cours", min_value=1, max_value=10, value=1)
                    credits_info = []
                    
                    for i in range(int(nb_credits)):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            type_credit = st.selectbox(f"Type de crédit {i+1}", 
                                                    ["Immobilier", "Consommation", "Auto", "Autre"], 
                                                    key=f"type_credit_{i}")
                        with col2:
                            mensualite_credit = st.number_input(f"Mensualité (DH) {i+1}", 
                                                             min_value=0, 
                                                             key=f"mensualite_{i}")
                        with col3:
                            fin_credit = st.date_input(f"Date de fin {i+1}", 
                                                    key=f"fin_credit_{i}")
                        
                        credits_info.append({
                            "type": type_credit,
                            "mensualite": mensualite_credit,
                            "fin": fin_credit
                        })
            
            with st.expander("🏦 Informations bancaires", expanded=True):
                form_progress.progress(0.5)
                
                # Informations sur le compte bancaire
                banque_col, agence_col = st.columns(2)
                with banque_col:
                    banque = st.text_input("Nom de la banque *", value="Banque Crédit")
                
                with agence_col:
                    agence = st.text_input("Agence *", help="Nom ou code de votre agence")
                
                numero_compte = st.text_input("Numéro de compte *", help="Format RIB ou IBAN")
                
                date_ouverture_col, mouvements_col = st.columns(2)
                with date_ouverture_col:
                    date_ouverture = st.date_input("Date d'ouverture du compte", 
                                              value=date(2020, 1, 1),
                                              max_value=date.today())
                
                with mouvements_col:
                    mouvements_mensuels = st.number_input("Mouvements mensuels moyens (DH)", min_value=0, value=10000)
                
                # Informations sur le découvert demandé
                st.subheader("Découvert demandé")
                
                # Récupérer les valeurs de la simulation si disponibles
                default_montant = 5000
                if "montant_decouvert" in st.session_state:
                    default_montant = st.session_state.montant_decouvert
                
                montant = st.number_input("Montant du découvert (DH) *",
                                       min_value=1000,
                                       max_value=50000,
                                       value=default_montant)
                
                # Type de découvert
                default_duree = "Ponctuel (1 mois)"
                if "duree_decouvert" in st.session_state:
                    default_duree = st.session_state.duree_decouvert
                
                type_options = ["Ponctuel (1 mois)", "Court terme (3 mois)", "Permanent"]
                type_decouvert = st.radio("Type de découvert *", 
                                         options=type_options,
                                         index=type_options.index(default_duree))
                
                # Motif de la demande
                motif = st.text_area("Motif de la demande *", 
                                  help="Précisez pourquoi vous avez besoin de ce découvert",
                                  height=100)
                
                # Taux fixe
                st.info(f"📈 Taux d'intérêt annuel: {taux_annuel}%")
            
            with st.expander("📎 Pièces justificatives", expanded=True):
                form_progress.progress(0.8)
                
                st.info("Pour une demande complète, veuillez fournir les documents suivants:")
                
                carte_id = st.file_uploader("Pièce d'identité (CIN) *", 
                                         type=["pdf", "png", "jpg", "jpeg"],
                                         help="Recto-verso de votre carte nationale d'identité")
                
                justificatif_domicile = st.file_uploader("Justificatif de domicile *", 
                                                      type=["pdf", "png", "jpg", "jpeg"],
                                                      help="Facture d'électricité, d'eau ou quittance de loyer de moins de 3 mois")
                
                bulletins = st.file_uploader("3 derniers bulletins de salaire *", 
                                          type=["pdf", "png", "jpg", "jpeg"], 
                                          accept_multiple_files=True,
                                          help="Ou attestation de revenus pour les professions libérales ou indépendants")
                
                releves = st.file_uploader("Relevés bancaires des 3 derniers mois *", 
                                        type=["pdf"], 
                                        accept_multiple_files=True)
                
                autres_documents = st.file_uploader("Autres documents pertinents (facultatif)", 
                                                type=["pdf", "jpg", "jpeg", "png"], 
                                                accept_multiple_files=True,
                                                help="Ex: Contrat de travail, justificatifs de revenus complémentaires...")
            
            # Consentements et validations
            st.markdown("### 📜 Consentements et validations")
            
            conditions_row1, conditions_row2 = st.columns(2)
            with conditions_row1:
                condition1 = st.checkbox("Je certifie l'exactitude des informations fournies *", value=False)
                condition2 = st.checkbox("J'accepte que mes données soient traitées conformément à la politique de confidentialité *", value=False)
            
            with conditions_row2:
                condition3 = st.checkbox("J'autorise la vérification de ma situation financière auprès d'organismes tiers *", value=False)
                condition4 = st.checkbox("J'accepte les conditions générales d'utilisation du découvert bancaire *", value=False)
            
            # Validation du formulaire
            if st.form_submit_button("📤 Soumettre ma demande"):
                # Vérification des champs obligatoires
                champs_obligatoires = [
                    nom, lieu_naissance, telephone, email, adresse, profession, 
                    employeur, anciennete_pro, banque, agence, numero_compte, motif
                ]
                
                fichiers_obligatoires = [
                    carte_id, justificatif_domicile
                ]
                
                conditions_obligatoires = [condition1, condition2, condition3, condition4]
                
                # Vérification des champs textuels
                if "" in champs_obligatoires or not all(champs_obligatoires):
                    st.error("❌ Veuillez remplir tous les champs obligatoires (marqués d'un *).")
                    return
                
                # Vérification des fichiers
                if None in fichiers_obligatoires or not all(fichiers_obligatoires):
                    st.error("❌ Veuillez fournir tous les documents obligatoires (marqués d'un *).")
                    return
                
                # Vérification des bulletins de salaire et relevés bancaires
                if len(bulletins) < 1:
                    st.error("❌ Veuillez fournir au moins un bulletin de salaire.")
                    return
                
                if len(releves) < 1:
                    st.error("❌ Veuillez fournir au moins un relevé bancaire.")
                    return
                
                # Vérification des conditions
                if not all(conditions_obligatoires):
                    st.error("❌ Veuillez accepter toutes les conditions obligatoires.")
                    return
                
                # Validation du format de l'email
                if not valider_email(email):
                    st.error("❌ Le format de l'adresse email est incorrect.")
                    return
                
                # Validation du format du téléphone
                if not valider_telephone(telephone):
                    st.error("❌ Le format du numéro de téléphone est incorrect. Utilisez le format +212XXXXXXXX ou 06XXXXXXXX.")
                    return
                
                # Si les validations sont passées, traitement de la demande
                try:
                    # Génération d'une référence unique pour la demande
                    reference_demande = f"DECOUVERT-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                    
                   # Création du dossier client avec le nouveau format: Nom Prenom - REF
                    nom_dossier = f"{nom.strip()} - {reference_demande}"
                    chemin_base = "demandes_clients/decouvert"
                    os.makedirs(chemin_base, exist_ok=True)
                    chemin_dossier = os.path.join(chemin_base, nom_dossier)

                    # Vérification de l'unicité (très peu probable avec ce format)
                    compteur = 1
                    while os.path.exists(chemin_dossier):
                        nom_dossier = f"{nom.strip()} - {reference_demande}_{compteur}"
                        chemin_dossier = os.path.join(chemin_base, nom_dossier)
                        compteur += 1

                    os.makedirs(chemin_dossier, exist_ok=True)
                    
                    # Préparation des données pour le PDF
                    donnees_formulaire = {
                        "nom": nom,
                        "naissance": naissance,
                        "lieu_naissance": lieu_naissance,
                        "nationalite": nationalite,
                        "situation_familiale": situation_familiale,
                        "adresse": adresse,
                        "telephone": telephone,
                        "email": email,
                        "profession": profession,
                        "employeur": employeur,
                        "anciennete_pro": anciennete_pro,
                        "revenu_mensuel_form": revenu_mensuel_form,
                        "revenu_conjoint": revenu_conjoint,
                        "banque": banque,
                        "agence": agence,
                        "numero_compte": numero_compte,
                        "date_ouverture": date_ouverture,
                        "mouvements_mensuels": mouvements_mensuels,
                        "montant": montant,
                        "type_decouvert": type_decouvert,
                        "motif": motif,
                        "taux_annuel": taux_annuel,
                        "ref_demande": reference_demande
                    }
                    
                    # Génération du PDF récapitulatif
                    pdf = generer_pdf_recapitulatif(donnees_formulaire)
                    chemin_pdf = os.path.join(chemin_dossier, f"{reference_demande}_recapitulatif.pdf")
                    pdf.output(chemin_pdf)
                    
                    # Sauvegarde des documents
                    sauvegarder_fichier(carte_id, chemin_dossier, "piece_identite.pdf")
                    sauvegarder_fichier(justificatif_domicile, chemin_dossier, "justificatif_domicile.pdf")
                    
                    # Sauvegarde des bulletins de salaire
                    for i, fichier in enumerate(bulletins):
                        sauvegarder_fichier(fichier, chemin_dossier, f"bulletin_salaire_{i+1}.pdf")
                    
                    # Sauvegarde des relevés bancaires
                    for i, fichier in enumerate(releves):
                        sauvegarder_fichier(fichier, chemin_dossier, f"releve_bancaire_{i+1}.pdf")
                    
                    # Sauvegarde des autres documents
                    if autres_documents:
                        for i, fichier in enumerate(autres_documents):
                            sauvegarder_fichier(fichier, chemin_dossier, f"document_complementaire_{i+1}.pdf")
                    
                    # Sauvegarde des données JSON (pour référence future)
                    chemin_json = os.path.join(chemin_dossier, f"{reference_demande}_data.json")
                    with open(chemin_json, "w") as f:
                        json.dump(donnees_formulaire, f, default=str)
                    
                    # Marquer la demande comme soumise dans la session
                    st.session_state.demande_soumise = True
                    st.session_state.reference_demande = reference_demande
                    st.session_state.chemin_pdf = chemin_pdf
                    
                    # Affichage de la confirmation (sera affiché après le rerun)
                    st.success("✅ Demande soumise avec succès!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Une erreur est survenue lors du traitement de votre demande: {str(e)}")
                    st.exception(e)

        # Affichage d'un encart informatif en bas du formulaire
        st.info("""
        ℹ️ **Après soumission, votre demande sera traitée sous 24h ouvrées.**
        
        Notre équipe examinera votre dossier et vous contactera rapidement pour vous notifier la décision.
        Les découverts sont généralement activés sous 48h après acceptation.
        """)