import os
import json
from typing import Dict, List
from models import DocumentInfo, State
from utilsAgentOCR import safe_print

# NOUVELLES IMPORTS POUR LE PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

def generer_rapport_complet(infos_documents: Dict[str, DocumentInfo], 
                           concordance: bool, 
                           problemes_concordance: List[str],
                           state: State = None,
                           analyse_detaillee: Dict = None) -> str:
    """
    Génère un rapport complet des résultats d'analyse - VERSION ADAPTÉE
    
    Args:
        infos_documents: Dict des DocumentInfo (compatible nouveau système)
        concordance: Boolean de concordance
        problemes_concordance: Liste des problèmes
        state: État du workflow (optionnel)
        analyse_detaillee: Analyse détaillée de concordance (nouveau)
    """
    rapport = "RAPPORT D'ANALYSE DE DOCUMENTS\n"
    rapport += "============================\n\n"
    
    # 1. Résumé exécutif
    rapport += "RÉSUMÉ EXÉCUTIF\n"
    rapport += "-" * 15 + "\n"
    rapport += f"Nombre de documents analysés: {len(infos_documents)}\n"
    rapport += f"Concordance des informations: {'✅ OUI' if concordance else '❌ NON'}\n"
    
    if not concordance:
        rapport += f"Nombre de problèmes détectés: {len(problemes_concordance)}\n"
    
    # Informations détaillées sur l'analyse (nouveau)
    if analyse_detaillee:
        rapport += f"Score de confiance: {analyse_detaillee.get('score_confiance', 0):.1f}/100\n"
        
        # Statistiques par type d'information
        stats = [
            ("Documents avec nom", analyse_detaillee.get('documents_avec_nom', 0)),
            ("Documents avec prénom", analyse_detaillee.get('documents_avec_prenom', 0)),
            ("Documents avec adresse", analyse_detaillee.get('documents_avec_adresse', 0)),
            ("Documents avec CIN", analyse_detaillee.get('documents_avec_cin', 0))
        ]
        
        rapport += "\nStatistiques d'extraction:\n"
        for desc, count in stats:
            rapport += f"• {desc}: {count}\n"
    
    # Ajouter les statistiques du workflow si disponibles
    if state:
        rapport += f"PDFs traités: {state.nb_pdfs_traites}\n"
        rapport += f"PDFs rejetés: {state.nb_pdfs_rejetes}\n"
        rapport += f"Images générées: {state.nb_images_generees}\n"
        if state.temps_execution:
            rapport += f"Temps d'exécution: {state.temps_execution:.2f} secondes\n"
    
    rapport += "\n"
    
    # 2. Détails des documents
    rapport += "DÉTAILS DES DOCUMENTS\n"
    rapport += "-" * 20 + "\n"
    
    for chemin, info in infos_documents.items():
        rapport += f"\n📄 Document: {os.path.basename(chemin)}\n"
        rapport += f"   Type: {info.type_document}\n"
        
        if info.nom:
            rapport += f"   Nom: {info.nom}\n"
        if info.prenom:
            rapport += f"   Prénom: {info.prenom}\n"
        if info.date_naissance:
            rapport += f"   Date de naissance: {info.date_naissance}\n"
        if info.adresse:
            rapport += f"   Adresse: {info.adresse}\n"
        if info.numero_document:
            rapport += f"   Numéro: {info.numero_document}\n"
        if info.date_emission:
            rapport += f"   Date d'émission: {info.date_emission}\n"
        if info.date_expiration:
            rapport += f"   Date d'expiration: {info.date_expiration}\n"
        
        # Informations de qualité d'extraction (nouveau)
        if info.autres_infos:
            qualite_image = info.autres_infos.get("qualite_image")
            confiance_classification = info.autres_infos.get("confiance_classification")
            
            if qualite_image or confiance_classification:
                rapport += "   Qualité d'extraction:\n"
                if qualite_image:
                    rapport += f"     • Qualité image: {qualite_image}\n"
                if confiance_classification:
                    rapport += f"     • Confiance classification: {confiance_classification}\n"
            
            # Autres informations
            autres_infos_filtrees = {k: v for k, v in info.autres_infos.items() 
                                   if k not in ["qualite_image", "confiance_classification", "observations"]}
            
            if autres_infos_filtrees:
                rapport += "   Autres informations:\n"
                for cle, valeur in autres_infos_filtrees.items():
                    rapport += f"     • {cle}: {valeur}\n"
    
    # 3. Analyse de concordance détaillée
    rapport += f"\nANALYSE DE CONCORDANCE\n"
    rapport += "-" * 20 + "\n"
    
    if concordance:
        rapport += "✅ Toutes les informations concordent entre les documents.\n"
        rapport += "Les données personnelles sont cohérentes à travers tous les documents analysés.\n"
    else:
        rapport += "❌ Des problèmes de concordance ont été détectés:\n\n"
        for i, probleme in enumerate(problemes_concordance, 1):
            rapport += f"{i}. {probleme}\n"
    
    # Analyse détaillée (nouveau)
    if analyse_detaillee and analyse_detaillee.get('recommandations'):
        rapport += f"\nRecommandations d'amélioration:\n"
        for recommandation in analyse_detaillee['recommandations']:
            rapport += f"• {recommandation}\n"
    
    # 4. Recommandations
    rapport += f"\nRECOMMANDATIONS\n"
    rapport += "-" * 15 + "\n"
    
    if concordance:
        score = analyse_detaillee.get('score_confiance', 100) if analyse_detaillee else 100
        
        if score >= 90:
            rapport += "✅ DOSSIER EXCELLENT\n"
            rapport += "Le dossier est de très haute qualité. Traitement automatique recommandé.\n"
        elif score >= 70:
            rapport += "✅ DOSSIER VALIDE\n"
            rapport += "Le dossier est complet et cohérent. Tous les documents peuvent être utilisés en confiance.\n"
        else:
            rapport += "⚠️ DOSSIER VALIDE AVEC RÉSERVES\n"
            rapport += "Le dossier est cohérent mais la qualité d'extraction peut être améliorée.\n"
    else:
        rapport += "⚠️ VÉRIFICATION MANUELLE REQUISE\n"
        rapport += "Des incohérences ont été détectées. Il est recommandé de:\n"
        rapport += "• Vérifier manuellement les documents présentant des discordances\n"
        rapport += "• Demander des documents de remplacement si nécessaire\n"
        rapport += "• Contacter le demandeur pour clarification\n"
    
    # 5. Erreurs rencontrées (si state disponible)
    if state and state.erreurs_rencontrees:
        rapport += f"\nERREURS TECHNIQUES RENCONTRÉES\n"
        rapport += "-" * 30 + "\n"
        for erreur in state.erreurs_rencontrees:
            rapport += f"• {erreur}\n"
    
    # 6. Pied de page
    rapport += f"\n" + "="*50 + "\n"
    rapport += "Rapport généré automatiquement par le système d'analyse de documents\n"
    rapport += f"Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return rapport

def sauvegarder_rapport_json(infos_documents: Dict[str, DocumentInfo], 
                            concordance: bool, 
                            problemes_concordance: List[str],
                            output_path: str,
                            analyse_detaillee: Dict = None,
                            resultats_ocr: Dict = None):
    """
    Sauvegarde les résultats en format JSON - VERSION ADAPTÉE
    
    Args:
        infos_documents: Dict des DocumentInfo
        concordance: Boolean de concordance  
        problemes_concordance: Liste des problèmes
        output_path: Chemin de sortie
        analyse_detaillee: Analyse détaillée (nouveau)
        resultats_ocr: Résultats bruts OCR (nouveau)
    """
    try:
        # Convertir les informations en format JSON-compatible
        donnees_json = {
            "resume": {
                "nombre_documents": len(infos_documents),
                "concordance": concordance,
                "nombre_problemes": len(problemes_concordance),
                "score_confiance": analyse_detaillee.get('score_confiance', 0) if analyse_detaillee else 0
            },
            "documents": {},
            "problemes_concordance": problemes_concordance,
            "analyse_detaillee": analyse_detaillee or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Ajouter les résultats OCR détaillés (nouveau)
        if resultats_ocr:
            donnees_json["details_extraction"] = {}
            for chemin, resultat in resultats_ocr.items():
                nom_fichier = os.path.basename(chemin)
                donnees_json["details_extraction"][nom_fichier] = {
                    "mode_extraction": resultat.get("mode", "NORMAL"),
                    "qualite": resultat.get("qualite", {}),
                    "extraction_brute": resultat.get("extraction_brute", "")
                }
        
        for chemin, info in infos_documents.items():
            nom_fichier = os.path.basename(chemin)
            donnees_json["documents"][nom_fichier] = {
                "type_document": info.type_document,
                "nom": info.nom,
                "prenom": info.prenom,
                "date_naissance": info.date_naissance,
                "numero_document": info.numero_document,
                "adresse": info.adresse,
                "date_emission": info.date_emission,
                "date_expiration": info.date_expiration,
                "autres_infos": info.autres_infos
            }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(donnees_json, f, ensure_ascii=False, indent=2)
        
        safe_print(f"Rapport JSON sauvegardé: {output_path}")
        return True
        
    except Exception as e:
        safe_print(f"Erreur lors de la sauvegarde JSON: {str(e)}")
        return False

def generer_rapport_pdf(infos_documents: Dict[str, DocumentInfo], 
                       concordance: bool, 
                       problemes_concordance: List[str],
                       state: State = None,
                       ref_demande: str = "N/A",
                       analyse_detaillee: Dict = None) -> bytes:
    """
    Génère un rapport PDF professionnel - VERSION ADAPTÉE
    """
    try:
        # Créer un buffer en mémoire
        buffer = io.BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Styles personnalisés
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=TA_CENTER
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.darkgreen
        )
        
        # Contenu du rapport
        story = []
        
        # En-tête principal
        story.append(Paragraph("RAPPORT D'ANALYSE OCR", title_style))
        story.append(Paragraph(f"Demande: {ref_demande}", styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # === RÉSUMÉ EXÉCUTIF ===
        story.append(Paragraph("RÉSUMÉ EXÉCUTIF", section_style))
        
        data_resume = [
            ['Métrique', 'Valeur'],
            ['Documents analysés', str(len(infos_documents))],
            ['Concordance', "✅ OK" if concordance else "❌ Problèmes détectés"],
            ['Problèmes détectés', str(len(problemes_concordance))]
        ]
        
        # Ajouter le score de confiance (nouveau)
        if analyse_detaillee:
            score = analyse_detaillee.get('score_confiance', 0)
            data_resume.append(['Score de confiance', f"{score:.1f}/100"])
        
        # Ajouter les stats du workflow si disponibles
        if state:
            data_resume.extend([
                ['PDFs traités', str(state.nb_pdfs_traites)],
                ['PDFs rejetés', str(state.nb_pdfs_rejetes)],
                ['Images générées', str(state.nb_images_generees)]
            ])
            if state.temps_execution:
                data_resume.append(['Temps d\'exécution', f"{state.temps_execution:.2f}s"])
        
        table_resume = Table(data_resume, colWidths=[2*inch, 2*inch])
        table_resume.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table_resume)
        story.append(Spacer(1, 20))
        
        # === DOCUMENTS ANALYSÉS ===
        if infos_documents:
            story.append(Paragraph("DOCUMENTS ANALYSÉS", section_style))
            
            for chemin, info in infos_documents.items():
                nom_fichier = os.path.basename(chemin)
                story.append(Paragraph(f"📄 {nom_fichier}", styles['Heading3']))
                
                # Créer tableau des informations du document
                data_doc = []
                if info.type_document:
                    data_doc.append(['Type:', info.type_document])
                if info.nom:
                    data_doc.append(['Nom:', info.nom])
                if info.prenom:
                    data_doc.append(['Prénom:', info.prenom])
                if info.date_naissance:
                    data_doc.append(['Date naissance:', info.date_naissance])
                if info.numero_document:
                    data_doc.append(['Numéro:', info.numero_document])
                if info.adresse:
                    data_doc.append(['Adresse:', info.adresse])
                if info.date_emission:
                    data_doc.append(['Date émission:', info.date_emission])
                if info.date_expiration:
                    data_doc.append(['Date expiration:', info.date_expiration])
                
                # Ajouter informations de qualité (nouveau)
                if info.autres_infos:
                    qualite_image = info.autres_infos.get("qualite_image")
                    confiance = info.autres_infos.get("confiance_classification")
                    
                    if qualite_image:
                        data_doc.append(['Qualité image:', qualite_image])
                    if confiance:
                        data_doc.append(['Confiance:', confiance])
                
                if data_doc:
                    table_doc = Table(data_doc, colWidths=[1.5*inch, 3*inch])
                    table_doc.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(table_doc)
                
                story.append(Spacer(1, 15))
        
        # === ANALYSE DE CONCORDANCE ===
        story.append(Paragraph("ANALYSE DE CONCORDANCE", section_style))
        
        if concordance:
            story.append(Paragraph("✅ Toutes les informations concordent entre les documents.", styles['Normal']))
            story.append(Paragraph("Les données personnelles sont cohérentes à travers tous les documents analysés.", styles['Normal']))
        else:
            story.append(Paragraph("❌ Des problèmes de concordance ont été détectés:", styles['Normal']))
            story.append(Spacer(1, 10))
            for i, probleme in enumerate(problemes_concordance, 1):
                story.append(Paragraph(f"{i}. {probleme}", styles['Normal']))
        
        # Recommandations d'analyse détaillée (nouveau)
        if analyse_detaillee and analyse_detaillee.get('recommandations'):
            story.append(Spacer(1, 10))
            story.append(Paragraph("Recommandations d'amélioration:", styles['Heading4']))
            for recommandation in analyse_detaillee['recommandations']:
                story.append(Paragraph(f"• {recommandation}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # === RECOMMANDATIONS ===
        story.append(Paragraph("RECOMMANDATIONS", section_style))
        
        if concordance:
            score = analyse_detaillee.get('score_confiance', 100) if analyse_detaillee else 100
            
            if score >= 90:
                story.append(Paragraph("✅ DOSSIER EXCELLENT", styles['Heading3']))
                story.append(Paragraph("Le dossier est de très haute qualité. Traitement automatique recommandé.", styles['Normal']))
            elif score >= 70:
                story.append(Paragraph("✅ DOSSIER VALIDE", styles['Heading3']))
                story.append(Paragraph("Le dossier est complet et cohérent. Tous les documents peuvent être utilisés en confiance.", styles['Normal']))
            else:
                story.append(Paragraph("⚠️ DOSSIER VALIDE AVEC RÉSERVES", styles['Heading3']))
                story.append(Paragraph("Le dossier est cohérent mais la qualité d'extraction peut être améliorée.", styles['Normal']))
        else:
            story.append(Paragraph("⚠️ VÉRIFICATION MANUELLE REQUISE", styles['Heading3']))
            story.append(Paragraph("Des incohérences ont été détectées. Il est recommandé de:", styles['Normal']))
            story.append(Paragraph("• Vérifier manuellement les documents présentant des discordances", styles['Normal']))
            story.append(Paragraph("• Demander des documents de remplacement si nécessaire", styles['Normal']))
            story.append(Paragraph("• Contacter le demandeur pour clarification", styles['Normal']))
        
        # === ERREURS TECHNIQUES ===
        if state and state.erreurs_rencontrees:
            story.append(Spacer(1, 20))
            story.append(Paragraph("ERREURS TECHNIQUES RENCONTRÉES", section_style))
            for erreur in state.erreurs_rencontrees:
                story.append(Paragraph(f"• {erreur}", styles['Normal']))
        
        # === PIED DE PAGE ===
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 60, styles['Normal']))
        story.append(Paragraph(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
        story.append(Paragraph("Système d'analyse OCR automatique v2.0", styles['Normal']))
        
        # Générer le PDF
        doc.build(story)
        
        # Récupérer le contenu
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        safe_print(f"Erreur lors de la génération PDF: {str(e)}")
        return None

def sauvegarder_rapport_complet(infos_documents: Dict[str, DocumentInfo], 
                               concordance: bool, 
                               problemes_concordance: List[str],
                               output_dir: str,
                               state: State = None,
                               ref_demande: str = "N/A",
                               analyse_detaillee: Dict = None,
                               resultats_ocr: Dict = None):
    """
    Sauvegarde le rapport sous tous les formats - VERSION ADAPTÉE
    
    Args:
        infos_documents: Dictionnaire des informations
        concordance: Boolean de concordance
        problemes_concordance: Liste des problèmes
        output_dir: Répertoire de sortie
        state: État du workflow
        ref_demande: Référence de la demande
        analyse_detaillee: Analyse détaillée de concordance (nouveau)
        resultats_ocr: Résultats bruts OCR (nouveau)
    """
    try:
        # 1. Rapport texte
        rapport_texte = generer_rapport_complet(
            infos_documents, concordance, problemes_concordance, state, analyse_detaillee
        )
        chemin_txt = os.path.join(output_dir, "rapport_ocr.txt")
        with open(chemin_txt, "w", encoding='utf-8') as f:
            f.write(rapport_texte)
        safe_print(f"Rapport TXT sauvegardé: {chemin_txt}")
        
        # 2. Rapport JSON
        chemin_json = os.path.join(output_dir, "rapport_analyse.json")
        sauvegarder_rapport_json(
            infos_documents, concordance, problemes_concordance, 
            chemin_json, analyse_detaillee, resultats_ocr
        )
        
        # 3. Rapport PDF
        rapport_pdf = generer_rapport_pdf(
            infos_documents, concordance, problemes_concordance, 
            state, ref_demande, analyse_detaillee
        )
        if rapport_pdf:
            chemin_pdf = os.path.join(output_dir, "rapport_ocr.pdf")
            with open(chemin_pdf, "wb") as f:
                f.write(rapport_pdf)
            safe_print(f"Rapport PDF sauvegardé: {chemin_pdf}")
        
        return True
        
    except Exception as e:
        safe_print(f"Erreur lors de la sauvegarde complète: {str(e)}")
        return False