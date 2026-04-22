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

# 2. CSS DEFINITIVO - OTTIMIZZATO MOBILE E VISIBILITÀ
st.markdown("""
    <style>
    /* SIDEBAR: Bottoni a 18px e Grassetto */
    section[data-testid="stSidebar"] button div p {
        font-size: 18px !important; 
        font-weight: 900 !important;
        color: #1e293b !important;
        text-transform: uppercase;
    }
    
    /* QUADRATI HOME: ULTRA-COMPATTI (95px) PER MOBILE */
    .card-home {
        background-color: white;
        padding: 4px 10px;
        border-radius: 6px;
        border: 2px solid #cbd5e1;
        height: 95px; 
        overflow-y: auto;
        margin-bottom: 5px;
    }
    
    .card-home h3 {
        font-size: 0.85rem !important;
        font-weight: 900;
        border-bottom: 2px solid #1e293b;
        padding-bottom: 1px;
        margin-bottom: 4px;
        text-transform: uppercase;
        color: #1e293b;
    }

    /* TESTI INTERNI: NOMI CLIENTI BELLI GROSSI */
    .client-name { 
        font-weight: 900; 
        font-size: 16px !important; 
        color: #000000; 
    }
    
    .pratica-label {
        font-size: 12px !important;
        font-weight: 800;
        color: #334155;
    }

    .item-row {
        padding: 2px 0;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* DATE: Visibili ma compatte */
    .date-badge { 
        padding: 2px 6px; 
        border-radius: 4px; 
        font-size: 12px !important; 
        font-weight: 900; 
        background-color: #1e293b; 
        color: #ffffff; 
        min-width: 75px;
        text-align: center;
    }
    
    .alert-text {
        color: #ef4444; 
        font-weight: 900; 
        font-size: 16px !important;
    }

    /* Scrollbar sottile */
    .card-home::-webkit-scrollbar { width: 3px; }
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
    st.markdown("<h2 style='font-weight:900; color:#1e293b; margin-bottom:10px;'>Archiflow - Suite Gestionale</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        # Solo pratiche non concluse
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
