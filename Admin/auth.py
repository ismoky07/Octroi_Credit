"""
admin/auth.py - Gestion de l'authentification pour l'interface d'administration
"""
import streamlit as st

def gerer_authentification():
    """
    Gère l'authentification de l'administrateur
    
    Returns:
        bool: True si authentifié, False sinon
    """
    # Initialiser l'état d'authentification
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    # Si déjà authentifié, retourner True
    if st.session_state.admin_authenticated:
        return True
    
    # Afficher l'interface de connexion
    afficher_interface_connexion()
    return False

def afficher_interface_connexion():
    """Affiche l'interface de connexion pour l'administrateur"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🔐 Authentification Administrateur</h2>
        <p>Veuillez vous identifier pour accéder à l'interface d'administration</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### 🏦 Connexion Sécurisée")
            
            # Formulaire de connexion
            with st.form("form_login"):
                username = st.text_input(
                    "👤 Identifiant", 
                    placeholder="Votre identifiant administrateur"
                )
                password = st.text_input(
                    "🔒 Mot de passe", 
                    type="password",
                    placeholder="Votre mot de passe"
                )
                
                col_login1, col_login2 = st.columns(2)
                
                with col_login1:
                    if st.form_submit_button("🚀 Se connecter", use_container_width=True):
                        if valider_credentials(username, password):
                            st.session_state.admin_authenticated = True
                            st.success("✅ Connexion réussie!")
                            st.rerun()
                        else:
                            st.error("❌ Identifiant ou mot de passe incorrect")
                
                with col_login2:
                    if st.form_submit_button("🔄 Réinitialiser", use_container_width=True):
                        st.rerun()
            
            # Informations de sécurité
            with st.expander("🛡️ Informations de sécurité"):
                st.info("""
                **Sécurité de l'accès :**
                - Utilisez un mot de passe fort
                - Ne partagez pas vos identifiants
                - Déconnectez-vous après utilisation
                - Accès limité aux administrateurs autorisés
                """)

def valider_credentials(username, password):
    """
    Valide les identifiants de connexion
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe
        
    Returns:
        bool: True si valide, False sinon
    """
    # Configuration des comptes administrateurs
    # IMPORTANT: En production, utilisez une base de données sécurisée !
    comptes_admin = {
        "admin": "adminpass",
        "superviseur": "superpass",
        "directeur": "directorpass"
    }
    
    # Vérification des identifiants
    if username in comptes_admin and comptes_admin[username] == password:
        # Stocker des informations sur l'utilisateur connecté
        st.session_state.admin_user = username
        st.session_state.admin_role = get_role_utilisateur(username)
        return True
    
    return False

def get_role_utilisateur(username):
    """
    Détermine le rôle de l'utilisateur connecté
    
    Args:
        username (str): Nom d'utilisateur
        
    Returns:
        str: Rôle de l'utilisateur
    """
    roles = {
        "admin": "Administrateur",
        "superviseur": "Superviseur",
        "directeur": "Directeur"
    }
    
    return roles.get(username, "Utilisateur")

def verifier_permissions(action_requise):
    """
    Vérifie si l'utilisateur connecté a les permissions pour une action
    
    Args:
        action_requise (str): Action à vérifier
        
    Returns:
        bool: True si autorisé, False sinon
    """
    if not st.session_state.get("admin_authenticated", False):
        return False
    
    role = st.session_state.get("admin_role", "")
    
    # Définir les permissions par rôle
    permissions = {
        "Directeur": ["all"],  # Toutes les permissions
        "Superviseur": ["view", "edit", "process"],  # Voir, éditer, traiter
        "Administrateur": ["view", "edit"]  # Voir et éditer uniquement
    }
    
    user_permissions = permissions.get(role, [])
    
    return "all" in user_permissions or action_requise in user_permissions

def afficher_info_utilisateur():
    """Affiche les informations de l'utilisateur connecté dans la sidebar"""
    if st.session_state.get("admin_authenticated", False):
        st.sidebar.markdown(f"""
        **👤 Connecté en tant que :**  
        {st.session_state.get('admin_user', 'Inconnu')}
        
        **🎭 Rôle :**  
        {st.session_state.get('admin_role', 'Inconnu')}
        """)

def deconnecter_utilisateur():
    """Déconnecte l'utilisateur actuel"""
    keys_to_remove = [
        "admin_authenticated", 
        "admin_user", 
        "admin_role"
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]