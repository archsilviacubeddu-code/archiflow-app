import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    # CSS per i bottoni giganti e colorati
    st.markdown("""
        <style>
        .btn-lavoro > div > button {
            height: 10em !important;
            font-size: 20px !important;
            border-radius: 20px !important;
            font-weight: bold !important;
            color: white !important;
            margin-bottom: 20px !important;
            white-space: pre-line !important;
        }
        /* Colori richiesti */
        .btn-dl > div > button { background-color: #E63946 !important; }    /* Rosso */
        .btn-pra > div > button { background-color: #457B9D !important; }   /* Blu */
        .btn-ape > div > button { background-color: #2A9D8F !important; }   /* Verde */
        .btn-mill > div > button { background-color: #8338EC !important; }  /* Viola */
        .btn-alt > div > button { background-color: #6C757D !important; }   /* Grigio */
        </style>
    """, unsafe_allow_html=True)

    # Navigazione interna
    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None

    if st.session_state.sezione_lavoro:
        # Render della sottopagina con filtro
        sezione = st.session_state.sezione_lavoro
        
        if st.button("⬅️ TORNA AI LAVORI"):
            st.session_state.sezione_lavoro = None
            st.rerun()
            
        st.header(f"📂 {sezione.upper()}")
        st.divider()

        # Filtro basato sulle scelte dell'anagrafica
        if sezione == "APE / LEGGE 10":
            df_filtro = df[df['Pratica'].isin(["APE", "Legge 10"])]
        elif sezione == "ALTRO":
            opzioni_standard = ["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10", "Millesimi"]
            df_filtro = df[~df['Pratica'].isin(opzioni_standard)]
        else:
            df_filtro = df[df['Pratica'] == sezione]

        if df_filtro.empty:
            st.info(f"Nessuna pratica trovata per: {sezione}")
        else:
            for i, r in df_filtro.iterrows():
                with st.expander(f"👤 {r['Cliente']} - 📍 {r['Web']}"): # Web = Indirizzo Pratica
                    c1, c2 = st.columns(2)
                    c1.write(f"**Stato:** {r['Stato']}")
                    c1.write(f"**Scadenza:** {r['Scadenza']}")
                    c2.write(f"**Tel:** {r['Telefono']}")
                    c2.write(f"**Email:** {r['Email']}")
                    st.write(f"**Note:** {r['Note']}")
                    
                    if sezione == "Direzione lavori":
                        if st.button(f"🎙️ Apri Diario Cantiere", key=f"dl_{r['id']}"):
                            st.session_state.cantiere_attivo = r['id']
                            st.info("Modulo Diario in attivazione...")
    else:
        # DASHBOARD PRINCIPALE
        st.title("🏗️ Area Lavori")
        
        row1_c1, row1_c2, row1_c3 = st.columns(3)
        row2_c1, row2_c2, row2_c3 = st.columns(3)

        with row1_c1:
            st.markdown('<div class="btn-lavoro btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True):
                st.session_state.sezione_lavoro = "Direzione lavori"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with row1_c2:
            st.markdown('<div class="btn-lavoro btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE\nURBANISTICHE", use_container_width=True):
                st.session_state.sezione_lavoro = "Pratica urbanistica"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with row1_c3:
            st.markdown('<div class="btn-lavoro btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True):
                st.session_state.sezione_lavoro = "APE / LEGGE 10"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_c1:
            st.markdown('<div class="btn-lavoro btn-mill">', unsafe_allow_html=True)
            if st.button("📊\nMILLESIMI", use_container_width=True):
                st.session_state.sezione_lavoro = "Millesimi"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_c2:
            st.markdown('<div class="btn-lavoro btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True):
                st.session_state.sezione_lavoro = "ALTRO"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
