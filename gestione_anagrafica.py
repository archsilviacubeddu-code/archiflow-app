import streamlit as st
import pandas as pd
import uuid

def mostra_anagrafica(df, DB_FILE, COL_ANAGRAFICA):
    st.markdown("""
        <style>
        .stDataEditor { border: 1px solid #e2e8f0 !important; border-radius: 10px !important; }
        .stButton > button { height: 40px !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("📇 Gestione Anagrafica")

    # BARRA SUPERIORE: AGGIUNGI E CERCA
    col_search, col_add = st.columns([4, 1])
    
    with col_search:
        search = st.text_input("🔍 Cerca cliente, cantiere o stato...", placeholder="Scrivi qui per filtrare la tabella...", label_visibility="collapsed")
    
    with col_add:
        if st.button("➕ NUOVO CLIENTE", use_container_width=True):
            nuovo_id = str(uuid.uuid4())[:8]
            # Creiamo la riga con valori di default chiari
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "Nuova Pratica", "Attivo", "", ""]], columns=COL_ANAGRAFICA)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

    # FILTRO LOGICO
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df_visualizza = df[mask]
    else:
        df_visualizza = df

    st.divider()

    # CONFIGURAZIONE DELLA TABELLA (NOME, PRATICA, STATO IN EVIDENZA)
    column_config = {
        "id": None, # Nascondiamo l'ID tecnico
        "Cliente": st.column_config.TextColumn("👤 CLIENTE", width="medium", help="Nome o Ragione Sociale"),
        "Pratica": st.column_config.TextColumn("🏗️ CANTIERE / PRATICA", width="large"),
        "Stato": st.column_config.SelectboxColumn("🚦 STATO", options=["Attivo", "Chiuso"], width="small"),
        "Indirizzo": st.column_config.TextColumn("📍 INDIRIZZO", width="medium"),
        "Telefono": st.column_config.TextColumn("📞 TEL"),
        "Email": st.column_config.TextColumn("📧 EMAIL"),
        "Note": st.column_config.TextColumn("📝 NOTE", width="large")
    }

    st.write("### Elenco Clienti")
    st.info("💡 Puoi modificare i dati direttamente nelle celle e selezionare le righe con le caselle a sinistra.")

    # TABELLA CON SELEZIONE MULTIPLA
    # Ordiniamo le colonne per mettere subito Nome, Pratica e Stato
    colonne_ordinate = ["Cliente", "Pratica", "Stato", "Indirizzo", "Telefono", "Email", "Note"]
    
    edited_df = st.data_editor(
        df_visualizza,
        column_config=column_config,
        column_order=colonne_ordinate,
        use_container_width=True,
        hide_index=False, # Mostra l'indice per la selezione
        key="editor_anagrafica",
        num_rows="dynamic" # Permette di aggiungere/eliminare righe
    )

    # BOTTONE DI SALVATAGGIO
    if st.button("💾 SALVA TUTTE LE MODIFICHE", use_container_width=True, type="primary"):
        # Sincronizziamo i cambiamenti nel database originale
        df.update(edited_df)
        df.to_csv(DB_FILE, index=False)
        st.success("Database aggiornato con successo!")
        st.rerun()
