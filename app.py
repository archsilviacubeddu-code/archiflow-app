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

# 2. CSS DEFINITIVO (Scritte giganti, scadenze corte, logo)
st.markdown("""
    <style>
    /* Scritte bottoni Sidebar: PIÙ GRANDI E GRASSETTO */
    section[data-testid="stSidebar"] button div p {
        font-size: 22px !important;
        font-weight: 900 !important;
        color: #1e293b !important;
    }
    
    /* Card Home: MOLTO PIÙ CORTE */
    .card-home {
        background-color: white;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        height: 220px; /* Ridotto drasticamente */
        overflow-y: auto;
        margin-bottom: 10px;
    }
    
    .card-home h3 {
        font-size: 1.3rem !important;
        font-weight: 900;
        border-bottom: 3px solid #1e293b;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }

    /* Clienti e Lavori: SCRITTE PIÙ GRANDI */
    .client-name { 
        font-weight: 900; 
        font-size: 19px !important; /* Molto più grande */
        color: #1e293b; 
    }
    
    .pratica-info {
        font-size: 14px;
        font-weight: 700;
        color: #64748b;
    }

    .item-row {
        padding: 6px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .date-badge { 
        padding: 5px 12px; 
        border-radius: 6px; 
        font-size: 13px; 
        font-weight: 900; 
        background-color: #1e293b; 
        color: white; 
    }

    .status-dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .bg-dafare { background-color: #94a3b8; }
    .bg-corso { background-color: #f59e0b; }
    .bg-conclusa { background-color: #10b981; }
    .bg-annullata { background-color: #ef4444; }
    .bg-sospesa { background-color: #6366f1; }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR COL LOGO
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center;'>🏛️ ARCHIFLOW</h1>", unsafe_allow_html=True)
    
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

# 4. PAGINE
if st.session_state.menu == "HOME":
    st.title("Archiflow - Suite Gestionale")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        df_scad = df[df['Scadenza'] != ""].sort_values(by="Scadenza").head(10)
        for _, r in df_scad.iterrows():
            st.markdown(f'''
                <div class="item-row">
                    <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                    <div class="date-badge">{r["Scadenza"]}</div>
                </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-home"><h3>🏗️ Lavori</h3>', unsafe_allow_html=True)
        for _, r in df.tail(10).iloc[::-1].iterrows():
            st.markdown(f'''
                <div class="item-row">
                    <span class="client-name">{r["Cliente"] if r["Cliente"] else "---"}</span>
                    <span class="pratica-info">{r["Pratica"]}</span>
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
                        <span style="color:#ef4444; font-weight:900; font-size:16px;">{len(mancanti)}!!</span>
                    </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu == "ANAGRAFICA":
    mostra_anagrafica(conn)
elif st.session_state.menu == "LAVORI":
    mostra_lavori(conn)
