import streamlit as st
import pandas as pd
import os
import openai

# Prova a importare il registratore vocale
try:
    from streamlit_mic_recorder import mic_recorder
    HAS_MIC = True
except:
    HAS_MIC = False

# 1. SETUP ESTETICO E CONFIGURAZIONE
st.set_page_config(page_title="Archiflow Suite Gestionale", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stSidebarNav"] {display: none;}
    
    /* MENU SIDEBAR */
    .sidebar-btn > div > button {
        height: 4.5em !important;
        font-weight: bold !important;
        font-size: 18px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* BOTTONI PLANCIA LAVORI */
    .btn-dl > div > button { background-color: #E63946 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-pra > div > button { background-color: #457B9D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ape > div > button { background-color: #2A9D8F !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-ril > div > button { background-color: #F4A261 !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-mill > div > button { background-color: #8338EC !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }
    .btn-alt > div > button { background-color: #6C757D !important; color: white !important; height: 10em !important; font-size: 20px !important; border-radius: 20px !important; border: none !important; font-weight: bold !important; }

    /* HEADER TABELLA */
    .table-header {
        background-color: #f1f5f9;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNZIONI AI
def genera_verbale_ai(testo, key):
    if not key: return "Inserisci API Key nella sidebar."
    try:
        client = openai.OpenAI(api_key=key)
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Sei l'Arch. Silvia Cubeddu. Trasforma gli appunti in un verbale tecnico professionale."},
                      {"role": "user", "content": testo}]
        )
        return res.choices[0].message.content
    except Exception as e: return f"Errore AI: {e}"

# 3. DATABASE
DB_ANA = "database_archiflow.csv"
DB_CAN = "cantieri.csv"
COL_ANA = ["id", "Cliente", "C.F. / P.IVA", "Indirizzo", "CAP", "Città", "Telefono", "Email", "Web", "Pratica", "Stato", "Scadenza", "Note"]
COL_CAN = ["id_cantiere", "Cliente", "Indirizzo", "Tipo", "Stato", "Note", "chk_durc", "chk_urbanistica", "chk_finelavori"]

def carica_db(f, c):
    if os.path.exists(f):
        df = pd.read_csv(f, dtype=str).fillna("")
        for col in c: 
            if col not in df.columns: df[col] = ""
        return df[c]
    return pd.DataFrame(columns=c)

def salva_db(df, f):
    df.to_csv(f, index=False)

df_ana = carica_db(DB_ANA, COL_ANA)
df_can = carica_db(DB_CAN, COL_CAN)

# 4. SIDEBAR
with st.sidebar:
    if os.path.exists("Logo.png"): st.image("Logo.png", use_container_width=True)
    else: st.title("ARCHIFLOW")
    st.divider()
    api_key = st.text_input("🔑 OpenAI API Key", type="password")
    st.divider()
    if "menu_sel" not in st.session_state: st.session_state.menu_sel = "HOME"
    st.markdown('<div class="sidebar-btn">', unsafe_allow_html=True)
    if st.button("🏠 HOME", use_container_width=True): st.session_state.menu_sel = "HOME"; st.rerun()
    if st.button("📇 ANAGRAFICA", use_container_width=True): st.session_state.menu_sel = "ANAGRAFICA"; st.rerun()
    if st.button("🏗️ LAVORI", use_container_width=True): st.session_state.menu_sel = "LAVORI"; st.session_state.sotto_menu = None; st.rerun()
    if st.button("📅 SCADENZE", use_container_width=True): st.session_state.menu_sel = "SCADENZE"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

menu = st.session_state.menu_sel

# --- LOGICA PAGINE ---

if menu == "HOME":
    st.title("Archiflow Dashboard")
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    # Mantenuta logica originale come richiesto
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo_ana = "add"; st.session_state.ana_sel = None; st.rerun()
    # ... (Anagrafica code...)

elif menu == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        
        if st.session_state.get("c_aperto"):
            # --- SCHEDA APRI SCHEDA (Dettaglio) ---
            id_c = st.session_state.c_aperto
            r = df_can[df_can['id_cantiere'] == id_c].iloc[0]
            st.subheader(f"📂 Scheda Tecnica: {r['Cliente']} - {r['Indirizzo']}")
            if st.button("⬅️ CHIUDI SCHEDA E TORNA ALLA LISTA"): st.session_state.c_aperto = None; st.rerun()
            
            with st.container():
                t1, t2 = st.tabs(["📝 DIARIO DI BORDO & AI", "📋 DOCUMENTI"])
                with t1:
                    if HAS_MIC:
                        audio = mic_recorder(start_prompt="🎤 Registra Sopralluogo", stop_prompt="💾 Salva Vocale", key='rec_sopra')
                        if audio: st.audio(audio['bytes'])
                    u_note = st.text_area("Note e osservazioni:", value=r['Note'], height=200)
                    if st.button("🤖 GENERA VERBALE AI"):
                        st.session_state.verb_ai = genera_verbale_ai(u_note, api_key)
                    if "verb_ai" in st.session_state:
                        st.text_area("Bozza Verbale:", value=st.session_state.verb_ai, height=300)
                with t2:
                    ck1 = st.checkbox("DURC", value=(r['chk_durc']=="1"))
                    ck2 = st.checkbox("Urbanistica", value=(r['chk_urbanistica']=="1"))
                    ck3 = st.checkbox("Fine Lavori", value=(r['chk_finelavori']=="1"))
                
                if st.button("💾 SALVA NOTE E DOCUMENTI"):
                    idx = df_can[df_can['id_cantiere'] == id_c].index[0]
                    df_can.at[idx, 'Note'] = u_note
                    df_can.at[idx, 'chk_durc'] = "1" if ck1 else "0"
                    df_can.at[idx, 'chk_urbanistica'] = "1" if ck2 else "0"
                    df_can.at[idx, 'chk_finelavori'] = "1" if ck3 else "0"
                    salva_db(df_can, DB_CAN); st.success("Scheda aggiornata!"); st.rerun()

        else:
            # --- LISTA CANTIERI RICHIESTA ---
            if st.button("➕ AGGIUNGI NUOVO CANTIERE"):
                new_c = {"id_cantiere": str(len(df_can)+1), "Cliente": "Nuovo", "Indirizzo": "-", "Tipo": "Interni", "Stato": "Da iniziare"}
                df_can = pd.concat([df_can, pd.DataFrame([new_c])], ignore_index=True)
                salva_db(df_can, DB_CAN); st.rerun()

            cerca = st.text_input("🔍 Cerca (Cliente, Via o Lettera)...")
            
            # Intestazione Tabella
            st.markdown("""
                <div class="table-header">
                    <div style="flex: 2;">CLIENTE</div>
                    <div style="flex: 2;">INDIRIZZO CANTIERE</div>
                    <div style="flex: 1.5;">TIPO</div>
                    <div style="flex: 1.5;">STATO</div>
                    <div style="flex: 2; text-align: right;">AZIONI</div>
                </div>
            """, unsafe_allow_html=True)
            
            filt = df_can[df_can.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)] if cerca else df_can
            
            for i, r in filt.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 2])
                    
                    # Campi editabili direttamente in riga
                    u_cli = col1.text_input("Cliente", value=r['Cliente'], key=f"cli_{i}", label_visibility="collapsed")
                    u_ind = col2.text_input("Indirizzo", value=r['Indirizzo'], key=f"ind_{i}", label_visibility="collapsed")
                    u_tp = col3.selectbox("Tipo", ["Interni", "Esterni"], index=0 if r['Tipo']=="Interni" else 1, key=f"tp_{i}", label_visibility="collapsed")
                    u_st = col4.selectbox("Stato", ["Da iniziare", "In corso", "Sospeso", "Ultimato"], index=["Da iniziare", "In corso", "Sospeso", "Ultimato"].index(r['Stato']) if r['Stato'] in ["Da iniziare", "In corso", "Sospeso", "Ultimato"] else 0, key=f"st_{i}", label_visibility="collapsed")
                    
                    # Bottoni Azione
                    c_act1, c_act2, c_act3 = col5.columns(3)
                    if c_act1.button("🔄", key=f"up_{i}", help="Aggiorna riga"):
                        df_can.loc[i, ['Cliente', 'Indirizzo', 'Tipo', 'Stato']] = [u_cli, u_ind, u_tp, u_st]
                        salva_db(df_can, DB_CAN); st.rerun()
                    if c_act2.button("📂", key=f"op_{i}", help="Apri Scheda Dettagliata"):
                        st.session_state.c_aperto = r['id_cantiere']; st.rerun()
                    if c_act3.button("🗑️", key=f"del_{i}", help="Cancella"):
                        df_can = df_can.drop(i); salva_db(df_can, DB_CAN); st.rerun()
                st.divider()

            if st.button("⬅️ TORNA AI LAVORI"): st.session_state.sotto_menu = None; st.rerun()

    else:
        # PLANCIA BOTTONI GIGANTI
        st.header("🏗️ Selezione Area")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", key="main_dl", use_container_width=True): st.session_state.sotto_menu = "DL"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("📐 RILIEVI", use_container_width=True): st.toast("Rilievi")
        with c2:
            if st.button("📋 PRATICHE CILA/SCIA", use_container_width=True): st.toast("Pratiche")
            if st.button("📊 MILLESIMI", use_container_width=True): st.toast("Millesimi")
        with c3:
            if st.button("⚡ APE / LEGGE 10", use_container_width=True): st.toast("APE")
            if st.button("➕ ALTRO", use_container_width=True): st.toast("Altro")
