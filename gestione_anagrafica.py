import streamlit as st
import pandas as pd
import uuid

def mostra_anagrafica(df, DB_FILE, COLONNE):
    st.markdown("""
        <style>
        .stDataEditor { border: 1px solid #e2e8f0 !important; border-radius: 10px !important; }
        /* Tasto salva rosso come gli altri bottoni della suite */
        .stButton > button[kind="primary"] {
            background-color: #E63946 !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📇 Gestione Anagrafica")

    # BARRA SUPERIORE
    col_search, col_add = st.columns([4, 1])
    with col_search:
        search = st.text_input("🔍 Filtra tabella...", placeholder="Cerca nome, pratica, stato...", label_visibility="collapsed")
    with col_add:
        if st.button("➕ NUOVO CLIENTE", use_container_width=True):
            nuovo_id = str(uuid.uuid4())[:8]
            nuova_riga = pd.DataFrame([[nuovo_id, "Nuovo Cliente", "", "", "", "", "", "", "", "Nuova Pratica", "Attivo", "", ""]], columns=COLONNE)
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

    # FILTRO
    df_visualizza = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)] if search else df

    st.divider()

    # CONFIGURAZIONE TABELLA
    column_config = {
        "id": None, 
        "Cliente": st.column_config.TextColumn("👤 CLIENTE", width="medium"),
        "Pratica": st.column_config.TextColumn("🏗️ CANTIERE / PRATICA", width="large"),
        "Stato": st.column_config.SelectboxColumn("🚦 STATO", options=["Attivo", "Chiuso"], width="small"),
        "Indirizzo": st.column_config.TextColumn("📍 INDIRIZZO"),
        "Note": st.column_config.TextColumn("📝 NOTE")
    }
    
    col_order = ["Cliente", "Pratica", "Stato", "Indirizzo", "Telefono", "Email", "Note"]

    st.write("### Elenco Clienti")
    st.info("💡 Per cancellare: seleziona le righe a sinistra, premi 'Canc' sulla tastiera e poi clicca Salva.")

    # TABELLA EDITABILE
    # Non usiamo più la logica complessa del session_state per evitare il KeyError
    edited_df = st.data_editor(
        df_visualizza,
        column_config=column_config,
        column_order=col_order,
        use_container_width=True,
        hide_index=False,
        key="editor_ana",
        num_rows="dynamic" # Questo abilita la selezione e cancellazione nativa
    )

    # BOTTONE SALVATAGGIO UNICO (Gestisce anche le cancellazioni)
    if st.button("💾 SALVA MODIFICHE E CANCELLAZIONI", use_container_width=True, type="primary"):
        # Se hai filtrato, dobbiamo ricongiungere i dati al df originale
        if search:
            # Rimuoviamo le righe vecchie presenti nel filtro e mettiamo quelle nuove
            df = df[~df['id'].isin(df_visualizza['id'])]
            df = pd.concat([df, edited_df], ignore_index=True)
        else:
            df = edited_df
        
        df.to_csv(DB_FILE, index=False)
        st.success("Database aggiornato con successo!")
        st.rerun()
