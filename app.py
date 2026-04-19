import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* MENU A SINISTRA: Bottoni grossi e accattivanti */
    [data-testid="stSidebarNav"] {display: none;} /* Nasconde il menu default */
    
    .sidebar-btn > div > button {
        height: 4em !important;
        font-weight: bold !important;
        font-size: 18px !important;
        margin-bottom: 10px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #ffffff !important;
        color: #1e293b !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: 0.3s !important;
    }
    .sidebar-btn > div > button:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
        background-color: #f0f7ff !important;
    }

    /* Pulsanti GIGANTI E COLORATI PAGINA LAVORI */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }

    .stButton > button:hover { opacity: 0.9 !important; transform: translateY(-2px); transition: 0.3s; }
    
    /* Lista anagrafica piccola */
    .list-btn > div > button { border-radius: 8px; height: 2.5em; font-size: 13px !important; font-weight: normal !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE LOCALE
DB_FILE = "database_archiflow.csv"

def carica_dati():
    colonne = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'id': str}).fillna("")
    else:
        return pd.DataFrame(columns=colonne)

def salva_dati(dataframe):
    dataframe.to_csv(DB_FILE, index=False)

df = carica_dati()

# 3. SIDEBAR CUSTOM (BOTTONI GROSSI)
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    st.divider()
    
    if "menu_sel" not in st.session_state:
        st.session_state.menu_sel = "HOME"

    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"
    if st.button("📅 SCADENZE", use_container_width=True): st.session_state.menu_sel = "SCADENZE"
    st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_sel

# --- LOGICA PAGINE ---

if menu == "HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.subheader("📅 Scadenze in Corso")
    if not df.empty and "Scadenza" in df.columns:
        scad_view = df[df['Scadenza'] != ""][['Cliente', 'Pratica', 'Scadenza', 'Stato']]
        st.dataframe(scad_view, use_container_width=True, hide_index=True)
    st.divider()
    st.write("### Vista Totale")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"
        st.session_state.cliente_sel = None
        st.rerun()

    col_list, col_form = st.columns([1, 2])
    with col_list:
        cerca = st.text_input("🔍 Filtra:")
        df_f = df[df['Cliente'].str.contains(cerca, case=False)] if cerca else df
        for _, row in df_f.iterrows():
            st.markdown('<div class="list-btn">', unsafe_allow_html=True)
            if st.button(f"👤 {row['Cliente']}", key=f"l_{row['id']}", use_container_width=True):
                st.session_state.modo = "modifica"
                st.session_state.cliente_sel = row['id']
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col_form:
        id_at = st.session_state.get('cliente_sel')
        modo = st.session_state.get('modo')
        
        if modo == "aggiungi":
            id_at = str(int(pd.to_numeric(df['id']).max() + 1)) if not df.empty else "1"
            dati_f = {col: "" for col in df.columns}
        elif modo == "modifica" and id_at:
            dati_f = df[df['id'] == id_at].iloc[0].to_dict()
        else:
            st.info("Seleziona un cliente o clicca AGGIUNGI")
            st.stop()

        with st.form("form_ana"):
            nuovi = {"id": id_at}
            c1, c2 = st.columns(2)
            for i, col in enumerate(df.columns[1:]):
                target = c1 if i % 2 == 0 else c2
                nuovi[col] = target.text_input(col, value=str(dati_f.get(col, "")))
            if st.form_submit_button("✅ CONFERMA"):
                if modo == "aggiungi":
                    df = pd.concat([df, pd.DataFrame([nuovi])], ignore_index=True)
                else:
                    idx = df[df['id'] == id_at].index[0]
                    for k, v in nuovi.items(): df.at[idx, k] = v
                salva_dati(df)
                st.session_state.modo = None
                st.rerun()

elif menu == "LAVORI":
    # SOLO I BOTTONI GIGANTI
    st.write("## ")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
        if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True): st.toast("DL Selezionata")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-ril">', unsafe_allow_html=True)
        if st.button("📐\nRILIEVI", use_container_width=True): st.toast("Rilievi Selezionati")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="btn-pra">', unsafe_allow_html=True)
        if st.button("📋\nPRATICHE\nCILA/SCIA", use_container_width=True): st.toast("Pratiche Selezionate")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-mill">', unsafe_allow_html=True)
        if st.button("📊\nMILLESIMI", use_container_width=True): st.toast("Millesimi Selezionati")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c3:
        st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
        if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True): st.toast("APE/L10 Selezionata")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-alt">', unsafe_allow_html=True)
        if st.button("➕\nALTRO", use_container_width=True): st.toast("Altro Selezionato")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "SCADENZE":
    st.header("📅 Scadenzario Generale")
    st.divider()
    st.dataframe(df[['Cliente', 'Pratica', 'Scadenza', 'Stato']], use_container_width=True, hide_index=True)
