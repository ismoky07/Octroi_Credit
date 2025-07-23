def calcul_mensualite(montant, taux_annuel, duree_mois):
    """
    Calcule la mensualité d'un crédit
    
    Args:
        montant (float): Montant du crédit en DH
        taux_annuel (float): Taux d'intérêt annuel en pourcentage
        duree_mois (int): Durée du crédit en mois
        
    Returns:
        float: Mensualité du crédit en DH
    """
    if montant <= 0 or duree_mois <= 0:
        return 0
    
    taux_mensuel = taux_annuel / 100 / 12
    if taux_mensuel == 0:  # Cas particulier: taux zéro
        return montant / duree_mois
        
    return montant * (taux_mensuel * (1 + taux_mensuel) ** duree_mois) / ((1 + taux_mensuel) ** duree_mois - 1)

def calculer_tableau_amortissement(montant, taux_annuel, duree_mois):
    """
    Génère le tableau d'amortissement complet d'un crédit
    
    Args:
        montant (float): Montant du crédit en DH
        taux_annuel (float): Taux d'intérêt annuel en pourcentage
        duree_mois (int): Durée du crédit en mois
        
    Returns:
        list: Liste de dictionnaires contenant les détails de chaque échéance
    """
    taux_mensuel = taux_annuel / 100 / 12
    mensualite = calcul_mensualite(montant, taux_annuel, duree_mois)
    
    tableau = []
    capital_restant = montant
    
    for mois in range(1, duree_mois + 1):
        interet = capital_restant * taux_mensuel
        amortissement = mensualite - interet
        capital_restant -= amortissement
        
        if capital_restant < 0.01:  # Éviter les arrondis négatifs
            capital_restant = 0
            
        tableau.append({
            "mois": mois,
            "mensualite": mensualite,
            "interet": interet,
            "amortissement": amortissement,
            "capital_restant": capital_restant
        })
    
    return tableau

def get_taux_endettement(revenu, charges, mensualite):
    """
    Calcule le taux d'endettement en pourcentage
    
    Args:
        revenu (float): Revenu mensuel net en DH
        charges (float): Charges mensuelles existantes en DH
        mensualite (float): Mensualité du nouveau crédit en DH
        
    Returns:
        float: Taux d'endettement en pourcentage
    """
    if revenu <= 0:
        return 100  # Si pas de revenu, endettement maximal
        
    return (charges + mensualite) / revenu * 100

def calculer_capacite_emprunt(revenu, charges, taux_annuel, duree_mois, taux_endettement_max=33):
    """
    Calcule la capacité maximale d'emprunt en fonction du revenu et des charges
    
    Args:
        revenu (float): Revenu mensuel net en DH
        charges (float): Charges mensuelles existantes en DH
        taux_annuel (float): Taux d'intérêt annuel en pourcentage
        duree_mois (int): Durée du crédit souhaitée en mois
        taux_endettement_max (float): Taux d'endettement maximal autorisé (défaut: 33%)
        
    Returns:
        float: Montant maximal empruntable en DH
    """
    if revenu <= 0 or duree_mois <= 0:
        return 0
    
    # Capacité de remboursement mensuelle
    capacite_remboursement = (revenu * taux_endettement_max / 100) - charges
    
    # Si la capacité est négative ou nulle, impossible d'emprunter
    if capacite_remboursement <= 0:
        return 0
    
    # Calcul du montant empruntable à partir de la mensualité
    taux_mensuel = taux_annuel / 100 / 12
    
    if taux_mensuel == 0:  # Cas particulier: taux zéro
        return capacite_remboursement * duree_mois
    
    montant = capacite_remboursement * ((1 + taux_mensuel) ** duree_mois - 1) / (taux_mensuel * (1 + taux_mensuel) ** duree_mois)
    
    return montant

def calculer_frais_dossier(montant, taux_frais=0.5, min_frais=1000, max_frais=5000):
    """
    Calcule les frais de dossier pour un crédit
    
    Args:
        montant (float): Montant du crédit en DH
        taux_frais (float): Taux des frais en pourcentage (défaut: 0.5%)
        min_frais (float): Montant minimum des frais (défaut: 1000 DH)
        max_frais (float): Montant maximum des frais (défaut: 5000 DH)
        
    Returns:
        float: Montant des frais de dossier en DH
    """
    frais = montant * taux_frais / 100
    
    # Application des bornes min et max
    if frais < min_frais:
        frais = min_frais
    elif frais > max_frais:
        frais = max_frais
    
    return frais