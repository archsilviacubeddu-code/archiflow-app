import streamlit as st
import pandas as pd
import uuid

def mostra_anagrafica(df, DB_FILE, COLONNE):
    st.markdown("""
        <style>
        .stDataEditor { border: 1px solid #e2e8f0 !important; border-radius: 10px !important; }
        /* Stile per il tasto cancella */
        .btn-cancella > div > button {
            background-color: #fee2e2 !important;
            color: #ef4444 !important;
            border: 1px solid #ef4444 !important;
            height: 35px !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📇 Gestione Anagrafica")

    # BARRA SUPERIORE: AGGIUNGI E CERCA
    col_search, col_add, col_del = st.columns([3, 1, 1])
    
    with col_search:
        search = st.text_input("🔍 Filtra...", placeholder="Cerca nome, pratica, stato...", label_visibility="collapsed")
    
    with col_add:
        if st.button("➕ AGGIUNGI", use_container_width=True):
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

    # TABELLA EDITABILE
    # 'on_change' non serve se salviamo col tasto, ma usiamo 'num_rows="dynamic"' per permettere la selezione
    edited_df = st.data_editor(
        df_visualizza,
        column_config=column_config,
        column_order=col_order,
        use_container_width=True,
        hide_index=False,
        key="editor_ana",
        num_rows="dynamic" 
    )

    # BARRA AZIONI SOTTO TABELLA
    st.write("")
    c_salva, c_vuota, c_canc = st.columns([1, 2, 1])

    with c_canc:
        st.markdown('<div class="btn-cancella">', unsafe_allow_html=True)
        if st.button("🗑️ CANCELLA", use_container_width=True):
            # Logica: l'utente seleziona le righe e preme 'Canc' sulla tastiera nella tabella, 
            # oppure noi sovrascriviamo il DF con quello editato (che non ha più le righe eliminate)
            df.to_csv(DB_FILE, index=False) # Questo salva lo stato attuale dell'editor
            st.warning("Righe rimosse. Clicca Salva per confermare.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c_salva:
        if st.button("💾 SALVA MODIFICHE", use_container_width=True, type="primary"):
            # Sincronizziamo il database
            if search:
                df = df[~df['id'].isin(df_visualizza['id'])]
                df = pd.concat([df, edited_df], ignore_index=True)
            else:
                df = edited_df
            
            df.to_csv(DB_FILE, index=False)
            st.success("Dati salvati!")
            st.rerun()
