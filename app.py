import streamlit as st
import pandas as pd
import os

# 1. SETUP "ARCHIFLOW SUITE GESTIONALE"
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* MENU SIDEBAR: Bottoni grossi e moderni */
    [data-testid="stSidebarNav"] {display: none;}
    .sidebar-btn > div > button {
        height: 4.5em !important;
        font-weight: bold !important;
        font-size: 18px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: 0.3s !important;
    }
    .sidebar-btn > div > button:hover { 
        border-color: #3b82f6 !important; 
        color: #3b82f6 !important;
        background-color: #f0f7ff !important;
    }

    /* BOTTONI LAVORI: Giganti e Colorati */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }

    .stButton > button:hover { opacity: 0.9 !important; transform: translateY(-2px); transition: 0.2s; }
    
    /* Input e form */
    .stTextInput input, .stTextArea textarea { border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE LOCALE - STRUTTURA RIGIDA
DB_FILE = "database_archiflow.csv"
COLONNE = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]

def carica_dati():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype={'id': str}).fillna("")
            for col in COLONNE:
                if col not in df.columns: df[col] = ""
            return df[COLONNE]
        except:
            return pd.DataFrame(columns=COLONNE)
    else:
        return pd.DataFrame(columns=COLONNE)

def salva_dati(dataframe):
    dataframe.to_csv(DB_FILE, index=False)

df = carica_dati()

# 3. SIDEBAR CUSTOM
with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
    st.divider()
    
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"

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
    st.subheader("Database Clienti")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"
        st.session_state.cliente_sel = None
        st.rerun()

    col_list, col_form = st.columns([1, 2])
    with col_list:
        cerca = st.text_input("🔍 Filtra per nome:")
        df_f = df[df['Cliente'].str.contains(cerca, case=False)] if cerca else df
        for _, row in df_f.iterrows():
            if st.button(f"👤 {row['Cliente']}", key=f"l_{row['id']}", use_container_width=True):
                st.session_state.modo = "modifica"
                st.session_state.cliente_sel = row['id']
                st.rerun()

    with col_form:
        id_at = st.session_state.get('cliente_sel')
        modo = st.session_state.get('modo')
        
        if modo == "aggiungi":
            id_at = str(int(pd.to_numeric(df['id']).max() + 1)) if not df.empty else "1"
            dati_f = {col: "" for col in COLONNE}
        elif modo == "modifica" and id_at:
            dati_f = df[df['id'] == id_at].iloc[0].to_dict()
        else:
            st.info("Seleziona un cliente dalla lista o clicca su AGGIUNGI")
            st.stop()

        with st.form("form_ana"):
            st.write(f"### Scheda ID: {id_at}")
            nuovi = {"id": id_at}
            c1, c2 = st.columns(2)
            for i, col in enumerate(COLONNE[1:]):
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
    # PLANCIA BOTTONI GIGANTI
    st.write("## ")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
        if st.button("🚧\nDIREZIONE\nLAVORI", key="b_dl", use_container_width=True): st.toast("DL Selezionata")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-ril">', unsafe_allow_html=True)
        if st.button("📐\nRILIEVI", key="b_ril", use_container_width=True): st.toast("Rilievi Selezionati")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-pra">', unsafe_allow_html=True)
        if st.button("📋\nPRATICHE\nCILA/SCIA", key="b_pra", use_container_width=True): st.toast("Pratiche Selezionate")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-mill">', unsafe_allow_html=True)
        if st.button("📊\nMILLESIMI", key="b_mill", use_container_width=True): st.toast("Millesimi Selezionati")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="btn-ape">', unsafe_allow_html=True)
        if st.button("⚡\nAPE /\nLEGGE 10", key="b_ape", use_container_width=True): st.toast("APE/L10 Selezionata")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-alt">', unsafe_allow_html=True)
        if st.button("➕\nALTRO", key="b_alt", use_container_width=True): st.toast("Altro Selezionato")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "SCADENZE":
    st.header("📅 Scadenze e Consegne")
    st.divider()
    if not df.empty:
        # Mostra solo i dati operativi necessari
        st.dataframe(df[["Cliente", "Pratica", "Scadenza", "Stato"]], use_container_width=True, hide_index=True)
    else:
        st.info("Nessun cliente in anagrafica.")
