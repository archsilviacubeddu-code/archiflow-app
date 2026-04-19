import streamlit as st
import pandas as pd
import os

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Pulsanti lista clienti Anagrafica (PICCOLI) */
    .stButton > button {
        border-radius: 8px; font-weight: normal; height: 2.5em; font-size: 13px !important;
    }
    /* Pulsanti GIGANTI SCHEDA LAVORI */
    .big-btn > div > button {
        height: 8em !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 15px !important;
        border: 2px solid #e2e8f0 !important;
        color: #1e293b !important;
        background-color: white !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .big-btn > div > button:hover {
        border-color: #3b82f6 !important;
        background-color: #eff6ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE LOCALE
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

# --- LOGICA ---

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
    
    col_list, col_form = st.columns([1, 2])
    with col_list:
        cerca = st.text_input("🔍 Filtra:")
        df_f = df[df['Cliente'].str.contains(cerca, case=False)] if cerca else df
        for _, row in df_f.iterrows():
            if st.button(f"👤 {row['Cliente']}", key=f"l_{row['id']}", use_container_width=True):
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
            st.info("Seleziona un cliente")
            st.stop()
        with st.form("form_ana"):
            nuovi = {"id": id_at}
            c1, c2 = st.columns(2)
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
    st.header("🏗️ Registro Operativo Lavori")
    
    # Selezione Cliente Centrale
    cl_lav = st.selectbox("Seleziona Cliente:", ["---"] + df['Cliente'].tolist() if not df.empty else ["---"])
    
    if cl_lav != "---":
        idx_l = df[df['Cliente'] == cl_lav].index[0]
        lavoro = df.iloc[idx_l].to_dict()
        
        st.divider()
        st.write(f"### 🔘 Imposta Tipo Pratica per: **{cl_lav}**")
        st.info(f"Pratica Attuale: **{lavoro['Pratica']}** | Stato: **{lavoro['Stato']}**")
        
        # GRIGLIA DI BOTTONI GIGANTI
        c1, c2, c3 = st.columns(3)
        nuova_p = lavoro['Pratica']
        
        with c1:
            st.markdown('<div class="big-btn">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", key="b_dl", use_container_width=True): nuova_p = "Direzione Lavori"
            if st.button("📐\nRILIEVI", key="b_ril", use_container_width=True): nuova_p = "Rilievi"
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="big-btn">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE\nCILA/SCIA", key="b_pra", use_container_width=True): nuova_p = "Pratiche CILA/SCIA"
            if st.button("📊\nMILLESIMI", key="b_mill", use_container_width=True): nuova_p = "Millesimi"
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c3:
            st.markdown('<div class="big-btn">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", key="b_ape", use_container_width=True): nuova_p = "APE / Legge 10"
            if st.button("➕\nALTRO", key="b_alt", use_container_width=True): nuova_p = "Altro"
            st.markdown('</div>', unsafe_allow_html=True)

        if nuova_p != lavoro['Pratica']:
            df.at[idx_l, 'Pratica'] = nuova_p
            salva_dati(df)
            st.rerun()
