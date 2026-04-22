import streamlit as st
import pandas as pd
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import widget_alert_home

st.set_page_config(page_title="Archiflow Suite", layout="wide")

# CSS Globale
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    .sidebar-btn > div > button {
        height: 4.5em !important; font-weight: bold !important; font-size: 18px !important;
        margin-bottom: 12px !important; border-radius: 12px !important;
        background-color: white !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    .card {
        background-color: white; padding: 20px; border-radius: 15px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        min-height: 300px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "database_archiflow.csv"
COLONNE = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note", "docs_json"]

def carica_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype=str).fillna("")
        for c in COLONNE:
            if c not in df.columns: df[c] = ""
        return df[COLONNE]
    return pd.DataFrame(columns=COLONNE)

if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"

with st.sidebar:
    st.title("🏛️ ARCHIFLOW")
    st.divider()
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.rerun()

df_globale = carica_db()

if st.session_state.menu_sel == "HOME":
    st.title("Benvenuta Architetto! 🏗️")
    col1, col2, col3 = st.columns(3)
    
    with col1: # SEMAFORO SCADENZE
        st.markdown('<div class="card"><h3>🚦 Semaforo Scadenze</h3>', unsafe_allow_html=True)
        scadenze = df_globale[df_globale['Scadenza'] != ""][["Cliente", "Scadenza", "Pratica"]]
        if not scadenze.empty:
            st.dataframe(scadenze, hide_index=True, use_container_width=True)
        else:
            st.info("Nessuna scadenza inserita.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2: # NUOVI LAVORI
        st.markdown('<div class="card"><h3>🆕 Ultimi Lavori</h3>', unsafe_allow_html=True)
        st.dataframe(df_globale[["Cliente", "Pratica"]].tail(5), hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3: # ALERT DOCUMENTI
        st.markdown('<div class="card"><h3>⚠️ Alert Documenti</h3>', unsafe_allow_html=True)
        widget_alert_home(df_globale)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_sel == "ANAGRAFICA":
    mostra_anagrafica(df_globale, DB_FILE, COLONNE)

elif st.session_state.menu_sel == "LAVORI":
    mostra_lavori(df_globale, DB_FILE)
