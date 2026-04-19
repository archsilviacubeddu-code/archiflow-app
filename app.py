import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

# 1. SETUP E NOME SUITE
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div.stButton > button {
        border-radius: 12px; font-weight: bold; height: 5em; 
        background-color: white; border: 2px solid #e2e8f0;
    }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #d1d5db !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).fillna("")

# Funzione per l'ID Automatico
def genera_id(dataframe):
    if dataframe.empty or 'id' not in dataframe.columns: return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR (LOGO E NAVIGAZIONE)
with st.sidebar:
    # Cerchiamo il file Logo.png
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.error("⚠️ File 'Logo.png' non trovato!")
        st.header("🏛️ ARCHIFLOW")
    
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- LOGICA PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale 🏛️")
    st.write("### Dashboard Generale")
    st.dataframe(df.tail(10), use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica Clienti")
    
    # Ricerca rapida
    cerca = st.text_input("🔍 Cerca per Nome o Cognome:")
    mask = df['Cliente'].str.contains(cerca, case=False) if (cerca and 'Cliente' in df.columns) else [True] * len(df)
    df_f = df[mask]

    opzioni = ["+ AGGIUNGI NUOVO"] + (df_f['Cliente'].tolist() if not df_f.empty else [])
    scelta = st.selectbox("Seleziona il profilo da gestire:", opzioni)
    
    # Caricamento dati nei box (Editabili, non celle!)
    if scelta == "+ AGGIUNGI NUOVO":
        id_at = genera_id(df)
        dati_f = {col: "" for col in df.columns}
        dati_f['id'] = id_at
    else:
        id_at = df[df['Cliente'] == scelta]['id'].values[0]
        dati_f = df[df['id'] == id_at].iloc[0].to_dict()

    # FORM DI MODIFICA
    with st.form("form_anagrafica"):
        st.subheader(f"Scheda Tecnica ID: {id_at}")
        nuovi_dati = {}
        
        # Genera un box di testo per ogni colonna del tuo foglio Google
        col1, col2 = st.columns(2)
        for i, colonna in enumerate(df.columns):
            if colonna.lower() == 'id':
                nuovi_dati[colonna] = id_at
                continue
            
            target = col1 if i % 2 == 0 else col2
            nuovi_dati[colonna] = target.text_input(f"Modifica {colonna}", value=str(dati_f.get(colonna, "")))
        
        st.divider()
        if st.form_submit_button("💾 SALVA MODIFICHE SU GOOGLE SHEETS"):
            if scelta == "+ AGGIUNGI NUOVO":
                df = pd.concat([df, pd.DataFrame([nuovi_dati])], ignore_index=True)
            else:
                idx = df[df['id'] == id_at].index[0]
                for k, v in nuovi_dati.items(): df.at[idx, k] = v
            
            conn.update(data=df)
            st.success("Dati aggiornati con successo! ✅")
            st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Gestione Cantieri")
    # Qui rimangono i tuoi 5 bottoni giganti per la parte operativa...
