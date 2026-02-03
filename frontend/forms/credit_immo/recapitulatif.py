"""
frontend/forms/credit_immo/recapitulatif.py - Génération du PDF récapitulatif pour crédit immobilier
"""
from fpdf import FPDF
from datetime import datetime

from backend.services.calcul import calcul_mensualite


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Recapitulatif de demande de credit immobilier', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')


def generer_pdf_recapitulatif(donnees):
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

    pdf.cell(50, 7, 'Telephone:', 0, 0)
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

    pdf.cell(50, 7, 'Revenu mensuel:', 0, 0)
    pdf.cell(0, 7, f"{donnees['revenu_mensuel_form']} DH", 0, 1)

    pdf.ln(5)

    # Informations sur le bien
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Bien immobilier', 0, 1)
    pdf.set_font('Arial', '', 10)

    pdf.cell(50, 7, 'Type de bien:', 0, 0)
    pdf.cell(0, 7, donnees.get("type_bien", "N/A"), 0, 1)

    pdf.cell(50, 7, 'Prix du bien:', 0, 0)
    pdf.cell(0, 7, f"{donnees.get('prix_bien', 0)} DH", 0, 1)

    pdf.cell(50, 7, 'Ville:', 0, 0)
    pdf.cell(0, 7, donnees.get("ville", "N/A"), 0, 1)

    pdf.ln(5)

    # Détails du crédit
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Details du credit', 0, 1)
    pdf.set_font('Arial', '', 10)

    pdf.cell(50, 7, 'Montant:', 0, 0)
    pdf.cell(0, 7, f"{donnees['montant']} DH", 0, 1)

    pdf.cell(50, 7, 'Duree:', 0, 0)
    pdf.cell(0, 7, f"{donnees['duree']} mois", 0, 1)

    mensualite = calcul_mensualite(donnees['montant'], donnees['taux_estim'], donnees['duree'])
    pdf.cell(50, 7, 'Mensualite estimee:', 0, 0)
    pdf.cell(0, 7, f"{mensualite:.2f} DH", 0, 1)

    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Reference: {donnees['ref_demande']}", 1, 1, 'C')

    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, f"Demande soumise le {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')

    return pdf
