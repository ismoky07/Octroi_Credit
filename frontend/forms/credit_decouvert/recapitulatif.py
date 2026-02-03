"""
frontend/forms/credit_decouvert/recapitulatif.py - Génération du PDF récapitulatif pour découvert
"""
from fpdf import FPDF
from datetime import datetime


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Recapitulatif de demande de decouvert bancaire', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')


def generer_pdf_recapitulatif(donnees):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Informations personnelles', 0, 1)
    pdf.set_font('Arial', '', 10)

    pdf.cell(50, 7, 'Nom:', 0, 0)
    pdf.cell(0, 7, donnees["nom"], 0, 1)

    pdf.cell(50, 7, 'Telephone:', 0, 0)
    pdf.cell(0, 7, donnees["telephone"], 0, 1)

    pdf.cell(50, 7, 'Email:', 0, 0)
    pdf.cell(0, 7, donnees["email"], 0, 1)

    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Details du decouvert', 0, 1)
    pdf.set_font('Arial', '', 10)

    pdf.cell(50, 7, 'Montant:', 0, 0)
    pdf.cell(0, 7, f"{donnees['montant']} DH", 0, 1)

    pdf.cell(50, 7, 'Type:', 0, 0)
    pdf.cell(0, 7, donnees.get("type_decouvert", "N/A"), 0, 1)

    pdf.cell(50, 7, 'Banque:', 0, 0)
    pdf.cell(0, 7, donnees.get("banque", "N/A"), 0, 1)

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Reference: {donnees['ref_demande']}", 1, 1, 'C')

    return pdf
