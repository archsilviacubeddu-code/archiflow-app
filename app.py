import streamlit as st
import pandas as pd
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_lavori import mostra_lavori
from gestione_documenti import widget_alert_home, inizializza_documenti

# 1. SETUP GENERALE
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS "CATTIVO": Colpiamo direttamente il testo dentro i bottoni della sidebar
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* SELETTORE SPECIFICO PER IL TESTO DEI BOTTONI NELLA SIDEBAR */
    div[data-testid="stSidebar"] button p {
        font-weight: 900 !important;
        font-style: italic !important;
        font-size: 24px !important;
        color: #1e293b !important;
        font-family: 'Source Sans Pro', sans-serif !important;
    }

    /* CONTAINER BOTTONI SIDEBAR */
    .sidebar-btn > div > button {
        height: 5.5em !important;
        margin-bottom: 15px !important;
        border-radius: 15px !important;
        border: 2px solid #cbd5e1 !important;
        background-color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .sidebar-btn > div > button:hover {
        border: 2px solid #457B9D !important;
        background-color: #f1f5f9 !important;
    }

    /* CARD HOME: Pulizia e proporzioni */
    .card-home {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .card-home h3 {
        color: #0f172a;
        font-size: 1.6rem !important;
        font-weight: 800;
        margin-bottom: 20px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 10px;
    }

    .item-row {
        padding: 15px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .item-row:last-child { border-bottom: none; }
    
    .client-name { font-weight: 800; color: #1e293b; font-size: 20px !important; }
    .pratica-type { color: #64748b; font-size: 13px; text-transform: uppercase; font-weight: 600; margin-left: 10px; }
    
    .date-badge {
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 14px;
        font-weight: 800;
        background-color: #1e293b;
        color: white;
    }

    .status-dot { height: 16px; width: 16px; border-radius: 50%; display: inline-block; }
    .bg-red { background-color: #ef4444; }
    .bg-yellow { background-color: #f59e0b; }
    .bg-green { background-color: #10b981; }
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
        st.markdown("<h1 style='font-style: italic; text-align:center;'>🏛️ ARCHIFLOW</h1>", unsafe_allow_html=True)
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
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

df_globale = carica_db()

# --- HOME PAGE ---
if st.session_state.menu_sel == "HOME":
    st.title("Archiflow - Suite Gestionale")
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card-home"><h3>🚦 Scadenze</h3>', unsafe_allow_html=True)
        df_scad = df_globale[df_globale['Scadenza'] != ""].copy()
        if not df_scad.empty:
            for _, r in df_scad.sort_values(by="Scadenza").head(8).iterrows():
                st_l = r['Stato'].lower()
                dot = "bg-red"
                if "corso" in st_l: dot = "bg-yellow"
                elif "chius" in st_l: dot = "bg-green"
                st.markdown(f'<div class="item-row"><div style="display:flex;align-items:center;gap:10px;"><span class="status-dot {dot}"></span><div><span class="client-name">{r["Cliente"]}</span><span class="pratica-type">{r["Pratica"]}</span></div></div><div class="date-badge">{r["Scadenza"]}</div></div>', unsafe_allow_html=True)
        else: st.info("Nessuna scadenza.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-home"><h3>🆕 Ultimi Lavori</h3>', unsafe_allow_html=True)
        if not df_globale.empty:
            for _, r in df_globale.tail(8).iloc[::-1].iterrows():
                if r['Cliente'].strip() != "":
                    st.markdown(f'<div class="item-row"><div><span class="client-name">{r["Cliente"]}</span><span class="pratica-type">{r["Pratica"]}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card-home"><h3>⚠️ Alert Documenti</h3>', unsafe_allow_html=True)
        alert_found = False
        if not df_globale.empty:
            for _, r in df_globale.iterrows():
                docs = inizializza_documenti(r['docs_json'])
                mancanti = [k for k, v in docs.items() if "🔴" in v or "🟡" in v]
                if mancanti:
                    alert_found = True
                    st.markdown(f'<div class="item-row"><div><span class="client-name">{r["Cliente"]}</span><span class="pratica-type" style="color:#ef4444;">Mancano {len(mancanti)} doc.</span></div></div>', unsafe_allow_html=True)
        if not alert_found: st.success("Documenti OK.")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_sel == "ANAGRAFICA":
    mostra_anagrafica(df_globale, DB_FILE, COLONNE)
elif st.session_state.menu_sel == "LAVORI":
    mostra_lavori(df_globale, DB_FILE)
