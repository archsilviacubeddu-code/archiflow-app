import streamlit as st
import pandas as pd
import json
import unicodedata

# 1. IL "CERVELLO" DELLE NECESSITÀ/DOCUMENTI
MODELLI_DOCUMENTI = {
    "DIREZIONE LAVORI": ["Sopralluogo iniziale", "Rilievo", "Pratica Urbanistica", "DURC", "Contratto Impresa", "Contratto Professionista", "Verifica POS", "Verifica PSC", "Notifica Preliminare", "Assicurazione", "Aggiornamento Computo", "SAL", "Verbali di cantiere"],
    "CANTIERE INTERNI": ["Sopralluogo", "Rilievo", "Pratica Urbanistica", "DURC", "Contratto Impresa", "Contratto Professionista", "POS", "PSC", "Notifica Preliminare", "Assicurazione", "Computo Metrico", "SAL", "Verbali"],
    "COMPUTO METRICO": ["Preventivo Firmato", "Delega Amministratore", "Regolamento Condominio", "Progetto Fabbricato", "Rilievo Facciate", "Rilievo Corpo Scala", "Rilievo Appartamenti", "Contratto d'Appalto", "Capitolato Generale"],
    "PROGETTAZIONE": ["Rilievo Stato dei Luoghi", "Verifica Legittimità", "Reperimento Progetto Fabbricato", "Misure Infissi", "Verifica Distacchi"],
    "RILIEVO": ["Coordinate Geografiche", "Misure Totali", "Misure Parziali", "Censimento Infissi", "Verifica Altezze/Distacchi", "Verifica Confini"],
    "CILA": ["Preventivo Firmato", "Delega Capofila", "Delega Altri Intestatari", "Documenti Identità", "Elaborato Grafico", "Analisi Urbanistica", "Verifica Legittimità", "Stesura Computo"],
    "SCIA": ["Preventivo Firmato", "Delega Capofila", "Delega Altri Intestatari", "Documenti Identità", "Elaborato Grafico", "Analisi Urbanistica", "Verifica Legittimità", "Stesura Computo"],
    "ACCERTAMENTO DI CONFORMITA": ["Preventivo Firmato", "Delega Capofila", "Delega Altri Intestatari", "Documenti Identità", "Elaborato Grafico", "Analisi Urbanistica", "Verifica Legittimità", "Computo Sanatoria"],
    "MILLESIMI": ["Preventivo Accettato", "Analisi Regolamento", "Progetto Fabbricato", "Rilievi Appartamenti e Pertinenze"],
    "PERIZIA": ["Sopralluogo/Rilievo", "Analisi Urbanistica", "Verifica Legittimità", "Relazione di Stima"],
    "ACCESSO ATTI": ["Documento Identità", "Atto di Proprietà", "Visura Catastale", "Planimetria Catastale", "Presentazione Modulo"],
    "RENDER": ["Rilievo Stato dei Luoghi", "Modellazione 2D", "Modellazione 3D", "Scelta Materiali/Luci"],
    "ALTRO": []
}

def pulisci_testo(testo):
    if not testo: return ""
    testo = str(testo).upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', testo) if unicodedata.category(c) != 'Mn')

def inizializza_documenti(riga_docs_json, tipo_pratica=None):
    """Carica i documenti salvati o inizializza il modello basato sulla pratica."""
    try:
        if riga_docs_json and str(riga_docs_json) != "nan" and riga_docs_json != "{}":
            return json.loads(riga_docs_json)
    except:
        pass
    
    nuovi_docs = {}
    if tipo_pratica:
        testo_pulito = pulisci_testo(tipo_pratica)
        chiavi_ordinate = sorted(MODELLI_DOCUMENTI.keys(), key=len, reverse=True)
        for chiave in chiavi_ordinate:
            if pulisci_testo(chiave) in testo_pulito:
                for voce in MODELLI_DOCUMENTI[chiave]:
                    nuovi_docs[voce] = "🔴 Da fare/Mancante"
                break 
    return nuovi_docs

# 2. INTERFACCIA GRAFICA (Semafori integrati con la tua logica)
def interfaccia_semafori(id_lavoro, df, idx, DB_FILE):
    st.write("### 🚦 Documenti e Necessità Operative")
    
    if 'docs_json' not in df.columns:
        df['docs_json'] = "{}"
    
    tipo_pratica = df.at[idx, 'Pratica'] if 'Pratica' in df.columns else None
    riga_json = df.at[idx, 'docs_json']
    
    docs_stato = inizializza_documenti(riga_json, tipo_pratica=tipo_pratica)
    
    # Visualizzazione Lista
    nuovi_stati = {}
    for i, (doc, attuale) in enumerate(docs_stato.items()):
        col_t, col_s = st.columns([3, 2])
        col_t.markdown(f"**{doc}**")
        
        opzioni = ["🟢 Consegnato/Fatto", "🟡 In Attesa", "🔴 Da fare/Mancante"]
        
        # Logica per impostare l'indice corretto basata sul testo salvato
        idx_default = 2 # Default su Rosso
        if "🟢" in attuale or "Consegnato" in attuale: idx_default = 0
        elif "🟡" in attuale or "Attesa" in attuale: idx_default = 1
            
        scelta = col_s.selectbox(
            f"Stato {doc}", opzioni, 
            index=idx_default, 
            key=f"sem_{id_lavoro}_{i}", 
            label_visibility="collapsed"
        )
        nuovi_stati[doc] = scelta

    st.divider()
    st.write("### ➕ Aggiungi Necessità Extra")
    c_add1, c_add2 = st.columns([3, 1])
    nuovo_nome = c_add1.text_input("Descrizione (es: Chiamare impresa...)", key=f"in_add_{id_lavoro}")
    
    if st.button("💾 SALVA STATO", use_container_width=True, key=f"save_btn_{id_lavoro}"):
        if nuovo_nome: 
            nuovi_stati[nuovo_nome] = "🔴 Da fare/Mancante"
        
        # Aggiornamento DataFrame e salvataggio su file
        df.at[idx, 'docs_json'] = json.dumps(nuovi_stati)
        df.to_csv(DB_FILE, index=False)
        st.success("Stato salvato correttamente!")
        st.rerun()

# 3. ALERT PER LA HOME
def widget_alert_home(df):
    pendenti = []
    if 'docs_json' in df.columns:
        for _, r in df.iterrows():
            docs = inizializza_documenti(r['docs_json'])
            # Consideriamo pendenti i gialli e i rossi
            non_fatti = [n for n, s in docs.items() if "🔴" in s or "🟡" in s]
            if non_fatti:
                pendenti.append({
                    "Cliente": r['Cliente'], 
                    "Pratica": r.get('Pratica', '-'),
                    "Necessità Aperte": len(non_fatti)
                })
