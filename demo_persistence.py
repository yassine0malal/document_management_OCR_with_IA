import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Session Persistence Demo")

# 1. Initialize Cookie Manager
cookie_manager = stx.CookieManager()

# 2. Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# 3. Synchronous Cookie Sync (Wait for browser)
if not st.session_state.logged_in:
    cookies = cookie_manager.get_all()
    
    # Wait for the component to initialize
    if cookies is None:
        st.info("Synchronisation de la session...")
        st.stop()
    
    # Auto-login if a valid cookie exists
    user_cookie = cookies.get('user_session')
    if user_cookie and user_cookie != "LOGOUT":
        st.session_state.logged_in = True
        st.session_state.user_name = user_cookie
        st.rerun()

# 4. Define Pages
def login_page():
    st.title("🔑 Page de Connexion")
    with st.form("login_form"):
        name = st.text_input("Votre Nom")
        submit = st.form_submit_button("Se connecter")
        
        if submit and name:
            st.session_state.logged_in = True
            st.session_state.user_name = name
            # Set persistent cookie for 3 hours
            expires = datetime.now() + timedelta(hours=3)
            cookie_manager.set('user_session', name, expires_at=expires)
            st.success("Connecté !")
            st.rerun()

def dashboard_page():
    st.title(f"📊 Dashboard - Bienvenue {st.session_state.user_name}")
    st.write("Le rafraîchissement de cette page ne vous déconnectera pas.")
    
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        # Force cookie expiration
        cookie_manager.set('user_session', 'LOGOUT', expires_at=datetime.now() - timedelta(days=1))
        st.rerun()

# 5. Main Logic
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
