import streamlit as st
import pandas as pd
import os

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div.stButton > button {
        border-radius: 12px; font-weight: bold; height: 4em; 
        background-color: white; border: 2px solid #e2e8f0;
    }
    div.stButton > button:hover { border-color: #3b82f6; color: #3b82f6; }
    .stTextInput input { border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIONE DATABASE LOCALE (CSV)
DB_FILE = "database_cantieri.csv"

def carica_dati():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'id': str}).fillna("")
    else:
        # Crea un database vuoto con le colonne base se non esiste
        colonne = ["id", "Cliente", "Telefono", "Email", "Indirizzo", "Pratica", "Stato", "Note"]
        return pd.DataFrame(columns=colonne)

def salva_dati(dataframe):
    dataframe.to_csv(DB_FILE, index=False)

df = carica_dati()

def genera_id(dataframe):
    if dataframe.empty: return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.write("### Ultime Pratiche Inserite")
    st.dataframe(df.tail(15), use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"
        st.rerun()

    cerca = st.text_input("🔍 Cerca cliente esistente:")
    df_f = df[df.astype(str).apply(lambda x: x.str.contains(cerca, case=False)).any(axis=1)] if cerca else df
    
    opzioni = ["---"] + df_f['Cliente'].tolist() if 'Cliente' in df.columns else ["---"]
    scelta = st.selectbox("Seleziona per modificare o cancellare:", opzioni)

    if scelta != "---":
        st.session_state.modo = "modifica"
        riga = df[df['Cliente'] == scelta].iloc[0]
        id_at = riga['id']
        dati_f = riga.to_dict()
    elif st.session_state.get('modo') == "aggiungi":
        id_at = genera_id(df)
        dati_f = {col: "" for col in df.columns}
        dati_f['id'] = id_at
    else:
        st.info("Seleziona un cliente o clicca 'Aggiungi Nuovo'")
        st.stop()

    with st.form("form_anagrafica"):
        st.write(f"### Scheda ID: {id_at}")
        nuovi_dati = {}
        c1, c2 = st.columns(2)
        
        for i, colonna in enumerate(df.columns):
            if colonna.lower() == 'id':
                nuovi_dati[colonna] = id_at
                continue
            target = c1 if i % 2 == 0 else c2
            nuovi_dati[colonna] = target.text_input(f"{colonna}", value=str(dati_f.get(colonna, "")))
        
        if st.form_submit_button("✅ CONFERMA"):
            if st.session_state.get('modo') == "aggiungi":
                df = pd.concat([df, pd.DataFrame([nuovi_dati])], ignore_index=True)
            else:
                idx = df[df['id'] == id_at].index[0]
                for k, v in nuovi_dati.items(): df.at[idx, k] = v
            
            salva_dati(df)
            st.success("Dati salvati localmente! ✅")
            st.session_state.modo = None
            st.rerun()

    if scelta != "---":
        if st.button("🗑️ CANCELLA CLIENTE DEFINITIVAMENTE"):
            df = df[df['id'] != id_at]
            salva_dati(df)
            st.warning("Rimosso.")
            st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Lavori")
    cl_lav = st.selectbox("Seleziona Cliente:", ["---"] + df['Cliente'].tolist() if not df.empty else ["---"])
    
    if cl_lav != "---":
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write("### 🔘 Tipo Pratica")
        b = st.columns(5)
        p_tipo = lavoro.get('Pratica', "")
        
        if b[0].button("🚧\nDL"): p_tipo = "Direzione Lavori"
        if b[1].button("📋\nCILA"): p_tipo = "Pratiche"
        if b[2].button("📐\nRILIEVI"): p_tipo = "Rilievi"
        if b[3].button("📊\nMILL."): p_tipo = "Millesimi"
        if b[4].button("➕\nALTRO"): p_tipo = "Altro"
        
        with st.form("form_lavoro_local"):
            st.info(f"Categoria: **{p_tipo}**")
            stato = st.selectbox("Stato", ["Da fare", "In corso", "Concluso"], index=0)
            note = st.text_area("Note", value=lavoro.get('Note', ""))
            
            if st.form_submit_button("✅ CONFERMA"):
                df.at[idx_l, 'Pratica'] = p_tipo
                df.at[idx_l, 'Stato'] = stato
                df.at[idx_l, 'Note'] = note
                salva_dati(df)
                st.success("Lavoro aggiornato! ✅")
                st.rerun()
