import streamlit as st
import pandas as pd
import os
from gestione_anagrafica import mostra_anagrafica
from gestione_documenti import interfaccia_semafori, widget_alert_home

# SETUP E CSS ORIGINALE
st.set_page_config(page_title="Archiflow Suite", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    .sidebar-btn > div > button { height: 4.5em !important; font-weight: bold !important; font-size: 18px !important; margin-bottom: 12px !important; border-radius: 12px !important; background-color: white !important; }
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    div[data-testid="column"] button[key^="up_"], div[data-testid="column"] button[key^="op_"], div[data-testid="column"] button[key^="del_"] { height: 110px !important; width: 100% !important; border-radius: 15px !important; font-weight: 700 !important; text-transform: uppercase !important; border: 2px solid #e2e8f0 !important; background-color: white !important; }
    div[data-testid="column"] button[key^="del_"] { background-color: #fee2e2 !important; border-color: #ef4444 !important; color: #ef4444 !important; }
    .table-header { background-color: #f1f5f9; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 5px; border: 1px solid #e2e8f0; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# CARICAMENTO DATI
DB_FILE = "database_archiflow.csv"
DB_CANTIERI = "cantieri.csv"
COL_ANAGRAFICA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]

def carica(file, colonne):
    if os.path.exists(file):
        df = pd.read_csv(file, dtype=str).fillna("")
        for col in colonne:
            if col not in df.columns: df[col] = ""
        return df[colonne]
    return pd.DataFrame(columns=colonne)

df_ana = carica(DB_FILE, COL_ANAGRAFICA)
df_can = carica(DB_CANTIERI, ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note", "docs_json"])

# SIDEBAR
with st.sidebar:
    st.title("ARCHIFLOW")
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.session_state.sotto_menu = None; st.rerun()

# PAGINE
if st.session_state.menu_sel == "HOME":
    st.title("Benvenuta Arch. Cubeddu")
    widget_alert_home(df_can)
    st.dataframe(df_ana[["Cliente", "Pratica", "Stato"]], use_container_width=True, hide_index=True)

elif st.session_state.menu_sel == "ANAGRAFICA":
    mostra_anagrafica(df_ana, DB_FILE, COL_ANAGRAFICA) # Chiama il file dell'anagrafica

elif st.session_state.menu_sel == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        if st.session_state.get("c_aperto"):
            id_c = st.session_state.c_aperto
            idx = df_can[df_can['id_cantiere'] == id_c].index[0]
            if st.button("⬅️ LISTA"): st.session_state.c_aperto = None; st.rerun()
            t1, t2 = st.tabs(["📋 DOCS", "🎙️ DIARIO"])
            with t1:
                if interfaccia_semafori(id_c, df_can, idx):
                    df_can.to_csv(DB_CANTIERI, index=False); st.rerun()
            with t2:
                n = st.text_area("Note:", value=df_can.at[idx, 'Note'], height=200)
                if st.button("💾 SALVA"):
                    df_can.at[idx, 'Note'] = n
                    df_can.to_csv(DB_CANTIERI, index=False); st.toast("Salvate!")
        else:
            for i, r in df_can.iterrows():
                c1, c2, c3 = st.columns([2, 2, 4])
                c1.write(r['Cliente']); c2.write(r['Indirizzo'])
                if c3.button("📂 APRI SCHEDA", key=f"op_c_{i}"):
                    st.session_state.c_aperto = r['id_cantiere']; st.rerun()
    else:
        st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
        if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True): 
            st.session_state.sotto_menu = "DL"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
