# Octroi de Credit - Application de Gestion de Credits Bancaires

Application Streamlit pour la gestion des demandes de credit bancaire avec analyse automatique de documents par OCR.

## Fonctionnalites

### Interface Client (Formulaires)
- **Credit Automobile** - Simulation et demande de financement vehicule
- **Credit Immobilier** - Demande de pret immobilier
- **Credit Consommation** - Financement de projets personnels
- **Decouvert Bancaire** - Demande de facilite de caisse

### Interface Administration
- **Dashboard** - Tableau de bord avec statistiques et graphiques
- **Gestion des Credits** - Suivi et traitement des demandes par type
- **Gestion des Clients** - Vue centralisee des clients et leurs demandes
- **Traitement OCR** - Analyse automatique des documents

### Module OCR (agent_OCR)
- Extraction automatique d'informations des documents (CIN, bulletins de salaire, releves bancaires)
- Verification de concordance entre documents
- Generation de rapports d'analyse (TXT, JSON, PDF)
- Score de confiance et recommandations

## Structure du Projet

```
Octroi-Credit/
├── backend/                    # Logique metier
│   ├── __init__.py
│   ├── config.py              # Configuration et constantes
│   ├── auth.py                # Authentification admin
│   ├── utils.py               # Fonctions utilitaires
│   ├── services/              # Services metier
│   │   ├── calcul.py          # Calculs financiers (mensualites, amortissement)
│   │   ├── validations.py     # Validations (email, telephone, CIN)
│   │   └── fichiers.py        # Gestion des fichiers
│   └── agent_OCR/             # Module d'analyse OCR
│       ├── models.py          # Modeles Pydantic (State, DocumentInfo)
│       ├── workflow.py        # Workflow LangGraph
│       ├── extraction.py      # Extraction OCR avec OpenAI GPT-4
│       ├── concordance.py     # Verification de concordance
│       ├── rapport.py         # Generation de rapports
│       ├── charger_document.py # Chargement et conversion PDF
│       ├── utils.py           # Utilitaires OCR
│       └── main.py            # Point d'entree OCR
│
├── frontend/                   # Interface utilisateur Streamlit
│   ├── __init__.py
│   ├── admin_main.py          # Orchestrateur interface admin
│   ├── main_forms.py          # Application formulaires clients
│   ├── pages/                 # Pages de l'interface admin
│   │   ├── dashboard.py       # Tableau de bord
│   │   ├── gestion_credits.py # Gestion des demandes
│   │   ├── gestion_clients.py # Gestion des clients
│   │   └── traitement_documents.py # Traitement OCR
│   └── forms/                 # Formulaires de demande
│       ├── credit_auto/       # Credit automobile
│       ├── credit_immo/       # Credit immobilier
│       ├── credit_conso/      # Credit consommation
│       └── credit_decouvert/  # Decouvert bancaire
│
├── data/                       # Donnees de l'application
│   └── demandes_clients/      # Dossiers des demandes
│       ├── auto/
│       ├── immo/
│       ├── conso/
│       └── decouvert/
│
├── run_admin.py               # Point d'entree - Interface admin
├── run_forms.py               # Point d'entree - Formulaires clients
├── requirements.txt           # Dependances Python
└── README.md
```

## Installation

### Prerequis
- Python 3.8 ou superieur
- pip (gestionnaire de paquets Python)

### Installation des dependances

```bash
# Cloner le projet
git clone <url-du-repo>
cd Octroi-Credit

# Creer un environnement virtuel (recommande)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dependances de base
pip install -r requirements.txt
```

### Installation du module OCR (optionnel)

Pour activer l'analyse automatique des documents, installez les dependances supplementaires:

```bash
pip install langgraph openai python-dotenv PyMuPDF reportlab Pillow
```

Configurez votre cle API OpenAI dans un fichier `.env`:

```env
OPENAI_API_KEY=votre_cle_api_openai
```

## Utilisation

### Lancer l'interface client (Formulaires)

```bash
streamlit run run_forms.py
```

Acces: http://localhost:8501

### Lancer l'interface administration

```bash
streamlit run run_admin.py
```

Acces: http://localhost:8501

**Identifiants par defaut:**
| Utilisateur | Mot de passe | Role |
|-------------|--------------|------|
| admin | adminpass | Administrateur |
| superviseur | superpass | Superviseur |
| directeur | directorpass | Directeur |

## Configuration

Les parametres de l'application sont dans `backend/config.py`:

```python
# Limites des credits
AUTO_MONTANT_MAX = 2000000      # Credit auto max
IMMO_MONTANT_MAX = 10000000     # Credit immo max
CONSO_MONTANT_MAX = 300000      # Credit conso max
DECOUVERT_MONTANT_MAX = 50000   # Decouvert max

# Taux d'endettement
ENDETTEMENT_MAX = 40            # Maximum autorise (%)
ENDETTEMENT_RECOMMANDE = 33     # Recommande (%)

# Taux d'interet par defaut
AUTO_TAUX_DEFAUT = 4.5
IMMO_TAUX_DEFAUT = 3.5
CONSO_TAUX_DEFAUT = 6.5
```

## Fonctionnement du Module OCR

### Workflow d'analyse

1. **Chargement** - Lecture des PDFs du dossier client
2. **Validation** - Verification de l'integrite des fichiers
3. **Conversion** - Transformation PDF vers images (PyMuPDF)
4. **Extraction** - Analyse OCR avec GPT-4 Vision
5. **Concordance** - Verification de coherence entre documents
6. **Rapport** - Generation des rapports d'analyse

### Types de documents supportes

- CIN (Carte d'Identite Nationale)
- Passeport
- Bulletins de salaire
- Releves bancaires
- Factures (electricite, eau)
- Justificatifs de domicile

### Informations extraites

- Nom et prenom
- Date de naissance
- Adresse complete
- Numeros de documents
- Dates d'emission/expiration
- Montants (salaires, soldes)

## Technologies Utilisees

| Technologie | Utilisation |
|-------------|-------------|
| **Streamlit** | Interface web |
| **Pandas** | Manipulation de donnees |
| **Plotly** | Graphiques interactifs |
| **Matplotlib** | Visualisations |
| **Pydantic** | Validation de donnees |
| **FPDF** | Generation PDF formulaires |
| **ReportLab** | Generation PDF rapports OCR |
| **LangGraph** | Orchestration workflow OCR |
| **OpenAI GPT-4** | Extraction OCR |
| **PyMuPDF** | Traitement PDF |

## Securite

- Authentification requise pour l'interface admin
- Gestion des roles (Administrateur, Superviseur, Directeur)
- Donnees stockees localement dans le dossier `data/`

**Important:** En production, remplacez:
- Les mots de passe par defaut
- Le stockage local par une base de donnees securisee
- Ajoutez le chiffrement des donnees sensibles

## Contribution

1. Fork le projet
2. Creez votre branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos modifications (`git commit -m 'Ajout nouvelle fonctionnalite'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT.

## Support

Pour toute question ou probleme, ouvrez une issue sur le repository.
