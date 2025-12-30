import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Main Layout */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 210, 255, 0.5);
    }
    
    /* Stats Styling */
    .stat-container {
        display: flex;
        justify-content: space-around;
        margin-top: 2rem;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: rgba(0, 210, 255, 0.1);
        border-radius: 10px;
        min-width: 150px;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00d2ff;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #888;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

def card(title, content):
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: #00d2ff; margin-top: 0;">{title}</h3>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)
