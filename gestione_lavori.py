import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    st.markdown("""
        <style>
        /* Bottoni lista: Larghi e puliti (CLONATO DA ANAGRAFICA) */
        div.stButton > button[key^="list_"] {
            height: 45px !important;
            width: 100% !important;
            text-align: left !important;
            border-radius: 10px !important;
            background-color: white !important;
            border: 1px solid #e2e8f0 !important;
            font-size: 15px !important;
        }
        
        /* Bottoni colonna destra impilati (CLONATO DA ANAGRAFICA) */
        div.stButton > button[key="btn_new"], .btn-del-massivo > div > button {
            height: 45px !important;
            font-weight: bold !important;
            margin-top: 5px !important;
        }

        /* Tasto CANCELLA (Rosso) */
        .btn-del-massivo > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
        }

        /* Tasto AGGIORNA (Blu Professionale) */
        .btn-aggiorna > div > button {
            background-color: #457B9D !important;
            color: white !important;
            height: 45px !important;
            font-weight: bold !important;
            border: none !important;
        }

        /* Tasto ELIMINA (Rosso) */
        .btn-elimina-singolo > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
            height: 45px !important;
            font-weight: bold !important;
        }

        /* DASHBOARD PRINCIPALE - BOTTONI GIGANTI */
        .btn-lavoro > div > button {
            height: 10em !important; font-size: 20px !important; border-radius: 20px !important;
            font-weight: bold !important; color: white !important; margin-bottom: 20px !important; white-space: pre-line !important;
        }
        .btn-dl > div > button { background-color: #E63946 !important; }
        .btn-pra > div > button { background-color: #457B9D !important; }
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        .btn-alt > div > button { background-color: #6C757D !important; }
        </style>
    """, unsafe_allow_html=True)

    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None
    if "lavoro_sel" not in st.session_state:
        st.session_state.lavoro_sel = None

    if st.session_state.sezione_lavoro:
        render_modulo(st.session_state.sezione_lavoro, df, DB_FILE)
    else:
        st.header("🏗️ Selezione Area di Lavoro")
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

def render_modulo(sezione, df, DB_FILE):
    st.header(f"📂 {sezione.upper()}")

    # Filtro dati per categoria
    if sezione == "APE / LEGGE 10":
        df_f = df[df['Pratica'].isin(["APE", "Legge 10"])]
    elif sezione == "ALTRO":
        opzioni_fisse = ["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10"]
        df_f = df[~df['Pratica'].isin(opzioni_fisse)]
    else:
        df_f = df[df['Pratica'] == sezione]

    # BARRA SUPERIORE (Clonata da Anagrafica)
    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra clienti...", label_visibility="collapsed")
    with c2:
        if st.button("➕ AGGIUNGI", key="btn_new", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            tipo = "APE" if sezione == "APE / LEGGE 10" else (sezione if sezione != "ALTRO" else "Altro")
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", tipo, "Attivo", "", ""]], columns=df.columns)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.lavoro_sel = len(df) - 1
            st.rerun()
        
        st.markdown('<div class="btn-del-massivo">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                df = df[~df['id'].isin(selezionati)]
                df.to_csv(DB_FILE, index=False)
                st.session_state.lavoro_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    df_filt = df_f[df_f.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df_f
    st.divider()

    # LAYOUT [1.2, 2] (Clonato da Anagrafica)
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            c_sel.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            if c_btn.button(f"👤 {r['Cliente']}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.lavoro_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('lavoro_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente']}")
            
            c1, c2 = st.columns(2)
            u_cli = c1.text_input("👤 Nome", r['Cliente'])
            u_cf = c2.text_input("🆔 C.F. / P.IVA", r['C.F. / P.IVA'])
            u_ind = st.text_input("📍 Indirizzo Cantiere", r['Indirizzo'])
            
            c3, c4 = st.columns(2)
            u_tel = c3.text_input("📞 Telefono", r['Telefono'])
            u_mail = c4.text_input("📧 Email", r['Email'])
            
            c5, c6, c7 = st.columns([1.5, 1, 1.5])
            u_pra = c5.text_input("🏗️ Pratica", r['Pratica'])
            u_sta = c6.selectbox("🚦 Stato", ["Attivo", "Chiuso"], index=0 if r['Stato']=="Attivo" else 1)
            u_sca = c7.text_input("📅 Scadenza", r['Scadenza'])
            
            u_note = st.text_area("📝 Note", r['Note'], height=180)

            st.write("---")
            b_agg_col, b_del_col = st.columns(2)
            
            with b_agg_col:
                st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                if st.button("🔄 AGGIORNA", use_container_width=True):
                    df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, r.get('CAP',''), r.get('Città',''), u_tel, u_mail, r.get('Web',''), u_pra, u_sta, u_sca, u_note]
                    df.to_csv(DB_FILE, index=False)
                    st.success("Salvato!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with b_del_col:
                st.markdown('<div class="btn-elimina-singolo">', unsafe_allow_html=True)
                if st.button("🗑️ ELIMINA", use_container_width=True):
                    df = df.drop(idx)
                    df.to_csv(DB_FILE, index=False)
                    st.session_state.lavoro_sel = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
