import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

# 1. SETUP SUITE
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

def genera_id(dataframe):
    if dataframe.empty or 'id' not in dataframe.columns: return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    else:
        st.header("ARCHIFLOW")
    
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.dataframe(df.tail(10), use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    # PULSANTE AGGIUNGI NUOVO IN ALTO
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.scelta_cliente = "+ AGGIUNGI NUOVO"
        st.rerun()

    # RICERCA
    cerca = st.text_input("🔍 Cerca cliente:")
    df_f = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    opzioni = ["+ AGGIUNGI NUOVO"] + (df_f['Cliente'].tolist() if 'Cliente' in df.columns else [])
    
    if 'scelta_cliente' not in st.session_state:
        st.session_state.scelta_cliente = opzioni[0]

    scelta = st.selectbox("Seleziona profilo:", opzioni, index=opzioni.index(st.session_state.scelta_cliente) if st.session_state.scelta_cliente in opzioni else 0)
    
    # CARICAMENTO DATI
    if scelta == "+ AGGIUNGI NUOVO":
        id_at = genera_id(df)
        dati_f = {col: "" for col in df.columns}
        dati_f['id'] = id_at
    else:
        id_at = df[df['Cliente'] == scelta]['id'].values[0]
        dati_f = df[df['id'] == id_at].iloc[0].to_dict()

    # FORM DI EDITING SOTTO IL CERCA
    with st.form("form_anagrafica_totale"):
        st.write(f"### Scheda ID: {id_at}")
        nuovi_dati = {}
        
        col1, col2 = st.columns(2)
        for i, colonna in enumerate(df.columns):
            if colonna.lower() == 'id':
                nuovi_dati[colonna] = id_at
                continue
            target = col1 if i % 2 == 0 else col2
            nuovi_dati[colonna] = target.text_input(f"{colonna}", value=str(dati_f.get(colonna, "")))
        
        st.divider()
        c_salva, c_cancella = st.columns([4, 1])
        
        if c_salva.form_submit_button("✅ CONFERMA E AGGIORNA"):
            if scelta == "+ AGGIUNGI NUOVO":
                df = pd.concat([df, pd.DataFrame([nuovi_dati])], ignore_index=True)
            else:
                idx = df[df['id'] == id_at].index[0]
                for k, v in nuovi_dati.items(): df.at[idx, k] = v
            conn.update(data=df)
            st.success("Dati salvati!")
            st.rerun()

    # TASTO CANCELLA FUORI DAL FORM PER SICUREZZA
    if scelta != "+ AGGIUNGI NUOVO":
        if st.button("🗑️ CANCELLA CLIENTE DEFINITIVAMENTE"):
            df = df[df['id'] != id_at]
            conn.update(data=df)
            st.warning("Cliente eliminato.")
            st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Lavori")
    cl_lav = st.selectbox("Seleziona Cliente:", df['Cliente'].tolist() if not df.empty else [])
    
    if cl_lav:
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write("### 🔘 Tipo di Pratica")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        p_tipo = lavoro.get('Pratica', "")
        if b1.button("🚧\nDIR.\nLAVORI"): p_tipo = "Direzione Lavori"
        if b2.button("📋\nPRATICHE\nCILA/SCIA"): p_tipo = "Pratiche"
        if b3.button("📐\nRILIEVI\nINFO"): p_tipo = "Rilievi"
        if b4.button("📊\nMILLESIMI"): p_tipo = "Millesimi"
        if b5.button("➕\nALTRO"): p_tipo = "Altro"
        
        with st.form("form_lavori_rapido"):
            st.info(f"Categoria: **{p_tipo}**")
            stato = st.selectbox("Stato", ["Da fare", "In corso", "Concluso"], index=0)
            note = st.text_area("Note", value=lavoro.get('Note', ""))
            
            if st.form_submit_button("✅ AGGIORNA SCHEDA"):
                df.at[idx_l, 'Pratica'] = p_tipo
                df.at[idx_l, 'Stato'] = stato
                df.at[idx_l, 'Note'] = note
                conn.update(data=df)
                st.success("Aggiornato!")
                st.rerun()
