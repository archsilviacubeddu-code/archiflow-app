import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    # CSS per layout e bottoni
    st.markdown("""
        <style>
        .btn-lavoro > div > button {
            height: 10em !important; font-size: 20px !important; border-radius: 20px !important;
            font-weight: bold !important; color: white !important; margin-bottom: 20px !important; white-space: pre-line !important;
        }
        .btn-dl > div > button { background-color: #E63946 !important; }
        .btn-pra > div > button { background-color: #457B9D !important; }
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        .btn-alt > div > button { background-color: #6C757D !important; }

        /* Stile lista lavori */
        div.stButton > button[key^="selwork_"] {
            text-align: left !important;
            padding: 10px !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            color: #1e293b !important;
        }
        div.stButton > button[key^="selwork_"]:hover {
            border-color: #3b82f6 !important;
            background-color: #eff6ff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None
    if "lavoro_id_attivo" not in st.session_state:
        st.session_state.lavoro_id_attivo = None

    if st.session_state.sezione_lavoro:
        render_modulo_lavoro(st.session_state.sezione_lavoro, df, DB_FILE)
    else:
        st.title("🏗️ Area Lavori")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="btn-lavoro btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True):
                st.session_state.sezione_lavoro = "Direzione lavori"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True):
                st.session_state.sezione_lavoro = "APE / LEGGE 10"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-lavoro btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE", use_container_width=True):
                st.session_state.sezione_lavoro = "Pratica urbanistica"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-lavoro btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True):
                st.session_state.sezione_lavoro = "ALTRO"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def render_modulo_lavoro(sezione, df, DB_FILE):
    # Header
    col_h1, col_h2 = st.columns([4,1])
    col_h1.header(f"📂 {sezione.upper()}")
    if col_h2.button("⬅️ CHIUDI"):
        st.session_state.sezione_lavoro = None
        st.session_state.lavoro_id_attivo = None
        st.rerun()

    st.divider()

    # Logica Filtro
    if sezione == "APE / LEGGE 10":
        df_f = df[df['Pratica'].isin(["APE", "Legge 10"])]
    elif sezione == "ALTRO":
        df_f = df[~df['Pratica'].isin(["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10"])]
    else:
        df_f = df[df['Pratica'] == sezione]

    col_sx, col_dx = st.columns([1.5, 2])

    with col_sx:
        # Cerca e Azioni
        c_search, c_new = st.columns([2, 1])
        term = c_search.text_input("🔍", placeholder="Cerca cliente...", label_visibility="collapsed")
        
        if c_new.button("➕ NUOVA SCHEDA", use_container_width=True):
            # Crea riga vuota specifica per la sezione
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            tipo_init = "APE" if sezione == "APE / LEGGE 10" else (sezione if sezione != "ALTRO" else "Altro")
            nuova_riga = pd.DataFrame([[nuovo_id, "NUOVO CLIENTE", "", "", "", "", "", "", "", tipo_init, "In corso", "", ""]], columns=df.columns)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.lavoro_id_attivo = nuovo_id
            st.rerun()

        if st.button("🗑️ CANCELLA", use_container_width=True):
            # Identifica ID selezionati dalle checkbox
            to_del = [k.replace("chk_work_", "") for k, v in st.session_state.items() if k.startswith("chk_work_") and v is True]
            if to_del:
                df = df[~df['id'].isin(to_del)]
                df.to_csv(DB_FILE, index=False)
                st.session_state.lavoro_id_attivo = None
                st.rerun()

        st.write("---")

        # Lista Clienti - Lavoro
        df_lista = df_f[df_f['Cliente'].str.contains(term, case=False)] if term else df_f
        
        for _, r in df_lista.iterrows():
            c_chk, c_name = st.columns([0.15, 0.85])
            c_chk.checkbox("", key=f"chk_work_{r['id']}", label_visibility="collapsed")
            # Visualizzazione: NOME CLIENTE — PRATICA
            label = f"👤 {r['Cliente']} — 📑 {r['Pratica']}"
            if c_name.button(label, key=f"selwork_{r['id']}", use_container_width=True):
                st.session_state.lavoro_id_attivo = r['id']
                st.rerun()

    with col_dx:
        id_attivo = st.session_state.get('lavoro_id_attivo')
        if id_attivo:
            # Recupera i dati freschi dal DF per l'ID selezionato
            r = df[df['id'] == id_attivo].iloc[0]
            
            st.subheader(f"🛠️ Scheda: {r['Cliente']}")
            st.info(f"Tipo di intervento: {r['Pratica']}")

            # Form di modifica
            with st.container(border=True):
                u_nome = st.text_input("Cliente", value=r['Cliente'])
                u_ind = st.text_input("Indirizzo / Riferimento Web", value=r['Web'])
                u_stato = st.selectbox("Stato Avanzamento", ["Da iniziare", "In corso", "Sospeso", "Ultimato"], 
                                      index=["Da iniziare", "In corso", "Sospeso", "Ultimato"].index(r['Stato']) if r['Stato'] in ["Da iniziare", "In corso", "Sospeso", "Ultimato"] else 0)
                
                if sezione == "Direzione lavori":
                    st.write("**Strumenti Cantiere:**")
                    u_note = st.text_area("Diario / Verbali", value=r['Note'], height=200)
                else:
                    u_note = st.text_area("Note e Dettagli", value=r['Note'], height=200)

                if st.button("💾 AGGIORNA DATI", type="primary", use_container_width=True):
                    idx = df[df['id'] == id_attivo].index[0]
                    df.at[idx, 'Cliente'] = u_nome
                    df.at[idx, 'Web'] = u_ind
                    df.at[idx, 'Stato'] = u_stato
                    df.at[idx, 'Note'] = u_note
                    df.to_csv(DB_FILE, index=False)
                    st.success("Scheda aggiornata correttamente!")
                    st.rerun()
        else:
            st.write("### ⬅️ Seleziona un lavoro dalla lista")
            st.caption("Puoi cercare per nome o selezionare più voci per la cancellazione massiva.")
