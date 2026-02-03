"""
frontend/pages/gestion_clients.py - Module de gestion des clients
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict

from backend.utils import formater_montant


def afficher_gestion_clients(demandes_toutes: List[Dict]):
    """
    Affiche la gestion centralisée des clients

    Args:
        demandes_toutes (List[Dict]): Toutes les demandes de crédit
    """
    st.header("👥 Gestion des clients")

    if not demandes_toutes:
        st.info("Aucun client trouvé.")
        return

    # Préparer les données clients
    clients_data = preparer_donnees_clients(demandes_toutes)

    if not clients_data:
        st.info("Aucune donnée client disponible.")
        return

    # Statistiques des clients
    afficher_statistiques_clients(clients_data)

    st.markdown("---")

    # Filtres
    clients_filtres = afficher_filtres_clients(clients_data)

    # Tableau des clients
    afficher_tableau_clients(clients_filtres)

    # Graphiques d'analyse
    afficher_analyses_clients(clients_data)


def preparer_donnees_clients(demandes_toutes: List[Dict]) -> List[Dict]:
    """
    Prépare les données des clients uniques avec leurs statistiques

    Args:
        demandes_toutes (List[Dict]): Toutes les demandes

    Returns:
        List[Dict]: Liste des clients avec leurs données agrégées
    """
    clients = {}

    for demande in demandes_toutes:
        nom = demande.get("nom", "")
        email = demande.get("email", "")

        if not nom:
            continue

        # Clé unique basée sur nom + email
        cle_client = f"{nom}_{email}" if email else nom

        if cle_client not in clients:
            clients[cle_client] = {
                "nom": nom,
                "email": email,
                "telephone": demande.get("telephone", ""),
                "adresse": demande.get("adresse", ""),
                "profession": demande.get("profession", ""),
                "revenu": demande.get("revenu_mensuel_form", 0),
                "demandes": [],
                "types_credit": set(),
                "montant_total": 0,
                "nb_demandes": 0,
                "statuts": set(),
                "conseillers": set()
            }

        # Ajouter cette demande aux statistiques du client
        client = clients[cle_client]
        client["demandes"].append(demande)
        client["nb_demandes"] += 1
        client["montant_total"] += demande.get("montant", 0)
        client["statuts"].add(demande.get("statut", "En attente"))

        if demande.get("conseiller"):
            client["conseillers"].add(demande.get("conseiller"))

        # Déterminer le type de crédit
        if "marque" in demande or demande.get("type_credit") == "auto":
            client["types_credit"].add("Auto")
        elif "type_bien" in demande or demande.get("type_credit") == "immo":
            client["types_credit"].add("Immobilier")
        elif "type_projet" in demande or demande.get("type_credit") == "conso":
            client["types_credit"].add("Consommation")
        elif "type_decouvert" in demande or demande.get("type_credit") == "decouvert":
            client["types_credit"].add("Découvert")

    # Convertir les sets en listes pour l'affichage
    clients_list = []
    for client_data in clients.values():
        client_data["types_credit"] = list(client_data["types_credit"])
        client_data["statuts"] = list(client_data["statuts"])
        client_data["conseillers"] = list(client_data["conseillers"])
        clients_list.append(client_data)

    return clients_list


def afficher_statistiques_clients(clients_data: List[Dict]):
    """
    Affiche les statistiques générales des clients

    Args:
        clients_data (List[Dict]): Données des clients
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total clients", len(clients_data))

    with col2:
        clients_actifs = sum(1 for c in clients_data
                           if any(statut in ["En attente", "En cours d'analyse", "En cours de traitement"]
                                 for statut in c["statuts"]))
        st.metric("🔄 Clients actifs", clients_actifs)

    with col3:
        demandes_totales = sum(c["nb_demandes"] for c in clients_data)
        moyenne_demandes = demandes_totales / len(clients_data) if clients_data else 0
        st.metric("📊 Moy. demandes/client", f"{moyenne_demandes:.1f}")

    with col4:
        montant_total = sum(c["montant_total"] for c in clients_data)
        st.metric("💰 Volume total", formater_montant(montant_total))


def afficher_filtres_clients(clients_data: List[Dict]) -> List[Dict]:
    """
    Affiche les filtres pour les clients et retourne les données filtrées

    Args:
        clients_data (List[Dict]): Données des clients

    Returns:
        List[Dict]: Clients filtrés
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtre par profession
        professions = ["Toutes"] + list(set([c["profession"] for c in clients_data if c["profession"]]))
        profession_filtre = st.selectbox("🏢 Profession", professions)

    with col2:
        # Filtre par type de crédit
        tous_types = set()
        for client in clients_data:
            tous_types.update(client["types_credit"])

        type_credit_filtre = st.selectbox("💳 Type de crédit", ["Tous"] + sorted(list(tous_types)))

    with col3:
        # Filtre par statut
        tous_statuts = set()
        for client in clients_data:
            tous_statuts.update(client["statuts"])

        statut_filtre = st.selectbox("📋 Statut", ["Tous"] + sorted(list(tous_statuts)))

    # Recherche par nom
    recherche_nom = st.text_input("🔍 Rechercher par nom", placeholder="Nom du client...")

    # Appliquer les filtres
    clients_filtres = clients_data

    if profession_filtre != "Toutes":
        clients_filtres = [c for c in clients_filtres if c["profession"] == profession_filtre]

    if type_credit_filtre != "Tous":
        clients_filtres = [c for c in clients_filtres if type_credit_filtre in c["types_credit"]]

    if statut_filtre != "Tous":
        clients_filtres = [c for c in clients_filtres if statut_filtre in c["statuts"]]

    if recherche_nom:
        clients_filtres = [c for c in clients_filtres
                          if recherche_nom.lower() in c["nom"].lower()]

    return clients_filtres


def afficher_tableau_clients(clients_filtres: List[Dict]):
    """
    Affiche le tableau des clients avec leurs informations

    Args:
        clients_filtres (List[Dict]): Clients filtrés
    """
    st.subheader(f"📋 Liste des clients ({len(clients_filtres)})")

    if not clients_filtres:
        st.info("Aucun client ne correspond aux critères de filtrage.")
        return

    # Préparer les données pour le tableau
    donnees_tableau = []

    for client in clients_filtres:
        donnees_tableau.append({
            "Nom": client["nom"],
            "Email": client["email"],
            "Téléphone": client["telephone"],
            "Profession": client["profession"],
            "Revenu (DH)": formater_montant(client["revenu"]),
            "Nb demandes": client["nb_demandes"],
            "Montant total": formater_montant(client["montant_total"]),
            "Types de crédit": ", ".join(client["types_credit"]),
            "Statuts": ", ".join(client["statuts"]),
            "Conseillers": ", ".join(client["conseillers"]) if client["conseillers"] else "Non assigné"
        })

    df_clients = pd.DataFrame(donnees_tableau)

    # Affichage du tableau avec possibilité de tri
    st.dataframe(
        df_clients,
        use_container_width=True,
        hide_index=True
    )

    # Boutons d'export
    col1, col2 = st.columns(2)

    with col1:
        # Export CSV
        csv = df_clients.to_csv(index=False)
        st.download_button(
            "📥 Exporter en CSV",
            data=csv,
            file_name="clients.csv",
            mime="text/csv"
        )

    with col2:
        # Export Excel
        try:
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_clients.to_excel(writer, sheet_name='Clients', index=False)

            st.download_button(
                "📊 Exporter en Excel",
                data=buffer.getvalue(),
                file_name="clients.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("📊 Export Excel non disponible (package xlsxwriter requis)")


def afficher_analyses_clients(clients_data: List[Dict]):
    """
    Affiche les analyses graphiques des clients

    Args:
        clients_data (List[Dict]): Données des clients
    """
    st.markdown("---")
    st.subheader("📊 Analyses des clients")

    col1, col2 = st.columns(2)

    with col1:
        # Répartition par profession
        afficher_repartition_professions(clients_data)

    with col2:
        # Distribution des revenus
        afficher_distribution_revenus(clients_data)

    # Analyse des clients multi-demandes
    afficher_analyse_multi_demandes(clients_data)


def afficher_repartition_professions(clients_data: List[Dict]):
    """
    Affiche la répartition des clients par profession

    Args:
        clients_data (List[Dict]): Données des clients
    """
    professions = {}

    for client in clients_data:
        profession = client["profession"] if client["profession"] else "Non renseigné"
        professions[profession] = professions.get(profession, 0) + 1

    if professions:
        # Limiter aux 8 professions les plus fréquentes
        professions_triees = sorted(professions.items(), key=lambda x: x[1], reverse=True)[:8]

        df_professions = pd.DataFrame(professions_triees, columns=['Profession', 'Nombre'])

        fig = px.pie(
            df_professions,
            names='Profession',
            values='Nombre',
            title="Répartition par profession",
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)


def afficher_distribution_revenus(clients_data: List[Dict]):
    """
    Affiche la distribution des revenus des clients

    Args:
        clients_data (List[Dict]): Données des clients
    """
    revenus = [client["revenu"] for client in clients_data if client["revenu"] > 0]

    if revenus:
        # Créer des tranches de revenus
        tranches = {
            "< 5 000 DH": sum(1 for r in revenus if r < 5000),
            "5 000 - 10 000 DH": sum(1 for r in revenus if 5000 <= r < 10000),
            "10 000 - 20 000 DH": sum(1 for r in revenus if 10000 <= r < 20000),
            "> 20 000 DH": sum(1 for r in revenus if r >= 20000)
        }

        # Filtrer les tranches avec des valeurs > 0
        tranches_filtre = {k: v for k, v in tranches.items() if v > 0}

        if tranches_filtre:
            df_revenus = pd.DataFrame({
                'Tranche': list(tranches_filtre.keys()),
                'Nombre': list(tranches_filtre.values())
            })

            fig = px.bar(
                df_revenus,
                x='Tranche',
                y='Nombre',
                title="Distribution des revenus",
                color='Tranche',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            fig.update_layout(showlegend=False)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)


def afficher_analyse_multi_demandes(clients_data: List[Dict]):
    """
    Affiche l'analyse des clients avec plusieurs demandes

    Args:
        clients_data (List[Dict]): Données des clients
    """
    # Clients avec plusieurs demandes
    clients_multi = [c for c in clients_data if c["nb_demandes"] > 1]

    if clients_multi:
        st.subheader(f"🔄 Clients multi-demandes ({len(clients_multi)})")

        # Tableau des clients multi-demandes
        donnees_multi = []

        for client in sorted(clients_multi, key=lambda x: x["nb_demandes"], reverse=True)[:10]:
            donnees_multi.append({
                "Client": client["nom"],
                "Nb demandes": client["nb_demandes"],
                "Montant total": formater_montant(client["montant_total"]),
                "Types": ", ".join(client["types_credit"]),
                "Statuts actuels": ", ".join(client["statuts"])
            })

        if donnees_multi:
            df_multi = pd.DataFrame(donnees_multi)
            st.dataframe(df_multi, use_container_width=True, hide_index=True)

        # Graphique de répartition
        repartition_demandes = {}
        for client in clients_data:
            nb_demandes = client["nb_demandes"]
            cle = f"{nb_demandes} demande{'s' if nb_demandes > 1 else ''}"
            repartition_demandes[cle] = repartition_demandes.get(cle, 0) + 1

        if repartition_demandes:
            df_repartition = pd.DataFrame({
                'Nombre de demandes': list(repartition_demandes.keys()),
                'Clients': list(repartition_demandes.values())
            })

            fig = px.bar(
                df_repartition,
                x='Nombre de demandes',
                y='Clients',
                title="Répartition des clients par nombre de demandes",
                color='Clients',
                color_continuous_scale='Blues'
            )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun client avec plusieurs demandes trouvé.")
