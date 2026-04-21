import streamlit as st
import pandas as pd
import os
from gestione_documenti import interfaccia_semafori, widget_alert_home

# 1. SETUP GENERALE E CSS (TUA FORMATTAZIONE ORIGINALE)
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

    /* BOTTONI DASHBOARD - ROSSI E GIGANTI */
    .btn-dl > div > button { 
        background-color: #E63946 !important; 
        color: white !important; 
        height: 8em !important; 
        font-size: 18px !important; 
        border-radius: 15px !important; 
        font-weight: bold !important; 
    }
    
    /* TASTI DIREZIONE LAVORI (UPDATE/OPEN/DELETE) */
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
    }

    div[data-testid="column"] button[key^="del_"] {
        background-color: #fee2e2 !important;
        border-color: #ef4444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARICAMENTO DATI (Sincronizzato)
DB_CANTIERI = "cantieri.csv"
def carica_cantieri():
    if os.path.exists(DB_CANTIERI):
        df = pd.read_csv(DB_CANTIERI, dtype=str).fillna("")
        if 'docs_json' not in df.columns: df['docs_json'] = "{}"
        return df
    return pd.DataFrame(columns=["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note", "docs_json"])

df_can = carica_cantieri()

# 3. SIDEBAR (MENU ICONICO)
with st.sidebar:
    st.title("ARCHIFLOW")
    st.divider()
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.session_state.sotto_menu = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGICA PAGINE ---

if st.session_state.menu_sel == "HOME":
    st.title("Benvenuta Arch. Cubeddu")
    widget_alert_home(df_can) # L'alert intelligente sotto il benvenuto
    st.divider()
    st.subheader("Riepilogo Cantieri Attivi")
    st.dataframe(df_can[["Cliente", "Indirizzo", "Stato"]], use_container_width=True, hide_index=True)

elif st.session_state.menu_sel == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        if st.session_state.get("c_aperto"):
            id_c = st.session_state.c_aperto
            idx = df_can[df_can['id_cantiere'] == id_c].index[0]
            
            if st.button("⬅️ TORNA ALLA LISTA CANTIERI"): 
                st.session_state.c_aperto = None; st.rerun()
            
            st.subheader(f"Cantiere: {df_can.at[idx, 'Cliente']}")
            
            tab1, tab2 = st.tabs(["📋 DOCUMENTI E SEMAFORI", "🎙️ DIARIO DI CANTIERE"])
            with tab1:
                if interfaccia_semafori(id_c, df_can, idx):
                    df_can.to_csv(DB_CANTIERI, index=False)
                    st.success("Stato documentale aggiornato!")
                    st.rerun()
            with tab2:
                st.write("### Note e Diario")
                nuove_note = st.text_area("Appunti sopralluogo:", value=df_can.at[idx, 'Note'], height=200)
                if st.button("💾 SALVA NOTE"):
                    df_can.at[idx, 'Note'] = nuove_note
                    df_can.to_csv(DB_CANTIERI, index=False)
                    st.toast("Note salvate!")
        else:
            # Lista cantieri con i tuoi tasti giganti
            for i, r in df_can.iterrows():
                col1, col2, col_btns = st.columns([2, 2, 4])
                col1.write(f"**{r['Cliente']}**")
                col2.write(r['Indirizzo'])
                
                c1, c2, c3 = col_btns.columns(3)
                if c2.button("📂\nAPRI SCHEDA", key=f"op_{i}"):
                    st.session_state.c_aperto = r['id_cantiere']; st.rerun()
                if c3.button("🗑️\nCANCELLA", key=f"del_{i}"):
                    df_can.drop(i).to_csv(DB_CANTIERI, index=False); st.rerun()
    else:
        # Dashboard Lavori con tasto rosso gigante
        st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
        if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True): 
            st.session_state.sotto_menu = "DL"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
