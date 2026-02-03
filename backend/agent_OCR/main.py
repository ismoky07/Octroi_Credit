"""
backend/agent_OCR/main.py - Point d'entree principal pour le traitement OCR
"""
import os
import sys
import traceback

from backend.agent_OCR.models import State
from backend.agent_OCR.workflow import construire_workflow
from backend.agent_OCR.utils import safe_print


def traiter_dossier_documents(dossier_path: str):
    """
    Fonction principale qui traite tous les documents d'un dossier
    et verifie la concordance des informations
    """
    safe_print(f"Traitement du dossier: {dossier_path}")

    # Verifier l'existence du dossier
    if not os.path.exists(dossier_path):
        safe_print(f"Le dossier n'existe pas: {dossier_path}")
        return None

    # Initialiser le workflow
    workflow = construire_workflow()

    # Preparer l'etat initial
    initial_state = State(dossier_path=dossier_path)

    # Executer le workflow
    try:
        result = workflow.invoke(initial_state)

        # Afficher les resultats
        safe_print("\n=== RESUME DES RESULTATS ===")

        # Acces au resultat final
        if hasattr(result, "infos_documents"):
            # Le resultat est deja un etat
            final_state = result
        elif isinstance(result, dict) and "verifier_concordance" in result:
            # Le resultat est un dictionnaire avec l'etat dans la cle du dernier noeud
            final_state = result["verifier_concordance"]
        else:
            # Fallback - utiliser le resultat tel quel
            safe_print("Structure de resultat inattendue, utilisation directe")
            final_state = result

        # Afficher les resultats des documents
        try:
            safe_print(f"Nombre de documents traites: {len(final_state.infos_documents)}")

            # Details des documents
            for chemin, info in final_state.infos_documents.items():
                safe_print(f"\nDocument: {os.path.basename(chemin)}")
                safe_print(f"Type: {info.type_document}")
                if info.nom:
                    safe_print(f"Nom: {info.nom}")
                if info.prenom:
                    safe_print(f"Prenom: {info.prenom}")
                if info.date_naissance:
                    safe_print(f"Date de naissance: {info.date_naissance}")
                if info.adresse:
                    safe_print(f"Adresse: {info.adresse}")
                if info.numero_document:
                    safe_print(f"Numero: {info.numero_document}")

                # Afficher les autres infos
                if info.autres_infos:
                    safe_print("Autres informations:")
                    for cle, valeur in info.autres_infos.items():
                        safe_print(f"  - {cle}: {valeur}")

            # Resultat de concordance
            safe_print("\nResultat de la verification de concordance:")
            if final_state.concordance is None:
                safe_print("Aucune verification de concordance effectuee")
            elif final_state.concordance:
                safe_print("Toutes les informations concordent entre les documents")
            else:
                safe_print("Des problemes de concordance ont ete detectes:")
                for probleme in final_state.problemes_concordance:
                    safe_print(f"  - {probleme}")
        except Exception as display_error:
            safe_print(f"Erreur lors de l'affichage des resultats: {str(display_error)}")
            safe_print(f"Type de resultat: {type(final_state)}")
            safe_print(f"Attributs disponibles: {dir(final_state)}")
            safe_print(f"Contenu brut: {final_state}")

        return final_state
    except Exception as e:
        safe_print(f"Erreur lors de l'execution du workflow: {str(e)}")
        safe_print("Details de l'erreur:")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Afficher l'encodage utilise
    safe_print(f"Encodage systeme: {sys.getdefaultencoding()}")

    # Exemple d'utilisation
    # dossier_path = "C:/chemin/vers/dossier/documents"
    # resultat = traiter_dossier_documents(dossier_path)
    pass
