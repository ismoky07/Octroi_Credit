import os
import io
import sys
import traceback
from models import State
from workflowAgentOCR import construire_workflow

# Fonction pour gérer en toute sécurité les affichages avec caractères spéciaux
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='backslashreplace').decode('ascii', errors='backslashreplace'))

def traiter_dossier_documents(dossier_path: str):
    """
    Fonction principale qui traite tous les documents d'un dossier
    et vérifie la concordance des informations
    """
    safe_print(f"Traitement du dossier: {dossier_path}")
    
    # Vérifier l'existence du dossier
    if not os.path.exists(dossier_path):
        safe_print(f"⚠️ Le dossier n'existe pas: {dossier_path}")
        return None
    
    # Initialiser le workflow
    workflow = construire_workflow()
    
    # Préparer l'état initial
    initial_state = State(dossier_path=dossier_path)
    
    # Exécuter le workflow
    try:
        result = workflow.invoke(initial_state)
        
        # Afficher les résultats
        safe_print("\n=== RÉSUMÉ DES RÉSULTATS ===")
        
        # Accès au résultat final
        if hasattr(result, "infos_documents"):
            # Le résultat est déjà un état
            final_state = result
        elif isinstance(result, dict) and "verifier_concordance" in result:
            # Le résultat est un dictionnaire avec l'état dans la clé du dernier nœud
            final_state = result["verifier_concordance"]
        else:
            # Fallback - utiliser le résultat tel quel
            safe_print("⚠️ Structure de résultat inattendue, utilisation directe")
            final_state = result
        
        # Afficher les résultats des documents
        try:
            safe_print(f"Nombre de documents traités: {len(final_state.infos_documents)}")
            
            # Détails des documents
            for chemin, info in final_state.infos_documents.items():
                safe_print(f"\nDocument: {os.path.basename(chemin)}")
                safe_print(f"Type: {info.type_document}")
                if info.nom:
                    safe_print(f"Nom: {info.nom}")
                if info.prenom:
                    safe_print(f"Prénom: {info.prenom}")
                if info.date_naissance:
                    safe_print(f"Date de naissance: {info.date_naissance}")
                if info.adresse:
                    safe_print(f"Adresse: {info.adresse}")
                if info.numero_document:
                    safe_print(f"Numéro: {info.numero_document}")
                
                # Afficher les autres infos
                if info.autres_infos:
                    safe_print("Autres informations:")
                    for cle, valeur in info.autres_infos.items():
                        safe_print(f"  - {cle}: {valeur}")
            
            # Résultat de concordance
            safe_print("\nRésultat de la vérification de concordance:")
            if final_state.concordance is None:
                safe_print("❓ Aucune vérification de concordance effectuée")
            elif final_state.concordance:
                safe_print("✅ Toutes les informations concordent entre les documents")
            else:
                safe_print("❌ Des problèmes de concordance ont été détectés:")
                for probleme in final_state.problemes_concordance:
                    safe_print(f"  - {probleme}")
        except Exception as display_error:
            safe_print(f"Erreur lors de l'affichage des résultats: {str(display_error)}")
            safe_print(f"Type de résultat: {type(final_state)}")
            safe_print(f"Attributs disponibles: {dir(final_state)}")
            safe_print(f"Contenu brut: {final_state}")
        
        return final_state
    except Exception as e:
        safe_print(f"Erreur lors de l'exécution du workflow: {str(e)}")
        safe_print("Détails de l'erreur:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Afficher l'encodage utilisé
    safe_print(f"Encodage système: {sys.getdefaultencoding()}")
    
    # Définir le chemin avec forward slashes pour éviter les problèmes d'échappement
    dossier_path = "C:/Users/HP/Desktop/Octroi-Credit/Admin/demandes_clients/decouvert/jean Dupont - DECOUVERT-250603-33E9"
    resultat = traiter_dossier_documents(dossier_path)