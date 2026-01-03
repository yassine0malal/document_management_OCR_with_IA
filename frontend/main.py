import streamlit as st
import extra_streamlit_components as stx
import pandas as pd
import time
import io
from datetime import datetime, timedelta
from api_client import api_client
from PIL import Image

# Page Config
st.set_page_config(
    page_title="IntelliDoc AI - Gestion Documentaire Intelligente", 
    layout="wide", 
    page_icon="📄",
    initial_sidebar_state="expanded"
)

# --- HELPERS ---
def format_size(size_bytes):
    if size_bytes is None: return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

# 1. Initialize Cookie Manager with a STABLE, UNIQUE key
cookie_manager = stx.CookieManager(key="intellidoc_v7_final")

# --- MODERN UI STYLES ---
MODERN_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container */
    .main {
        background-color: #f8f9fc;
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        color: white;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #94a3b8;
    }

    /* Custom Cards */
    .st-emotion-cache-12w0qpk {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 1.5rem;
        background: white;
    }

    /* Status Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-success { background-color: #dcfce7; color: #166534; }
    .badge-warning { background-color: #fef9c3; color: #854d0e; }
    .badge-error { background-color: #fee2e2; color: #991b1b; }
    .badge-info { background-color: #e0f2fe; color: #075985; }

    /* Extraction Box */
    .extraction-container {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background: white;
        overflow: hidden;
        margin-top: 1.5rem;
    }
    .extraction-header {
        background-color: #f1f5f9;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 700;
        color: #334155;
    }
    .extraction-body {
        padding: 1.5rem;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.6;
        white-space: pre-wrap;
        max-height: 500px;
        overflow-y: auto;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }

    /* Learning Loop Info */
    .learning-loop {
        background-color: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #0369a1;
        border-radius: 0 8px 8px 0;
    }
    /* Buttons highlight */
    .landing-btn-primary {
        background-color: #3b82f6;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .landing-btn-primary:hover { transform: scale(1.05); }
</style>
"""

def login_page():
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
        st.title("📄 IntelliDoc AI")
        st.markdown("<p style='color: #64748b;'>Système de Gestion Intelligente des Documents</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### 🔑 Connexion")
            email = st.text_input("Adresse Email", placeholder="votre@email.com")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            
            if st.button("Se connecter", use_container_width=True, type="primary"):
                if email and password:
                    res, status_code = api_client.login(email, password)
                    if status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.user = res['user']
                        st.session_state.token = res['access_token']
                        
                        expires = datetime.now() + timedelta(days=30)
                        cookie_manager.set('jwt_token', res['access_token'], expires_at=expires, path='/', key="login_v8")
                        
                        st.success("Connexion réussie ! Redirection...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Erreur : {res.get('detail', 'Identifiants incorrects')}")
                else:
                    st.warning("Veuillez remplir tous les champs.")
        
        if st.button("Créer un compte", use_container_width=True):
            st.session_state.unauth_view = "register"
            st.rerun()
        
        if st.button("⬅️ Retour à l'accueil", use_container_width=True):
            st.session_state.unauth_view = "landing"
            st.rerun()

def register_page():
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
        st.title("✨ Inscription")
        st.markdown("<p style='color: #64748b;'>Rejoignez IntelliDoc AI aujourd'hui</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container():
            nom = st.text_input("Nom Complet", placeholder="Jean Dupont")
            email = st.text_input("Adresse Email", placeholder="jean@exemple.com")
            pwd = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            
            if st.button("Créer mon compte", use_container_width=True, type="primary"):
                if nom and email and pwd:
                    res, status = api_client.register(nom, email, pwd)
                    if status == 200:
                        st.success("Compte créé ! Connectez-vous maintenant.")
                        time.sleep(1.5)
                        st.session_state.unauth_view = "login"
                        st.rerun()
                    else:
                        st.error(f"Erreur : {res.get('detail', 'Échec de l\'inscription')}")
                else:
                    st.warning("Veuillez remplir tous les champs.")
            
            if st.button("Déjà un compte ? Se connecter", use_container_width=True):
                st.session_state.unauth_view = "login"
                st.rerun()
                
            if st.button("⬅️ Retour à l'accueil", use_container_width=True):
                st.session_state.unauth_view = "landing"
                st.rerun()

def landing_page():
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 4rem 1rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; border-radius: 12px; margin-bottom: 2rem;">
            <h1 style="font-size: 3.5rem; margin-bottom: 1rem;">📄 IntelliDoc AI</h1>
            <p style="font-size: 1.5rem; opacity: 0.9; max-width: 800px; margin: 0 auto 2rem;">
                La solution intelligente pour l'extraction OCR et la classification automatique de vos documents professionnels.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons (Streamlit Native to avoid JS complexity)
    c1, mid, c2 = st.columns([1, 2, 1])
    with mid:
        col_l, col_r = st.columns(2)
        if col_l.button("🚀 Commencer gratuitement", use_container_width=True, type="primary"):
            st.session_state.unauth_view = "login"
            st.rerun()
        if col_r.button("🏢 En savoir plus", use_container_width=True):
            st.toast("IntelliDoc v7.5 - Nouveau moteur OCR activé !")

    st.markdown("<br>", unsafe_allow_html=True)

    # Features Section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="st-emotion-cache-12w0qpk" style="height: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔍</div>
                <h3>OCR de pointe</h3>
                <p>Extraction textuelle avancée supportant PDF et documents scannés avec une précision optimale.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="st-emotion-cache-12w0qpk" style="height: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🧠</div>
                <h3>IA Cognitive</h3>
                <p>Nos modèles de Machine Learning classent automatiquement vos documents : Factures, Contrats, etc.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="st-emotion-cache-12w0qpk" style="height: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">📁</div>
                <h3>Gestion Pro</h3>
                <p>Bibliothèque sécurisée avec recherche plein texte, filtres avancés et exports Excel/CSV.</p>
            </div>
        """, unsafe_allow_html=True)

def dashboard_page():
    st.markdown("## 🚀 Upload & Traitement")
    st.markdown("Analysez vos documents en quelques secondes grâce à notre IA.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Charger un document")
        uploaded_file = st.file_uploader("Format supporté : PNG, JPG, JPEG, PDF (Propulsion Tesseract/ML)", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if uploaded_file:
            # File Details Card
            st.markdown(f"""
                <div class="st-emotion-cache-12w0qpk">
                    <b>📄 Détails du fichier :</b><br>
                    • Nom : {uploaded_file.name}<br>
                    • Taille : {uploaded_file.size / 1024:.1f} KB<br>
                    • Type : {uploaded_file.type}<br>
                </div>
            """, unsafe_allow_html=True)
            
            # Preview section
            st.markdown("#### 👁️ Aperçu")
            try:
                if uploaded_file.type.startswith('image'):
                    image = Image.open(uploaded_file)
                    st.image(image, use_container_width=True)
                else:
                    st.info("Aperçu visuel disponible pour les images uniquement.")
            except:
                st.info("Aperçu non disponible pour ce type de fichier.")
            finally:
                # Reset file pointer for the real API call later
                uploaded_file.seek(0)

    with col2:
        if uploaded_file:
            if st.button("Lancer l'Analyse Intelligente", type="primary", use_container_width=True):
                # 1. Progress Bar Logic
                progress_container = st.empty()
                status_text = st.empty()
                
                bar = progress_container.progress(0)
                
                # Step 1: Upload
                status_text.info("📤 Étape 1/4 : Téléchargement du document...")
                bar.progress(25)
                time.sleep(0.5)
                
                # Step 2: OCR
                status_text.info("🔍 Étape 2/4 : Extraction du texte (OCR)...")
                bar.progress(50)
                
                # Real API Call
                res, status_code = api_client.upload_document(
                    st.session_state.token, 
                    uploaded_file.read(), 
                    uploaded_file.name
                )
                
                if status_code == 200:
                    # Step 3: Classification
                    status_text.info("🧠 Étape 3/4 : Classification par Intelligence Artificielle...")
                    bar.progress(75)
                    time.sleep(0.5)
                    
                    # Step 4: Done
                    status_text.success("✅ Étape 4/4 : Analyse terminée !")
                    bar.progress(100)
                    time.sleep(0.5)
                    
                    # Clear progress
                    progress_container.empty()
                    status_text.empty()
                    
                    # 2. Result Display
                    conf = res['confidence'] * 100
                    conf_class = "badge-success" if conf > 80 else ("badge-warning" if conf > 60 else "badge-error")
                    conf_label = "Fiable" if conf > 80 else ("À vérifier" if conf > 60 else "Incertain")
                    
                    st.markdown(f"""
                        <div class="extraction-container">
                            <div class="extraction-header">
                                <span>📄 {res['filename']}</span>
                                <span class="badge {conf_class}">{res['category']} • {conf:.1f}% ({conf_label})</span>
                            </div>
                            <div class="extraction-body">{res['text']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # 3. Collaborative Feedback Loop
                    st.subheader("💬 Votre avis (Optionnel)")
                    st.info("💡 Si l'IA n'a pas classé le document correctement ou pour toute observation, notez-le ici.")
                    
                    avis_post = st.text_area("Observations ou corrections :", 
                                          placeholder="Ex: La catégorie devrait être CONTRAT, ou bien le texte est mal extrait...",
                                          key=f"avis_post_{res['id']}")
                    
                    if st.button("🚀 Enregistrer l'avis et Finaliser", use_container_width=True, type="primary"):
                        if avis_post:
                            _, up_status = api_client.update_document_category(st.session_state.token, res['id'], avis_utilisateur=avis_post)
                            if up_status == 200:
                                st.success("Merci pour votre retour ! Analyse enregistrée.")
                            else:
                                st.error("Erreur lors de l'enregistrement de l'avis.")
                        else:
                            st.success("Analyse enregistrée avec succès !")
                        
                        time.sleep(1.5)
                        st.rerun()
                    
                    st.markdown("""
                        <div class="learning-loop">
                            💡 <b>Learning Loop :</b> Vos corrections manuelles aident nos modèles à s'améliorer continuellement pour mieux reconnaître vos futurs documents.
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Erreur lors du traitement : {res.get('detail', 'Inconnu')}")
        else:
            st.info("Veuillez uploader un fichier pour voir les résultats d'analyse.")

def library_page():
    st.markdown("## 📁 Mes Documents")
    
    docs, status = api_client.get_documents(st.session_state.token)
    
    if status == 200 and docs:
        df = pd.DataFrame(docs)
        df['date_upload'] = pd.to_datetime(df['date_upload'])
        
        # 1. Search & Filters
        col_search, col_cat, col_score = st.columns([2, 1, 1])
        with col_search:
            search_query = st.text_input("🔍 Rechercher par mot-clé...", placeholder="Ex: 'Total', 'Contrat', etc.")
        with col_cat:
            categories = ["Toutes"] + sorted(df['categorie'].unique().tolist())
            filter_cat = st.selectbox("Catégorie", categories)
        with col_score:
            filter_score = st.slider("Confiance min (%)", 0, 100, 0)

        # 2. Export Actions
        st.markdown("---")
        exp1, exp2, exp3 = st.columns([1, 1, 2])
        with exp1:
            if st.button("📄 Export CSV", use_container_width=True):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Confirmer CSV", csv, "docs_export.csv", "text/csv")
        with exp2:
            if st.button("📗 Export Excel", use_container_width=True):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Documents')
                st.download_button("Confirmer Excel", buffer.getvalue(), "docs_export.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Filtering Logic
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df['texte_extrait'].str.contains(search_query, case=False, na=False)]
        if filter_cat != "Toutes":
            filtered_df = filtered_df[filtered_df['categorie'] == filter_cat]
        if filter_score > 0:
            filtered_df = filtered_df[filtered_df['score_confiance'] * 100 >= filter_score]

        # 3. Display Table
        st.markdown(f"**{len(filtered_df)} documents trouvés**")
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                with st.expander(f"📄 {row['nom_fichier']} - {row['categorie']} ({row['date_upload'].strftime('%d/%m/%Y')})"):
                    # Visual Confidence Bar
                    conf_pct = row['score_confiance'] * 100
                    if conf_pct >= 80: bar_color = "#2ecc71" # Green
                    elif conf_pct >= 60: bar_color = "#ffa500" # Orange
                    else: bar_color = "#ff4b4b" # Red
                    
                    st.markdown(f"""
                        <div style="margin-bottom: 5px; font-size: 0.8rem; color: #64748b; font-weight: 600;">Fiabilité de l'IA : {conf_pct:.1f}%</div>
                        <div style="width: 100%; background-color: #f1f5f9; border-radius: 10px; height: 8px; margin-bottom: 20px; overflow: hidden; border: 1px solid #e2e8f0;">
                            <div style="width: {conf_pct}%; background-color: {bar_color}; height: 100%; transition: width 0.5s ease-in-out;"></div>
                        </div>
                    """, unsafe_allow_html=True)

                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(f"**Texte Extrait :**")
                        st.code(row['texte_extrait'][:400] + "..." if len(row['texte_extrait']) > 400 else row['texte_extrait'])
                    with c2:
                        st.markdown(f"**Détails :**")
                        st.write(f"Type : {row['categorie']}")
                        st.write(f"Format : {row.get('type_mime', 'Inconnu')}")
                        st.write(f"Taille : {format_size(row.get('taille'))}")
                        st.write(f"Confiance : {conf_pct:.1f}%")
                        st.download_button("📥 TXT", row['texte_extrait'], file_name=f"{row['nom_fichier']}.txt", key=f"dl_{row['id_document']}")
                    with c3:
                        st.write("")
                        if st.button("🗑️ Supprimer", key=f"del_{row['id_document']}", type="secondary"):
                            del_res, del_status = api_client.delete_document(st.session_state.token, row['id_document'])
                            if del_status == 200:
                                st.toast("✅ Document supprimé !")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Erreur de suppression.")
        else:
            st.warning("Aucun document ne correspond à vos critères.")
    else:
        st.info("Votre bibliothèque est vide. Commencez par uploader un document !")

def statistics_page():
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown("## 📊 Tableau de Bord Analytique")
    st.markdown("---")
    
    token = st.session_state.token
    stats_data, stats_status = api_client.get_stats(token)
    docs_data, docs_status = api_client.get_documents(token)
    
    if stats_status == 200 and docs_status == 200:
        df = pd.DataFrame(docs_data)
        
        if df.empty:
            st.info("📊 Pas encore de données à analyser. Commencez par uploader des documents !")
            return

        # --- 1. KPIs de haut niveau ---
        total_docs = len(df)
        avg_conf = df['score_confiance'].mean() * 100
        docs_to_verify = len(df[df['score_confiance'] < 0.6])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Documents", total_docs)
        col2.metric("Confiance Moyenne", f"{avg_conf:.1f}%")
        col3.metric("À vérifier (<60%)", docs_to_verify, delta=-docs_to_verify, delta_color="inverse")
        col4.metric("Catégories Actives", df['categorie'].nunique())

        st.markdown("### 📈 Performance & Détection")
        
        # --- 2. Jauge de Confiance & Évolution Temporelle ---
        row1_col1, row1_col2 = st.columns([1, 2])
        
        with row1_col1:
            # Gauge Chart for global confidence
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_conf,
                title = {'text': "Indice de Qualité Global", 'font': {'size': 18}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#3498db"},
                    'steps': [
                        {'range': [0, 60], 'color': "#ff4b4b"},
                        {'range': [60, 80], 'color': "#ffa500"},
                        {'range': [80, 100], 'color': "#2ecc71"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#34495e"})
            st.plotly_chart(fig_gauge, use_container_width=True)

        with row1_col2:
            # Time Evolution (Area Chart)
            df['date_upload'] = pd.to_datetime(df['date_upload'])
            df_time = df.groupby(df['date_upload'].dt.date).size().reset_index(name='count')
            fig_time = px.area(df_time, x='date_upload', y='count', title="Flux d'Entrée des Documents",
                             labels={'date_upload': 'Date de dépôt', 'count': 'Nombre de documents'})
            fig_time.update_traces(line_color='#3498db', fillcolor='rgba(52, 152, 219, 0.2)')
            fig_time.update_layout(height=330, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_time, use_container_width=True)

        # --- 3. Répartition par Catégorie & Score par Catégorie ---
        st.markdown("### 🏷️ Classification par Type")
        row2_col1, row2_col2 = st.columns(2)
        
        with row2_col1:
            # Bar chart by category with distinct colors
            df_cat = df['categorie'].value_counts().reset_index()
            df_cat.columns = ['cat', 'count']
            fig_cat = px.bar(df_cat, x='cat', y='count', color='cat', title="Répartition des Catégories",
                           color_discrete_sequence=px.colors.qualitative.Safe)
            fig_cat.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with row2_col2:
            # Score by category - Vertical Bar with conditional coloring
            df_score = df.groupby('categorie')['score_confiance'].mean().reset_index()
            df_score['score_pct'] = df_score['score_confiance'] * 100
            
            colors = []
            for s in df_score['score_pct']:
                if s >= 80: colors.append('#2ecc71')
                elif s >= 60: colors.append('#ffa500')
                else: colors.append('#ff4b4b')
                
            fig_score = px.bar(df_score, x='categorie', y='score_pct', title="Précision Moyenne par Type (%)",
                             labels={'score_pct': 'Confiance %', 'categorie': 'Catégorie'})
            fig_score.update_traces(marker_color=colors)
            fig_score.update_layout(height=350)
            st.plotly_chart(fig_score, use_container_width=True)

        # --- 4. Section Conditionnelle (Admin vs Utilisateur) ---
        is_admin = st.session_state.user.get('role') == 'admin'
        
        if is_admin:
            st.markdown("### 🫂 Activité des Utilisateurs (Admin)")
            row3_col1, row3_col2 = st.columns(2)
            
            with row3_col1:
                # Role distribution (Mocked or real if available in DB)
                role_data = pd.DataFrame({'Rôle': ['Admin', 'Utilisateurs'], 'Nombre': [1, total_docs // 5 + 1]})
                fig_roles = px.pie(role_data, values='Nombre', names='Rôle', hole=0.5, title="Typologie des Comptes",
                                color_discrete_sequence=['#34495e', '#3498db'])
                fig_roles.update_layout(height=350)
                st.plotly_chart(fig_roles, use_container_width=True)
                
            with row3_col2:
                # Top Contributors
                df_users = df['id_user'].value_counts().reset_index()
                df_users.columns = ['user_id', 'count']
                df_users['Utilisateur'] = df_users['user_id'].apply(lambda x: f"Collaborateur #{x}")
                fig_top = px.bar(df_users.head(5), x='count', y='Utilisateur', orientation='h', 
                            title="Top Contributeurs (Nombre de Docs)",
                            labels={'count': 'Documents traités', 'Utilisateur': 'Utilisateur'})
                fig_top.update_traces(marker_color='#34495e')
                fig_top.update_layout(height=350, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.markdown("### 📊 Méta-Analyse Personnelle")
            row3_col1, row3_col2 = st.columns(2)
            
            with row3_col1:
                # File Extensions Breakdown
                df['extension'] = df['nom_fichier'].apply(lambda x: x.split('.')[-1].upper() if '.' in x else 'Inconnu')
                df_ext = df['extension'].value_counts().reset_index()
                df_ext.columns = ['ext', 'count']
                fig_ext = px.pie(df_ext, values='count', names='ext', hole=0.5, title="Formats de vos Fichiers",
                                color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_ext.update_layout(height=350)
                st.plotly_chart(fig_ext, use_container_width=True)
                
            with row3_col2:
                # Confidence Grouping
                def group_conf(score):
                    if score >= 0.8: return "Élevée (>80%)"
                    elif score >= 0.6: return "Moyenne (60-80%)"
                    else: return "Faible (<60%)"
                
                df['conf_group'] = df['score_confiance'].apply(group_conf)
                df_conf_group = df['conf_group'].value_counts().reset_index()
                df_conf_group.columns = ['qualite', 'count']
                
                # Sort order
                order = ["Élevée (>80%)", "Moyenne (60-80%)", "Faible (<60%)"]
                df_conf_group['qualite'] = pd.Categorical(df_conf_group['qualite'], categories=order, ordered=True)
                df_conf_group = df_conf_group.sort_values('qualite')
                
                fig_qual = px.bar(df_conf_group, x='qualite', y='count', title="Audit de Qualité de votre Bibliothèque",
                                labels={'count': 'Nombre de docs', 'qualite': 'Niveau de confiance'},
                                color='qualite', color_discrete_map={
                                    "Élevée (>80%)": "#2ecc71",
                                    "Moyenne (60-80%)": "#ffa500",
                                    "Faible (<60%)": "#ff4b4b"
                                })
                fig_qual.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_qual, use_container_width=True)

    else:
        st.warning("📊 Les statistiques sont en cours de calcul. Veuillez uploader plus de documents pour un affichage complet.")

def main():
    # 2. State Initialization (EXACT ORIGINAL LOGIC)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'unauth_view' not in st.session_state:
        st.session_state.unauth_view = "landing" # "landing", "login", "register"
    if 'sync_attempts' not in st.session_state:
        st.session_state.sync_attempts = 0
    if 'sync_complete' not in st.session_state:
        st.session_state.sync_complete = False

    # 3. DEFINITIVE SESSION SYNCHRONIZATION (EXACT ORIGINAL LOGIC)
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

    if not st.session_state.logged_in:
        if st.session_state.unauth_view == "landing":
            landing_page()
        elif st.session_state.unauth_view == "login":
            login_page()
        elif st.session_state.unauth_view == "register":
            register_page()
    else:
        # --- SIDEBAR HEADER ---
        with st.sidebar:
            st.markdown(f"""
                <div style="text-align: center; padding: 1rem 0;">
                    <div style="font-size: 3rem;">👤</div>
                    <h3 style="margin-bottom: 0;">{st.session_state.user['nom']}</h3>
                    <p style="color: #64748b; font-size: 0.9rem;">{st.session_state.user['email']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            menu = st.radio(
                "Menu Principal", 
                ["🚀 Analyse", "📁 Bibliothèque", "📊 Statistiques"],
                captions=["Nouveau traitement", "Gérer mes documents", "Données & Insights"]
            )
            
            st.markdown("---")
            # 4. LOGOUT (EXACT ORIGINAL LOGIC)
            if st.button("🔌 Déconnexion", use_container_width=True, type="secondary"):
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

        # Render Page
        st.markdown(MODERN_CSS, unsafe_allow_html=True)
        if menu == "🚀 Analyse":
            dashboard_page()
        elif menu == "📁 Bibliothèque":
            library_page()
        elif menu == "📊 Statistiques":
            statistics_page()

if __name__ == "__main__":
    main()
