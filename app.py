import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# 1. DESIGN "ARCHIFLOW" OTTIMIZZATO
st.set_page_config(page_title="Archiflow Suite", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Campi di testo più grandi e puliti */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    /* Pulsanti Categorie */
    div.stButton > button {
        border-radius: 15px; font-weight: bold; height: 5em; 
        background-color: white; border: 2px solid #e2e8f0;
        transition: 0.3s;
    }
    div.stButton > button:hover { border-color: #3b82f6; color: #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE
COLONNE = ['Cliente', 'CF_PIVA', 'Indirizzo', 'Telefono', 'Email', 'Pratica', 'Stato', 'Scadenza', 'Note']
DB_FILE = 'registro_studio_v5.csv'

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=COLONNE).to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE, dtype=str).fillna("")

# 3. SIDEBAR CON LOGO
with st.sidebar:
    try:
        st.image('logo.png', use_container_width=True)
    except:
        st.header("🏛️ ARCHIFLOW")
    
    st.divider()
    menu = st.radio("VAI A:", ["🏠 HOME", "📇 ANAGRAFICA", "🏗️ LAVORI"])

# 4. LOGICA DI SALVATAGGIO AUTOMATICO
def auto_salva(nome_cliente, nuovi_dati):
    global df
    if nome_cliente in df['Cliente'].values:
        idx = df[df['Cliente'] == nome_cliente].index[0]
        for col, val in nuovi_dati.items():
            df.at[idx, col] = val
    else:
        nuova_riga = pd.DataFrame([nuovi_dati])
        df = pd.concat([df, nuova_riga], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.toast("Sincronizzazione completata! ✅")

# --- PAGINE ---

if menu == "🏠 HOME":
    st.title("Benvenuta Silvia 📊")
    st.metric("Pratiche Attive", len(df[df['Stato'] != 'Conclusa']))
    st.dataframe(df.tail(5), use_container_width=True)

elif menu == "📇 ANAGRAFICA":
    st.header("📇 Gestione Cliente")
    
    # CERCA O CREA
    cerca = st.selectbox("🔍 Cerca cliente esistente o scrivi per nuovo:", ["NUOVO CLIENTE"] + list(df['Cliente'].unique()))
    
    # Caricamento dati
    if cerca != "NUOVO CLIENTE":
        d = df[df['Cliente'] == cerca].iloc[0].to_dict()
    else:
        d = {c: "" for c in COLONNE}

    # CAMPI PULITI (Niente celle!)
    with st.container():
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome Cliente", value=d['Cliente'])
        cf = c2.text_input("Codice Fiscale / P.IVA", value=d['CF_PIVA'])
        
        c3, c4 = st.columns(2)
        tel = c3.text_input("Telefono", value=d['Telefono'])
        mail = c4.text_input("Email", value=d['Email'])
        
        ind = st.text_input("Indirizzo Sede", value=d['Indirizzo'])
        note = st.text_area("Note Generali", value=d['Note'])

        # Se modifichi qualcosa, salva da solo
        nuovi_valori = {
            'Cliente': nome, 'CF_PIVA': cf, 'Indirizzo': ind, 
            'Telefono': tel, 'Email': mail, 'Note': note
        }
        if nome != d['Cliente'] or cf != d['CF_PIVA'] or tel != d['Telefono']:
             if nome: # Salva solo se c'è almeno il nome
                auto_salva(cerca, nuovi_valori)

elif menu == "🏗️ LAVORI":
    st.header("🏗️ Scheda Lavori")
    
    cerca_l = st.selectbox("🔍 Seleziona Cantiere/Cliente:", df['Cliente'].unique())
    
    if cerca_l:
        d_l = df[df['Cliente'] == cerca_l].iloc[0].to_dict()
        
        st.write("### 🛠️ Tipo di Pratica")
        cb = st.columns(5)
        # Pulsanti che impostano il valore
        p_tipo = d_l['Pratica']
        if cb[0].button("🏗️ DIREZIONE\nLAVORI"): p_tipo = "Direzione Lavori"
        if cb[1].button("📋 PRATICHE\n(CILA/SCIA)"): p_tipo = "Pratiche"
        if cb[2].button("📏 RILIEVI\nINFO"): p_tipo = "Rilievi"
        if cb[3].button("📊 MILLESIMI"): p_tipo = "Millesimi"
        if cb[4].button("➕ ALTRO"): p_tipo = "Altro"
        
        st.info(f"Selezionato: **{p_tipo}**")
        
        c1, c2 = st.columns(2)
        stato = c1.selectbox("Stato Avanzamento", ["Da Fare", "In Corso", "Conclusa", "Annullata"], 
                             index=["Da Fare", "In Corso", "Conclusa", "Annullata"].index(d_l['Stato']) if d_l['Stato'] in ["Da Fare", "In Corso", "Conclusa", "Annullata"] else 0)
        scadenza = c2.text_input("Scadenza (GG/MM/AAAA)", value=d_l['Scadenza'])
        
        # Salvataggio automatico se cambia qualcosa
        if p_tipo != d_l['Pratica'] or stato != d_l['Stato']:
            d_l.update({'Pratica': p_tipo, 'Stato': stato, 'Scadenza': scadenza})
            auto_salva(cerca_l, d_l)
            st.rerun()
