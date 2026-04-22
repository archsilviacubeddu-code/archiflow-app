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

# 2. CSS - CARATTERI RIDOTTI E COMPATTI
st.markdown("""
    <style>
    /* Bottoni Sidebar: Testo più piccolo */
    section[data-testid="stSidebar"] button div p {
        font-size: 14px !important; /* Ridotto da 20 */
        font-weight: 700 !important;
        color: #1e293b !important;
        text-transform: uppercase;
    }
    
    /* QUADRATI HOME: BASSI */
    .card-home {
        background-color: white;
        padding: 5px 10px;
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        height: 110px; 
        overflow-y: auto;
        margin-bottom: 5px;
    }
    
    .card-home h3 {
        font-size: 0.85rem !important; /* Titolo card più piccolo */
        font-weight: 900;
        border-bottom: 2px solid #1e293b;
        padding-bottom: 2px;
        margin-bottom: 5px;
        text-transform: uppercase;
        color: #1e293b;
    }

    /* Testi Nomi Clienti: Più piccoli e puliti */
    .client-name { 
        font-weight: 700; 
        font-size: 13px !important; /* Ridotto da 18 */
        color: #000000; 
    }
    
    .pratica-label {
        font-size: 11px !important; /* Ridotto da 14 */
        font-weight: 600;
        color: #475569;
    }

    .item-row {
        padding: 3px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* DATE: Più piccole e discrete */
    .date-badge { 
        padding: 2px 6px; 
        border-radius: 4px; 
        font-size: 11px !important; /* Ridotto da 14 */
        font-weight: 800; 
        background-color: #1e293b; 
        color: #ffffff; 
        min-width: 70px;
        text-align: center;
    }
    
    .alert-text {
        color: #ef4444; 
        font-weight: 900; 
        font-size: 14px !important; /* Ridotto da 18 */
    }

    /* Scrollbar sottile */
    .card-home::-webkit-scrollbar { width: 3px; }
    .card-home::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR CON LOGO
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.markdown("<h3 style='text-align:center;'>🏛️ ARCHIFLOW</h3>", unsafe_allow_html=True)
    
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
    st.markdown("<h3 style='font-weight:900; color:#1e293b; margin-bottom:15px;'>Archiflow - Suite Gestionale</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
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
