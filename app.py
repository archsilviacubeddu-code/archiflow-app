import streamlit as st
import pandas as pd
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import widget_alert_home, inizializza_documenti

# 1. SETUP GENERALE
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS AGGRESSIVO: Riordino dei pesi visivi per non avere vuoti schifosi
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Card Home: Altezza flessibile ma contenuto centrato */
    .card-home {
        background-color: white;
        padding: 35px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
    }
    
    /* Titoli Card - Imponenti */
    .card-home h3 {
        color: #0f172a;
        font-size: 1.9rem !important;
        font-weight: 800;
        margin-bottom: 25px;
        border-bottom: 3px solid #334155;
        padding-bottom: 10px;
    }

    /* Righe della lista - Spaziate per riempire il quadrato */
    .item-row {
        padding: 18px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .item-row:last-child { border-bottom: none; }
    
    .info-box { display: flex; align-items: center; gap: 15px; }
    
    /* Testi molto più grandi */
    .client-name { 
        font-weight: 800; 
        color: #1e293b; 
        font-size: 22px !important; 
        line-height: 1.2;
    }
    
    .pratica-type { 
        color: #64748b; 
        font-size: 15px; 
        text-transform: uppercase; 
        letter-spacing: 1.2px; 
        font-weight: 600;
    }
    
    .date-badge {
        padding: 10px 18px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 800;
        background-color: #1e293b;
        color: white;
        min-width: 110px;
        text-align: center;
    }

    /* Semafori - Più visibili */
    .status-dot {
        height: 20px;
        width: 20px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }
    .bg-red { background-color: #ef4444; box-shadow: 0 0 12px rgba(239, 68, 68, 0.5); }
    .bg-yellow { background-color: #f59e0b; box-shadow: 0 0 12px rgba(245, 158, 11, 0.5); }
    .bg-green { background-color: #10b981; box-shadow: 0 0 12px rgba(16, 185, 129, 0.5); }
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
    if os.path.exists("Logo.png"): st.image("Logo.png", use_container_width=True)
    st.divider()
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

df_globale = carica_db()

if st.session_state.menu_sel == "HOME":
    st.title("Archiflow - Suite Gestionale")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1: # SCADENZE
        st.markdown('<div class="card-home"><h3>🚦 Scadenze Lavori</h3>', unsafe_allow_html=True)
        df_scad = df_globale[df_globale['Scadenza'] != ""].copy()
        if not df_scad.empty:
            # Mostriamo i primi 6 per non far esplodere la card
            for _, r in df_scad.sort_values(by="Scadenza").head(6).iterrows():
                stato = r['Stato'].lower()
                dot_color = "bg-red"
                if "corso" in stato: dot_color = "bg-yellow"
                elif "chius" in stato: dot_color = "bg-green"
                
                st.markdown(f"""
                    <div class="item-row">
                        <div class="info-box">
                            <span class="status-dot {dot_color}"></span>
                            <div>
                                <span class="client-name">{r['Cliente']}</span><br>
                                <span class="pratica-type">{r['Pratica']}</span>
                            </div>
                        </div>
                        <div class="date-badge">{r['Scadenza']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else: st.info("Nessuna scadenza.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2: # ULTIMI
        st.markdown('<div class="card-home"><h3>🆕 Ultimi Lavori</h3>', unsafe_allow_html=True)
        if not df_globale.empty:
            for _, r in df_globale.tail(6).iloc[::-1].iterrows():
                if r['Cliente'].strip() != "":
                    st.markdown(f"""
                        <div class="item-row">
                            <div class="info-box">
                                <div>
                                    <span class="client-name">{r['Cliente']}</span><br>
                                    <span class="pratica-type">{r['Pratica']}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3: # ALERT
        st.markdown('<div class="card-home"><h3>⚠️ Alert Documenti</h3>', unsafe_allow_html=True)
        alert_found = False
        if not df_globale.empty:
            # Mostriamo solo i primi 6 alert per estetica
            count = 0
            for _, r in df_globale.iterrows():
                if count < 6:
                    docs = inizializza_documenti(r['docs_json'])
                    mancanti = [k for k, v in docs.items() if "🔴" in v or "🟡" in v]
                    if mancanti:
                        alert_found = True
                        count += 1
                        st.markdown(f"""
                            <div class="item-row">
                                <div>
                                    <span class="client-name">{r['Cliente']}</span><br>
                                    <span class="pratica-type" style="color: #ef4444;">Mancano {len(mancanti)} documenti</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
        if not alert_found: st.success("Tutto in regola.")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_sel == "ANAGRAFICA":
    mostra_anagrafica(df_globale, DB_FILE, COLONNE)
elif st.session_state.menu_sel == "LAVORI":
    mostra_lavori(df_globale, DB_FILE)
