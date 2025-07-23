from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class DocumentInfo(BaseModel):
    """Modèle pour les informations extraites d'un document"""
    type_document: str = Field(description="Type du document (CIN, Passeport, Justificatif de domicile, etc.)")
    nom: Optional[str] = Field(description="Nom de la personne", default=None)
    prenom: Optional[str] = Field(description="Prénom de la personne", default=None)
    date_naissance: Optional[str] = Field(description="Date de naissance", default=None)
    numero_document: Optional[str] = Field(description="Numéro du document", default=None)
    adresse: Optional[str] = Field(description="Adresse complète", default=None)
    date_emission: Optional[str] = Field(description="Date d'émission du document", default=None)
    date_expiration: Optional[str] = Field(description="Date d'expiration du document", default=None)
    autres_infos: Dict = Field(description="Autres informations spécifiques au document", default_factory=dict)

class State(BaseModel):
    """État du workflow enrichi"""
    # Chemins et dossiers
    dossier_path: str
    pdf_paths: List[str] = Field(default_factory=list)
    pdfs_rejetes: List[str] = Field(default_factory=list)  # Nouveau
    images_paths: List[str] = Field(default_factory=list)
    
    # Données extraites
    documents_texte: Dict[str, str] = Field(default_factory=dict)
    infos_documents: Dict[str, DocumentInfo] = Field(default_factory=dict)
    
    # Résultats de concordance
    concordance: Optional[bool] = None
    problemes_concordance: List[str] = Field(default_factory=list)
    
    # Rapports et archivage - Nouveaux champs
    rapport_path: Optional[str] = Field(default=None)
    rapport_contenu: Optional[str] = Field(default=None)
    archive_path: Optional[str] = Field(default=None)
    
    # Statistiques - Nouveaux champs
    nb_pdfs_traites: int = Field(default=0)
    nb_pdfs_rejetes: int = Field(default=0)
    nb_images_generees: int = Field(default=0)  
    nb_documents_analyses: int = Field(default=0)
    
    # État du workflow - Nouveaux champs
    workflow_status: str = Field(default="INITIALISE")
    erreurs_rencontrees: List[str] = Field(default_factory=list)
    temps_execution: Optional[float] = Field(default=None)