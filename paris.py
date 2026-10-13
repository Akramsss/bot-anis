import requests
import time
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()
# --- PARAMÈTRES À REMPLIR ---
URL_API_CROUS = "https://trouverunlogement.lescrous.fr/api/fr/search/47"

MON_EMAIL = os.getenv("MON_EMAIL")
MOT_DE_PASSE_EMAIL = os.getenv("MOT_DE_PASSE_EMAIL")
EMAIL_DESTINATION = os.getenv("EMAIL_DESTINATION")

# Les filtres de recherche qu'on a interceptés !
PAYLOAD = {
    "idTool": 47,
    "need_aggregation": True,
    "page": 1,
    "pageSize": 24,
    "sector": None,
    "occupationModes": [],
    # "location":[{"lon":1.4462445,"lat":49.241431},{"lon":3.5592208,"lat":48.1201456}],
    "location":[{"lon":2.224122,"lat":48.902156},{"lon":2.4697602,"lat":48.8155755}],
    "residence": None,
    "precision": 5,
    "equipment": [],
    "price": {"max": 10000000},
    "area": {"min": 0},
    "adaptedPmr": False,
    "toolMechanism": "residual"
}

def envoyer_alerte(nombre_logements):
    message = f"Vite ! {nombre_logements} logement(s) viennent d'apparaître à Limoges sur le site du CROUS.\nLien direct : https://trouverunlogement.lescrous.fr/"
    msg = MIMEText(message)
    msg['Subject'] = "🚨 ALERTE : Logement CROUS disponible !"
    msg['From'] = MON_EMAIL
    msg['To'] = EMAIL_DESTINATION

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MON_EMAIL, MOT_DE_PASSE_EMAIL)
            server.send_message(msg)
        print("✉️ Alerte email envoyée avec succès !")
    except Exception as e:
        print(f"❌ Erreur email : {e}")

def verifier_disponibilites():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://trouverunlogement.lescrous.fr/",
            "Content-Type": "application/json"
        }
        
        reponse = requests.post(URL_API_CROUS, headers=headers, json=PAYLOAD)
        
        if reponse.status_code == 200:
            try:
                # On essaie de lire le JSON
                donnees = reponse.json()
                liste_logements = donnees.get('results', {}).get('items', []) 
                
                if len(liste_logements) > 0:
                    print(f"🎉 BINGO ! {len(liste_logements)} logement(s) trouvé(s) !")
                    envoyer_alerte(len(liste_logements))
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Toujours rien de disponible...")
                    
            except Exception:
                print(f"[{time.strftime('%H:%M:%S')}] 🛑 Le serveur bloque l'accès aux données.")
                print("Voici les 500 premiers caractères de sa réponse brute :")
                # On affiche le texte brut pour comprendre ce qui bloque
                print(reponse.text[:500]) 
                
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Erreur du serveur CROUS (Code {reponse.status_code})")
            
    except Exception as e:
        print(f"Erreur de réseau : {e}")

# --- LANCEMENT DU PROGRAMME ---
if __name__ == "__main__":
    print("🚀 Démarrage du radar à logements CROUS pour Pris...")
    while True:
        verifier_disponibilites()
        # Pause de 10 minutes (600 secondes) pour ne pas se faire repérer
        time.sleep(600)
