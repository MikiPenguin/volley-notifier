import os
import requests

# Legge l'URL del webhook dalle variabili d'ambiente di GitHub Actions
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_test_notification():
    if not DISCORD_WEBHOOK_URL:
        print("Errore: Nessun webhook configurato.")
        return

    embed = {
        "title": "🏐 Volley Notifier Attivo!",
        "description": "Il sistema di monitoraggio delle partite di Serie A è stato configurato con successo.",
        "color": 3447003, # Blu
        "footer": {"text": "FIPAV Match Notifier"}
    }
    
    payload = {"embeds": [embed]}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    
    if response.status_code == 204:
        print("Notifica di test inviata con successo!")
    else:
        print(f"Errore nell'invio: {response.status_code}")

if __name__ == "__main__":
    send_test_notification()
