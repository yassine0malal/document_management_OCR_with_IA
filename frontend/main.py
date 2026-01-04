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
    page_icon="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/svgs/solid/file-invoice.svg",
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
    /* Google Fonts & Font Awesome */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@400;700;800&family=Roboto+Mono&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container */
    .main {
        background-color: #020617;
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
    .badge-warning { background-color: #fff7ed; color: #9a3412; }
    .badge-error { background-color: #fee2e2; color: #991b1b; }
    .badge-info { background-color: #e0f2fe; color: #075985; }
    
    .badge i { margin-right: 6px; }

    /* Button Icon Injection */
    [data-testid^="stBaseButton-"] button p:before {
        font-family: "Font Awesome 6 Free" !important;
        font-weight: 900 !important;
        margin-right: 8px !important;
        display: inline-block !important;
    }
    [data-testid="stBaseButton-logout_btn"] button p:before { content: "\f2f5"; }
    [data-testid^="stBaseButton-del_btn_"] button p:before { content: "\f2ed"; }
    [data-testid="stBaseButton-csv_btn"] button p:before { content: "\f6dd"; }
    [data-testid="stBaseButton-excel_btn"] button p:before { content: "\f1c3"; }
    [data-testid^="stBaseButton-txt_btn_"] button p:before { content: "\f56d"; }
    [data-testid="stBaseButton-back_home_btn"] button p:before { content: "\f015"; }

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
    /* Landing Page Specifics */
    .landing-hero {
        background: radial-gradient(circle at top left, #4f46e5 0%, #1e1b4b 100%);
        border-radius: 28px;
        padding: 5rem 2rem;
        text-align: center;
        margin-bottom: 4rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
    }


    /* Feature Cards Styling */
    .feature-card {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5) !important;
        height: 100%;
        backdrop-filter: blur(10px);
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6);
        border-color: rgba(99, 102, 241, 0.5);
    }
    .feature-icon {
        font-size: 2.5rem;
        color: #818cf8;
        margin-bottom: 1.5rem;
        display: inline-block;
    }
    .feature-title {
        color: white;
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .feature-desc {
        color: #94a3b8;
        line-height: 1.6;
        font-size: 1rem;
    }

    /* File Uploader Enhancement */
    [data-testid="stFileUploader"] section {
        padding: 4rem 2rem !important; /* Large drop zone */
        background-color: #f8fafc;
        border: 2px dashed #cbd5e1;
        text-align: center;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #6366f1;
        background-color: #eef2ff;
    }
    [data-testid="stFileUploader"] button {
        background-color: #6366f1 !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4) !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #4f46e5 !important;
        transform: translateY(-1px);
    }
    .hero-title-outer {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 5.2rem !important;
        color: #ffffff !important;
        margin-bottom: 1.5rem;
        line-height: 1.1;
        text-align: center !important;
        letter-spacing: -0.03em;
        max-width: 1100px;
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
    }
    .hero-subtitle-outer {
        font-size: 1.6rem;
        color: #94a3b8 !important;
        max-width: 800px;
        margin: 0 auto 3rem;
        text-align: center;
        line-height: 1.6;
        font-weight: 400;
    }
    .hero-cta-section {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 5rem;
    }
    .btn-primary-custom {
        background-color: #6366f1 !important;
        color: white !important;
        padding: 14px 32px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }
    .btn-secondary-custom {
        background-color: transparent !important;
        color: white !important;
        padding: 14px 32px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }
    .hero-visual-section {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 40px;
        max-width: 1500px;
        margin: 0 auto 6rem;
    }
    .hero-primary-box {
        flex: 2;
        background: radial-gradient(circle at top left, #4f46e5 0%, #1e1b4b 100%);
        border-radius: 40px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 50px 80px -20px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
        height: 600px;
    }
    .hero-secondary-box {
        flex: 1;
        background: radial-gradient(circle at bottom right, #3730a3 0%, #1e1b4b 100%);
        border-radius: 35px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 40px 70px -15px rgba(0, 0, 0, 0.4);
        height: 480px;
        overflow: hidden;
    }
    .hero-inner-overlay {
        position: absolute;
        bottom: 40px;
        left: 40px;
        z-index: 20;
        text-align: left;
        pointer-events: none;
    }
    .inner-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin-bottom: 0.6rem !important;
        line-height: 1 !important;
    }
    .inner-subtitle {
        font-size: 1.3rem !important;
        color: #c7d2fe !important;
        opacity: 0.95;
    }
    .image-fill {
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.85;
    }
    .hero-image-container {
        width: 100%;
        height: 100%;
        background: #000 !important;
    }
    .video-hero-container {
        max-width: 1400px;
        margin: 0 auto 5rem;
        border-radius: 40px;
        overflow: hidden;
        box-shadow: 0 50px 100px -20px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.3);
        background: #000;
    }
    .video-hero-container video {
        width: 100%;
        display: block;
    }
    .hero-image-container:hover {
        transform: translateY(-10px) scale(1.01);
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 3rem 2rem;
        border-radius: 28px;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        text-align: center;
        height: 100%;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }
    .feature-card:hover {
        transform: translateY(-12px);
        background: rgba(255, 255, 255, 0.85) !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
        border-color: #6366f1 !important;
    }
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 2rem;
        display: block;
    }
    /* Explicitly targeting the tags to override Streamlit defaults */
    .feature-card h2.feature-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #1e1b4b !important;
        margin-bottom: 1rem !important;
        margin-top: 0 !important;
    }
    .feature-card p.feature-desc {
        color: #475569 !important;
        line-height: 1.6 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0 !important;
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
"""

def login_page():
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin-bottom: 0;'><i class='fa-solid fa-shield-halved'></i> IntelliDoc AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b;'>Système de Gestion Intelligente des Documents</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### <i class='fa-solid fa-key'></i> Connexion", unsafe_allow_html=True)
            email = st.text_input("Adresse Email", placeholder="votre@email.com")
            password = st.text_input("Mot de passe", type="password", placeholder="********")
            
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
        
        if st.button("Retour à l'accueil", use_container_width=True):
            st.session_state.unauth_view = "landing"
            st.rerun()

def register_page():
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin-bottom: 0;'><i class='fa-solid fa-user-plus'></i> Inscription</h1>", unsafe_allow_html=True)
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
                
            if st.button("Retour à l'accueil", use_container_width=True, key="back_home_btn"):
                st.session_state.unauth_view = "landing"
                st.rerun()

def landing_page():
    st.markdown(MODERN_CSS, unsafe_allow_html=True)
    
    # Hero Section - Loading visuals
    img1_path = "/home/yassine0malal/.gemini/antigravity/brain/84f6eede-ed34-4cc1-8a4b-ac54a21208a5/hero_ai_docs_illustration_1767514798526.png"
    img2_path = "/home/yassine0malal/.gemini/antigravity/brain/84f6eede-ed34-4cc1-8a4b-ac54a21208a5/hero_doc_analytics_small_1767516140481.png"
    video_path = "hero-homepage-bike.webm"
    import base64
    def get_b64(path):
        try:
            with open(path, "rb") as f:
                return f"data:image/{'png' if path.endswith('.png') else 'webm'};base64,{base64.b64encode(f.read()).decode()}"
        except: return ""

    html_img1 = get_b64(img1_path)
    html_img2 = get_b64(img2_path)
    html_video = get_b64(video_path)

    st.markdown(f"""
        <div style="padding-top: 4rem; text-align: center; width: 100%;">
            <h1 class="hero-title-outer">Best OCR Models</h1>
            <p class="hero-subtitle-outer">Everything you need to build and deploy intelligent document classification and advanced text recognition applications.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons - Centered
    c1, mid, c2 = st.columns([1, 1.8, 1])
    with mid:
        col_l, col_r = st.columns(2)
        if col_l.button("Get Started", use_container_width=True, type="primary"):
            st.session_state.unauth_view = "login"
            st.rerun()
        if col_r.button("Request a Demo", use_container_width=True):
            st.toast("IntelliDoc AI Enterprise - Contactez-nous pour une démo.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # VIDEO Section
    if html_video:
        # Load Landing Specific Visuals
        try:
            l_img1_path = "/home/yassine0malal/.gemini/antigravity/brain/84f6eede-ed34-4cc1-8a4b-ac54a21208a5/uploaded_image_1_1767522356944.png"
            l_img0_path = "/home/yassine0malal/.gemini/antigravity/brain/84f6eede-ed34-4cc1-8a4b-ac54a21208a5/uploaded_image_0_1767522356944.png"
            with open(l_img1_path, "rb") as f1, open(l_img0_path, "rb") as f0:
                l_img1_b64 = base64.b64encode(f1.read()).decode()
                l_img0_b64 = base64.b64encode(f0.read()).decode()
        except:
            l_img1_b64 = ""
            l_img0_b64 = ""

        c_video, c_vis = st.columns([1.8, 0.8])
        
        with c_video:
            st.markdown(f"""
                <div class="video-hero-container" style="height: 100%;">
                    <video autoplay loop muted playsinline style="width: 100%; border-radius: 16px;">
                        <source src="{html_video}" type="video/webm">
                        Your browser does not support the video tag.
                    </video>
                </div>
            """, unsafe_allow_html=True)
            
        with c_vis:
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; gap: 20px; height: 100%; justify-content: center;">
                    <div style="border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 10px 30px rgba(0,0,0,0.4); transform: rotate(2deg);">
                        <img src="data:image/png;base64,{l_img1_b64}" style="width: 100%; display: block;" alt="Landing OCR">
                    </div>
                    <div style="border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 10px 30px rgba(0,0,0,0.4); transform: rotate(-2deg);">
                        <img src="data:image/png;base64,{l_img0_b64}" style="width: 100%; display: block;" alt="Landing Pipeline">
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Hero Visuals - Below video
    st.markdown(f"""
        <div class="hero-visual-section">
            <div class="hero-primary-box">
                <div class="hero-inner-overlay">
                    <h2 class="inner-title">IntelliDoc AI</h2>
                    <p class="inner-subtitle">Extraction de pointe & automatisation intelligente.</p>
                </div>
                <div class="hero-image-container">
                    <img src="{html_img1}" class="image-fill" alt="Primary Visual">
                </div>
            </div>
            <div class="hero-secondary-box">
                <div class="hero-image-container">
                    <img src="{html_img2}" class="image-fill" alt="Analytics Visual">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Features Section
    st.markdown("<h2 style='text-align: center; margin-bottom: 3rem; font-family: Outfit;'>Pourquoi choisir IntelliDoc ?</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="background-color: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 2rem; text-align: center; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); height: 100%;">
                <span class="feature-icon"><i class="fa-solid fa-magnifying-glass"></i></span>
                <h2 class="feature-title">OCR Haute Précision</h2>
                <p class="feature-desc">Extraction textuelle avancée supportant PDF et documents scannés avec une fidélité inégalée.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div style="background-color: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 2rem; text-align: center; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); height: 100%;">
                <span class="feature-icon"><i class="fa-solid fa-brain"></i></span>
                <h2 class="feature-title">Classification IA</h2>
                <p class="feature-desc">Nos modèles de Deep Learning organisent automatiquement vos factures, contrats et reçus.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div style="background-color: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 2rem; text-align: center; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); height: 100%;">
                <span class="feature-icon"><i class="fa-solid fa-bolt-lightning"></i></span>
                <h2 class="feature-title">Flux Automatisé</h2>
                <p class="feature-desc">Gagnez 80% de temps sur le traitement administratif grâce à une intégration sans friction.</p>
            </div>
        """, unsafe_allow_html=True)

def dashboard_page():
    st.markdown("## <i class='fa-solid fa-rocket'></i> Upload & Traitement", unsafe_allow_html=True)
    st.markdown("Analysez vos documents en quelques secondes grâce à notre IA.")
    
    # 1. Load Visual Sidebar Assets
    try:
        img1_path = "/home/yassine0malal/.gemini/antigravity/brain/84f6eede-ed34-4cc1-8a4b-ac54a21208a5/uploaded_image_1_1767520059275.png"
        img0_path = "/home/yassine0malal/.gemini/antigravity/brain/84f6eede-ed34-4cc1-8a4b-ac54a21208a5/uploaded_image_0_1767520059275.png"
        import base64
        with open(img1_path, "rb") as f1, open(img0_path, "rb") as f0:
            img1_b64 = base64.b64encode(f1.read()).decode()
            img0_b64 = base64.b64encode(f0.read()).decode()
    except:
        img1_b64 = ""
        img0_b64 = ""

    col1, col2, col_vis = st.columns([1.1, 1, 0.4])
    
    with col1:
        st.markdown("### <i class='fa-solid fa-cloud-arrow-up'></i> Charger un document", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Format supporté : PNG, JPG, JPEG, PDF (Propulsion Tesseract/ML)", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if uploaded_file:
            # File Details Card
            st.markdown(f"""
                <div class="st-emotion-cache-12w0qpk">
                    <b><i class="fa-solid fa-file-lines"></i> Détails :</b><br>
                    • Nom : {uploaded_file.name}<br>
                    • Taille : {uploaded_file.size / 1024:.1f} KB<br>
                    • Type : {uploaded_file.type}<br>
                </div>
            """, unsafe_allow_html=True)
            
            # Preview section
            st.markdown("#### <i class='fa-solid fa-eye'></i> Aperçu", unsafe_allow_html=True)
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

    # Initialize session state for analysis persistence
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = None
    if 'current_file_id' not in st.session_state:
        st.session_state.current_file_id = None

    with col2:
        if uploaded_file:
            # Reset if a new file is uploaded
            if st.session_state.current_file_id != uploaded_file.name:
                st.session_state.last_analysis = None
                st.session_state.current_file_id = uploaded_file.name

            if st.button("Lancer l'Analyse Intelligente", type="primary", use_container_width=True):
                # 1. Progress Bar Logic
                progress_container = st.empty()
                status_text = st.empty()
                
                bar = progress_container.progress(0)
                
                # Step 1: Upload
                status_text.info("Téléchargement du document (1/4)...")
                bar.progress(25)
                time.sleep(0.5)
                
                # Step 2: OCR
                status_text.info("Extraction du texte (OCR) (2/4)...")
                bar.progress(50)
                
                # Real API Call
                res, status_code = api_client.upload_document(
                    st.session_state.token, 
                    uploaded_file.read(), 
                    uploaded_file.name
                )
                
                if status_code == 200:
                    st.session_state.last_analysis = res
                    st.rerun() # Refresh to show results area
                else:
                    st.error(f"Erreur API : {res.get('detail', 'Inconnue')}")

        # Display Results and Feedback area if analysis is done
        if st.session_state.last_analysis:
            res = st.session_state.last_analysis
            
            # 1. Show Analysis Complete Status
            st.success("Analyse terminée et enregistrée !")
            st.markdown("### <i class='fa-solid fa-circle-check' style='color: #2ecc71;'></i> Analyse terminée", unsafe_allow_html=True)
            
            # 2. Result Display
            conf = res['confidence'] * 100
            conf_class = "badge-success" if conf > 80 else ("badge-warning" if conf > 60 else "badge-error")
            conf_label = "Fiable" if conf > 80 else ("À vérifier" if conf > 60 else "Incertain")
            
            st.markdown(f"""
                <div class="extraction-container">
                    <div class="extraction-header">
                        <span><i class="fa-solid fa-file-invoice"></i> {res['filename']}</span>
                        <span class="badge {conf_class}">{res['category']} • {conf:.1f}% ({conf_label})</span>
                    </div>
                    <div class="extraction-body">{res['text']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 3. Integrated Post-Analysis Feedback
            st.markdown("### <i class='fa-solid fa-comment-dots'></i> Votre Avis / Observations", unsafe_allow_html=True)
            st.caption("Ajoutez un commentaire sur cette analyse pour l'enregistrer dans la base de données.")
            
            avis_post = st.text_area("Observations :", 
                                  placeholder="Ex: L'IA a bien travaillé, ou précisez une correction...",
                                  key=f"avis_persist_{res['id']}")
            
            if st.button("Valider et Terminer", use_container_width=True, type="primary"):
                if avis_post:
                    _, up_status = api_client.update_document_category(st.session_state.token, res['id'], avis_utilisateur=avis_post)
                    if up_status == 200:
                        st.success("Commentaire enregistré !")
                    else:
                        st.error("Erreur lors de l'enregistrement.")
                
                # Cleanup and Reset
                st.session_state.last_analysis = None
                st.session_state.current_file_id = None
                time.sleep(1)
                st.rerun()
            
            st.markdown("""
                <div class="learning-loop">
                    <i class="fa-solid fa-lightbulb"></i> <b>Learning Loop :</b> Vos corrections manuelles aident nos modèles à s'améliorer continuellement pour mieux reconnaître vos futurs documents.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Veuillez uploader un fichier pour voir les résultats d'analyse.")

    # 4. Right Sidebar Visuals (Reserved Space)
    with col_vis:
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; gap: 20px; padding-top: 10px;">
                <!-- top image: OCR technical banner -->
                <div style="border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <img src="data:image/png;base64,{img1_b64}" style="width: 100%; display: block;" alt="OCR Analysis">
                </div>
                <!-- bottom image: Architecture Pipeline visual -->
                <div style="border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <img src="data:image/png;base64,{img0_b64}" style="width: 100%; display: block;" alt="Architecture Pipeline">
                </div>
                <!-- footer indicator -->
                <div style="text-align: center; margin-top: 10px;">
                    <div style="font-size: 1.5rem; color: #6366f1; margin-bottom: 5px;">
                        <i class="fa-solid fa-microchip fa-fade"></i>
                    </div>
                    <p style="color: #6366f1; font-weight: 700; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.8;">Technical Workflow</p>
                    <div style="height: 2px; width: 30px; background: #6366f1; margin: 0 auto; border-radius: 2px;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def library_page():
    st.markdown("## <i class='fa-solid fa-folder-open'></i> Mes Documents", unsafe_allow_html=True)
    
    docs, status = api_client.get_documents(st.session_state.token)
    
    if status == 200 and docs:
        df = pd.DataFrame(docs)
        df['date_upload'] = pd.to_datetime(df['date_upload'])
        
        # 1. Search & Filters
        col_search, col_cat, col_score = st.columns([2, 1, 1])
        with col_search:
            search_query = st.text_input("Recherche", placeholder="Rechercher par mot-clé...")
            st.markdown("<p style='font-size: 0.9rem; color: #64748b;'><i class='fa-solid fa-magnifying-glass'></i> Filtrer vos documents</p>", unsafe_allow_html=True)
        with col_cat:
            categories = ["Toutes"] + sorted(df['categorie'].unique().tolist())
            filter_cat = st.selectbox("Catégorie", categories)
        with col_score:
            filter_score = st.slider("Confiance min (%)", 0, 100, 0)

        # 2. Export Actions
        st.markdown("---")
        exp1, exp2, exp3 = st.columns([1, 1, 2])
        with exp1:
            if st.button("Export CSV", use_container_width=True, key="csv_btn_trigger"):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Confirmer CSV", csv, "docs_export.csv", "text/csv", key="csv_btn")
        with exp2:
            if st.button("Export Excel", use_container_width=True, key="excel_btn_trigger"):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Documents')
                st.download_button("Confirmer Excel", buffer.getvalue(), "docs_export.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="excel_btn")
        
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
                # Using Font Awesome in expander title
                with st.expander(f" {row['nom_fichier']} - {row['categorie']} ({row['date_upload'].strftime('%d/%m/%Y')})"):
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
                        st.download_button("TXT", row['texte_extrait'], file_name=f"{row['nom_fichier']}.txt", key=f"txt_btn_{row['id_document']}")
                    with c3:
                        st.write("")
                        if st.button("Supprimer", key=f"del_btn_{row['id_document']}", type="secondary"):
                            del_res, del_status = api_client.delete_document(st.session_state.token, row['id_document'])
                            if del_status == 200:
                                st.toast("Document supprimé avec succès.")
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
    
    st.markdown("## <i class='fa-solid fa-chart-line'></i> Tableau de Bord Analytique", unsafe_allow_html=True)
    st.markdown("---")
    
    token = st.session_state.token
    stats_data, stats_status = api_client.get_stats(token)
    docs_data, docs_status = api_client.get_documents(token)
    
    if stats_status == 200 and docs_status == 200:
        df = pd.DataFrame(docs_data)
        
        if df.empty:
            st.info("Pas encore de données à analyser. Commencez par uploader des documents !")
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

        st.markdown("### <i class='fa-solid fa-chart-line'></i> Performance & Détection", unsafe_allow_html=True)
        
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
        st.markdown("### <i class='fa-solid fa-tags'></i> Classification par Type", unsafe_allow_html=True)
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
            st.markdown("### <i class='fa-solid fa-users'></i> Activité des Utilisateurs (Admin)", unsafe_allow_html=True)
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
            st.markdown("### <i class='fa-solid fa-microscope'></i> Méta-Analyse Personnelle", unsafe_allow_html=True)
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
        st.warning("Les statistiques sont en cours de calcul. Veuillez uploader plus de documents pour un affichage complet.")

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
                    <div style="border: 4px solid #f3f3f3; border-top: 4px solid #6366f1; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite;"></div>
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
                <div style="text-align: center; padding: 1.5rem 0;">
                    <div style="font-size: 3.5rem; color: #6366f1;"><i class="fa-solid fa-circle-user"></i></div>
                    <h3 style="margin-bottom: 0; color: white;">{st.session_state.user['nom']}</h3>
                    <p style="color: #94a3b8; font-size: 0.9rem;">{st.session_state.user['email']}</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            
            st.markdown("### <i class='fa-solid fa-bars'></i> Menu Principal", unsafe_allow_html=True)

            menu = st.radio(
                "Navigation", 
                ["Analyse", "Bibliothèque", "Statistiques"],
                captions=["Nouveau traitement", "Gérer mes documents", "Données & Insights"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            # 4. LOGOUT (EXACT ORIGINAL LOGIC)
            if st.button("Déconnexion", use_container_width=True, type="secondary", key="logout_btn"):
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
        if menu == "Analyse":
            dashboard_page()
        elif menu == "Bibliothèque":
            library_page()
        elif menu == "Statistiques":
            statistics_page()

if __name__ == "__main__":
    main()
