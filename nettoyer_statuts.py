"""
nettoyer_statuts.py - Nettoie tous les fichiers de statut de traitement
Lancez ce script pour supprimer les fichiers de statut corrompus
"""

import os
import glob

def nettoyer_fichiers_statut():
    """Supprime tous les fichiers traitement_status.json"""
    
    print("🧹 Nettoyage des fichiers de statut...")
    
    # Chercher tous les fichiers traitement_status.json
    patterns = [
        "demandes_clients/**/traitement_status.json",
        "demandes_clients/*/*/traitement_status.json",
        "**/traitement_status.json"
    ]
    
    fichiers_trouves = []
    for pattern in patterns:
        fichiers_trouves.extend(glob.glob(pattern, recursive=True))
    
    if not fichiers_trouves:
        print("✅ Aucun fichier de statut trouvé")
        return
    
    print(f"📄 {len(fichiers_trouves)} fichier(s) de statut trouvé(s):")
    
    for fichier in fichiers_trouves:
        print(f"  - {fichier}")
        try:
            os.remove(fichier)
            print(f"    ✅ Supprimé")
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
    
    print("🎉 Nettoyage terminé!")
    print("Relancez maintenant Streamlit pour tester.")

if __name__ == "__main__":
    nettoyer_fichiers_statut()