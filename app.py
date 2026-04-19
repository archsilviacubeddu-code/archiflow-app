import streamlit as st
import pandas as pd
import os

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Stile BOTTONI GIGANTI COLORATI */
    div.stButton > button {
        border-radius: 15px; font-weight: bold; transition: 0.3s;
        height: 7em !important; width: 100%; font-size: 14px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    /* Colori specifici per tipo di lavoro */
    .btn-dl { background-color: #e63946 !important; color: white !important; }
    .btn-pratiche { background-color: #457b9d !important; color: white !important; }
    .btn-ape { background-color: #2a9d8f !important; color: white !important; }
    .btn-rilievi { background-color: #f4a261 !important; color: white !important; }
    .btn-mill { background-color: #8338ec !important; color: white !important; }
    .btn-altro { background-color: #6c757d !important; color: white !important; }
    
    .stTextInput input, .stSelectbox, .stTextArea textarea { border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIONE DATABASE LOCALE (CSV)
DB_FILE = "database_archiflow.csv"

def carica_dati():
    colonne = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Note"]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'id': str}).fillna("")
    else:
        return pd.DataFrame(columns=colonne)

def salva_dati(dataframe):
    dataframe.to_csv(DB_FILE, index=False)

df = carica_dati()

# 3. SIDEBAR
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- LOGICA PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"
        st.session_state.cliente_selezionato = None
        st.rerun()
    
    st.divider()
    col_list, col_form = st.columns([1, 2])
    
    with col_list:
        cerca = st.text_input("🔍 Filtra:")
        df_f = df[df['Cliente'].str.contains(cerca, case=False)] if cerca else df
        for _, row in df_f.iterrows():
            if st.button(f"👤 {row['Cliente']}", key=f"list_{row['id']}", use_container_width=True):
                st.session_state.modo = "modifica"
                st.session_state.cliente_selezionato = row['id']
                st.rerun()

    with col_form:
        id_at = st.session_state.get('cliente_selezionato')
        if st.session_state.get('modo') == "aggiungi":
            id_at = str(int(pd.to_numeric(df['id']).max() + 1)) if not df.empty else "1"
            dati_f = {col: "" for col in df.columns}
        elif id_at:
            dati_f = df[df['id'] == id_at].iloc[0].to_dict()
        else:
            st.info("Seleziona un cliente a sinistra")
            st.stop()

        with st.form("form_ana"):
            st.write(f"### Dati Cliente ID: {id_at}")
            c1, c2 = st.columns(2)
            nuovi = {"id": id_at}
            for i, col in enumerate(df.columns[1:]):
                target = c1 if i % 2 == 0 else c2
                nuovi[col] = target.text_input(col, value=str(dati_f.get(col, "")))
            
            if st.form_submit_button("✅ CONFERMA"):
                if st.session_state.modo == "aggiungi":
                    df = pd.concat([df, pd.DataFrame([nuovi])], ignore_index=True)
                else:
                    idx = df[df['id'] == id_at].index[0]
                    for k, v in nuovi.items(): df.at[idx, k] = v
                salva_dati(df)
                st.session_state.modo = None
                st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Operativo")
    
    cl_lav = st.selectbox("Seleziona Cliente:", ["---"] + df['Cliente'].tolist() if not df.empty else ["---"])
    
    if cl_lav != "---":
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.divider()
        col_info, col_tasti = st.columns([1, 1.2])
        
        with col_info:
            st.subheader("Dettaglio Attuale")
            st.info(f"**Cliente:** {cl_lav}\n\n**Pratica:** {lavoro['Pratica']}\n\n**Stato:** {lavoro['Stato']}")
            
            with st.form("update_note"):
                nuovo_s = st.selectbox("Cambia Stato:", ["Da fare", "In corso", "Annullata", "Conclusa"], 
                                     index=["Da fare", "In corso", "Annullata", "Conclusa"].index(lavoro['Stato']) if lavoro['Stato'] in ["Da fare", "In corso", "Annullata", "Conclusa"] else 0)
                nuove_n = st.text_area("Note/Protocolli:", value=lavoro['Note'])
                if st.form_submit_button("💾 Salva Stato e Note"):
                    df.at[idx_l, 'Stato'] = nuovo_s
                    df.at[idx_l, 'Note'] = nuove_n
                    salva_dati(df)
                    st.rerun()

        with col_tasti:
            st.subheader("Seleziona Tipo Pratica")
            t1, t2 = st.columns(2)
            
            # Azioni Bottoni
            nuova_p = lavoro['Pratica']
            
            if t1.button("🚧\nDIREZIONE\nLAVORI", key="dl"): nuova_p = "Direzione Lavori"
            if t2.button("📋\nPRATICHE\nCILA/SCIA", key="pra"): nuova_p = "Pratiche CILA/SCIA"
            if t1.button("⚡\nAPE / LEGGE 10", key="ape"): nuova_p = "APE/Legge 10"
            if t2.button("📐\nRILIEVI", key="ril"): nuova_p = "Rilievi"
            if t1.button("📊\nMILLESIMI", key="mill"): nuova_p = "Millesimi"
            if t2.button("➕\nALTRO", key="alt"): nuova_p = "Altro"

            if nuova_p != lavoro['Pratica']:
                df.at[idx_l, 'Pratica'] = nuova_p
                salva_dati(df)
                st.rerun()
