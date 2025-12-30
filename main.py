import streamlit as st
import pandas as pd
import bcrypt
import os
from datetime import datetime
from database_manager import db_manager
from ocr_engine import ocr_engine
from classifier import classifier
from styles import apply_custom_styles, card
import io
import extra_streamlit_components as stx

# Initialize Cookie Manager
cookie_manager = stx.CookieManager()

# Page Config
st.set_page_config(page_title="IntelliDoc System", layout="wide", page_icon="📄")
apply_custom_styles()

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Auto-login from cookie
if not st.session_state.logged_in:
    user_id_cookie = cookie_manager.get('user_id')
    if user_id_cookie:
        user = db_manager.execute_query("SELECT * FROM Utilisateurs WHERE id_user = %s", (user_id_cookie,))
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user[0]

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_page():
    st.markdown('<div class="main-header">🔑 Connexion au Système</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            
            if submit:
                user = db_manager.execute_query("SELECT * FROM Utilisateurs WHERE email = %s", (email,))
                if user and check_password(password, user[0]['mot_de_passe_hash']):
                    st.session_state.logged_in = True
                    st.session_state.user = user[0]
                    # Set cookie for persistence (expires in 30 days)
                    cookie_manager.set('user_id', str(user[0]['id_user']), key="set_user_id")
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect.")
        
        st.info("👋 Nouveau ? Contactez l'administrateur.")
        # Shortcut for testing
        if st.button("Mode Démo (Créer Admin)"):
            hashed = hash_password("admin123")
            db_manager.execute_query("INSERT IGNORE INTO Utilisateurs (nom, email, mot_de_passe_hash, role) VALUES (%s, %s, %s, %s)", 
                                    ("Admin", "admin@example.com", hashed, "admin"))
            st.success("Admin créé: admin@example.com / admin123")

def dashboard_page():
    st.markdown(f'<div class="main-header">📊 Tableau de Bord - Bienvenue {st.session_state.user["nom"]}</div>', unsafe_allow_html=True)
    
    # Stats row
    count_docs = db_manager.execute_query("SELECT COUNT(*) as total FROM Documents WHERE id_user = %s", (st.session_state.user['id_user'],))[0]['total']
    categories_counts = db_manager.execute_query("SELECT categorie, COUNT(*) as nb FROM Documents WHERE id_user = %s GROUP BY categorie", (st.session_state.user['id_user'],))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
        <div class="stat-item">
            <div class="stat-value">{count_docs}</div>
            <div class="stat-label">Documents Totaux</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Quick Upload
    st.divider()
    st.subheader("📤 Upload Rapide")
    uploaded_file = st.file_uploader("Choisir un document (Image)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        if st.button("Lancer l'analyse"):
            with st.spinner("OCR en cours..."):
                file_bytes = uploaded_file.read()
                text, error = ocr_engine.extract_from_bytes(file_bytes)
                
                if error:
                    st.error(f"Erreur OCR: {error}")
                else:
                    with st.spinner("Classification en cours..."):
                        cat, conf = classifier.classify(text)
                        
                        # Save to DB
                        os.makedirs('uploads', exist_ok=True)
                        save_path = os.path.join('uploads', uploaded_file.name)
                        with open(save_path, 'wb') as f:
                            f.write(file_bytes)
                        
                        db_manager.execute_query("""
                            INSERT INTO Documents (id_user, nom_fichier, chemin_fichier, texte_extrait, categorie, score_confiance)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (st.session_state.user['id_user'], uploaded_file.name, save_path, text, cat, conf))
                        
                        st.success(f"Analyse terminée ! Catégorie: **{cat}** (Confiance: {conf*100:.1f}%)")
                        with st.expander("Voir le texte extrait"):
                            st.write(text)

def library_page():
    st.markdown('<div class="main-header">📁 Bibliothèque de Documents</div>', unsafe_allow_html=True)
    
    search_query = st.text_input("Rechercher dans les documents...")
    docs = db_manager.execute_query("""
        SELECT id_document, nom_fichier, categorie, score_confiance, date_upload 
        FROM Documents 
        WHERE id_user = %s AND (nom_fichier LIKE %s OR texte_extrait LIKE %s)
        ORDER BY date_upload DESC
    """, (st.session_state.user['id_user'], f'%{search_query}%', f'%{search_query}%'))
    
    if docs:
        df = pd.DataFrame(docs)
        st.dataframe(df, use_container_width=True)
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter en CSV", data=csv, file_name="export_docs.csv", mime="text/csv")
    else:
        st.info("Aucun document trouvé.")

def stats_page():
    st.markdown('<div class="main-header">📈 Statistiques de Classification</div>', unsafe_allow_html=True)
    
    res = db_manager.execute_query("""
        SELECT categorie, COUNT(*) as nb 
        FROM Documents 
        WHERE id_user = %s 
        GROUP BY categorie
    """, (st.session_state.user['id_user'],))
    
    if res:
        df = pd.DataFrame(res)
        st.bar_chart(df.set_index('categorie'))
        
        st.subheader("Répartition détaillée")
        col1, col2 = st.columns(2)
        with col1:
            st.table(df)
    else:
        st.info("Données insuffisantes pour les statistiques.")

def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.title("🚀 IntelliDoc AI")
        menu = st.sidebar.radio("Navigation", ["Tableau de bord", "Bibliothèque", "Statistiques", "Déconnexion"])
        
        if menu == "Tableau de bord":
            dashboard_page()
        elif menu == "Bibliothèque":
            library_page()
        elif menu == "Statistiques":
            stats_page()
        elif menu == "Déconnexion":
            st.session_state.logged_in = False
            st.session_state.user = None
            cookie_manager.delete('user_id', key="delete_user_id")
            st.rerun()

if __name__ == "__main__":
    main()
