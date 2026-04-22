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

# 2. CSS DEFINITIVO
st.markdown("""
    <style>
    /* Bottoni Sidebar: Grandi e Grassetto */
    section[data-testid="stSidebar"] button div p {
        font-size: 20px !important;
        font-weight: 900 !important;
        color: #1e293b !important;
        text-transform: uppercase;
    }
    
    /* QUADRATI HOME: ALTEZZA MINIMA (100px) */
    .card-home {
        background-color: white;
        padding: 5px 12px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        height: 100px; 
        overflow-y: auto;
        margin-bottom: 5px;
    }
    
    .card-home h3 {
        font-size: 0.9rem !important;
        font-weight: 900;
        border-bottom: 2px solid #1e293b;
        padding-bottom: 2px;
        margin-bottom: 5px;
        text-transform: uppercase;
        color: #1e293b;
    }

    /* Testi Nomi e Clienti: +2 caratteri più grossi */
    .client-name { 
        font-weight: 900; 
        font-size: 17px !important; /* Aumentato da 14/15 a 17 */
        color: #1e293b; 
    }
    
    .pratica-label {
        font-size: 13px !important; /* Aumentato da 11 a 13 */
        font-weight: 700;
        color: #475569;
    }

    .item-row {
        padding: 4px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .date-badge { 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 12px; 
        font-weight: 900; 
        background-color: #1e293b; 
        color: white; 
    }
    
    /* Scrollbar minimal */
    .card-home::-webkit-scrollbar { width: 3px; }
    .card-home::-webkit-scrollbar-thumb { background: #e2e8f0; }
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
    st.markdown("<h2 style='font-weight:900;'>Archiflow - Suite Gestionale</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        df_scad = df[df['Scadenza'] != ""].sort_values(by="Scadenza").head(5)
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
                        <span style="color:#ef4444; font-weight:900; font-size:15px;">{len(mancanti)}!!</span>
                    </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu == "ANAGRAFICA":
    mostra_anagrafica(conn)
elif st.session_state.menu == "LAVORI":
    mostra_lavori(conn)
