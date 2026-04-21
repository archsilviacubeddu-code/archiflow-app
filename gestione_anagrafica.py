import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COL_ANAGRAFICA):
    st.header("📇 Gestione Anagrafica")

    # BARRA SUPERIORE: RICERCA E AGGIUNGI
    col_search, col_add = st.columns([4, 1])
    with col_search:
        search = st.text_input("🔍 Cerca cliente...", placeholder="Inserisci nome o parte del nome...")
    with col_add:
        if st.button("➕ NUOVO CLIENTE", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "", "Attivo", "", ""]], columns=COL_ANAGRAFICA)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

    # FILTRO
    df_filtrato = df[df['Cliente'].str.contains(search, case=False)] if search else df

    st.divider()

    # SCHEDA DETTAGLIATA (Se un cliente è selezionato)
    if st.session_state.get("cliente_selezionato") is not None:
        idx = st.session_state.cliente_selezionato
        r = df.loc[idx]
        
        with st.expander(f"📂 SCHEDA CLIENTE: {r['Cliente']}", expanded=True):
            st.subheader(f"Dettagli di {r['Cliente']}")
            
            c1, c2 = st.columns(2)
            u_cli = c1.text_input("Nome Cliente", r['Cliente'])
            u_cf = c2.text_input("C.F. / P.IVA", r['C.F. / P.IVA'])
            
            c3, c4, c5 = st.columns([2, 1, 1])
            u_ind = c3.text_input("Indirizzo", r['Indirizzo'])
            u_cap = c4.text_input("CAP", r['CAP'])
            u_cit = c5.text_input("Città", r['Città'])
            
            c6, c7 = st.columns(2)
            u_tel = c6.text_input("Telefono", r['Telefono'])
            u_mail = c7.text_input("Email", r['Email'])
            
            c8, c9, c10 = st.columns(3)
            u_pra = c8.text_input("Pratica", r['Pratica'])
            u_sta = c9.selectbox("Stato", ["Attivo", "Chiuso"], index=0 if r['Stato']=="Attivo" else 1)
            u_sca = c10.text_input("Scadenza", r['Scadenza'])
            
            u_note = st.text_area("Note", r['Note'])

            st.divider()
            col_agg, col_del, col_chiudi = st.columns([1, 1, 1])
            
            if col_agg.button("🔄 AGGIORNA DATI", use_container_width=True):
                df.loc[idx] = [r['id'], u_cli, u_cf, u_ind, u_cap, u_cit, u_tel, u_mail, r['Web'], u_pra, u_sta, u_sca, u_note]
                df.to_csv(DB_FILE, index=False)
                st.success("Dati aggiornati correttamente!")
                st.rerun()
                
            if col_del.button("🗑️ CANCELLA CLIENTE", use_container_width=True):
                df = df.drop(idx)
                df.to_csv(DB_FILE, index=False)
                st.session_state.cliente_selezionato = None
                st.rerun()
                
            if col_chiudi.button("❌ CHIUDI SCHEDA", use_container_width=True):
                st.session_state.cliente_selezionato = None
                st.rerun()

    # LISTA CLIENTI (Cliccabile)
    st.write("### Elenco Clienti")
    st.markdown('<div class="table-header">Clicca sul nome per aprire la scheda</div>', unsafe_allow_html=True)
    
    for i, r in df_filtrato.iterrows():
        if st.button(f"👤 {r['Cliente']} | {r['Pratica']} | 📍 {r['Indirizzo']}", key=f"btn_cli_{i}", use_container_width=True):
            st.session_state.cliente_selezionato = i
            st.rerun()
