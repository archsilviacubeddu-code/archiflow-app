import streamlit as st
import pandas as pd
import os

# IMPORTAZIONE DEI MODULI (Assicurati che i file .py siano nella stessa cartella)
try:
    from gestione_anagrafica import mostra_anagrafica
    from gestione_lavori import mostra_lavori
except ImportError as e:
    st.error(f"Errore di caricamento moduli: {e}. Verifica che i file gestione_anagrafica.py e gestione_lavori.py siano presenti nel repository.")

# 1. SETUP GENERALE
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* MENU SIDEBAR */
    .sidebar-btn > div > button {
        height: 4.5em !important;
        font-weight: bold !important;
        font-size: 18px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE E FUNZIONE CARICA
DB_FILE = "database_archiflow.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]

def carica(file, colonne):
    if os.path.exists(file):
        df = pd.read_csv(file, dtype=str).fillna("")
        for c in colonne: 
            if c not in df.columns: df[c] = ""
        return df[colonne]
    return pd.DataFrame(columns=colonne)

# 3. SIDEBAR CON LOGO E NAVIGAZIONE
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.title("🏛️ ARCHIFLOW")
    
    st.divider()
    
    if "menu_sel" not in st.session_state: 
        st.session_state.menu_sel = "HOME"
    
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    
    if st.button("🏠 HOME", use_container_width=True): 
        st.session_state.menu_sel = "HOME"
        st.rerun()
        
    if st.button("📇 ANAGRAFICA", use_container_width=True): 
        st.session_state.menu_sel = "ANAGRAFICA"
        st.rerun()
        
    if st.button("🏗️ LAVORI", use_container_width=True): 
        st.session_state.menu_sel = "LAVORI"
        st.session_state.sezione_lavoro = None 
        st.session_state.lavoro_sel = None
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGICA DI NAVIGAZIONE
menu = st.session_state.menu_sel

if menu == "HOME":
    df_ana = carica(DB_FILE, COL_ANA)
    st.title("Archiflow - Suite Gestionale")
    st.divider()
    st.dataframe(df_ana[["Cliente", "Pratica", "Stato"]], use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    df_ana = carica(DB_FILE, COL_ANA)
    mostra_anagrafica(df_ana, DB_FILE, COL_ANA)

elif menu == "LAVORI":
    df_ana = carica(DB_FILE, COL_ANA)
    mostra_lavori(df_ana, DB_FILE)
