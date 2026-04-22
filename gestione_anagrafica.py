import streamlit as st
import pandas as pd
from gestione_documenti import interfaccia_semafori

def mostra_anagrafica(df, DB_FILE, COLONNE):
    # CSS - Mantengo il tuo stile ma sistemo i tasti in alto
    st.markdown("""
        <style>
        div.stButton > button[key^="list_"] {
            height: 45px !important; width: 100% !important; text-align: left !important;
            border-radius: 10px !important; background-color: white !important;
            border: 1px solid #e2e8f0 !important; font-size: 15px !important;
        }
        .btn-aggiorna > div > button {
            background-color: #457B9D !important; color: white !important;
            height: 50px !important; font-weight: bold !important; width: 100% !important;
        }
        .btn-cancella-top > div > button {
            background-color: #fee2e2 !important; color: #ef4444 !important;
            border: 1px solid #ef4444 !important; height: 45px !important; font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica")

    # 1. TASTI DI COMANDO IN ALTO
    c_cmd1, c_cmd2 = st.columns(2)
    with c_cmd1:
        if st.button("➕ AGGIUNGI CLIENTE", key="btn_new", use_container_width=True):
            nuovo_id = str(df['id'].astype(int).max() + 1) if not df.empty else "1"
            # Creiamo la riga vuota
            nuova_riga = pd.DataFrame([[nuovo_id, "", "", "", "", "", "", "", "", "Altro", "Da fare", "", "", "{}"]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.session_state.cliente_sel = len(df) - 1
            st.rerun()
    
    with c_cmd2:
        st.markdown('<div class="btn-cancella-top">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA SELEZIONATI", use_container_width=True):
            # Troviamo chi ha la spunta
            selezionati = [k.replace("check_", "") for k, v in st.session_state.items() if k.startswith("check_") and v is True]
            if selezionati:
                df = df[~df['id'].isin(selezionati)]
                df.to_csv(DB_FILE, index=False)
                # Puliamo i quadratini dalla memoria
                for k in selezionati: 
                    if f"check_{k}" in st.session_state: del st.session_state[f"check_{k}"]
                st.session_state.cliente_sel = None
                st.success(f"Ho buttato via {len(selezionati)} contatti!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 2. LISTA E SCHEDA
    col_lista, col_scheda = st.columns([1.2, 2])

    with col_lista:
        search = st.text_input("🔍 Cerca...", placeholder="Filtra...", label_visibility="collapsed")
        df_f = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)] if search else df
        
        for i, r in df_f.iterrows():
            cl1, cl2 = st.columns([0.2, 0.8])
            # Il quadratino per la cancellazione
            cl1.checkbox("", key=f"check_{r['id']}", label_visibility="collapsed")
            # Il tasto per aprire la scheda
            nome_display = r['Cliente'] if r['Cliente'] != "" else "Nuovo Cliente"
            if cl2.button(f"👤 {nome_display}", key=f"list_{r['id']}", use_container_width=True):
                st.session_state.cliente_sel = i
                st.rerun()

    with col_scheda:
        idx = st.session_state.get('cliente_sel')
        if idx is not None and idx in df.index:
            r = df.loc[idx]
            st.subheader(f"Dettaglio: {r['Cliente'] or 'Nuovo'}")
            
            u_cli = st.text_input("Ragione Sociale", r['Cliente'])
            u_cf = st.text_input("C.F. / P.IVA", r['C.F. / P.IVA'])
            
            c_p1, c_p2 = st.columns(2)
            # IL TUO MENU A TENDINA COMPLETO
            voci_pratica = [
                "Cantiere interni", "Cantiere esterni", "Direzione lavori", 
                "Computo metrico", "Progettazione", "Rilievo", "CILA", "SCIA", 
                "Accertamento di conformità", "Millesimi", "Perizia", 
                "Accesso atti", "Render", "Altro"
            ]
            default_p = r['Pratica'] if r['Pratica'] in voci_pratica else "Altro"
            u_pra = c_p1.selectbox("Tipo Pratica", voci_pratica, index=voci_pratica.index(default_p))
            u_sca = c_p2.text_input("Scadenza", r['Scadenza'])
            
            st.write("---")
            # Qui andranno i documenti (per ora li chiamiamo e basta)
            interfaccia_semafori(u_pra, df, idx)
            
            st.write("---")
            st.markdown('<div class="btn-aggiorna">', unsafe_allow_html=True)
            if st.button("💾 AGGIORNA E SALVA TUTTO"):
                df.at[idx, 'Cliente'] = u_cli
                df.at[idx, 'C.F. / P.IVA'] = u_cf
                df.at[idx, 'Pratica'] = u_pra
                df.at[idx, 'Scadenza'] = u_sca
                # Salviamo sul file
                df.to_csv(DB_FILE, index=False)
                st.success("Tutto salvato!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
