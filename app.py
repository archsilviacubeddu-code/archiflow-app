import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import uuid

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide", page_icon="🏛️")

# CSS per pulizia e usabilità mobile
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stDataFrame { border-radius: 10px; }
    h1 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>🔒 Accesso Archiflow</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Password", type="password")
        if st.button("ENTRA"):
            if pwd == st.secrets["password"]:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Password errata")
    st.stop()

# --- CONNESSIONE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    data = conn.read(ttl=0).dropna(how="all").fillna("")
    data.columns = [c.upper() for c in data.columns]
    return data

df = get_data()

# --- SIDEBAR (SOLO HOME, ANAGRAFICA, LAVORI) ---
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.title("🏛️ ARCHIFLOW")
    st.divider()
    menu = st.radio("MENU", ["🏠 Home", "👤 Anagrafica", "🏗️ Lavori"])
    st.divider()
    if st.button("🔄 SINCRONIZZA"):
        st.cache_data.clear()
        st.rerun()

st.markdown("<h1 style='text-align: right;'>Archiflow - Suite Gestionale</h1>", unsafe_allow_html=True)
st.divider()

# --- FUNZIONE DI EDITING (MODIFICA, AGGIORNA, CANCELLA) ---
def gestione_dati(df_filtered):
    event = st.dataframe(df_filtered, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="multi-row")
    
    sel = event.selection.rows
    if sel:
        df_sel = df_filtered.iloc[sel]
        
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button(f"🗑️ CANCELLA ({len(df_sel)})", type="primary"):
                df_new = df.drop(df_sel.index)
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_new)
                st.rerun()
        
        if len(df_sel) == 1:
            idx_orig = df_sel.index[0]
            r = df.iloc[idx_orig]
            with st.expander("📝 MODIFICA / AGGIORNA SCHEDA", expanded=True):
                with st.form("edit_form"):
                    nuovi = {}
                    cols = st.columns(3)
                    # Tutte le caselle del Google Sheet diventano editabili
                    for i, col_name in enumerate(df.columns):
                        nuovi[col_name] = cols[i % 3].text_input(col_name, str(r[col_name]))
                    
                    if st.form_submit_button("💾 SALVA MODIFICHE"):
                        for col_name in df.columns:
                            df.at[idx_orig, col_name] = nuovi[col_name]
                        conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df)
                        st.success("Aggiornato!")
                        st.rerun()

# --- PAGINE ---
if menu == "🏠 Home":
    st.subheader(f"Dashboard Studio")
    st.metric("Totale Anagrafiche", len(df))
    st.dataframe(df[['CLIENTE', 'PRATICA', 'STATO']].tail(5), use_container_width=True, hide_index=True)

elif menu == "👤 Anagrafica":
    st.header("👤 Anagrafica Clienti")
    cerca = st.text_input("🔍 Cerca...", "").lower()
    df_f = df[df.apply(lambda r: cerca in str(r.values).lower(), axis=1)] if cerca else df
    gestione_dati(df_f)
    
    with st.expander("➕ AGGIUNGI NUOVO"):
        with st.form("new"):
            nome = st.text_input("Nome Cliente*")
            if st.form_submit_button("CREA"):
                if nome:
                    nuova_riga = {c: "" for c in df.columns}
                    nuova_riga['CLIENTE'] = nome
                    nuova_riga['STATO'] = 'In Corso'
                    df_up = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_up)
                    st.rerun()

elif menu == "🏗️ Lavori":
    st.header("🏗️ Registro Lavori")
    # Pulsanti rapidi per tipologia
    tabs = st.tabs(["Tutti", "Direzione Lavori", "Pratiche", "APE/Legge 10", "Tabelle Millesimali", "Altro"])
    categorie = ["Tutti", "Direzione Lavori", "Pratiche", "APE/Legge 10", "Tabelle Millesimali", "Altro"]
    
    for i, tab in enumerate(tabs):
        with tab:
            filtro = categorie[i]
            df_m = df if filtro == "Tutti" else df[df['PRATICA'].str.contains(filtro, case=False, na=False)]
            gestione_dati(df_m)