import streamlit as st
import pandas as pd
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import widget_alert_home, inizializza_documenti

# 1. SETUP GENERALE
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS PROFESSIONALE: Card pulite, niente tabelle, semafori tondi e luminosi
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Stile Card Home */
    .card-home {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        min-height: 400px;
    }
    
    /* Titoli Card */
    .card-home h3 {
        color: #1e293b;
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 12px;
    }

    /* Righe della lista (Sostituiscono le tabelle brutte) */
    .item-row {
        padding: 14px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .item-row:last-child { border-bottom: none; }
    
    .info-box { display: flex; align-items: center; gap: 12px; }
    .client-name { font-weight: 700; color: #334155; font-size: 15px; display: block; }
    .pratica-type { color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
    
    .date-badge {
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        background-color: #f1f5f9;
        color: #475569;
    }

    /* Semafori Dinamici */
    .status-dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }
    .bg-red { background-color: #ef4444; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
    .bg-yellow { background-color: #f59e0b; box-shadow: 0 0 10px rgba(245, 158, 11, 0.4); }
    .bg-green { background-color: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# 2. CONFIGURAZIONE DATABASE
DB_FILE = "database_archiflow.csv"
COLONNE = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note", "docs_json"]

def carica_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype=str).fillna("")
        for c in COLONNE:
            if c not in df.columns: df[c] = ""
        return df[COLONNE]
    return pd.DataFrame(columns=COLONNE)

# 3. NAVIGAZIONE SIDEBAR
if "menu_sel" not in st.session_state: 
    st.session_state.menu_sel = "HOME"

with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #1e293b;'>🏛️ ARCHIFLOW</h1>", unsafe_allow_html=True)
        st.divider()
    
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

df_globale = carica_db()
menu = st.session_state.menu_sel

if menu == "HOME":
    st.title("Archiflow - Suite Gestionale")
    st.write("Quadro generale delle attività.")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1: # CARD SCADENZE CON SEMAFORI
        st.markdown('<div class="card-home"><h3>🚦 Scadenze Lavori</h3>', unsafe_allow_html=True)
        df_scad = df_globale[df_globale['Scadenza'] != ""].copy()
        if not df_scad.empty:
            df_scad = df_scad.sort_values(by="Scadenza")
            for _, r in df_scad.iterrows():
                # Logica Colore Semaforo
                stato = r['Stato'].lower()
                dot_color = "bg-red" # Default
                if "corso" in stato: dot_color = "bg-yellow"
                elif "chius" in stato: dot_color = "bg-green"
                elif "annull" in stato: dot_color = "bg-red"

                st.markdown(f"""
                    <div class="item-row">
                        <div class="info-box">
                            <span class="status-dot {dot_color}"></span>
                            <div>
                                <span class="client-name">{r['Cliente']}</span>
                                <span class="pratica-type">{r['Pratica']}</span>
                            </div>
                        </div>
                        <div class="date-badge">{r['Scadenza']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nessuna scadenza imminente.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2: # CARD ULTIMI INSERIMENTI
        st.markdown('<div class="card-home"><h3>🆕 Ultimi Lavori</h3>', unsafe_allow_html=True)
        if not df_globale.empty:
            for _, r in df_globale.tail(5).iloc[::-1].iterrows():
                st.markdown(f"""
                    <div class="item-row">
                        <div class="info-box">
                            <div>
                                <span class="client-name">{r['Cliente']}</span>
                                <span class="pratica-type">{r['Pratica']}</span>
                            </div>
                        </div>
                        <div class="date-badge">ID {r['id']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Database vuoto.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3: # CARD ALERT DOCUMENTI
        st.markdown('<div class="card-home"><h3>⚠️ Alert Documenti</h3>', unsafe_allow_html=True)
        alert_found = False
        if not df_globale.empty:
            for _, r in df_globale.iterrows():
                docs = inizializza_documenti(r['docs_json'])
                mancanti = [k for k, v in docs.items() if "🔴" in v or "🟡" in v]
                if mancanti:
                    alert_found = True
                    st.markdown(f"""
                        <div class="item-row">
                            <div class="info-box">
                                <div>
                                    <span class="client-name">{r['Cliente']}</span>
                                    <span class="pratica-type" style="color: #ef4444;">Mancano {len(mancanti)} documenti</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        if not alert_found:
            st.success("Tutti i documenti sono in regola.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "ANAGRAFICA":
    mostra_anagrafica(df_globale, DB_FILE, COLONNE)

elif menu == "LAVORI":
    mostra_lavori(df_globale, DB_FILE)
