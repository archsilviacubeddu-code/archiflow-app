import streamlit as st
import pandas as pd
import openai

# Funzione AI estrapolata dal tuo codice
def genera_verbale_ai(testo, key):
    if not key: return "Inserisci API Key nella sidebar di app.py (o dove configurata)."
    try:
        client = openai.OpenAI(api_key=key)
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sei l'Architetto Silvia Cubeddu. Trasforma gli appunti di cantiere in un verbale tecnico professionale."},
                {"role": "user", "content": testo}
            ]
        )
        return res.choices[0].message.content
    except Exception as e: return f"Errore AI: {e}"

def mostra_lavori(df, DB_FILE):
    st.markdown("""
        <style>
        .btn-lavoro > div > button {
            height: 10em !important;
            font-size: 20px !important;
            border-radius: 20px !important;
            font-weight: bold !important;
            color: white !important;
            margin-bottom: 20px !important;
            white-space: pre-line !important;
        }
        .btn-dl > div > button { background-color: #E63946 !important; }
        .btn-pra > div > button { background-color: #457B9D !important; }
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        .btn-alt > div > button { background-color: #6C757D !important; }
        </style>
    """, unsafe_allow_html=True)

    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None

    if st.session_state.sezione_lavoro:
        render_sottopagina(st.session_state.sezione_lavoro, df, DB_FILE)
    else:
        st.title("🏗️ Area Lavori")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="btn-lavoro btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True):
                st.session_state.sezione_lavoro = "Direzione lavori"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True):
                st.session_state.sezione_lavoro = "APE / LEGGE 10"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-lavoro btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE", use_container_width=True):
                st.session_state.sezione_lavoro = "Pratica urbanistica"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True):
                st.session_state.sezione_lavoro = "ALTRO"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def render_sottopagina(sezione, df, DB_FILE):
    if st.button("⬅️ TORNA AI LAVORI"):
        st.session_state.sezione_lavoro = None
        st.rerun()
    
    st.header(f"📂 {sezione.upper()}")
    st.divider()

    # Logica di filtro
    if sezione == "APE / LEGGE 10":
        df_f = df[df['Pratica'].isin(["APE", "Legge 10"])]
    elif sezione == "ALTRO":
        df_f = df[~df['Pratica'].isin(["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10"])]
    else:
        df_f = df[df['Pratica'] == sezione]

    if df_f.empty:
        st.info(f"Nessuna pratica '{sezione}' trovata.")
    else:
        for i, r in df_f.iterrows():
            with st.expander(f"👤 {r['Cliente']} - 📍 {r['Web']}"):
                if sezione == "Direzione lavori":
                    # --- LOGICA ESTRAPOLATA DAL TUO CODICE ---
                    tab1, tab2 = st.tabs(["📋 Checklist Documenti", "🎙️ Diario Cantiere & AI"])
                    
                    with tab1:
                        st.write("**Verifica Documentale Corrente:**")
                        # Utilizziamo le note o campi extra se vuoi salvare lo stato
                        ck1 = st.checkbox("DURC Regolare", key=f"durc_{i}")
                        ck2 = st.checkbox("Pratica Urbanistica Depositata", key=f"urb_{i}")
                        ck3 = st.checkbox("Comunicazione Fine Lavori", key=f"fine_{i}")
                    
                    with tab2:
                        # Campo per l'API KEY (deve essere definita in app.py o inserita qui)
                        api_key = st.text_input("API Key OpenAI", type="password", key=f"key_{i}")
                        
                        u_note = st.text_area("Note Sopralluogo / Appunti:", value=r['Note'], height=150, key=f"note_{i}")
                        
                        col_ai1, col_ai2 = st.columns(2)
                        if col_ai1.button("🤖 Genera Verbale con AI", key=f"ai_{i}"):
                            res = genera_verbale_ai(u_note, api_key)
                            st.session_state[f"verbale_{i}"] = res
                        
                        if f"verbale_{i}" in st.session_state:
                            st.text_area("Verbale Professionale Generato:", value=st.session_state[f"verbale_{i}"], height=200, key=f"v_res_{i}")
                    
                    if st.button("💾 SALVA AGGIORNAMENTI", key=f"save_{i}", use_container_width=True):
                        # Aggiorniamo il DF originale
                        df.at[i, 'Note'] = u_note
                        df.to_csv(DB_FILE, index=False)
                        st.success("Dati cantiere aggiornati!")
                else:
                    # Visualizzazione semplice per le altre categorie
                    st.write(f"**Stato:** {r['Stato']} | **Scadenza:** {r['Scadenza']}")
                    st.write(f"**Note:** {r['Note']}")
                    if st.button("Modifica in Anagrafica", key=f"edit_{i}"):
                        st.session_state.menu_sel = "ANAGRAFICA"
                        st.session_state.cliente_sel = i
                        st.rerun()
