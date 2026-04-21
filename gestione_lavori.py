import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    # CSS CLONATO DALL'ANAGRAFICA + AGGIUNTA TASTO BACK
    st.markdown("""
        <style>
        /* Pulsanti della Dashboard Iniziale */
        .btn-lavoro > div > button {
            height: 10em !important; font-size: 20px !important; border-radius: 20px !important;
            font-weight: bold !important; color: white !important; margin-bottom: 20px !important; white-space: pre-line !important;
        }
        .btn-dl > div > button { background-color: #E63946 !important; }
        .btn-pra > div > button { background-color: #457B9D !important; }
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        .btn-alt > div > button { background-color: #6C757D !important; }

        /* Bottoni lista sinistra */
        div.stButton > button[key^="worklist_"] {
            height: 45px !important; width: 100% !important; text-align: left !important;
            border-radius: 10px !important; background-color: white !important; border: 1px solid #e2e8f0 !important;
            font-size: 15px !important;
        }
        
        /* Pulsanti Azione (Aggiungi/Cancella/Back) */
        div.stButton > button[key="btn_new_work"], 
        div.stButton > button[key="btn_back_work"],
        .btn-del-massivo-work > div > button {
            height: 45px !important; font-weight: bold !important; margin-top: 5px !important;
        }

        /* Tasto BACK (Grigio scuro professionale) */
        div.stButton > button[key="btn_back_work"] {
            background-color: #334155 !important; color: white !important; border: none !important;
        }

        .btn-del-massivo-work > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important;
        }

        .btn-aggiorna-work > div > button { background-color: #457B9D !important; color: white !important; height: 45px !important; font-weight: bold !important; border: none !important; }
        .btn-elimina-work > div > button { background-color: #fee2e2 !important; color: #ef4444 !important; border: 1px solid #ef4444 !important; height: 45px !important; }
        </style>
    """, unsafe_allow_html=True)

    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None
    if "lavoro_sel" not in st.session_state:
        st.session_state.lavoro_sel = None

    if st.session_state.sezione_lavoro:
        render_modulo_coerente(st.session_state.sezione_lavoro, df, DB_FILE)
    else:
        # DASHBOARD PRINCIPALE
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

def render_modulo_coerente(sezione, df, DB_FILE):
    # Header solo titolo
    st.header(f"📂 {sezione.upper()}")

    # Filtro dei dati per la sezione specifica
    if sezione == "APE / LEGGE 10":
        df_f = df[df['Pratica'].isin(["APE", "Legge 10"])]
    elif sezione == "ALTRO":
        df_f = df[~df['Pratica'].isin(["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10"])]
    else:
        df_f = df[df['Pratica'] == sezione]

    # LAYOUT A DUE COLONNE
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        # TASTO BACK IN CIMA ALLA LISTA
        if st.button("⬅️ BACK", key="btn_back_work", use_container_width=True):
            st.session_state.sezione_lavoro = None
            st.session_state.lavoro_sel = None
            st.rerun()
        
        st.write("") # Spaziatore

        # BARRA AZIONI (Cerca + Aggiungi)
        c_search, c_add = st.columns([2, 1])
        search = c_search.text_input("🔍", placeholder="Cerca...", label_visibility="collapsed")
        
        if c_add.button("➕", key="btn_new_work", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            tipo_init = "APE" if sezione == "APE / LEGGE 10" else (sezione if sezione != "ALTRO" else "Altro")
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Lavoro", "", "", "", "", "", "", "", tipo_init, "Da fare", "", ""]], columns=df.columns)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.lavoro_sel = len(df) - 1
            st.rerun()

        # TASTO CANCELLA SOTTO
        st.markdown('<div class="btn-del-massivo-work">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA SELEZIONATI", key="btn_del_work", use_container_width=True):
            to_del = [k.replace("workchk_", "") for k, v in st.session_state.items() if k.startswith("workchk_") and v is True]
            if to_del:
                df = df[~df['id'].isin(to_del)]
                df.to_csv(DB_FILE, index=False)
                st.session_state.lavoro_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # LISTA FILTRATA
        df_filt = df_f[df_f.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df_f
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            c_sel.checkbox("", key=f"workchk_{r['id']}", label_visibility="collapsed")
            if c_btn.button(f"👤 {r['Cliente']} — {r['Pratica']}", key=f"worklist_{r['id']}", use_container_width=True):
                st.session_state.lavoro_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('lavoro_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente']}")
            
            with st.container(border=True):
                c1, c2 = st.columns(2)
                u_cli = c1.text_input("👤 Nome / Ragione Sociale", r['Cliente'])
                u_cf = c2.text_input("🆔 C.F. / P.IVA", r['C.F. / P.IVA'])
                u_ind_pra = st.text_input("📍 Indirizzo Pratica / Cantiere", r.get('Web', ''))
                
                c3, c4, c5 = st.columns([1.5, 1, 1.5])
                u_pra = c3.text_input("🏗️ Tipo Pratica", r['Pratica'], disabled=True)
                u_sta = c4.selectbox("🚦 Stato", ["Da fare", "In corso", "Chiusa", "Annullata"], 
                                    index=["Da fare", "In corso", "Chiusa", "Annullata"].index(r['Stato']) if r['Stato'] in ["Da fare", "In corso", "Chiusa", "Annullata"] else 0)
                u_sca = c5.text_input("📅 Scadenza", r['Scadenza'])
                u_note = st.text_area("📝 Note", r['Note'], height=200)

                st.write("---")
                b_agg_col, b_del_col = st.columns(2)
                with b_agg_col:
                    st.markdown('<div class="btn-aggiorna-work">', unsafe_allow_html=True)
                    if st.button("🔄 AGGIORNA", key=f"save_w_{idx}", use_container_width=True):
                        df.loc[idx, ['Cliente', 'C.F. / P.IVA', 'Web', 'Stato', 'Scadenza', 'Note']] = [u_cli, u_cf, u_ind_pra, u_sta, u_sca, u_note]
                        df.to_csv(DB_FILE, index=False)
                        st.success("Dati aggiornati!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with b_del_col:
                    st.markdown('<div class="btn-elimina-work">', unsafe_allow_html=True)
                    if st.button("🗑️ ELIMINA", key=f"del_w_{idx}", use_container_width=True):
                        df = df.drop(idx)
                        df.to_csv(DB_FILE, index=False)
                        st.session_state.lavoro_sel = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("⬅️ Seleziona un cliente dalla lista per aprire la scheda lavoro.")
