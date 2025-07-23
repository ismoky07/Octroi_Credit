from fpdf import FPDF
from datetime import datetime
from forms.commun.fonction_de_calcul import calcul_mensualite

class PDF(FPDF):
    """Classe personnalisée pour créer des PDF avec en-tête et pied de page"""
    def header(self):
        # Logo
        # self.image('logo.png', 10, 8, 33)  # Décommenter et ajuster si logo disponible
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Récapitulatif de demande de crédit immobilier', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generer_pdf_recapitulatif(donnees):
    """
    Génère un PDF récapitulatif de la demande de crédit immobilier
    
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
    
    pdf.cell(50, 7, 'Type de logement:', 0, 0)
    pdf.cell(0, 7, donnees["logement"], 0, 1)
    
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
    
    # Informations sur le bien immobilier (spécifique au crédit immobilier)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Bien immobilier', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(50, 7, 'Type de bien:', 0, 0)
    pdf.cell(0, 7, donnees["type_bien"], 0, 1)
    
    pdf.cell(50, 7, 'Surface:', 0, 0)
    pdf.cell(0, 7, f"{donnees['surface']} m²", 0, 1)
    
    if "etage" in donnees:
        if donnees["type_bien"] == "Appartement":
            pdf.cell(50, 7, 'Étage:', 0, 0)
        else:
            pdf.cell(50, 7, 'Nombre d\'étages:', 0, 0)
        pdf.cell(0, 7, donnees["etage"], 0, 1)
    
    pdf.cell(50, 7, 'Adresse du bien:', 0, 0)
    pdf.multi_cell(0, 7, donnees["adresse_bien"], 0)
    
    pdf.cell(50, 7, 'Ville:', 0, 0)
    pdf.cell(0, 7, donnees["ville"], 0, 1)
    
    pdf.cell(50, 7, 'Quartier:', 0, 0)
    pdf.cell(0, 7, donnees["quartier"], 0, 1)
    
    pdf.cell(50, 7, 'État du bien:', 0, 0)
    pdf.cell(0, 7, donnees["etat_bien"], 0, 1)
    
    if "caracteristiques" in donnees and donnees["caracteristiques"]:
        pdf.cell(50, 7, 'Caractéristiques:', 0, 0)
        pdf.multi_cell(0, 7, donnees["caracteristiques"], 0)
    
    pdf.cell(50, 7, 'Prix:', 0, 0)
    pdf.cell(0, 7, f"{donnees['prix_bien']} DH", 0, 1)
    
    pdf.ln(5)
    
    # Informations sur le crédit
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Détails du crédit', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(50, 7, 'Montant financement:', 0, 0)
    pdf.cell(0, 7, f"{donnees['montant']} DH", 0, 1)
    
    pdf.cell(50, 7, 'Apport personnel:', 0, 0)
    pdf.cell(0, 7, f"{donnees['apport']} DH", 0, 1)
    
    pdf.cell(50, 7, 'Durée:', 0, 0)
    pdf.cell(0, 7, f"{donnees['duree']} mois ({donnees['duree']//12} ans)", 0, 1)
    
    pdf.cell(50, 7, 'Taux d\'intérêt:', 0, 0)
    pdf.cell(0, 7, f"{donnees['taux_estim']}%", 0, 1)
    
    # Mensualité estimée
    mensualite = calcul_mensualite(donnees['montant'], donnees['taux_estim'], donnees['duree'])
    pdf.cell(50, 7, 'Mensualité estimée:', 0, 0)
    pdf.cell(0, 7, f"{mensualite:.2f} DH", 0, 1)
    
    # Coût total du crédit
    cout_total = mensualite * donnees['duree'] - donnees['montant']
    pdf.cell(50, 7, 'Coût total du crédit:', 0, 0)
    pdf.cell(0, 7, f"{cout_total:.2f} DH", 0, 1)
    
    pdf.ln(10)
    
    # Référence de la demande
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Référence de votre demande: {donnees['ref_demande']}", 1, 1, 'C')
    
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, f"Demande soumise le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 0, 1, 'C')
    
    # Note de bas de page
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 5, """Note: Ce document est un récapitulatif de votre demande de crédit immobilier. 
    Il ne constitue pas une offre de crédit définitive. Votre demande sera étudiée par notre service 
    financier et une réponse vous sera communiquée dans les 5 jours ouvrés suivant la réception de votre 
    dossier complet. Un conseiller spécialisé en crédit immobilier vous accompagnera durant toute la durée 
    de votre projet.""")
    
    return pdf