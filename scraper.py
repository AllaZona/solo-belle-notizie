import feedparser
import json

# Leggiamo le ultime notizie dall'ANSA
FEED_URL = "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml"

# Il nostro filtro "positivo" di base
PAROLE_POSITIVE = ['scoperta', 'successo', 'crescita', 'guarigione', 'salvataggio', 'vittoria', 'innovazione', 'aiuto', 'progresso', 'pace', 'accordo']
PAROLE_NEGATIVE = ['morti', 'crisi', 'tragedia', 'incidente', 'guerra', 'omicidio', 'arresto', 'crollo', 'paura', 'violenza']

def analizza_notizia(testo):
    testo = testo.lower()
    punteggio = 0
    for parola in PAROLE_POSITIVE:
        if parola in testo: punteggio += 1
    for parola in PAROLE_NEGATIVE:
        if parola in testo: punteggio -= 2 # Le parole negative pesano di più
    return punteggio > 0

print("Cerco notizie...")
feed = feedparser.parse(FEED_URL)
notizie_positive = []

for entry in feed.entries:
    if analizza_notizia(entry.title):
        notizie_positive.append({
            "titolo": entry.title,
            "link": entry.link
        })

# Salviamo i risultati in un file
with open('notizie.json', 'w', encoding='utf-8') as f:
    json.dump(notizie_positive, f, ensure_ascii=False, indent=2)

print(f"Finito! Trovate {len(notizie_positive)} notizie positive.")
