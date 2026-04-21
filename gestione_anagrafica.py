import streamlit as st
import pandas as pd

def mostra_anagrafica(df, DB_FILE, COLONNE):
    st.header("📇 Gestione Anagrafica")
    
    # TASTO AGGIUNGI (In alto come nel tuo codice)
    if st.button("➕ AGGIUNGI NUOVO CLIENTE"):
        st.session_state.modo = "aggiungi"
        st.session_state.cliente_sel = None
        st.rerun()

    # CERCA
    cerca_ana = st.text_input("🔍 Cerca Cliente:")
    df_filt_ana = df[df.apply(lambda r: cerca_ana.lower() in r.astype(str).str.lower().values, axis=1)] if cerca_ana else df

    # LAYOUT A DUE COLONNE (Sinistra: Lista / Destra: Form)
    col_list, col_form = st.columns([1, 2])

    with col_list:
        if not df_filt_ana.empty:
            # Mostra solo ID e Cliente per la selezione
            df_sel = df_filt_ana[["id", "Cliente"]].copy()
            df_sel.insert(0, "Seleziona", False)
            
            # Tabella di selezione (stile del tuo codice)
            edited_df = st.data_editor(
                df_sel, 
                hide_index=True, 
                disabled=["id", "Cliente"], 
                use_container_width=True, 
                key="sel_ana"
            )
            
            selected_ids = edited_df[edited_df["Seleziona"] == True]["id"].tolist()
            
            if selected_ids and st.button("📂 APRI SCHEDA", use_container_width=True):
                st.session_state.modo = "modifica"
                st.session_state.cliente_sel = selected_ids[-1]
                st.rerun()

    with col_form:
        modo = st.session_state.get('modo')
        if modo:
            id_at = st.session_state.get('cliente_sel')
            
            # Recupero dati per il form
            if id_at:
                # Trova il cliente selezionato
                riga_cliente = df[df['id'] == id_at]
                if not riga_cliente.empty:
                    dati_f = riga_cliente.iloc[0].to_dict()
                else:
                    dati_f = {c: "" for c in COLONNE}
            else:
                dati_f = {c: "" for c in COLONNE}

            with st.form("form_ana"):
                st.write(f"### Dettagli: {dati_f.get('Cliente', 'Nuovo')}")
                
                # Campi del form disposti su due colonne (come nel tuo codice)
                nuovi = {"id": id_at if id_at else str(len(df)+1)}
                c1, c2 = st.columns(2)
                
                # Loop per creare i campi Nome, CF, Indirizzo, Stato ecc.
                for i, col in enumerate(COLONNE[1:]):
                    nuovi[col] = (c1 if i % 2 == 0 else c2).text_input(col, value=str(dati_f.get(col, "")))
                
                st.write("---")
                b_save, b_del = st.columns(2)
                
                # TASTO SALVA / AGGIORNA
                if b_save.form_submit_button("✅ SALVA / AGGIORNA", use_container_width=True):
                    if modo == "aggiungi":
                        df = pd.concat([df, pd.DataFrame([nuovi])], ignore_index=True)
                    else:
                        df.loc[df['id'] == id_at] = list(nuovi.values())
                    
                    df.to_csv(DB_FILE, index=False)
                    st.success("Salvato correttamente!")
                    st.session_state.modo = None
                    st.rerun()
                
                # TASTO CANCELLA (Quello che avevi chiesto di ripristinare)
                if b_del.form_submit_button("🗑️ ELIMINA CLIENTE", use_container_width=True):
                    if id_at:
                        df = df[df['id'] != id_at]
                        df.to_csv(DB_FILE, index=False)
                        st.warning("Cliente eliminato.")
                        st.session_state.modo = None
                        st.session_state.cliente_sel = None
                        st.rerun()
