import os
import requests
from bs4 import BeautifulSoup

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
            
            # Cerca elementi testuali o righe che contengono le informazioni del match
            for element in soup.find_all(['tr', 'div'], class_=['match-row', 'row', 'card', 'cell'] or True):
                text = element.get_text(" ", strip=True)
                # Filtra per elementi che contengono una data o un orario tipico delle partite
                if ("Ore" in text or "Sabato" in text or "Domenica" in text or "Mercoledí" in text) and len(text) > 30:
                    clean_text = " ".join(text.split())
                    if clean_text not in partite:
                        partite.append(clean_text)
                        if len(partite) >= 3:
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
            
            # Cerca blocchi di match nel calendario femminile
            for element in soup.find_all(['div', 'tr', 'li'], class_=True):
                text = element.get_text(" ", strip=True)
                if ("LVF" in text or "Giornata" in text) and ("/" in text or "Ore" in text):
                    clean_text = " ".join(text.split())
                    if len(clean_text) > 25 and clean_text not in partite:
                        partite.append(clean_text)
                        if len(partite) >= 3:
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
    
    txt_m = "\n\n".join([f"• {p}" for p in partite_m]) if partite_m else "Nessun match imminente trovato al momento."
    fields.append({
        "name": "🏐 Serie A Maschile",
        "value": txt_m[:1024],
        "inline": False
    })
    
    txt_f = "\n\n".join([f"• {p}" for p in partite_f]) if partite_f else "Nessun match imminente trovato al momento."
    fields.append({
        "name": "🏐 Serie A Femminile",
        "value": txt_f[:1024],
        "inline": False
    })

    embed = {
        "title": "📅 Prossime Partite di Pallavolo Serie A",
        "color": 3447003,
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
