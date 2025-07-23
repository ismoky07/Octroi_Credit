# Module d'envoi d'emails pour le système de crédit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import datetime

# Configuration des emails (à modifier selon votre serveur SMTP)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "votre_email@gmail.com"  # À remplacer par votre email réel
EMAIL_HOST_PASSWORD = "mot_de_passe_app"   # À remplacer par votre mot de passe d'application

# Adresse email de l'expéditeur (banque)
EMAIL_FROM = "Banque Crédit <credit@banque.ma>"

def envoyer_email_prise_en_charge(destinataire, nom_client, reference, type_credit, conseiller, pieces_jointes=None):
    """
    Envoie un email de prise en charge au client
    
    Args:
        destinataire (str): Adresse email du destinataire
        nom_client (str): Nom du client
        reference (str): Référence de la demande
        type_credit (str): Type de crédit demandé
        conseiller (str): Nom du conseiller en charge du dossier
        pieces_jointes (list): Liste des chemins des fichiers à joindre (optionnel)
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    # Créer le message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = destinataire
    msg['Subject'] = f"Prise en charge de votre demande de {type_credit} - Réf: {reference}"
    
    # Date actuelle formatée
    date_actuelle = datetime.datetime.now().strftime("%d/%m/%Y")
    
    # Corps du message
    texte = f"""
    Bonjour {nom_client},
    
    Nous accusons réception de votre demande de {type_credit} soumise le {date_actuelle}.
    
    Votre demande portant la référence {reference} a été prise en charge par notre équipe. Votre conseiller dédié, {conseiller}, analysera votre dossier dans les meilleurs délais.
    
    Vous serez contacté(e) prochainement pour la suite du traitement de votre dossier. N'hésitez pas à nous contacter si vous avez des questions.
    
    Nous vous remercions de votre confiance.
    
    Cordialement,
    {conseiller}
    Conseiller crédit
    Service client - Banque Crédit
    Tel: +212 5XX-XXX-XXX
    """
    
    # Ajouter le corps du message
    msg.attach(MIMEText(texte, 'plain'))
    
    # Ajouter les pièces jointes éventuelles
    if pieces_jointes:
        for fichier in pieces_jointes:
            if os.path.isfile(fichier):
                with open(fichier, 'rb') as f:
                    partie = MIMEApplication(f.read(), Name=os.path.basename(fichier))
                partie['Content-Disposition'] = f'attachment; filename="{os.path.basename(fichier)}"'
                msg.attach(partie)
    
    # Essayer d'envoyer l'email
    try:
        # Connexion au serveur SMTP
        serveur = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        serveur.starttls()  # Sécuriser la connexion
        serveur.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Envoyer l'email
        texte_email = msg.as_string()
        serveur.sendmail(EMAIL_FROM, destinataire, texte_email)
        
        # Fermer la connexion
        serveur.quit()
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False

def envoyer_email_notification_statut(destinataire, nom_client, reference, type_credit, statut, commentaire=None):
    """
    Envoie un email de notification de changement de statut au client
    
    Args:
        destinataire (str): Adresse email du destinataire
        nom_client (str): Nom du client
        reference (str): Référence de la demande
        type_credit (str): Type de crédit demandé
        statut (str): Nouveau statut de la demande
        commentaire (str): Commentaire éventuel sur le statut
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    # Créer le message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = destinataire
    
    # Objet selon le statut
    if statut == "Accepté":
        msg['Subject'] = f"Bonne nouvelle ! Votre demande de {type_credit} a été acceptée - Réf: {reference}"
    elif statut == "Refusé":
        msg['Subject'] = f"Suivi de votre demande de {type_credit} - Réf: {reference}"
    else:
        msg['Subject'] = f"Mise à jour de votre demande de {type_credit} - Réf: {reference}"
    
    # Date actuelle formatée
    date_actuelle = datetime.datetime.now().strftime("%d/%m/%Y")
    
    # Corps du message selon le statut
    if statut == "Accepté":
        texte = f"""
        Bonjour {nom_client},
        
        Nous avons le plaisir de vous informer que votre demande de {type_credit} (référence {reference}) a été ACCEPTÉE.
        
        Un conseiller vous contactera très prochainement pour finaliser votre dossier et organiser la signature du contrat.
        """
        if commentaire:
            texte += f"\n\nInformations complémentaires: {commentaire}"
    
    elif statut == "Refusé":
        texte = f"""
        Bonjour {nom_client},
        
        Nous vous informons que suite à l'étude de votre dossier, nous ne sommes malheureusement pas en mesure de donner une suite favorable à votre demande de {type_credit} (référence {reference}).
        """
        if commentaire:
            texte += f"\n\nMotif: {commentaire}"
        texte += "\n\nNous restons à votre disposition pour étudier d'autres solutions adaptées à votre situation."
    
    elif statut == "Demande de documents complémentaires":
        texte = f"""
        Bonjour {nom_client},
        
        Dans le cadre de l'étude de votre demande de {type_credit} (référence {reference}), nous avons besoin de documents complémentaires.
        
        {commentaire if commentaire else 'Veuillez nous contacter pour plus de détails.'}
        
        Vous pouvez nous transmettre ces documents en répondant à cet email ou en vous connectant à votre espace client.
        """
    
    else:  # Autres statuts
        texte = f"""
        Bonjour {nom_client},
        
        Nous vous informons que le statut de votre demande de {type_credit} (référence {reference}) a été mis à jour vers: {statut}.
        """
        if commentaire:
            texte += f"\n\nCommentaire: {commentaire}"
    
    # Fin commune
    texte += f"""
    
    Pour toute question relative à votre dossier, n'hésitez pas à nous contacter en mentionnant votre référence {reference}.
    
    Nous vous remercions de votre confiance.
    
    Cordialement,
    Service crédit
    Banque Crédit
    Tel: +212 5XX-XXX-XXX
    """
    
    # Ajouter le corps du message
    msg.attach(MIMEText(texte, 'plain'))
    
    # Essayer d'envoyer l'email
    try:
        # Connexion au serveur SMTP
        serveur = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        serveur.starttls()  # Sécuriser la connexion
        serveur.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Envoyer l'email
        texte_email = msg.as_string()
        serveur.sendmail(EMAIL_FROM, destinataire, texte_email)
        
        # Fermer la connexion
        serveur.quit()
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False