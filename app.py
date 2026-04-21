import streamlit as st
import pandas as pd
import os
from gestione_documenti import interfaccia_semafori, widget_alert_home

st.set_page_config(page_title="Archiflow Suite", layout="wide")

# Database dei cantieri
DB_CANTIERI = "cantieri.csv"

def carica_dati():
    if os.path.exists(DB_CANTIERI):
        df = pd.read_csv(DB_CANTIERI, dtype=str).fillna("")
        if 'docs_json' not in df.columns:
            df['docs_json'] = "{}"
        return df
    return pd.DataFrame(columns=["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note", "docs_json"])

df_can = carica_dati()

# Menu Laterale
with st.sidebar:
    st.title("ARCHIFLOW")
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    if st.button("🏠 HOME", use_container_width=True): 
        st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): 
        st.session_state.menu_sel = "LAVORI"; st.session_state.sotto_menu = None; st.rerun()

# Logica Pagine
if st.session_state.menu_sel == "HOME":
    st.title("Benvenuta Arch. Cubeddu")
    widget_alert_home(df_can) # Qui compaiono gli alert automatici

elif st.session_state.menu_sel == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        if st.session_state.get("c_aperto"):
            id_c = st.session_state.c_aperto
            idx = df_can[df_can['id_cantiere'] == id_c].index[0]
            if st.button("⬅️ Torna alla lista"): 
                st.session_state.c_aperto = None; st.rerun()
            
            tab1, tab2 = st.tabs(["📋 Documenti", "🎙️ Diario"])
            with tab1:
                # Interfaccia a semafori
                if interfaccia_semafori(id_c, df_can, idx):
                    df_can.to_csv(DB_CANTIERI, index=False)
                    st.success("Salvataggio completato!")
                    st.rerun()
        else:
            for i, r in df_can.iterrows():
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{r['Cliente']}** - {r['Indirizzo']}")
                if col2.button("📂 APRI", key=f"op_{i}"):
                    st.session_state.c_aperto = r['id_cantiere']; st.rerun()
    else:
        if st.button("🚧 DIREZIONE LAVORI", use_container_width=True): 
            st.session_state.sotto_menu = "DL"; st.rerun()
