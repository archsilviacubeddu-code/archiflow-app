import streamlit as st
import pandas as pd
import os
from gestione_anagrafica import mostra_anagrafica

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

    /* BOTTONI DASHBOARD LAVORI */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE
DB_FILE = "database_archiflow.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]

def carica(file, colonne):
    if os.path.exists(file):
        df = pd.read_csv(file, dtype=str).fillna("")
        for c in colonne: 
            if c not in df.columns: df[c] = ""
        return df[colonne]
    return pd.DataFrame(columns=colonne)

df_ana = carica(DB_FILE, COL_ANA)

# 3. SIDEBAR CON LOGO
with st.sidebar:
    # Richiamo esatto del file Logo.png
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    
    st.divider()
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_sel

# --- LOGICA NAVIGAZIONE ---
if menu == "HOME":
    st.title("Archiflow- Suite Gestionale")
    st.divider()
    st.dataframe(df_ana[["Cliente", "Pratica", "Stato"]], use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    mostra_anagrafica(df_ana, DB_FILE, COL_ANA)

elif menu == "LAVORI":
    st.header("🏗️ Selezione Area di Lavoro")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
        st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-pra">', unsafe_allow_html=True)
        st.button("📋\nPRATICHE", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
        st.button("⚡\nAPE", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
