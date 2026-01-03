import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
import time
from datetime import datetime, timedelta
from api_client import api_client

# Page Config
st.set_page_config(page_title="IntelliDoc AI - Système de Gestion", layout="wide", page_icon="📄")

# 1. Initialize Cookie Manager with a STABLE, UNIQUE key
cookie_manager = stx.CookieManager(key="intellidoc_v7_final")

def login_page():
    st.markdown("## 🔑 Connexion")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter")
        
        if submit:
            res, status_code = api_client.login(email, password)
            if status_code == 200:
                st.session_state.logged_in = True
                st.session_state.user = res['user']
                st.session_state.token = res['access_token']
                
                # Persistence (30 days)
                expires = datetime.now() + timedelta(days=30)
                cookie_manager.set('jwt_token', res['access_token'], expires_at=expires, path='/', key="set_token_login")
                
                st.success("Connexion réussie ! Chargement de votre espace...")
                time.sleep(0.7) # Allow browser some time to write the cookie
                st.rerun()
            else:
                st.error(f"Erreur : {res.get('detail', 'Identifiants incorrects')}")

# --- UI STYLES ---
RESULT_BOX_CSS = """
<style>
    .extraction-container {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    .extraction-header {
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 15px;
        color: #2c3e50;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .extraction-text {
        font-family: 'Courier New', Courier, monospace;
        color: #34495e;
        line-height: 1.6;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    .badge {
        background-color: #3498db;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
    }
</style>
"""

def dashboard_page():
    st.markdown(RESULT_BOX_CSS, unsafe_allow_html=True)
    st.title(f"🚀 Tableau de Bord - {st.session_state.user['nom']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📤 Upload de Document")
        uploaded_file = st.file_uploader("Choisir une image pour analyse OCR/IA", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            if st.button("Lancer l'analyse intelligente"):
                with st.spinner("Analyse en cours..."):
                    res, status_code = api_client.upload_document(
                        st.session_state.token, 
                        uploaded_file.read(), 
                        uploaded_file.name
                    )
                    if status_code == 200:
                        st.success(f"Analyse terminée avec succès !")
                        
                        # Beautiful Result Box
                        st.markdown(f"""
                            <div class="extraction-container">
                                <div class="extraction-header">
                                    <span>📄 Texte Extrait</span>
                                    <span class="badge">{res['category']} ({int(res['confidence']*100)}%)</span>
                                </div>
                                <div class="extraction-text">{res['text']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Erreur serveur : {res.get('detail', 'Inconnu')}")

    with col2:
        st.subheader("📊 Votre Activité")
        stats, _ = api_client.get_stats(st.session_state.token)
        if stats:
            df = pd.DataFrame(stats)
            st.bar_chart(df.set_index('categorie'))

def library_page():
    st.title("📁 Bibliothèque")
    docs, _ = api_client.get_documents(st.session_state.token)
    if docs:
        df = pd.DataFrame(docs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun document enregistré.")

def main():
    # 2. State Initialization
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'sync_attempts' not in st.session_state:
        st.session_state.sync_attempts = 0
    if 'sync_complete' not in st.session_state:
        st.session_state.sync_complete = False

    # 3. DEFINITIVE SESSION SYNCHRONIZATION
    if not st.session_state.logged_in and not st.session_state.sync_complete:
        cookies = cookie_manager.get_all()
        
        # Phase A: Wait for component to load
        if cookies is None:
            st.markdown("""
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column;">
                    <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite;"></div>
                    <h3 style="margin-top: 20px; color: #34495e; font-family: sans-serif;">Synchronisation de sécurité...</h3>
                    <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
                </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        # Phase B: Grab Token & Retry loop
        token = cookies.get('jwt_token')
        
        if not token or token == "LOGOUT":
            if st.session_state.sync_attempts < 10:
                st.session_state.sync_attempts += 1
                time.sleep(0.2)
                st.rerun()
            else:
                # No token found after retries -> show login
                st.session_state.sync_complete = True
                st.rerun()
        else:
            # Token found! Validate with Backend
            user_data, status_code = api_client.get_me(token)
            if status_code == 200:
                st.session_state.logged_in = True
                st.session_state.user = user_data
                st.session_state.token = token
            else:
                # Invalid/Expired token -> Clear it
                cookie_manager.set('jwt_token', 'LOGOUT', expires_at=datetime.now() - timedelta(days=1), path='/', key="clear_invalid_token_sync")
            
            st.session_state.sync_complete = True
            st.rerun()

    # 4. NAVIGATION / ROUTING
    if not st.session_state.logged_in:
        login_page()
    else:
        # Side Menu
        st.sidebar.title("IntelliDoc AI")
        menu = st.sidebar.radio("Navigation", ["Tableau de bord", "Bibliothèque"])
        
        # Dedicated Logout Button (Prevents refresh loop bugs)
        st.sidebar.markdown("---")
        if st.sidebar.button("Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.sync_complete = True
            st.session_state.sync_attempts = 0
            
            # Clear cookie permanently
            past = datetime.now() - timedelta(days=7)
            cookie_manager.set('jwt_token', 'LOGOUT', expires_at=past, path='/', key="logout_action_v7")
            
            st.info("Déconnexion en cours...")
            time.sleep(0.6)
            st.rerun()

        # Render Pages
        if menu == "Tableau de bord":
            dashboard_page()
        elif menu == "Bibliothèque":
            library_page()

if __name__ == "__main__":
    main()
