"""
backend/agent_OCR/charger_document.py - Chargement et conversion de documents
"""
import os
from pathlib import Path
from typing import List
import fitz  # PyMuPDF

from backend.agent_OCR.utils import safe_print


def charger_documents(dossier_path: str) -> List[str]:
    """Charge tous les fichiers PDF d'un dossier et retourne leurs chemins"""
    pdf_paths = []

    # Normaliser le chemin d'entree
    dossier_path = dossier_path.replace('\\', '/')
    safe_print(f"Chargement des documents depuis: {dossier_path}")

    try:
        for fichier in os.listdir(dossier_path):
            if fichier.lower().endswith('.pdf'):
                # Construire le chemin avec des forward slashes
                chemin_pdf = f"{dossier_path}/{fichier}"
                pdf_paths.append(chemin_pdf)
                safe_print(f"Fichier PDF trouve: {chemin_pdf}")
    except Exception as e:
        safe_print(f"Erreur lors du listage du dossier {dossier_path}: {str(e)}")

    safe_print(f"Nombre total de PDF trouves: {len(pdf_paths)}")
    return pdf_paths


def verifier_pdf(pdf_path: str) -> bool:
    """Verifie si le PDF peut etre ouvert et obtient des informations de base"""
    try:
        # Ouvrir le PDF avec PyMuPDF
        doc = fitz.open(pdf_path)

        # Obtenir des informations
        page_count = len(doc)

        # Fermer le document
        doc.close()

        # Un PDF valide doit avoir au moins une page
        if page_count > 0:
            safe_print(f"PDF valide: {os.path.basename(pdf_path)} ({page_count} pages)")
            return True
        else:
            safe_print(f"PDF vide: {os.path.basename(pdf_path)}")
            return False

    except Exception as e:
        safe_print(f"PDF invalide: {os.path.basename(pdf_path)} - {str(e)}")
        return False


def convertir_pdf_en_images(pdf_paths, output_dir=None, dpi=300):
    """
    Convertit une liste de fichiers PDF en images en utilisant PyMuPDF (Fitz).
    Cette fonction ne necessite pas Poppler.
    """
    if not isinstance(pdf_paths, list):
        raise TypeError("pdf_paths doit etre une liste de chemins de fichiers PDF.")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        safe_print(f"Dossier de sortie cree: {output_dir}")

    images_paths = []

    for pdf_path in pdf_paths:
        try:
            safe_print(f"Conversion du PDF: {pdf_path}")

            # Verifier l'existence du fichier
            if not os.path.exists(pdf_path):
                safe_print(f"Le fichier n'existe pas: {pdf_path}")
                continue

            # Ouvrir le document PDF avec PyMuPDF
            doc = fitz.open(pdf_path)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]

            safe_print(f"Conversion de {len(doc)} page(s) pour {base_name}")

            # Convertir chaque page en image
            for i, page in enumerate(doc):
                # Calculer le facteur de zoom base sur DPI
                zoom = dpi / 72  # 72 DPI est la resolution par defaut des PDF

                # Creer une matrice de transformation pour le zoom
                mat = fitz.Matrix(zoom, zoom)

                # Rendre la page comme une image
                pix = page.get_pixmap(matrix=mat)

                # Definir le chemin de sortie
                if output_dir:
                    image_path = os.path.join(output_dir, f"{base_name}_page_{i+1:02d}.png")
                else:
                    image_path = f"{base_name}_page_{i+1:02d}.png"

                # Sauvegarder l'image
                pix.save(image_path)
                images_paths.append(image_path)
                safe_print(f"Image sauvegardee: {image_path}")

            # Fermer le document
            doc.close()

        except Exception as e:
            safe_print(f"Erreur lors de la conversion du PDF {pdf_path}: {str(e)}")

    safe_print(f"Nombre total d'images generees: {len(images_paths)}")
    return images_paths


def sauvegarder_images(images_data, output_dir):
    """
    Sauvegarde les images dans le dossier specifie
    Cette fonction est integree dans convertir_pdf_en_images
    """
    # Cette fonction est maintenant integree dans convertir_pdf_en_images
    # Elle est gardee ici pour compatibilite si necessaire
    pass
