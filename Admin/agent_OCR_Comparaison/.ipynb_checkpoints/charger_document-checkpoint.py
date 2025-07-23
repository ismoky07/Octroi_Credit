import os
from pathlib import Path
from typing import List
from pdf2image import convert_from_path

def charger_documents(dossier_path: str) -> List[str]:
    """Charge tous les fichiers PDF d'un dossier et retourne leurs chemins"""
    pdf_paths = []
    
    for fichier in os.listdir(dossier_path):
        if fichier.lower().endswith('.pdf'):
            pdf_paths.append(os.path.join(dossier_path, fichier))
    
    return pdf_paths

def convertir_pdf_en_images(pdf_paths: List[str], output_dir: str = None) -> List[str]:
    """Convertit des PDF en images pour faciliter l'OCR"""
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    images_paths = []
    
    for pdf_path in pdf_paths:
        try:
            # Créer un nom de base pour les images
            base_name = Path(pdf_path).stem
            
            # Convertir le PDF en images
            images = convert_from_path(pdf_path)
            
            # Sauvegarder les images
            for i, image in enumerate(images):
                if output_dir:
                    image_path = os.path.join(output_dir, f"{base_name}_page{i+1}.jpg")
                    image.save(image_path, "JPEG")
                    images_paths.append(image_path)
                else:
                    # Si pas de dossier de sortie, on garde l'image en mémoire 
                    image_path = f"{base_name}_page{i+1}"
                    images_paths.append(image_path)
        except Exception as e:
            print(f"Erreur lors de la conversion du PDF {pdf_path}: {str(e)}")
    
    return images_paths