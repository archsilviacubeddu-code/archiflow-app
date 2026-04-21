import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COLONNE):
    st.markdown("""
        <style>
        /* Bottoni lista: Larghi e puliti */
        div.stButton > button[key^="list_"] {
            height: 50px !important;
            width: 100% !important;
            text-align: left !important;
            border-radius: 10px !important;
            background-color: white !important;
            border: 1px solid #e2e8f0 !important;
            font-size: 15px !important;
        }
        /* Tasto CANCELLA in alto (rosso e cattivo) */
        .btn-del-massivo > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
            font-weight: bold !important;
            height: 40px !important;
        }
        /* Checkbox più visibili */
        .stCheckbox { margin-top: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    # BARRA SUPERIORE: CERCA, AGGIUNGI, CANCELLA
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra clienti...", label_visibility="collapsed")
    with c2:
        if st.button("➕ AGGIUNGI", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "Nuova Pratica", "Attivo", "", ""]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()
    
    # CANCELLAZIONE DI MASSA
    with c3:
        st.markdown('<div class="btn-del-massivo">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            # Prende tutti gli ID spuntati
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                df = df[~df['id'].isin(selezionati)]
                df.to_csv(DB_FILE, index=False)
                # Svuota i checkbox nello stato
                for s_key in list(st.session_state.keys()):
                    if s_key.startswith("check_"): st.session_state[s_key] = False
                st.session_state.cliente_sel = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
    st.divider()

    # LAYOUT: LISTA MULTIPLA (SINISTRA) | SCHEDA (DESTRA)
    col_lista, col_scheda = st.columns([1.5, 2])

    with col_lista:
        st.write("### Selezione e Apertura")
        for i, r in df_filt.iterrows():
            c_sel, c_btn = st.columns([0.15, 0.85])
            # Checkbox per cancellazione massiva
            c_sel.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            # Tasto largo per aprire la scheda specifica
            label_btn = f"👤 {r['Cliente']} | {r['Pratica']} | {r['Stato']}"
            if c_btn.button(label_btn, key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('cliente_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"📑 Scheda: {r['Cliente']}")
            
            # Form Modifica
            c1, c2 = st.columns(2)
            u_cli = c1.text_input("Ragione Sociale", r['Cliente'])
            u_cf = c2.text_input("C.F. / P.IVA", r['C.F. / P.IVA'])
            u_ind = st.text_input("Indirizzo Cantiere", r['Indirizzo'])
            
            c3, c4 = st.columns(2)
            u_tel = c3.text_input("Telefono", r['Telefono'])
            u_mail = c4.text_input("Email", r['Email'])
            
            c5, c6, c7 = st.columns([1.5, 1, 1.5])
            u_pra = c5.text_input("Pratica / Cantiere", r['Pratica'])
            u_sta = c6.selectbox("Stato", ["Attivo", "Chiuso"], index=0 if r['Stato']=="Attivo" else 1)
            u_sca = c7.text_input("Scadenza", r['Scadenza'])
            
            u_note = st.text_area("Note Interne", r['Note'], height=180)

            st.write("---")
            b_agg, b_del_singolo = st.columns(2)
            
            if b_agg.button("🔄 AGGIORNA DATI", use_container_width=True, type="primary"):
                df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, r.get('CAP',''), r.get('Città',''), u_tel, u_mail, r.get('Web',''), u_pra, u_sta, u_sca, u_note]
                df.to_csv(DB_FILE, index=False)
                st.success("Salvataggio effettuato!")
                st.rerun()

            if b_del_singolo.button("🗑️ ELIMINA SCHEDA", use_container_width=True):
                df = df.drop(idx)
                df.to_csv(DB_FILE, index=False)
                st.session_state.cliente_sel = None
                st.rerun()
        else:
            st.info("Spunta i quadratini a sinistra per cancellare in massa, o clicca sul nome per aprire la scheda.")
