from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    """Classe personnalisée pour créer des PDF avec en-tête et pied de page"""
    def header(self):
        # Logo
        # self.image('logo.png', 10, 8, 33)  # Décommenter et ajuster si logo disponible
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Récapitulatif de demande de découvert bancaire', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generer_pdf_recapitulatif(donnees):
    """
    Génère un PDF récapitulatif de la demande de découvert bancaire
    
    Args:
        donnees (dict): Dictionnaire contenant toutes les informations de la demande
        
    Returns:
        PDF: Objet PDF prêt à être sauvegardé
    """
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Informations personnelles
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Informations personnelles', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(50, 7, 'Nom et prénom:', 0, 0)
    pdf.cell(0, 7, donnees["nom"], 0, 1)
    
    pdf.cell(50, 7, 'Date de naissance:', 0, 0)
    pdf.cell(0, 7, str(donnees["naissance"]), 0, 1)
    
    pdf.cell(50, 7, 'Lieu de naissance:', 0, 0)
    pdf.cell(0, 7, donnees["lieu_naissance"], 0, 1)
    
    pdf.cell(50, 7, 'Nationalité:', 0, 0)
    pdf.cell(0, 7, donnees["nationalite"], 0, 1)
    
    pdf.cell(50, 7, 'Situation familiale:', 0, 0)
    pdf.cell(0, 7, donnees["situation_familiale"], 0, 1)
    
    pdf.cell(50, 7, 'Adresse:', 0, 0)
    pdf.multi_cell(0, 7, donnees["adresse"], 0)
    
    pdf.cell(50, 7, 'Téléphone:', 0, 0)
    pdf.cell(0, 7, donnees["telephone"], 0, 1)
    
    pdf.cell(50, 7, 'Email:', 0, 0)
    pdf.cell(0, 7, donnees["email"], 0, 1)
    
    pdf.ln(5)
    
    # Informations professionnelles
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Situation professionnelle', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(50, 7, 'Profession:', 0, 0)
    pdf.cell(0, 7, donnees["profession"], 0, 1)
    
    pdf.cell(50, 7, 'Employeur:', 0, 0)
    pdf.cell(0, 7, donnees["employeur"], 0, 1)
    
    pdf.cell(50, 7, 'Ancienneté:', 0, 0)
    pdf.cell(0, 7, donnees["anciennete_pro"], 0, 1)
    
    pdf.cell(50, 7, 'Revenu mensuel:', 0, 0)
    pdf.cell(0, 7, f"{donnees['revenu_mensuel_form']} DH", 0, 1)
    
    if donnees.get('revenu_conjoint', 0) > 0:
        pdf.cell(50, 7, 'Revenu du conjoint:', 0, 0)
        pdf.cell(0, 7, f"{donnees['revenu_conjoint']} DH", 0, 1)
    
    pdf.ln(5)
    
    # Informations bancaires (spécifique au découvert)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Informations bancaires', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(50, 7, 'Banque:', 0, 0)
    pdf.cell(0, 7, donnees["banque"], 0, 1)
    
    pdf.cell(50, 7, 'Agence:', 0, 0)
    pdf.cell(0, 7, donnees["agence"], 0, 1)
    
    pdf.cell(50, 7, 'Numéro de compte:', 0, 0)
    pdf.cell(0, 7, donnees["numero_compte"], 0, 1)
    
    pdf.cell(50, 7, 'Date d\'ouverture:', 0, 0)
    pdf.cell(0, 7, str(donnees["date_ouverture"]), 0, 1)
    
    pdf.cell(50, 7, 'Mouvements mensuels:', 0, 0)
    pdf.cell(0, 7, f"{donnees['mouvements_mensuels']} DH", 0, 1)
    
    pdf.ln(5)
    
    # Informations sur le découvert
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Découvert demandé', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(50, 7, 'Montant du découvert:', 0, 0)
    pdf.cell(0, 7, f"{donnees['montant']} DH", 0, 1)
    
    pdf.cell(50, 7, 'Type de découvert:', 0, 0)
    pdf.cell(0, 7, donnees["type_decouvert"], 0, 1)
    
    pdf.cell(50, 7, 'Taux d\'intérêt annuel:', 0, 0)
    pdf.cell(0, 7, f"{donnees['taux_annuel']}%", 0, 1)
    
    pdf.cell(50, 7, 'Motif de la demande:', 0, 0)
    pdf.multi_cell(0, 7, donnees["motif"], 0)
    
    pdf.ln(5)
    
    # Coûts estimés
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Coûts estimés', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    if donnees["type_decouvert"] == "Ponctuel (1 mois)":
        interet_mensuel = donnees["montant"] * (donnees["taux_annuel"] / 100 / 12)
        pdf.cell(50, 7, 'Intérêts mensuels:', 0, 0)
        pdf.cell(0, 7, f"{interet_mensuel:.2f} DH", 0, 1)
    elif donnees["type_decouvert"] == "Court terme (3 mois)":
        interet_3mois = donnees["montant"] * (donnees["taux_annuel"] / 100 / 4)
        pdf.cell(50, 7, 'Intérêts sur 3 mois:', 0, 0)
        pdf.cell(0, 7, f"{interet_3mois:.2f} DH", 0, 1)
    else:  # Permanent
        interet_annuel = donnees["montant"] * (donnees["taux_annuel"] / 100)
        pdf.cell(50, 7, 'Intérêts annuels:', 0, 0)
        pdf.cell(0, 7, f"{interet_annuel:.2f} DH", 0, 1)
    
    pdf.cell(50, 7, 'Commission d\'ouverture:', 0, 0)
    pdf.cell(0, 7, "100 DH", 0, 1)
    
    pdf.ln(10)
    
    # Référence de la demande
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Référence de votre demande: {donnees['ref_demande']}", 1, 1, 'C')
    
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, f"Demande soumise le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 0, 1, 'C')
    
    # Note de bas de page
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 5, """Note: Ce document est un récapitulatif de votre demande de découvert bancaire. 
    Il ne constitue pas une autorisation de découvert. Votre demande sera étudiée par notre service 
    financier et une réponse vous sera communiquée dans les 24h ouvrées suivant la réception de votre dossier complet.
    
    Le découvert est soumis à des conditions d'utilisation spécifiques. Vous recevrez, en cas d'acceptation, 
    une convention de découvert détaillant ces conditions ainsi que les frais applicables.""")
    
    return pdf