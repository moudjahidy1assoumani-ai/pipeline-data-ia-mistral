import streamlit as st
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

# 1. CONFIGURATION DE L'API DIRECTE MISTRAL
MISTRAL_API_KEY = "VOTRE_CLE_MISTRAL_ICI"

def appeler_api_mistral_direct(texte_a_analyser):
    # L'adresse officielle du serveur de Mistral
    url_api = "https://api.mistral.ai/v1/chat/completions"
    
    # Les en-têtes nécessaires pour s'authentifier de manière sécurisée
    headers = {
        "Content-Type": "application/semibold+json", # Format de données standard
        "Authorization": f"Bearer {MISTRAL_API_KEY}" # La clé secrète
    }
    
    # Les données qu'on envoie au moteur de l'IA (Modèle + Prompt)
    payload = {
        "model": "open-mistral-7b",
        "messages": [
            {
                "role": "user",
                "content": f"Fais un résumé synthétique en 3 points clés de ce texte qui traite de l'intelligence artificielle :\n{texte_a_analyser}"
            }
        ]
    }
    
    # On effectue l'appel réseau
    reponse = requests.post(url_api, headers=headers, json=payload)
    
    if reponse.status_code == 200:
        # Si le serveur répond 'OK', on extrait le texte de la réponse
        donnees_recues = reponse.json()
        return donnees_recues["choices"][0]["message"]["content"]
    else:
        # Si le serveur renvoie une erreur (Ex: clé invalide)
        raise Exception(f"Erreur serveur Mistral (Code {reponse.status_code}) : {reponse.text}")

# 2. FONCTION DE SCRAPING (WIKIPÉDIA)
def scraper_vraies_donnees():
    url = "https://fr.wikipedia.org/wiki/Intelligence_artificielle"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        reponse = requests.get(url, headers=headers)
        soup = BeautifulSoup(reponse.text, "html.parser")
        paragraphes = soup.find_all("p")
        
        phrases_extraites = []
        for p in paragraphes:
            texte = p.text.strip()
            if len(texte) > 40:
                phrases_extraites.append(texte)
            if len(phrases_extraites) == 5:
                break
        return phrases_extraites
    except Exception as e:
        st.error(f"Erreur lors du scraping : {e}")
        return []

# 3. ALGORITHME DE SENTIMENT (NLP)
dictionnaire_sentiment = {
    "grand": 1, "évolution": 1, "progrès": 1, "succès": 1, "important": 1, "intelligence": 1, "capacité": 1,
    "limite": -1, "danger": -1, "risque": -1, "critique": -1, "menace": -1, "problème": -1, "erreur": -1
}

def analyser_phrase(phrase):
    mots = phrase.lower().split()
    score = 0
    for mot in mots:
        mot_propre = mot.strip(",.()\"'")
        if mot_propre in dictionnaire_sentiment:
            score += dictionnaire_sentiment[mot_propre]
    if score > 0: return "Positif"
    elif score < 0: return "Négatif"
    else: return "Neutre"

# 4. INTERFACE GRAPHIQUE (STREAMLIT)
st.set_page_config(page_title="Vrai Dashboard Data & IA", layout="wide")
st.title("🚀 Vrai Projet : Pipeline Data & IA en Production (API Rest)")

# --- BOUTON ACTION 1 : SCRAPING ---
if st.button("🌐 Étape 1 : Scraper Wikipédia en temps réel"):
    with st.spinner("Le robot extrait les données de Wikipédia..."):
        st.session_state.textes = scraper_vraies_donnees()
    st.success(f"Réussite ! {len(st.session_state.textes)} paragraphes réels ont été extraits du code HTML.")

if "textes" in st.session_state and st.session_state.textes:
    st.subheader("📋 Textes bruts récupérés :")
    for t in st.session_state.textes:
        st.write(f"- {t[:150]}...")
        
    # --- BOUTON ACTION 2 : DATA ANALYTICS ---
    if st.button("📊 Étape 2 : Analyser la tonalité du texte (NLP)"):
        positifs, negatifs, neutres = 0, 0, 0
        st.session_state.phrases_critiques = []
        
        for t in st.session_state.textes:
            res = analyser_phrase(t)
            if res == "Positif": positifs += 1
            elif res == "Négatif": 
                negatifs += 1
                st.session_state.phrases_critiques.append(t)
            else: neutres += 1
            
        st.markdown("### 📈 Répartition des tonalités détectées")
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.pie([positifs, negatifs, neutres], labels=['Positifs', 'Négatifs', 'Neutres'], autopct='%1.0f%%', colors=['#2ecc71', '#e74c3c', '#f39c12'])
        st.pyplot(fig)
        
    # --- BOUTON ACTION 3 : VRAIE IA MISTRAL (APPEL REST) ---
    if "phrases_critiques" in st.session_state:
        st.write("---")
        if st.button("🤖 Étape 3 : Demander une synthèse réelle à Mistral AI"):
            if not st.session_state.phrases_critiques:
                texte_pour_ia = "\n".join(st.session_state.textes)
            else:
                texte_pour_ia = "\n".join(st.session_state.phrases_critiques)
                
            with st.spinner("Envoi direct du flux JSON à Mistral AI via HTTP..."):
                try:
                    # On utilise notre fonction personnalisée de requêtage direct
                    resultat_texte = appeler_api_mistral_direct(texte_pour_ia)
                    
                    st.success("### 📜 Rapport généré en direct par Mistral AI :")
                    st.write(resultat_texte)
                    
                except Exception as e:
                    st.error(f"Erreur d'appel API : {e}")