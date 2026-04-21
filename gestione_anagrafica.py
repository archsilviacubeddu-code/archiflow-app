import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COLONNE):
    # CSS per rimettere lo stile pulito, tasti della lista a sinistra e scheda a destra
    st.markdown("""
        <style>
        /* Bottoni della lista: Sottili, eleganti e a larghezza fissa */
        div.stButton > button[key^="list_"] {
            height: 45px !important;
            width: 100% !important;
            max-width: 450px !important;
            padding: 5px 15px !important;
            font-size: 14px !important;
            text-align: left !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            background-color: white !important;
            margin-bottom: -5px !important;
            display: block !important;
        }
        div.stButton > button[key^="list_"]:hover {
            border-color: #3b82f6 !important;
            background-color: #f8fafc !important;
        }
        /* Stile per i campi input della scheda */
        .stTextInput input {
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    # BARRA SUPERIORE
    c1, c2 = st.columns([4, 1])
    with c1:
        search = st.text_input("🔍 Cerca...", placeholder="Cerca per nome, pratica o indirizzo...", label_visibility="collapsed")
    with c2:
        if st.button("➕ AGGIUNGI CLIENTE", use_container_width=True):
            st.session_state.modo = "aggiungi"
            st.session_state.cliente_sel = None
            st.rerun()

    # FILTRO
    df_filt = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df

    st.divider()

    # LAYOUT: LISTA A SINISTRA (1/3) | SCHEDA A DESTRA (2/3)
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        st.write("### 👥 Elenco")
        for i, r in df_filt.iterrows():
            # Il tasto mostra Stato, Nome e Indirizzo. Cliccandolo si apre la scheda a destra.
            stato_icon = "🟢" if r['Stato'] == "Attivo" else "⚪"
            label = f"{stato_icon} **{r['Cliente']}**\n📍 {r['Indirizzo']}"
            if st.button(label, key=f"list_{i}"):
                st.session_state.modo = "modifica"
                st.session_state.cliente_sel = i
                st.rerun()

    with col_scheda:
        modo = st.session_state.get('modo')
        idx = st.session_state.get('cliente_sel')

        if modo:
            # Recuperiamo i dati se siamo in modifica, altrimenti foglio bianco
            r = df.loc[idx] if idx is not None else {c: "" for c in COLONNE}
            
            st.subheader(f"📑 Scheda: {r.get('Cliente', 'Nuovo Cliente')}")
            
            with st.container():
                # Organizzazione dei campi
                c1, c2 = st.columns(2)
                u_cli = c1.text_input("Ragione Sociale / Nome", r.get('Cliente', ''))
                u_cf = c2.text_input("C.F. / P.IVA", r.get('C.F. / P.IVA', ''))
                
                u_ind = st.text_input("Indirizzo Cantiere", r.get('Indirizzo', ''))
                
                c3, c4 = st.columns(2)
                u_tel = c3.text_input("Telefono", r.get('Telefono', ''))
                u_mail = c4.text_input("Email", r.get('Email', ''))
                
                c5, c6, c7 = st.columns([1.5, 1, 1.5])
                u_pra = c5.text_input("Pratica", r.get('Pratica', ''))
                u_sta = c6.selectbox("Stato", ["Attivo", "Chiuso"], index=0 if r.get('Stato')=="Attivo" else 1)
                u_sca = c7.text_input("Scadenza", r.get('Scadenza', ''))
                
                u_note = st.text_area("Note e Appunti", r.get('Note', ''), height=150)

                st.write("---")
                # TASTI AZIONE DENTRO LA SCHEDA
                b_agg, b_del, b_chiudi = st.columns(3)
                
                if b_agg.button("🔄 AGGIORNA DATI", use_container_width=True, type="primary"):
                    # Lista dati aggiornata
                    nuovi_valori = [
                        r['id'] if idx is not None else str(len(df)+1), 
                        u_cli, u_cf, u_ind, r.get('CAP',''), r.get('Città',''), 
                        u_tel, u_mail, r.get('Web',''), u_pra, u_sta, u_sca, u_note
                    ]
                    
                    if modo == "aggiungi":
                        df.loc[len(df)] = nuovi_valori
                    else:
                        df.loc[idx] = nuovi_valori
                        
                    df.to_csv(DB_FILE, index=False)
                    st.success("Dati salvati!")
                    st.rerun()

                if b_del.button("🗑️ CANCELLA CLIENTE", use_container_width=True):
                    if idx is not None:
                        df = df.drop(idx)
                        df.to_csv(DB_FILE, index=False)
                        st.session_state.modo = None
                        st.session_state.cliente_sel = None
                        st.rerun()

                if b_chiudi.button("❌ CHIUDI", use_container_width=True):
                    st.session_state.modo = None
                    st.rerun()
        else:
            st.info("👈 Seleziona un cliente dalla lista per vedere o modificare i dettagli.")
