import streamlit as st
import pandas as pd
import os
from gestione_documenti import interfaccia_semafori, widget_alert_home

# 1. SETUP GENERALE E CSS (IDENTICO ALL'ORIGINALE)
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    .sidebar-btn > div > button { height: 4.5em !important; font-weight: bold !important; font-size: 18px !important; margin-bottom: 12px !important; border-radius: 12px !important; background-color: white !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; }
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 8em !important; font-size: 18px !important; border-radius: 15px !important; font-weight: bold !important; }
    div[data-testid="column"] button[key^="up_"], div[data-testid="column"] button[key^="op_"], div[data-testid="column"] button[key^="del_"] { height: 110px !important; width: 100% !important; border-radius: 15px !important; font-weight: 700 !important; text-transform: uppercase !important; border: 2px solid #e2e8f0 !important; background-color: white !important; }
    div[data-testid="column"] button[key^="del_"] { background-color: #fee2e2 !important; border-color: #ef4444 !important; color: #ef4444 !important; }
    .table-header { background-color: #f1f5f9; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 5px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARICAMENTO DATI
DB_FILE = "database_archiflow.csv"
DB_CANTIERI = "cantieri.csv"
COL_ANAGRAFICA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]

def carica_dati(file, colonne):
    if os.path.exists(file):
        df = pd.read_csv(file, dtype=str).fillna("")
        for col in colonne:
            if col not in df.columns: df[col] = ""
        return df[colonne]
    return pd.DataFrame(columns=colonne)

df = carica_dati(DB_FILE, COL_ANAGRAFICA)
df_can = carica_dati(DB_CANTIERI, ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note", "docs_json"])

# 3. SIDEBAR
with st.sidebar:
    st.title("ARCHIFLOW")
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.session_state.sotto_menu = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGICA PAGINE ---

if st.session_state.menu_sel == "HOME":
    st.title("Benvenuta Arch. Cubeddu")
    widget_alert_home(df_can)
    st.divider()
    st.subheader("Scadenze e Pratiche")
    st.dataframe(df[["Cliente", "Pratica", "Scadenza", "Stato"]], use_container_width=True, hide_index=True)

elif st.session_state.menu_sel == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    h = st.columns([1.5, 1.5, 1.5, 1, 1, 1, 1, 4.5])
    labels = ["Cliente", "C.F./P.IVA", "Indirizzo", "Telefono", "Email", "Pratica", "Stato", "Azioni"]
    for i, label in enumerate(labels): h[i].markdown(f'<div class="table-header">{label}</div>', unsafe_allow_html=True)
    for i, r in df.iterrows():
        c = st.columns([1.5, 1.5, 1.5, 1, 1, 1, 1, 4.5])
        u_cli = c[0].text_input("Cli", r['Cliente'], key=f"cli_{i}", label_visibility="collapsed")
        u_cf = c[1].text_input("CF", r['C.F. / P.IVA'], key=f"cf_{i}", label_visibility="collapsed")
        u_ind = c[2].text_input("Ind", r['Indirizzo'], key=f"ind_{i}", label_visibility="collapsed")
        u_tel = c[3].text_input("Tel", r['Telefono'], key=f"tel_{i}", label_visibility="collapsed")
        u_mail = c[4].text_input("Mail", r['Email'], key=f"mail_{i}", label_visibility="collapsed")
        u_pra = c[5].text_input("Pra", r['Pratica'], key=f"pra_{i}", label_visibility="collapsed")
        u_sta = c[6].selectbox("Sta", ["Attivo", "Chiuso"], index=0 if r['Stato']=="Attivo" else 1, key=f"sta_{i}", label_visibility="collapsed")
        btns = c[7].columns(3)
        if btns[0].button("🔄\nAGGIORNA", key=f"up_{i}"):
            df.loc[i] = [r['id'], u_cli, u_cf, u_ind, r['CAP'], r['Città'], u_tel, u_mail, r['Web'], u_pra, u_sta, r['Scadenza'], r['Note']]
            df.to_csv(DB_FILE, index=False); st.rerun()
        if btns[1].button("📂\nAPRI", key=f"op_{i}"): st.info(f"Scheda {u_cli}")
        if btns[2].button("🗑️\nCANCELLA", key=f"del_{i}"):
            df.drop(i).to_csv(DB_FILE, index=False); st.rerun()

elif st.session_state.menu_sel == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        if st.session_state.get("c_aperto"):
            id_c = st.session_state.c_aperto
            idx_can = df_can[df_can['id_cantiere'] == id_c].index[0]
            if st.button("⬅️ TORNA ALLA LISTA"): st.session_state.c_aperto = None; st.rerun()
            t1, t2 = st.tabs(["📋 DOCUMENTI", "🎙️ DIARIO"])
            with t1:
                if interfaccia_semafori(id_c, df_can, idx_can):
                    df_can.to_csv(DB_CANTIERI, index=False); st.rerun()
            with t2:
                nuove_note = st.text_area("Note:", value=df_can.at[idx_can, 'Note'], height=200)
                if st.button("💾 SALVA NOTE"):
                    df_can.at[idx_can, 'Note'] = nuove_note
                    df_can.to_csv(DB_CANTIERI, index=False); st.toast("Salvate!")
        else:
            for i, r in df_can.iterrows():
                col1, col2, col_btns = st.columns([2, 2, 4.5])
                col1.write(f"**{r['Cliente']}**"); col2.write(r['Indirizzo'])
                b = col_btns.columns(3)
                if b[1].button("📂\nAPRI SCHEDA", key=f"op_can_{i}"):
                    st.session_state.c_aperto = r['id_cantiere']; st.rerun()
                if b[2].button("🗑️\nCANCELLA", key=f"del_can_{i}"):
                    df_can.drop(i).to_csv(DB_CANTIERI, index=False); st.rerun()
    else:
        st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
        if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True): 
            st.session_state.sotto_menu = "DL"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
