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

    /* STILE LISTA */
    .lista-header { background-color: #f1f5f9; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 10px; border: 1px solid #e2e8f0; }
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

# --- LOGICA ---

if menu == "HOME":
    st.title("Archiflow Dashboard")
    st.dataframe(df_ana, use_container_width=True, hide_index=True)

elif menu == "ANAGRAFICA":
    st.header("📇 Gestione Anagrafica")
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo_ana = "add"; st.session_state.ana_sel = None; st.rerun()
    # Logica Anagrafica Standard...

elif menu == "LAVORI":
    if st.session_state.get("sotto_menu") == "DL":
        st.header("🚧 Direzione Lavori")
        
        if st.session_state.get("c_aperto"):
            # --- SCHEDA DETTAGLIO ---
            id_c = st.session_state.c_aperto
            r = df_can[df_can['id_cantiere'] == id_c].iloc[0]
            st.subheader(f"📍 {r['Cliente']} - {r['Indirizzo']}")
            if st.button("⬅️ TORNA ALLA LISTA"): st.session_state.c_aperto = None; st.rerun()
            
            with st.form("f_cantiere_full"):
                t1, t2 = st.tabs(["📋 CHECKLIST & INFO", "🎙️ DIARIO & AI"])
                with t1:
                    st.write(f"**Cliente:** {r['Cliente']} | **Indirizzo:** {r['Indirizzo']}")
                    ck1 = st.checkbox("DURC", value=(r['chk_durc']=="1"))
                    ck2 = st.checkbox("Pratica Urbanistica", value=(r['chk_urbanistica']=="1"))
                    ck3 = st.checkbox("Fine Lavori", value=(r['chk_finelavori']=="1"))
                with t2:
                    if HAS_MIC:
                        audio = mic_recorder(start_prompt="🎤 Registra", stop_prompt="🛑 Salva", key='rec_full')
                        if audio: st.audio(audio['bytes'])
                    u_note = st.text_area("Note e Appunti:", value=r['Note'], height=200)
                    if st.form_submit_button("🤖 GENERA VERBALE AI"):
                        st.session_state.verb_ai = genera_verbale_ai(u_note, api_key)
                    if "verb_ai" in st.session_state:
                        st.text_area("Verbale AI:", value=st.session_state.verb_ai, height=250)
                if st.form_submit_button("💾 SALVA SCHEDA COMPLETA"):
                    idx = df_can[df_can['id_cantiere'] == id_c].index[0]
                    df_can.at[idx, 'chk_durc'] = "1" if ck1 else "0"
                    df_can.at[idx, 'chk_urbanistica'] = "1" if ck2 else "0"
                    df_can.at[idx, 'chk_finelavori'] = "1" if ck3 else "0"
                    df_can.at[idx, 'Note'] = u_note
                    salva_db(df_can, DB_CAN); st.success("Salvato!"); st.rerun()

        else:
            # --- LISTA CANTIERI EDITABILE ---
            if st.button("➕ AGGIUNGI NUOVO CANTIERE"):
                new_c = {"id_cantiere": str(len(df_can)+1), "Cliente": "Nuovo", "Indirizzo": "-", "Tipo": "Interni", "Stato": "Iniziale"}
                df_can = pd.concat([df_can, pd.DataFrame([new_c])], ignore_index=True)
                salva_db(df_can, DB_CAN); st.rerun()

            cerca = st.text_input("🔍 Cerca cantiere...")
            
            st.markdown('<div class="lista-header">CLIENTE | INDIRIZZO | TIPO | STATO</div>', unsafe_allow_html=True)
            
            filt = df_can[df_can.apply(lambda r: cerca.lower() in r.astype(str).str.lower().values, axis=1)] if cerca else df_can
            
            for _, r in filt.iterrows():
                with st.expander(f"📌 {r['Cliente']} — {r['Indirizzo']} — {r['Tipo']} — {r['Stato']}"):
                    with st.form(key=f"f_edit_{r['id_cantiere']}"):
                        c1, c2, c3, c4 = st.columns(4)
                        new_cli = c1.text_input("Cliente", value=r['Cliente'])
                        new_ind = c2.text_input("Indirizzo", value=r['Indirizzo'])
                        new_tp = c3.selectbox("Tipo", ["Interni", "Esterni"], index=0 if r['Tipo']=="Interni" else 1)
                        new_st = c4.selectbox("Stato", ["Iniziale", "In Corso", "Chiuso"], index=0)
                        
                        col_b1, col_b2, col_b3 = st.columns([1,1,2])
                        if col_b1.form_submit_button("🔄 AGGIORNA"):
                            idx = df_can[df_can['id_cantiere'] == r['id_cantiere']].index[0]
                            df_can.loc[idx, ['Cliente', 'Indirizzo', 'Tipo', 'Stato']] = [new_cli, new_ind, new_tp, new_st]
                            salva_db(df_can, DB_CAN); st.rerun()
                        if col_b2.form_submit_button("🗑️ CANCELLA"):
                            df_can = df_can[df_can['id_cantiere'] != r['id_cantiere']]
                            salva_db(df_can, DB_CAN); st.rerun()
                        if col_b3.form_submit_button("📂 APRI SCHEDA DETTAGLIATA"):
                            st.session_state.c_aperto = r['id_cantiere']; st.rerun()

            if st.button("⬅️ TORNA AI LAVORI"): st.session_state.sotto_menu = None; st.rerun()

    else:
        # PLANCIA BOTTONI GIGANTI
        st.header("🏗️ Selezione Area")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", key="m_dl", use_container_width=True): st.session_state.sotto_menu = "DL"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("📐 RILIEVI", use_container_width=True): st.toast("Rilievi")
        with c2:
            if st.button("📋 PRATICHE CILA/SCIA", use_container_width=True): st.toast("Pratiche")
            if st.button("📊 MILLESIMI", use_container_width=True): st.toast("Millesimi")
        with c3:
            if st.button("⚡ APE / LEGGE 10", use_container_width=True): st.toast("APE")
            if st.button("➕ ALTRO", use_container_width=True): st.toast("Altro")
