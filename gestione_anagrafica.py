import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COLONNE):
    st.markdown("""
        <style>
        div.stButton > button[key^="list_"] {
            height: 45px !important;
            width: 100% !important;
            text-align: left !important;
            border-radius: 10px !important;
            background-color: white !important;
            border: 1px solid #e2e8f0 !important;
            font-size: 15px !important;
        }
        
        div.stButton > button[key="btn_new"], .btn-del-massivo > div > button {
            height: 45px !important;
            font-weight: bold !important;
            margin-top: 5px !important;
        }

        .btn-del-massivo > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
        }

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

    st.header("📇 Gestione Anagrafica")

    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra clienti...", label_visibility="collapsed")
    
    with c2:
        if st.button("➕ AGGIUNGI", key="btn_new", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "Cantiere", "Da fare", "", ""]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.cliente_sel = len(df) - 1
            st.rerun()
        
        st.markdown('<div class="btn-del-massivo">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                df = df[~df['id'].isin(selezionati)]
                df.to_csv(DB_FILE, index=False)
                for s_key in list(st.session_state.keys()):
                    if s_key.startswith("check_"): st.session_state[s_key] = False
                st.session_state.cliente_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
    st.divider()

    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            c_sel.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            if c_btn.button(f"👤 {r['Cliente']}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('cliente_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente']}")
            
            # DATI CLIENTE
            c1, c2 = st.columns(2)
            u_cli = c1.text_input("👤 Nome / Ragione Sociale", r['Cliente'])
            u_cf = c2.text_input("🆔 C.F. / P.IVA", r['C.F. / P.IVA'])
            
            c3, c4, c5 = st.columns([2, 1, 1.5])
            u_ind = c3.text_input("🏠 Indirizzo", r['Indirizzo'])
            u_cap = c4.text_input("📮 CAP", r.get('CAP', ''))
            u_cit = c5.text_input("🏙️ Città", r.get('Città', ''))

            st.write("---")
            # DATI PRATICA / CANTIERE
            u_ind_cantiere = st.text_input("📍 Indirizzo Pratica / Cantiere", r.get('Web', '')) # Usiamo Web come storage temporaneo se non vuoi cambiare CSV, o mappalo correttamente
            
            c6, c7, c8 = st.columns([1.5, 1, 1.5])
            
            # Menu Pratica
            opzioni_pratica = ["Cantiere", "Direzione lavori", "Progettazione", "Pratica urbanistica", "Rilievo", "APE", "Legge 10", "Millesimi", "Perizia", "Consulenza", "Altro"]
            default_pra = r['Pratica'] if r['Pratica'] in opzioni_pratica else "Altro"
            u_pra_sel = c6.selectbox("🏗️ Tipo Pratica", opzioni_pratica, index=opzioni_pratica.index(default_pra))
            
            if u_pra_sel == "Altro":
                u_pra = c6.text_input("Specifica altro...", r['Pratica'] if r['Pratica'] not in opzioni_pratica else "")
            else:
                u_pra = u_pra_sel

            # Menu Stato
            opzioni_stato = ["Da fare", "In corso", "Chiusa", "Annullata"]
            default_sta = r['Stato'] if r['Stato'] in opzioni_stato else "Da fare"
            u_sta = c7.selectbox("🚦 Stato", opzioni_stato, index=opzioni_stato.index(default_sta))
            
            u_sca = c8.text_input("📅 Scadenza", r['Scadenza'])
            
            c9, c10 = st.columns(2)
            u_tel = c9.text_input("📞 Telefono", r['Telefono'])
            u_mail = c10.text_input("📧 Email", r['Email'])
            
            u_note = st.text_area("📝 Note", r['Note'], height=120)

            st.write("---")
            b_agg_col, b_del_col = st.columns(2)
            
            with b_agg_col:
                st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
                if st.button("🔄 AGGIORNA", use_container_width=True):
                    df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, u_ind_cantiere, u_pra, u_sta, u_sca, u_note]
                    df.to_csv(DB_FILE, index=False)
                    st.success("Salvato!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with b_del_col:
                st.markdown('<div class="btn-elimina-singolo">', unsafe_allow_html=True)
                if st.button("🗑️ ELIMINA", use_container_width=True):
                    df = df.drop(idx)
                    df.to_csv(DB_FILE, index=False)
                    st.session_state.cliente_sel = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
