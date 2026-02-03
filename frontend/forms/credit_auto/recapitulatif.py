"""
frontend/forms/credit_auto/recapitulatif.py - Génération du PDF récapitulatif pour crédit auto
"""
from fpdf import FPDF
from datetime import datetime

from backend.services.calcul import calcul_mensualite


class PDF(FPDF):
    """Classe personnalisée pour créer des PDF avec en-tête et pied de page"""
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Récapitulatif de demande de crédit automobile', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')


def generer_pdf_recapitulatif(donnees):
    """
    Génère un PDF récapitulatif de la demande de crédit automobile

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

    pdf.cell(50, 7, 'Nom et prenom:', 0, 0)
    pdf.cell(0, 7, donnees["nom"], 0, 1)

    pdf.cell(50, 7, 'Date de naissance:', 0, 0)
    pdf.cell(0, 7, str(donnees["naissance"]), 0, 1)

    pdf.cell(50, 7, 'Lieu de naissance:', 0, 0)
    pdf.cell(0, 7, donnees["lieu_naissance"], 0, 1)

    pdf.cell(50, 7, 'Nationalite:', 0, 0)
    pdf.cell(0, 7, donnees["nationalite"], 0, 1)

    pdf.cell(50, 7, 'Situation familiale:', 0, 0)
    pdf.cell(0, 7, donnees["situation_familiale"], 0, 1)

    pdf.cell(50, 7, 'Adresse:', 0, 0)
    pdf.multi_cell(0, 7, donnees["adresse"], 0)

    pdf.cell(50, 7, 'Telephone:', 0, 0)
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

    pdf.cell(50, 7, 'Anciennete:', 0, 0)
    pdf.cell(0, 7, donnees["anciennete_pro"], 0, 1)

    pdf.cell(50, 7, 'Revenu mensuel:', 0, 0)
    pdf.cell(0, 7, f"{donnees['revenu_mensuel_form']} DH", 0, 1)

    if donnees.get('revenu_conjoint', 0) > 0:
        pdf.cell(50, 7, 'Revenu du conjoint:', 0, 0)
        pdf.cell(0, 7, f"{donnees['revenu_conjoint']} DH", 0, 1)

    pdf.ln(5)

    # Informations sur le véhicule
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Vehicule', 0, 1)
    pdf.set_font('Arial', '', 10)

    pdf.cell(50, 7, 'Marque et modele:', 0, 0)
    pdf.cell(0, 7, f"{donnees['marque']} {donnees['modele']}", 0, 1)

    pdf.cell(50, 7, 'Annee:', 0, 0)
    pdf.cell(0, 7, donnees["annee"], 0, 1)

    pdf.cell(50, 7, 'Kilometrage:', 0, 0)
    pdf.cell(0, 7, donnees["kilometrage"], 0, 1)

    pdf.cell(50, 7, 'Prix:', 0, 0)
    pdf.cell(0, 7, f"{donnees['prix_vehicule']} DH", 0, 1)

    pdf.ln(5)

    # Informations sur le crédit
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Details du credit', 0, 1)
    pdf.set_font('Arial', '', 10)

    pdf.cell(50, 7, 'Montant financement:', 0, 0)
    pdf.cell(0, 7, f"{donnees['montant']} DH", 0, 1)

    pdf.cell(50, 7, 'Apport personnel:', 0, 0)
    pdf.cell(0, 7, f"{donnees['apport']} DH", 0, 1)

    pdf.cell(50, 7, 'Duree:', 0, 0)
    pdf.cell(0, 7, f"{donnees['duree']} mois", 0, 1)

    pdf.cell(50, 7, "Taux d'interet:", 0, 0)
    pdf.cell(0, 7, f"{donnees['taux_estim']}%", 0, 1)

    # Mensualité estimée
    mensualite = calcul_mensualite(donnees['montant'], donnees['taux_estim'], donnees['duree'])
    pdf.cell(50, 7, 'Mensualite estimee:', 0, 0)
    pdf.cell(0, 7, f"{mensualite:.2f} DH", 0, 1)

    # Coût total du crédit
    cout_total = mensualite * donnees['duree'] - donnees['montant']
    pdf.cell(50, 7, 'Cout total du credit:', 0, 0)
    pdf.cell(0, 7, f"{cout_total:.2f} DH", 0, 1)

    pdf.ln(10)

    # Référence de la demande
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Reference de votre demande: {donnees['ref_demande']}", 1, 1, 'C')

    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, f"Demande soumise le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", 0, 1, 'C')

    # Note de bas de page
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 5, """Note: Ce document est un recapitulatif de votre demande de credit automobile.
    Il ne constitue pas une offre de credit definitive. Votre demande sera etudiee par notre service
    financier et une reponse vous sera communiquee dans les meilleurs delais.""")

    return pdf
