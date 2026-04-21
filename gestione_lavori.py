import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    st.markdown("""
        <style>
        /* DASHBOARD PRINCIPALE - BOTTONI GIGANTI RIFINITI */
        .btn-lavoro > div > button {
            height: 10em !important; 
            font-size: 20px !important; 
            border-radius: 20px !important;
            font-weight: bold !important; 
            color: white !important; 
            margin-bottom: 20px !important; 
            white-space: pre-line !important;
            border: none !important;
            transition: 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }
        .btn-lavoro > div > button:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.2) !important;
        }
        
        .btn-dl > div > button { background-color: #E63946 !important; }
        .btn-pra > div > button { background-color: #457B9D !important; }
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        .btn-alt > div > button { background-color: #6C757D !important; }

        /* LISTA SINISTRA - IDENTICA AD ANAGRAFICA */
        div.stButton > button[key^="list_"] {
            height: 45px !important;
            width: 100% !important;
            text-align: left !important;
            border-radius: 10px !important;
            background-color: white !important;
            border: 1px solid #e2e8f0 !important;
            font-size: 15px !important;
        }
        
        /* BOTTONI AZIONE (AGGIUNGI / CANCELLA) - IDENTICI AD ANAGRAFICA */
        div.stButton > button[key="btn_new"], .btn-del-massivo > div > button {
            height: 45px !important;
            font-weight: bold !important;
            margin-top: 5px !important;
        }

        /* TASTO BACK PICCOLO SOPRA LA RICERCA */
        div.stButton > button[key="btn_back"] {
            height: 30px !important;
            font-size: 12px !important;
            margin-bottom: 10px !important;
            padding: 0px 10px !important;
        }

        .btn-del-massivo > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
        }

        /* BOTTONI SCHEDA (AGGIORNA / ELIMINA) - IDENTICI AD ANAGRAFICA */
        .btn-aggiorna > div > button {
            background-color: #457B9D !important;
            color: white !important;
            height: 45px !important;
            font-weight: bold !important;
            border: none !important;
        }

        .btn-elimina-singolo > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
            height: 45px !important;
            font-weight: bold !important;
        }
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

def render_modulo(sezione, df, DB_FILE):
    st.header(f"📂 {sezione.upper()}")

    # Filtro dati
    if sezione == "APE / LEGGE 10":
        df_f = df[df['Pratica'].isin(["APE", "Legge 10"])]
    elif sezione == "ALTRO":
        df_f = df[~df['Pratica'].isin(["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10"])]
    else:
        df_f = df[df['Pratica'] == sezione]

    # Layout Anagrafica [1.2, 2]
    c_list, c_form = st.columns([1.2, 2])

    with c_list:
        if st.button("⬅️ BACK", key="btn_back"):
            st.session_state.sezione_lavoro = None
            st.session_state.lavoro_sel = None
            st.rerun()

        # Barra superiore [3, 1]
        c1, c2 = st.columns([3, 1])
        with c1:
            search = st.text_input("🔍 Cerca...", placeholder="Filtra...", label_visibility="collapsed")
        with c2:
            if st.button("➕", key="btn_new", use_container_width=True):
                nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
                tipo = "APE" if sezione == "APE / LEGGE 10" else (sezione if sezione != "ALTRO" else "Altro")
                nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Lavoro", "", "", "", "", "", "", "", tipo, "Da fare", "", ""]], columns=df.columns)
                df = pd.concat([df, nuova_riga], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.session_state.lavoro_sel = len(df) - 1
                st.rerun()
        
        st.markdown('<div class="btn-del-massivo">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            ids = [k.replace("chk_", "") for k, v in st.session_state.items() if k.startswith("chk_") and v is True]
            if ids:
                df = df[~df['id'].isin(ids)]
                df.to_csv(DB_FILE, index=False)
                st.session_state.lavoro_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        df_filt = df_f[df_f.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df_f
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            c_sel.checkbox("", key=f"chk_{r['id']}", label_visibility="collapsed")
            if c_btn.button(f"👤 {r['Cliente']} — {r['Pratica']}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.lavoro_sel = i
                st.rerun()

    with c_form:
        idx = st.session_state.get('lavoro_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente']}")
            
            with st.container(border=True):
                c_a, c_b = st.columns(2)
                u_cli = c_a.text_input("👤 Nome / Ragione Sociale", r['Cliente'])
                u_cf = c_b.text_input("🆔 C.F. / P.IVA", r['C.F. / P.IVA'])
                
                c_c, c_d, c_e = st.columns([2, 1, 1.5])
                u_ind = c_c.text_input("🏠 Indirizzo Residenza", r['Indirizzo'])
                u_cap = c_d.text_input("📮 CAP", r.get('CAP', ''))
                u_cit = c_e.text_input("🏙️ Città", r.get('Città', ''))

                st.write("---")
                u_web = st.text_input("📍 Indirizzo Pratica / Cantiere", r.get('Web', ''))
                
                c_f, c_g, c_h = st.columns([1.5, 1, 1.5])
                u_pra = c_f.text_input("🏗️ Tipo Pratica", r['Pratica'], disabled=True)
                u_sta = c_g.selectbox("🚦 Stato", ["Da fare", "In corso", "Chiusa", "Annullata"], 
                                     index=["Da fare", "In corso", "Chiusa", "Annullata"].index(r['Stato']) if r['Stato'] in ["Da fare", "In corso", "Chiusa", "Annullata"] else 0)
                u_sca = c_h.text_input("📅 Scadenza", r['Scadenza'])
                
                u_note = st.text_area("📝 Note", r['Note'], height=120)

                st.write("---")
                b_agg_col, b_del_col = st.columns(2)
                
                with b_agg_col:
                    st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                    if st.button("🔄 AGGIORNA", key=f"up_{idx}", use_container_width=True):
                        df.loc[idx, ['Cliente', 'C.F. / P.IVA', 'Indirizzo', 'CAP', 'Città', 'Web', 'Stato', 'Scadenza', 'Note']] = [u_cli, u_cf, u_ind, u_cap, u_cit, u_web, u_sta, u_sca, u_note]
                        df.to_csv(DB_FILE, index=False)
                        st.success("Salvato!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                with b_del_col:
                    st.markdown('<div class="btn-elimina-singolo">', unsafe_allow_html=True)
                    if st.button("🗑️ ELIMINA", key=f"del_{idx}", use_container_width=True):
                        df = df.drop(idx)
                        df.to_csv(DB_FILE, index=False)
                        st.session_state.lavoro_sel = None
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Seleziona un lavoro dalla lista a sinistra.")
