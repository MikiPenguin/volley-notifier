import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URL del Webhook di Discord salvato nei Secrets di GitHub
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_partite_maschile():
    """Estrae le prossime partite dalla Lega Volley Maschile."""
    url = "https://www.legavolley.it/calendario/"
    partite = []
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Cerca le righe delle partite o le schede dei match nel calendario
            # La lega volley maschile struttura i match in blocchi/tabelle
            rows = soup.find_all("tr") or soup.find_all("div", class_="match-card")
            
            for row in rows:
                text = row.get_text(" ", strip=True)
                # Filtra per partite non ancora giocate (es. con orario o data attiva)
                if "Ore" in text or "Domenica" in text or "Sabato" in text:
                    # Rimuove spazi eccessivi
                    clean_text = " ".join(text.split())
                    if len(clean_text) > 20:
                        partite.append(clean_text)
                        if len(partite) >= 3: # Prendiamo le prime 3 imminenti
                            break
    except Exception as e:
        print(f"Errore nello scraping Maschile: {e}")
        
    return partite

def get_partite_femminile():
    """Estrae le prossime partite dalla Lega Volley Femminile."""
    url = "https://www.legavolleyfemminile.it/calendario/"
    partite = []
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Cerca i blocchi delle partite nel calendario femminile
            matches = soup.find_all("div", class_="match") or soup.find_all("tr")
            
            for match in matches:
                text = match.get_text(" ", strip=True)
                if "LVF A1" in text or "LVF A2" in text or "Giornata" in text:
                    clean_text = " ".join(text.split())
                    if len(clean_text) > 20:
                        partite.append(clean_text)
                        if len(partite) >= 3: # Prendiamo le prime 3 imminenti
                            break
    except Exception as e:
        print(f"Errore nello scraping Femminile: {e}")
        
    return partite

def send_discord_notification(partite_m, partite_f):
    """Invia un messaggio formattato in Embed su Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("Errore: DISCORD_WEBHOOK_URL non trovato.")
        return

    fields = []
    
    # Sezione Maschile
    txt_m = "\n\n".join([f"• {p}" for p in partite_m]) if partite_m else "Nessun match imminente trovato."
    fields.append({
        "name": "🏐 Serie A Maschile",
        "value": txt_m[:1024], # Limite caratteri Discord
        "inline": False
    })
    
    # Sezione Femminile
    txt_f = "\n\n".join([f"• {p}" for p in partite_f]) if partite_f else "Nessun match imminente trovato."
    fields.append({
        "name": "🏐 Serie A Femminile",
        "value": txt_f[:1024],
        "inline": False
    })

    embed = {
        "title": "📅 Prossime Partite di Pallavolo Serie A",
        "color": 3447003, # Colore Blu
        "fields": fields,
        "footer": {"text": "FIPAV / Lega Volley Notifier"}
    }
    
    payload = {"embeds": [embed]}
    res = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    
    if res.status_code in [200, 204]:
        print("Notifica inviata con successo su Discord!")
    else:
        print(f"Errore invio Discord: {res.status_code}")

if __name__ == "__main__":
    print("Raccolta dati partite in corso...")
    partite_maschile = get_partite_maschile()
    partite_femminile = get_partite_femminile()
    
    send_discord_notification(partite_maschile, partite_femminile)
