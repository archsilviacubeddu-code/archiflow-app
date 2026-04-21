import streamlit as st
import pandas as pd
import uuid

def mostra_anagrafica(df, DB_FILE, COLONNE):
    st.markdown("""
        <style>
        .stDataEditor { border: 1px solid #e2e8f0 !important; border-radius: 10px !important; }
        .btn-delete-multi > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📇 Gestione Anagrafica Clienti")

    # 1. BARRA SUPERIORE: AGGIUNGI E CERCA
    col_search, col_add = st.columns([4, 1])
    with col_search:
        search = st.text_input("🔍 Filtra tabella...", placeholder="Cerca nome, cantiere, pratica o stato...", label_visibility="collapsed")
    with col_add:
        if st.button("➕ NUOVO CLIENTE", use_container_width=True):
            nuovo_id = str(uuid.uuid4())[:8]
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "Nuova Pratica", "Attivo", "", ""]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

    # 2. FILTRO LOGICO
    df_visualizza = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df

    st.divider()

    # 3. CONFIGURAZIONE TABELLA (NOME, PRATICA, STATO)
    column_config = {
        "id": None, # Nascondiamo l'ID
        "Cliente": st.column_config.TextColumn("👤 CLIENTE", width="medium"),
        "Pratica": st.column_config.TextColumn("🏗️ CANTIERE / PRATICA", width="large"),
        "Stato": st.column_config.SelectboxColumn("🚦 STATO", options=["Attivo", "Chiuso"], width="small"),
        "Indirizzo": st.column_config.TextColumn("📍 INDIRIZZO"),
        "Note": st.column_config.TextColumn("📝 NOTE")
    }

    # Ordine colonne per avere subito quello che ti serve
    col_order = ["Cliente", "Pratica", "Stato", "Indirizzo", "Telefono", "Email", "Note"]

    st.write("### Elenco Clienti")
    st.info("💡 Spunta le caselle a sinistra per selezionare i clienti da eliminare o modificare.")

    # 4. TABELLA EDITABILE CON SELEZIONE
    # Usiamo 'id' come indice per tracciare la selezione
    df_visualizza = df_visualizza.set_index("id")
    
    edited_df = st.data_editor(
        df_visualizza,
        column_config=column_config,
        column_order=col_order,
        use_container_width=True,
        key="editor_multi_ana",
        num_rows="fixed" # Impedisce aggiunte casuali dentro la tabella
    )

    # 5. AZIONI SOTTO LA TABELLA
    st.write("##")
    col_save, col_del_multi = st.columns([3, 1])

    with col_save:
        if st.button("💾 SALVA MODIFICHE TABELLA", use_container_width=True, type="primary"):
            # Riportiamo l'ID come colonna e salviamo
            final_df = edited_df.reset_index()
            final_df.to_csv(DB_FILE, index=False)
            st.success("Tutte le modifiche sono state salvate!")
            st.rerun()

    with col_del_multi:
        st.markdown('<div class="btn-delete-multi">', unsafe_allow_html=True)
        # Identifichiamo le righe selezionate tramite lo stato dell'editor
        if "editor_multi_ana" in st.session_state:
            selezione = st.session_state["editor_multi_ana"]["rows_added"] # In alcuni casi Streamlit usa questo per i nuovi
            # Ma per la selezione di righe esistenti usiamo la logica degli indici selezionati
            # Nota: Streamlit gestisce la selezione tramite le righe "attive" o editate.
            # Per una cancellazione multipla "vecchia scuola" basata su checkbox:
            pass 
        
        # Tecnica più sicura per eliminazione multipla in Streamlit:
        if st.button("🗑️ CANCELLA SELEZIONATI", use_container_width=True):
            # Se l'utente ha usato l'interfaccia dell'editor per cancellare righe
            rows_to_delete = st.session_state["editor_multi_ana"].get("deleted_rows", [])
            if rows_to_delete:
                # rows_to_delete contiene gli indici della visualizzazione corrente
                indices_to_drop = df_visualizza.index[rows_to_delete]
                df = df[~df['id'].isin(indices_to_drop)]
                df.to_csv(DB_FILE, index=False)
                st.warning(f"Eliminati {len(rows_to_delete)} clienti.")
                st.rerun()
            else:
                st.error("Seleziona le righe cliccando sul bordo sinistro della tabella e premi 'Canc' o usa il menu dell'editor.")
        st.markdown('</div>', unsafe_allow_html=True)
