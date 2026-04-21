import streamlit as st
import pandas as pd

def mostra_lavori(df, DB_FILE):
    # CSS per i bottoni giganti colorati
    st.markdown("""
        <style>
        .btn-lavoro > div > button {
            height: 10em !important;
            font-size: 20px !important;
            border-radius: 20px !important;
            font-weight: bold !important;
            color: white !important;
            margin-bottom: 20px !important;
            white-space: pre-line !important; /* Permette il ritorno a capo nei bottoni */
        }
        /* Colore Direzione Lavori: Rosso */
        .btn-dl > div > button { background-color: #E63946 !important; }
        /* Colore Pratiche: Blu */
        .btn-pra > div > button { background-color: #457B9D !important; }
        /* Colore APE: Verde */
        .btn-ape > div > button { background-color: #2A9D8F !important; }
        /* Colore Millesimi: Viola */
        .btn-mill > div > button { background-color: #8338EC !important; }
        /* Colore Altro: Grigio */
        .btn-alt > div > button { background-color: #6C757D !important; }
        </style>
    """, unsafe_allow_html=True)

    # Inizializza lo stato della navigazione interna ai lavori
    if "sezione_lavoro" not in st.session_state:
        st.session_state.sezione_lavoro = None

    # SE ABBIAMO SELEZIONATO UNA SEZIONE, MOSTRAMO I CLIENTI FILTRATI
    if st.session_state.sezione_lavoro:
        render_sottopagina(st.session_state.sezione_lavoro, df)
    else:
        # DASHBOARD PRINCIPALE CON I 5 BOTTONI
        st.title("🏗️ Area Lavori")
        st.write("Seleziona l'area di intervento per gestire i cantieri aperti")
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown('<div class="btn-lavoro btn-dl">', unsafe_allow_html=True)
            if st.button("🚧\nDIREZIONE\nLAVORI", use_container_width=True):
                st.session_state.sezione_lavoro = "Direzione lavori"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="btn-lavoro btn-mill">', unsafe_allow_html=True)
            if st.button("📊\nMILLESIMI", use_container_width=True):
                st.session_state.sezione_lavoro = "Millesimi"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="btn-lavoro btn-pra">', unsafe_allow_html=True)
            if st.button("📋\nPRATICHE\nURBANISTICHE", use_container_width=True):
                st.session_state.sezione_lavoro = "Pratica urbanistica"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="btn-lavoro btn-alt">', unsafe_allow_html=True)
            if st.button("➕\nALTRO", use_container_width=True):
                st.session_state.sezione_lavoro = "Altro"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="btn-lavoro btn-ape">', unsafe_allow_html=True)
            if st.button("⚡\nAPE /\nLEGGE 10", use_container_width=True):
                st.session_state.sezione_lavoro = "APE/Legge 10"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def render_sottopagina(sezione, df):
    # Tasto per tornare indietro
    if st.button("⬅️ TORNA ALLA DASHBOARD"):
        st.session_state.sezione_lavoro = None
        st.rerun()
    
    st.header(f"Sezione: {sezione.upper()}")
    st.divider()

    # LOGICA DI FILTRO
    if sezione == "APE/Legge 10":
        # Filtra sia APE che Legge 10 come avevi chiesto
        mask = df['Pratica'].isin(["APE", "Legge 10"])
    elif sezione == "Altro":
        # Tutto quello che non rientra nelle categorie standard
        categorie_fisse = ["Direzione lavori", "Pratica urbanistica", "APE", "Legge 10", "Millesimi"]
        mask = ~df['Pratica'].isin(categorie_fisse)
    else:
        # Filtro secco per la categoria
        mask = df['Pratica'] == sezione

    df_lavoro = df[mask]

    if df_lavoro.empty:
        st.info(f"Non ci sono pratiche di tipo '{sezione}' registrate in anagrafica.")
    else:
        # Mostra i clienti come schede espandibili
        for i, r in df_lavoro.iterrows():
            with st.expander(f"👤 {r['Cliente']} - 📍 {r['Web']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Indirizzo Cliente:** {r['Indirizzo']}, {r['CAP']} {r['Città']}")
                    st.write(f"**Stato:** {r['Stato']}")
                    st.write(f"**Note:** {r['Note']}")
                with col2:
                    st.write(f"**Scadenza:** {r['Scadenza']}")
                    st.write(f"**Tel:** {r['Telefono']}")
                
                st.divider()
                # QUI AGGIUNGEREMO I PULSANTI AZIONE (Verbali, Documenti, ecc.)
                if sezione == "Direzione lavori":
                    if st.button(f"📸 Diario di Cantiere / Verbali", key=f"btn_dl_{r['id']}"):
                        st.info("Apertura modulo Diario AI...")
