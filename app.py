import streamlit as st
import pandas as pd
import os
import openai
from gestione_anagrafica import mostra_anagrafica

# 1. SETUP CSS (ORIGINALE + PERSONALIZZAZIONE BOTTONI)
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

    /* BOTTONI DASHBOARD LAVORI - COLORI ORIGINALI */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }

    /* CSS GESTIONE DIREZIONE LAVORI (TUO ORIGINALE) */
    div[data-testid="column"] button[key^="up_"], 
    div[data-testid="column"] button[key^="op_"], 
    div[data-testid="column"] button[key^="del_"] {
        height: 110px !important; 
        width: 100% !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        border: 2px solid #e2e8f0 !important;
        background-color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="column"] button[key^="del_"] {
        background-color: #fee2e2 !important;
        border-color: #ef4444 !important;
    }
    .table-header { background-color: #f1f5f9; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 5px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE E FUNZIONI BASE
DB_FILE = "database_archiflow.csv"
DB_CANTIERI = "cantieri.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
COL_CAN = ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note"]

def carica(file, colonne):
    if os.path.exists(file):
        df = pd.read_csv(file, dtype=str).fillna("")
        for c in colonne: 
            if c not in df.columns: df[c] = ""
        return df[colonne]
    return pd.DataFrame(columns=colonne)

df_ana = carica(DB_FILE, COL_ANA)
df_can = carica(DB_CANTIERI, COL_CAN)

# 3. SIDEBAR CON IL TUO LOGO E API KEY
with st.sidebar:
    # --- IL TUO LOGO E TITOLO ORIGINALE ---
    st.title("🏛️ ARCHIFLOW")
    st.subheader("Suite Gestionale v1.0")
    # -------------------------------------
    api_key = st.text_input("🔑 OpenAI API Key", type="password")
    st.divider()
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.session_state.sotto_menu = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_sel

# --- LOGICA NAVIGAZIONE ---
if menu == "HOME":
    st.title("Benvenuta Arch. Cubeddu")
    # Quadro sinottico anagrafica
    st.dataframe(df_ana[["Cliente", "Pratica", "Stato"]], use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    # Richiama il modulo professionale
    mostra_anagrafica(df_ana, DB_FILE, COL_ANA)

elif menu == "LAVORI":
    # Manteniamo la logica DL che hai programmato tu
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        # Logica Direzione Lavori (Tua originale)
        if st.session_state.get("c_aperto"):
            id_c = st.session_state.c_aperto
            idx = df_can[df_can['id_cantiere'] == id_c].index[0]
            if st.button("⬅️ LISTA CANTIERI"): st.session_state.c_aperto = None; st.rerun()
            # ... Tua logica Diario/AI qui ...
        else:
            # Lista Cantieri (Tua originale)
            for i, r in df_can.iterrows():
                # ... Tuo layout colonne qui ...
                pass
    else:
        # DASHBOARD COLORATA (Tua originale)
        st.header("🏗️ Selezione Area di Lavoro")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True): st.session_state.sotto_menu = "DL"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            # ... Rilievi ...
        with c2:
            st.markdown('<div class="btn-pra">', unsafe_allow_html=True)
            st.button("📋\nPRATICHE", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            # ... Millesimi ...
        with c3:
            st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
            st.button("⚡\nAPE", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            # ... Altro ...
