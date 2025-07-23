"""
admin/dashboard.py - Tableau de bord général avec statistiques et graphiques
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from typing import List, Dict
import os
import json
from utilsAdmin import formater_montant
from utilsAdmin import charger_toutes_demandes as charger_demandes


def afficher_tableau_bord_general(demandes_toutes: List[Dict] = None):
    """
    Affiche le tableau de bord général avec les statistiques globales
    
    Args:
        demandes_toutes (List[Dict], optional): Toutes les demandes de crédit.
                                               Si None, les charge automatiquement.
    """
    st.header("📊 Vue d'ensemble générale")
    
    # Charger les demandes si non fournies
    if demandes_toutes is None:
        demandes_toutes = charger_toutes_demandes()
    
    if not demandes_toutes:
        st.info("Aucune demande de crédit pour le moment.")
        return
    
    # KPIs principaux
    afficher_kpis_principaux(demandes_toutes)
    
    st.markdown("---")
    
    # Graphiques de répartition
    col1, col2 = st.columns(2)
    
    with col1:
        afficher_repartition_types_credit(demandes_toutes)
    
    with col2:
        afficher_repartition_statuts(demandes_toutes)
    
    # Évolution temporelle et montants
    afficher_evolution_temporelle(demandes_toutes)
    afficher_montants_par_type(demandes_toutes)
    
    # Tableau récapitulatif
    afficher_tableau_recapitulatif(demandes_toutes)

def afficher_kpis_principaux(demandes_toutes: List[Dict]):
    """
    Affiche les KPIs principaux du tableau de bord
    
    Args:
        demandes_toutes (List[Dict]): Toutes les demandes
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nb_total = len(demandes_toutes)
        st.metric("📈 Total demandes", nb_total)
    
    with col2:
        en_cours = sum(1 for d in demandes_toutes 
                      if d.get("statut", "En attente") in ["En attente", "En cours d'analyse", "En cours de traitement"])
        st.metric("⏳ En cours", en_cours)
    
    with col3:
        acceptees = sum(1 for d in demandes_toutes if d.get("statut") == "Accepté")
        taux_acceptation = (acceptees / nb_total * 100) if nb_total > 0 else 0
        st.metric("✅ Acceptées", acceptees, f"{taux_acceptation:.1f}%")
    
    with col4:
        refusees = sum(1 for d in demandes_toutes if d.get("statut") == "Refusé")
        taux_refus = (refusees / nb_total * 100) if nb_total > 0 else 0
        st.metric("❌ Refusées", refusees, f"{taux_refus:.1f}%")

def afficher_repartition_types_credit(demandes_toutes: List[Dict]):
    """
    Affiche la répartition par type de crédit
    
    Args:
        demandes_toutes (List[Dict]): Toutes les demandes
    """
    st.subheader("📊 Répartition par type")
    
    types_credit = {
        "Auto": sum(1 for d in demandes_toutes if d.get("type_credit") == "auto" or "marque" in d),
        "Immobilier": sum(1 for d in demandes_toutes if d.get("type_credit") == "immo" or "type_bien" in d),
        "Consommation": sum(1 for d in demandes_toutes if d.get("type_credit") == "conso" or "type_projet" in d),
        "Découvert": sum(1 for d in demandes_toutes if d.get("type_credit") == "decouvert" or "type_decouvert" in d)
    }
    
    # Filtrer les types avec des valeurs > 0
    types_credit_filtre = {k: v for k, v in types_credit.items() if v > 0}
    
    if types_credit_filtre:
        df_types = pd.DataFrame({
            'Type': list(types_credit_filtre.keys()),
            'Nombre': list(types_credit_filtre.values())
        })
        
        fig = px.pie(
            df_types, 
            names='Type', 
            values='Nombre',
            title="Demandes par type de crédit",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée à afficher")

def afficher_repartition_statuts(demandes_toutes: List[Dict]):
    """
    Affiche la répartition par statut
    
    Args:
        demandes_toutes (List[Dict]): Toutes les demandes
    """
    st.subheader("📋 Répartition par statut")
    
    # Compter les demandes par statut
    statuts = {}
    for d in demandes_toutes:
        statut = d.get("statut", "En attente")
        statuts[statut] = statuts.get(statut, 0) + 1
    
    if statuts:
        df_statuts = pd.DataFrame({
            'Statut': list(statuts.keys()),
            'Nombre': list(statuts.values())
        })
        
        # Couleurs personnalisées selon le statut
        couleurs_statut = {
            "En attente": "#FFA500",
            "En cours d'analyse": "#4169E1", 
            "En cours de traitement": "#FF6347",
            "Traitement terminé": "#32CD32",
            "Accepté": "#228B22",
            "Refusé": "#DC143C",
            "Annulé": "#696969"
        }
        
        couleurs = [couleurs_statut.get(statut, "#808080") for statut in df_statuts['Statut']]
        
        fig = px.bar(
            df_statuts,
            x='Statut',
            y='Nombre',
            title="Nombre de demandes par statut",
            color='Statut',
            color_discrete_map=couleurs_statut
        )
        
        fig.update_layout(showlegend=False)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée à afficher")

def afficher_evolution_temporelle(demandes_toutes: List[Dict]):
    """
    Affiche l'évolution temporelle des demandes
    
    Args:
        demandes_toutes (List[Dict]): Toutes les demandes
    """
    st.subheader("📈 Évolution temporelle")
    
    # Préparer les données temporelles
    dates = []
    for d in demandes_toutes:
        # Extraire la date de la référence ou utiliser la date de soumission si disponible
        if "date_soumission" in d:
            if isinstance(d["date_soumission"], str):
                try:
                    dates.append(datetime.fromisoformat(d["date_soumission"]).date())
                except:
                    dates.append(date.today())
            else:
                dates.append(d["date_soumission"])
        elif "ref_demande" in d:
            # Format: TYPE-YYMMDD-XXXX
            ref = d["ref_demande"]
            try:
                date_str = ref.split("-")[1]
                date_obj = datetime.strptime(f"20{date_str}", "%Y%m%d").date()
                dates.append(date_obj)
            except (IndexError, ValueError):
                # Utiliser une date par défaut si impossible de parser
                dates.append(date.today())
        else:
            dates.append(date.today())
    
    if dates:
        # Compter les demandes par date
        demandes_par_date = {}
        for d in dates:
            d_str = d.strftime("%Y-%m-%d")
            demandes_par_date[d_str] = demandes_par_date.get(d_str, 0) + 1
        
        # Trier par date
        dates_triees = sorted(demandes_par_date.keys())
        counts_tries = [demandes_par_date[d] for d in dates_triees]
        
        # Créer un DataFrame pour le graphique
        df_dates = pd.DataFrame({
            'Date': pd.to_datetime(dates_triees),
            'Nombre': counts_tries
        })
        
        fig = px.line(
            df_dates,
            x='Date',
            y='Nombre',
            markers=True,
            title="Évolution des demandes de crédit",
            labels={"Date": "Date", "Nombre": "Nombre de demandes"}
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Nombre de demandes"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def afficher_montants_par_type(demandes_toutes: List[Dict]):
    """
    Affiche les montants par type de crédit
    
    Args:
        demandes_toutes (List[Dict]): Toutes les demandes
    """
    st.subheader("💰 Montants par type de crédit")
    
    # Calculer la somme des montants par type
    montants_par_type = {
        "Auto": sum(d.get("montant", 0) for d in demandes_toutes 
                   if d.get("type_credit") == "auto" or "marque" in d),
        "Immobilier": sum(d.get("montant", 0) for d in demandes_toutes 
                         if d.get("type_credit") == "immo" or "type_bien" in d),
        "Consommation": sum(d.get("montant", 0) for d in demandes_toutes 
                           if d.get("type_credit") == "conso" or "type_projet" in d),
        "Découvert": sum(d.get("montant", 0) for d in demandes_toutes 
                        if d.get("type_credit") == "decouvert" or "type_decouvert" in d)
    }
    
    # Filtrer les types avec des montants > 0
    montants_filtre = {k: v for k, v in montants_par_type.items() if v > 0}
    
    if montants_filtre:
        df_montants = pd.DataFrame({
            'Type': list(montants_filtre.keys()),
            'Montant': list(montants_filtre.values())
        })
        
        fig = px.bar(
            df_montants,
            x='Type',
            y='Montant',
            title="Montant total par type de crédit (DH)",
            labels={"Type": "Type de crédit", "Montant": "Montant (DH)"},
            color='Type',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        # Formatter l'axe y avec des séparateurs de milliers
        fig.update_layout(
            yaxis=dict(tickformat=",.0f"),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Affichage des montants sous forme de métriques
        col1, col2, col3, col4 = st.columns(4)
        types_ordre = ["Auto", "Immobilier", "Consommation", "Découvert"]
        colonnes = [col1, col2, col3, col4]
        
        for i, type_credit in enumerate(types_ordre):
            if type_credit in montants_filtre:
                with colonnes[i]:
                    st.metric(
                        f"💰 {type_credit}",
                        formater_montant(montants_filtre[type_credit])
                    )

def afficher_tableau_recapitulatif(demandes_toutes: List[Dict]):
    """
    Affiche un tableau récapitulatif des demandes récentes
    
    Args:
        demandes_toutes (List[Dict]): Toutes les demandes
    """
    st.subheader("📋 Demandes récentes")
    
    if not demandes_toutes:
        st.info("Aucune demande à afficher")
        return
    
    # Préparer les données pour le tableau
    donnees_tableau = []
    
    for demande in demandes_toutes[-10:]:  # 10 dernières demandes
        # Déterminer le type de crédit
        type_credit = "Inconnu"
        if "marque" in demande or demande.get("type_credit") == "auto":
            type_credit = "Auto"
        elif "type_bien" in demande or demande.get("type_credit") == "immo":
            type_credit = "Immobilier"
        elif "type_projet" in demande or demande.get("type_credit") == "conso":
            type_credit = "Consommation"
        elif "type_decouvert" in demande or demande.get("type_credit") == "decouvert":
            type_credit = "Découvert"
        
        # Déterminer la date
        date_demande = date.today()
        if "date_soumission" in demande:
            if isinstance(demande["date_soumission"], str):
                try:
                    date_demande = datetime.fromisoformat(demande["date_soumission"]).date()
                except:
                    pass
            else:
                date_demande = demande["date_soumission"]
        elif "ref_demande" in demande:
            ref = demande["ref_demande"]
            try:
                date_str = ref.split("-")[1]
                date_demande = datetime.strptime(f"20{date_str}", "%Y%m%d").date()
            except:
                pass
        
        donnees_tableau.append({
            "Référence": demande.get("ref_demande", "N/A"),
            "Date": date_demande,
            "Client": demande.get("nom", "N/A"),
            "Type": type_credit,
            "Montant": formater_montant(demande.get("montant", 0)),
            "Statut": demande.get("statut", "En attente"),
            "Conseiller": demande.get("conseiller", "Non assigné")
        })
    
    if donnees_tableau:
        df = pd.DataFrame(donnees_tableau)
        
        # Trier par date décroissante
        df = df.sort_values('Date', ascending=False)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Aucune donnée à afficher dans le tableau")

def charger_toutes_demandes():
    """
    Charge toutes les demandes de crédit depuis les dossiers
    
    Returns:
        list: Liste de dictionnaires contenant les données des demandes
    """
    return charger_demandes()