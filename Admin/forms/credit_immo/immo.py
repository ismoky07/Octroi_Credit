import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import uuid
from datetime import datetime, date

from forms.commun.fonction_de_calcul import calcul_mensualite, calculer_tableau_amortissement, get_taux_endettement
from forms.commun.champs_validations import calculer_age, valider_email, valider_telephone
from forms.credit_immo.recapitulatif import generer_pdf_recapitulatif
from forms.commun.sauvegarder_fichier import sauvegarder_fichier, get_binary_file_downloader_html

def run():
    """
    Application principale pour le crédit immobilier
    """
    # Titre principal
    st.title("🏠 Crédit Immobilier - Simulation et Demande")
    
    # Onglets pour séparer simulation et demande
    tab1, tab2 = st.tabs(["📊 Simulateur de crédit", "📝 Formulaire de demande"])
    
    # Onglet 1: Simulateur de crédit
    with tab1:
        st.header("Simulateur de crédit immobilier")
        
        # Affichage du contenu dans des colonnes
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Données du prêt")
            prix_bien_sim = st.number_input("💰 Prix du bien immobilier (DH)", min_value=100000, max_value=10000000, step=50000, value=1000000)
            apport_sim = st.number_input("💵 Apport personnel (DH)", min_value=0, max_value=prix_bien_sim, step=50000, value=int(prix_bien_sim * 0.2))
            montant_sim = prix_bien_sim - apport_sim
            st.info(f"Montant à financer: {montant_sim} DH")
            
            taux_annuel = st.slider("📈 Taux d'intérêt annuel (%)", min_value=0.0, max_value=10.0, step=0.1, value=3.5)
            duree_mois = st.select_slider("📆 Durée de remboursement", 
                                         options=[60, 120, 180, 240, 300, 360], 
                                         value=240,
                                         format_func=lambda x: f"{x} mois ({x//12} ans)")
            
            # Frais de notaire et d'acquisition
            frais_notaire = st.number_input("📝 Frais de notaire (DH)", min_value=0, value=int(prix_bien_sim * 0.06))
            frais_dossier = st.number_input("📋 Frais de dossier (DH)", min_value=0, value=5000)
        
        with col2:
            st.subheader("Situation financière")
            revenu_mensuel = st.number_input("💼 Revenu net mensuel (DH)", min_value=0, value=15000)
            charges = st.number_input("📉 Charges mensuelles hors crédit (DH)", min_value=0, value=3500)
            autres_credits = st.number_input("🏦 Mensualités autres crédits (DH)", min_value=0, value=0)
            
            charges_totales = charges + autres_credits
            
            # Type de bien immobilier
            type_bien = st.selectbox("🏠 Type de bien", [
                "Appartement", "Villa", "Maison", "Terrain", "Local commercial", "Autre"
            ])
            
            # Calcul automatique
            mensualite = calcul_mensualite(montant_sim, taux_annuel, duree_mois)
            cout_total = mensualite * duree_mois
            taux_endettement = get_taux_endettement(revenu_mensuel, charges_totales, mensualite)
            
            # Affichage des résultats
            st.markdown("### 🔍 Résultats de la simulation")
            
            # KPIs en 3 colonnes
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                st.metric("Mensualité", f"{mensualite:.2f} DH")
            
            with res_col2:
                st.metric("Coût total du crédit", f"{cout_total - montant_sim:.2f} DH")
            
            with res_col3:
                color = "green" if taux_endettement <= 33 else "orange" if taux_endettement <= 40 else "red"
                st.markdown(f"<span style='color:{color}; font-size:24px;'>⚖️ {taux_endettement:.1f}%</span> d'endettement", unsafe_allow_html=True)
        
        # Coût total et éligibilité
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
            
            # Jauge d'éligibilité
            st.progress(eligibilite / 100)
            
            # Résumé du coût total
            st.subheader("💰 Coût du projet")
            cout_projet = prix_bien_sim + frais_notaire + frais_dossier
            st.info(f"Prix total: {cout_projet:,.2f} DH")
            
            # Détail des coûts
            st.markdown(f"- Prix du bien: {prix_bien_sim:,.2f} DH")
            st.markdown(f"- Frais de notaire: {frais_notaire:,.2f} DH")
            st.markdown(f"- Frais de dossier: {frais_dossier:,.2f} DH")
            
            # Bouton pour passer à la demande
            if st.button("📝 Passer à la demande de crédit", disabled=(eligibilite == 0)):
                # Sauvegarde des données de simulation dans session_state
                st.session_state.prix_bien_sim = prix_bien_sim
                st.session_state.apport_sim = apport_sim
                st.session_state.montant_sim = montant_sim
                st.session_state.taux_annuel = taux_annuel
                st.session_state.duree_mois = duree_mois
                st.session_state.revenu_mensuel = revenu_mensuel
                st.session_state.type_bien = type_bien
                st.session_state.go_to_form = True
                st.rerun()
        
        # Affichage du tableau d'amortissement dans la colonne droite
        with graph_col:
            st.subheader("📅 Tableau d'amortissement")
            
            # Calcul du tableau d'amortissement
            if montant_sim > 0 and duree_mois > 0:
                tableau = calculer_tableau_amortissement(montant_sim, taux_annuel, duree_mois)
                
                # Conversion en DataFrame pour affichage
                df_amortissement = pd.DataFrame(tableau)
                df_amortissement = df_amortissement.round(2)
                
                # Affichage d'un graphique
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.fill_between(df_amortissement['mois'], df_amortissement['capital_restant'], alpha=0.3, color='blue')
                ax.plot(df_amortissement['mois'], df_amortissement['capital_restant'], '-', color='blue', label='Capital restant')
                ax.set_title('Évolution du capital restant')
                ax.set_xlabel('Mois')
                ax.set_ylabel('Montant (DH)')
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend()
                
                st.pyplot(fig)
                
                # Tableau détaillé par années
                with st.expander("Voir le tableau d'amortissement par année"):
                    # Regroupement par année
                    df_years = df_amortissement.copy()
                    df_years['année'] = (df_years['mois'] - 1) // 12 + 1
                    df_annual = df_years.groupby('année').agg({
                        'mensualite': 'sum',
                        'interet': 'sum',
                        'amortissement': 'sum',
                        'capital_restant': 'last'
                    }).reset_index()
                    
                    # Renommage pour affichage
                    df_annual = df_annual.rename(columns={
                        'année': 'Année',
                        'mensualite': 'Total Mensualités (DH)',
                        'interet': 'Total Intérêts (DH)',
                        'amortissement': 'Total Amortissement (DH)',
                        'capital_restant': 'Capital restant (DH)'
                    })
                    
                    # Affichage
                    st.dataframe(df_annual, use_container_width=True)
                
                # Tableau détaillé mois par mois
                with st.expander("Voir le tableau d'amortissement détaillé"):
                    # Renommage pour affichage
                    df_display = df_amortissement.rename(columns={
                        'mois': 'Mois',
                        'mensualite': 'Mensualité (DH)',
                        'interet': 'Intérêts (DH)',
                        'amortissement': 'Amortissement (DH)',
                        'capital_restant': 'Capital restant (DH)'
                    })
                    
                    # Affichage avec filtres
                    st.dataframe(df_display, use_container_width=True)
    
    # Onglet 2: Formulaire de demande
    with tab2:
        st.header("Formulaire de demande de crédit immobilier")
        st.markdown("Veuillez remplir soigneusement les informations ci-dessous pour constituer votre dossier de demande.")
        
        # Si formulaire soumis avec succès, afficher uniquement la confirmation
        if "demande_soumise" in st.session_state and st.session_state.demande_soumise:
            st.success("✅ Votre demande de crédit immobilier a été soumise avec succès!")
            st.info(f"📋 Référence de votre demande: {st.session_state.reference_demande}")
            
            if "chemin_pdf" in st.session_state:
                with open(st.session_state.chemin_pdf, "rb") as f:
                    st.download_button(
                        "📥 Télécharger le récapitulatif PDF",
                        data=f,
                        file_name="demande_credit_immobilier.pdf"
                    )
            
            if st.button("📝 Nouvelle demande"):
                st.session_state.demande_soumise = False
                st.rerun()
            
            return
        
        # Formulaire principal
        with st.form("form_credit_immo", clear_on_submit=False):
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
                
                logement_col, duree_col = st.columns(2)
                with logement_col:
                    logement = st.selectbox("Type de logement actuel *", 
                                         ["Locataire", "Propriétaire", "Hébergé à titre gratuit", "Logement de fonction"])
                
                with duree_col:
                    duree_occupation = st.text_input("Durée d'occupation actuelle *", help="Ex: 3 ans et 4 mois")
            
            with st.expander("💼 Situation professionnelle", expanded=True):
                form_progress.progress(0.25)
                
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
            
            with st.expander("🏠 Informations sur le bien immobilier", expanded=True):
                form_progress.progress(0.4)
                
                # Type de bien
                default_type_bien = "Appartement"
                if "type_bien" in st.session_state:
                    default_type_bien = st.session_state.type_bien
                
                type_bien = st.selectbox("Type de bien *", [
                    "Appartement", "Villa", "Maison", "Terrain", "Local commercial", "Autre"
                ], index=["Appartement", "Villa", "Maison", "Terrain", "Local commercial", "Autre"].index(default_type_bien))
                
                # Surface et localisation
                surface_col, etage_col = st.columns(2)
                with surface_col:
                    surface = st.number_input("Surface (m²) *", min_value=0, value=100)
                
                with etage_col:
                    if type_bien == "Appartement":
                        etage = st.text_input("Étage *", value="3")
                    else:
                        etage = st.text_input("Nombre d'étages", value="1")
                
                adresse_col, ville_col = st.columns(2)
                with adresse_col:
                    adresse_bien = st.text_area("Adresse du bien *", height=100)
                
                with ville_col:
                    ville = st.text_input("Ville *", value="Casablanca")
                    quartier = st.text_input("Quartier *")
                
                # État du bien
                etat_bien = st.selectbox("État du bien *", [
                    "Neuf", "À construire", "Ancien en bon état", "À rénover", "En construction"
                ])
                
                # Description et caractéristiques
                caracteristiques = st.text_area("Caractéristiques du bien (nombre de pièces, équipements, etc.)", height=100)
                
                # Récupérer prix du bien de la simulation si disponible
                default_prix = 0
                if "prix_bien_sim" in st.session_state:
                    default_prix = st.session_state.prix_bien_sim
                
                prix_bien = st.number_input("Prix du bien (DH) *", 
                                         min_value=0,
                                         value=default_prix)
                
                vendeur = st.text_input("Nom du vendeur/promoteur")
                
            with st.expander("💰 Modalités du financement", expanded=True):
                form_progress.progress(0.6)
                
                # Récupérer l'apport de la simulation si disponible
                default_apport = 0
                if "apport_sim" in st.session_state:
                    default_apport = st.session_state.apport_sim
                
                # Calcul automatique du montant en fonction du prix et de l'apport
                apport = st.number_input("Apport personnel (DH)",
                                      min_value=0,
                                      max_value=prix_bien if prix_bien > 0 else 0,
                                      value=default_apport)
                
                montant_max = prix_bien - apport if prix_bien > apport else 0
                montant = st.number_input("Montant du crédit demandé (DH) *",
                                       min_value=100000 if montant_max >= 100000 else 0,
                                       max_value=montant_max,
                                       value=montant_max)
                
                # Récupérer durée de la simulation si disponible
                default_duree = 240
                if "duree_mois" in st.session_state:
                    default_duree = st.session_state.duree_mois
                
                duree = st.select_slider("Durée de remboursement (mois) *", 
                                      options=[60, 120, 180, 240, 300, 360],
                                      value=default_duree,
                                      format_func=lambda x: f"{x} mois ({x//12} ans)")
                
                # Récupérer taux de la simulation si disponible
                default_taux = 3.5
                if "taux_annuel" in st.session_state:
                    default_taux = st.session_state.taux_annuel
                
                # Taux préférentiel basé sur le profil
                taux_estim = st.slider("Taux d'intérêt souhaité (%)",
                                    min_value=0.0,
                                    max_value=10.0,
                                    value=default_taux,
                                    step=0.1)
                
                # Options de financement supplémentaires
                col1, col2 = st.columns(2)
                with col1:
                    assurance_credit = st.radio("Souhaitez-vous souscrire à une assurance crédit ?", ["Oui", "Non"])
                
                with col2:
                    frais_notaire_inclus = st.radio("Souhaitez-vous inclure les frais de notaire dans le financement ?", ["Non", "Oui"])
                
                # Calcul automatique de la mensualité estimée
                mensualite_form = calcul_mensualite(montant, taux_estim, duree)
                st.info(f"📌 Mensualité estimée: {mensualite_form:.2f} DH/mois")
                
                # Vérification rapide du taux d'endettement
                if revenu_mensuel_form > 0:
                    taux_endettement_form = (charges_mensuelles + mensualite_form) / revenu_mensuel_form * 100
                    if taux_endettement_form > 40:
                        st.warning(f"⚠️ Attention: Votre taux d'endettement serait de {taux_endettement_form:.1f}%, ce qui est supérieur au seuil recommandé de 33%.")
            
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
                
                compromis_vente = st.file_uploader("Compromis/Promesse de vente ou Attestation réservation *", 
                                                type=["pdf", "jpg", "jpeg", "png"])
                
                plans = st.file_uploader("Plans du bien immobilier", 
                                      type=["pdf", "jpg", "jpeg", "png"],
                                      accept_multiple_files=True)
                
                autres_documents = st.file_uploader("Autres documents pertinents (facultatif)", 
                                                type=["pdf", "jpg", "jpeg", "png"], 
                                                accept_multiple_files=True,
                                                help="Ex: Contrat de travail, actes de propriété...")
            
            # Consentements et validations
            st.markdown("### 📜 Consentements et validations")
            
            conditions_row1, conditions_row2 = st.columns(2)
            with conditions_row1:
                condition1 = st.checkbox("Je certifie l'exactitude des informations fournies *", value=False)
                condition2 = st.checkbox("J'accepte que mes données soient traitées conformément à la politique de confidentialité *", value=False)
            
            with conditions_row2:
                condition3 = st.checkbox("J'autorise la vérification de ma situation financière auprès d'organismes tiers *", value=False)
                condition4 = st.checkbox("J'accepte d'être contacté au sujet de ma demande de crédit *", value=False)
            
            # Validation du formulaire
            if st.form_submit_button("📤 Soumettre ma demande"):
                # Vérification des champs obligatoires
                champs_obligatoires = [
                    nom, lieu_naissance, telephone, email, adresse, profession, 
                    employeur, anciennete_pro, adresse_bien, ville, quartier
                ]
                
                fichiers_obligatoires = [
                    carte_id, justificatif_domicile, compromis_vente
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
                    reference_demande = f"IMMO-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
                    
                    # Création du dossier client avec le nouveau format: Nom Prenom - REF
                    nom_dossier = f"{nom.strip()} - {reference_demande}"
                    chemin_base = "demandes_clients/immo"
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
                        "logement": logement,
                        "duree_occupation": duree_occupation,
                        "profession": profession,
                        "employeur": employeur,
                        "anciennete_pro": anciennete_pro,
                        "revenu_mensuel_form": revenu_mensuel_form,
                        "revenu_conjoint": revenu_conjoint,
                        "type_bien": type_bien,
                        "surface": surface,
                        "etage": etage,
                        "adresse_bien": adresse_bien,
                        "ville": ville,
                        "quartier": quartier,
                        "etat_bien": etat_bien,
                        "caracteristiques": caracteristiques,
                        "prix_bien": prix_bien,
                        "montant": montant,
                        "duree": duree,
                        "apport": apport,
                        "taux_estim": taux_estim,
                        "ref_demande": reference_demande
                    }
                    
                    # Génération du PDF récapitulatif
                    pdf = generer_pdf_recapitulatif(donnees_formulaire)
                    chemin_pdf = os.path.join(chemin_dossier, f"{reference_demande}_recapitulatif.pdf")
                    pdf.output(chemin_pdf)
                    
                    # Sauvegarde des documents
                    sauvegarder_fichier(carte_id, chemin_dossier, "piece_identite.pdf")
                    sauvegarder_fichier(justificatif_domicile, chemin_dossier, "justificatif_domicile.pdf")
                    sauvegarder_fichier(compromis_vente, chemin_dossier, "compromis_vente.pdf")
                    
                    # Sauvegarde des bulletins de salaire
                    for i, fichier in enumerate(bulletins):
                        sauvegarder_fichier(fichier, chemin_dossier, f"bulletin_salaire_{i+1}.pdf")
                    
                    # Sauvegarde des relevés bancaires
                    for i, fichier in enumerate(releves):
                        sauvegarder_fichier(fichier, chemin_dossier, f"releve_bancaire_{i+1}.pdf")
                    
                    # Sauvegarde des plans
                    if plans:
                        for i, fichier in enumerate(plans):
                            sauvegarder_fichier(fichier, chemin_dossier, f"plan_{i+1}.pdf")
                    
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
        ℹ️ **Après soumission, votre demande sera traitée sous 5 jours ouvrés.**
        
        Notre équipe examinera votre dossier et vous contactera pour la suite du processus.
        Un conseiller spécialisé en crédit immobilier vous accompagnera durant toute la durée de votre projet.
        """)