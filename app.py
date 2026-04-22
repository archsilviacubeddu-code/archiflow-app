import streamlit as st
import pandas as pd
import sqlite3
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import inizializza_documenti

# 1. SETUP
st.set_page_config(page_title="Archiflow", layout="wide")

conn = sqlite3.connect("archiflow_db.sqlite", check_same_thread=False)

# 2. CSS DEFINITIVO - VISIBILITÀ TOTALE
st.markdown("""
    <style>
    /* Bottoni Sidebar: Grandi e Grassetto */
    section[data-testid="stSidebar"] button div p {
        font-size: 20px !important;
        font-weight: 900 !important;
        color: #1e293b !important;
        text-transform: uppercase;
    }
    
    /* QUADRATI HOME: BASSI MA CON TESTO CHIARO */
    .card-home {
        background-color: white;
        padding: 8px 12px;
        border-radius: 8px;
        border: 2px solid #cbd5e1; /* Bordo più marcato */
        height: 115px; /* Alzato di un filo per far respirare le date */
        overflow-y: auto;
        margin-bottom: 5px;
    }
    
    .card-home h3 {
        font-size: 1rem !important;
        font-weight: 900;
        border-bottom: 3px solid #1e293b;
        padding-bottom: 2px;
        margin-bottom: 8px;
        text-transform: uppercase;
        color: #1e293b;
    }

    /* Testi Nomi Clienti: BELLI GROSSI E NERI */
    .client-name { 
        font-weight: 900; 
        font-size: 18px !important; 
        color: #000000; 
    }
    
    .pratica-label {
        font-size: 14px !important;
        font-weight: 800;
        color: #334155;
    }

    .item-row {
        padding: 6px 0;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* DATE: FINALMENTE VISIBILI */
    .date-badge { 
        padding: 4px 10px; 
        border-radius: 6px; 
        font-size: 14px !important; /* Data più grande */
        font-weight: 900; 
        background-color: #1e293b; 
        color: #ffffff; 
        min-width: 90px;
        text-align: center;
    }
    
    .alert-text {
        color: #ef4444; 
        font-weight: 900; 
        font-size: 18px !important;
    }

    /* Scrollbar */
    .card-home::-webkit-scrollbar { width: 4px; }
    .card-home::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR CON LOGO
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.markdown("<h2 style='text-align:center;'>🏛️ ARCHIFLOW</h2>", unsafe_allow_html=True)
    
    st.divider()
    if st.button("🏠 HOME", use_container_width=True):
        st.session_state.menu = "HOME"
        st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True):
        st.session_state.menu = "ANAGRAFICA"
        st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True):
        st.session_state.menu = "LAVORI"
        st.rerun()

if "menu" not in st.session_state:
    st.session_state.menu = "HOME"

df = pd.read_sql("SELECT * FROM lavori", conn)

# 4. PAGINA HOME
if st.session_state.menu == "HOME":
    st.markdown("<h2 style='font-weight:900; color:#1e293b;'>Archiflow - Suite Gestionale</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        # Solo chi ha una data e non è concluso
        df_scad = df[(df['Scadenza'] != "") & (df['Stato'] != "Conclusa")].sort_values(by="Scadenza").head(5)
        for _, r in df_scad.iterrows():
            st.markdown(f'''
                <div class="item-row">
                    <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                    <div class="date-badge">{r["Scadenza"]}</div>
                </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-home"><h3>🏗️ Lavori</h3>', unsafe_allow_html=True)
        for _, r in df.tail(5).iloc[::-1].iterrows():
            st.markdown(f'''
                <div class="item-row">
                    <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                    <span class="pratica-label">{r["Pratica"]}</span>
                </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card-home"><h3>⚠️ Alert</h3>', unsafe_allow_html=True)
        for _, r in df.iterrows():
            mancanti = [k for k, v in inizializza_documenti(r['docs_json'], r['Pratica']).items() if "🔴" in v]
            if mancanti:
                st.markdown(f'''
                    <div class="item-row">
                        <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                        <span class="alert-text">{len(mancanti)}!!</span>
                    </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu == "ANAGRAFICA":
    mostra_anagrafica(conn)
elif st.session_state.menu == "LAVORI":
    mostra_lavori(conn)
