import streamlit as st
import pandas as pd
import os

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Pulsanti Navigazione e Form */
    div.stButton > button {
        border-radius: 12px; font-weight: bold; transition: 0.3s;
    }
    /* Stile BOTTONI GIGANTI COLORATI */
    .btn-dl { background-color: #ff4b4b !important; color: white !important; height: 6em !important; }
    .btn-pratiche { background-color: #3b82f6 !important; color: white !important; height: 6em !important; }
    .btn-rilievi { background-color: #10b981 !important; color: white !important; height: 6em !important; }
    .btn-mill { background-color: #f59e0b !important; color: white !important; height: 6em !important; }
    .btn-altro { background-color: #6366f1 !important; color: white !important; height: 6em !important; }
    
    .stTextInput input, .stSelectbox, .stTextArea textarea { border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIONE DATABASE LOCALE (CSV)
DB_FILE = "database_archiflow.csv"

def carica_dati():
    colonne = [
        "id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", 
        "Telefono", "Email", "Web", "Pratica", "Stato", "Note"
    ]
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, dtype={'id': str}).fillna("")
    else:
        return pd.DataFrame(columns=colonne)

def salva_dati(dataframe):
    dataframe.to_csv(DB_FILE, index=False)

df = carica_dati()

def genera_id(dataframe):
    if dataframe.empty: return "1"
    ids = pd.to_numeric(dataframe['id'], errors='coerce').fillna(0)
    return str(int(ids.max() + 1))

# 3. SIDEBAR (LOGO E MENU)
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    st.divider()
    menu = st.radio("NAVIGAZIONE", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ SCHEDA LAVORI"])

# --- PAGINE ---

if menu == "🏠 HOME":
    st.title("Archiflow Suite Gestionale")
    st.divider()
    st.write("### Stato Globale dei Cantieri")
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
        st.write("### 🔍 Lista Clienti")
        cerca = st.text_input("Filtra per nome:")
        df_f = df[df['Cliente'].str.contains(cerca, case=False)] if cerca else df
        for _, row in df_f.iterrows():
            if st.button(f"👤 {row['Cliente']}", key=f"btn_{row['id']}", use_container_width=True):
                st.session_state.modo = "modifica"
                st.session_state.cliente_selezionato = row['id']
                st.rerun()

    with col_form:
        id_at = st.session_state.get('cliente_selezionato')
        modo = st.session_state.get('modo')
        if modo == "aggiungi":
            id_at = genera_id(df)
            dati_f = {col: "" for col in df.columns}
        elif modo == "modifica" and id_at:
            dati_f = df[df['id'] == id_at].iloc[0].to_dict()
        else:
            st.info("Seleziona un cliente dalla lista o clicca su 'Aggiungi Nuovo'")
            st.stop()

        with st.form("form_anagrafica"):
            nuovi_dati = {"id": id_at}
            c1, c2 = st.columns(2)
            nuovi_dati["Cliente"] = c1.text_input("Cliente", value=str(dati_f.get("Cliente", "")))
            nuovi_dati["C.F. / P.IVA"] = c2.text_input("C.F. / P.IVA", value=str(dati_f.get("C.F. / P.IVA", "")))
            nuovi_dati["Indirizzo"] = c1.text_input("Indirizzo", value=str(dati_f.get("Indirizzo", "")))
            nuovi_dati["CAP"] = c2.text_input("CAP", value=str(dati_f.get("CAP", "")))
            nuovi_dati["Città"] = c1.text_input("Città", value=str(dati_f.get("Città", "")))
            nuovi_dati["Telefono"] = c2.text_input("Telefono", value=str(dati_f.get("Telefono", "")))
            nuovi_dati["Email"] = c1.text_input("Email", value=str(dati_f.get("Email", "")))
            nuovi_dati["Web"] = c2.text_input("Web", value=str(dati_f.get("Web", "")))
            
            st.divider()
            nuovi_dati["Pratica"] = st.text_input("Tipo Pratica (Modificabile manualmente)", value=str(dati_f.get("Pratica", "")))
            nuovi_dati["Stato"] = st.selectbox("Stato", ["Da fare", "In corso", "Annullata", "Conclusa"], 
                                             index=["Da fare", "In corso", "Annullata", "Conclusa"].index(dati_f.get("Stato", "Da fare")) if dati_f.get("Stato") in ["Da fare", "In corso", "Annullata", "Conclusa"] else 0)
            nuovi_dati["Note"] = st.text_area("Note", value=str(dati_f.get("Note", "")))
            
            if st.form_submit_button("✅ CONFERMA"):
                if modo == "aggiungi":
                    df = pd.concat([df, pd.DataFrame([nuovi_dati])], ignore_index=True)
                else:
                    idx = df[df['id'] == id_at].index[0]
                    for k, v in nuovi_dati.items(): df.at[idx, k] = v
                salva_dati(df)
                st.session_state.modo = None
                st.rerun()

elif menu == "🏗️ SCHEDA LAVORI":
    st.header("🏗️ Registro Operativo Cantieri")
    cl_lav = st.selectbox("Seleziona Pratica Cliente:", ["---"] + df['Cliente'].tolist() if not df.empty else ["---"])
    
    if cl_lav != "---":
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.write(f"### 🔘 Imposta Categoria per: **{cl_lav}**")
        
        # BOTTONI COLORATI GIGANTI
        c1, c2, c3, c4, c5 = st.columns(5)
        nuova_p = lavoro['Pratica']
        
        if c1.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True): nuova_p = "Direzione Lavori"
        if c2.button("📋\nPRATICHE\nCILA/SCIA", use_container_width=True): nuova_p = "Pratiche"
        if c3.button("📐\nRILIEVI\nFOTOGRAM.", use_container_width=True): nuova_p = "Rilievi"
        if c4.button("📊\nMILLESIMI\nTABELLE", use_container_width=True): nuova_p = "Millesimi"
        if c5.button("➕\nALTRO\nPERIZIE", use_container_width=True): nuova_p = "Altro"

        # Form per aggiornare Stato e Note
        with st.form("aggiorna_lavoro"):
            st.success(f"Categoria Selezionata: **{nuova_p}**")
            col_s, col_n = st.columns([1, 2])
            nuovo_s = col_s.selectbox("Aggiorna Stato", ["Da fare", "In corso", "Annullata", "Conclusa"], 
                                     index=["Da fare", "In corso", "Annullata", "Conclusa"].index(lavoro['Stato']) if lavoro['Stato'] in ["Da fare", "In corso", "Annullata", "Conclusa"] else 0)
            nuove_note = col_n.text_area("Aggiorna Note/Protocolli", value=lavoro['Note'])
            
            if st.form_submit_button("✅ AGGIORNA SCHEDA"):
                df.at[idx_l, 'Pratica'] = nuova_p
                df.at[idx_l, 'Stato'] = nuovo_s
                df.at[idx_l, 'Note'] = nuove_note
                salva_dati(df)
                st.rerun()
