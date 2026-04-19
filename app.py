import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configurazione Pagina
st.set_page_config(page_title="Archiflow - Suite Gestionale", layout="wide")

# CSS per il titolo a destra
st.markdown("""
    <style>
    .titolo-destra { text-align: right; color: #333333; font-family: 'Helvetica'; margin-bottom: 0; }
    .sottotitolo-destra { text-align: right; color: #666666; font-size: 1.1rem; margin-top: 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. MENU FISSO A SINISTRA
with st.sidebar:
    try:
        st.image("Logo.png", use_container_width=True)
    except:
        st.info("Carica logo.png")
    
    st.divider()
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        pw = st.text_input("Password", type="password")
        if pw == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.stop()
    
    st.subheader("📍 Menu")
    menu = st.radio("Seleziona sezione:", ["🏠 Home", "📇 Anagrafica", "🏗️ Scheda Lavori"])

# 3. TESTATA A DESTRA
st.markdown('<h1 class="titolo-destra">Archiflow - Suite Gestionale</h1>', unsafe_allow_html=True)
st.markdown('<p class="sottotitolo-destra">Arch. Silvia Cubeddu</p>', unsafe_allow_html=True)
st.divider()

# 4. CONNESSIONE DATI
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# --- LOGICA PAGINE ---

if menu == "🏠 Home":
    st.title("Benvenuta, Silvia 🏛️")
    st.write("Suite pronta. Gestisci i tuoi cantieri dal menu a sinistra.")

elif menu == "📇 Anagrafica":
    st.header("📇 Gestione Anagrafica")
    
    # CERCA
    search = st.text_input("🔍 Cerca cliente:")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    # MODULO INSERIMENTO
    with st.expander("➕ AGGIUNGI NUOVO CLIENTE"):
        with st.form("nuovo_cliente"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome *")
            cognome = c2.text_input("Cognome *")
            
            # Menu Pratica
            opzioni_pratica = ["Direzione Lavori", "CILA", "SCIA", "Perizia", "Millesimi", "Rilievo", "Sopralluogo", "APE", "Altro"]
            pratica_sel = st.selectbox("Tipo Pratica", opzioni_pratica)
            if pratica_sel == "Altro":
                pratica_final = st.text_input("Specifica Pratica")
            else:
                pratica_final = pratica_sel
            
            # Menu Stato
            opzioni_stato = ["Da fare", "In corso", "Concluso", "Annullato"]
            stato_final = st.selectbox("Stato Lavoro", opzioni_stato)
            
            note = st.text_area("Altre Note")
            
            submit = st.form_submit_button("SALVA CLIENTE")
            
            if submit:
                if nome and cognome:
                    nuovo_rigo = {col: "" for col in df.columns}
                    nuovo_rigo.update({"Nome": nome, "Cognome": cognome, "Pratica": pratica_final, "Stato": stato_final, "Note": note})
                    new_df = pd.concat([df, pd.DataFrame([nuovo_rigo])], ignore_index=True)
                    conn.update(data=new_df)
                    st.success("Dati salvati!")
                    st.rerun()
                else:
                    st.error("Nome e Cognome sono obbligatori!")

    st.write("---")
    edited_df = st.data_editor(df_filtered, num_rows="dynamic", use_container_width=True)
    
    if st.button("🔄 AGGIORNA TUTTO"):
        conn.update(data=edited_df)
        st.success("Database sincronizzato!")

elif menu == "🏗️ Scheda Lavori":
    st.header("🏗️ Scheda Lavori")
    # Filtro rapido per stato
    filtro_stato = st.multiselect("Filtra per stato:", ["Da fare", "In corso", "Concluso", "Annullato"], default=["In corso", "Da fare"])
    if filtro_stato:
        df_lavori = df[df["Stato"].isin(filtro_stato)]
    else:
        df_lavori = df
    st.dataframe(df_lavori, use_container_width=True)
