import feedparser
import json

# Elenco fonti RSS (Italiane, Internazionali e siti specializzati in buone notizie)
FEEDS = [
    # Fonti Italiane
    {"nome": "ANSA", "url": "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml", "lingua": "it"},
    {"nome": "Corriere della Sera", "url": "https://xml2.corriereobjects.it/rss/homepage.xml", "lingua": "it"},
    {"nome": "Repubblica", "url": "https://www.repubblica.it/rss/homepage/rss2.0.xml", "lingua": "it"},
    {"nome": "Focus", "url": "https://www.focus.it/rss/tutte-le-notizie", "lingua": "it"},
    
    # Fonti Internazionali Generaliste
    {"nome": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "lingua": "en"},
    {"nome": "The Guardian", "url": "https://www.theguardian.com/world/rss", "lingua": "en"},
    
    # Fonti Internazionali dedicate a notizie positive
    {"nome": "Positive News", "url": "https://www.positive.news/feed/", "lingua": "en"},
    {"nome": "Good News Network", "url": "https://www.goodnewsnetwork.org/feed/", "lingua": "en"}
]

# Dizionari per il filtraggio
PAROLE_POSITIVE_IT = [
    'scoperta', 'successo', 'crescita', 'guarigione', 'salvataggio', 'vittoria',
    'innovazione', 'aiuto', 'progresso', 'pace', 'accordo', 'svolta', 'traguardo', 'solidarietà'
]
PAROLE_NEGATIVE_IT = [
    'morti', 'crisi', 'tragedia', 'incidente', 'guerra', 'omicidio', 'arresto',
    'crollo', 'paura', 'violenza', 'attacco', 'ucciso', 'vittime'
]

PAROLE_POSITIVE_EN = [
    'breakthrough', 'discovery', 'success', 'healing', 'rescue', 'victory',
    'innovation', 'progress', 'peace', 'milestone', 'hope', 'award', 'recovery'
]
PAROLE_NEGATIVE_EN = [
    'death', 'killed', 'crisis', 'tragedy', 'accident', 'war', 'murder',
    'arrest', 'collapse', 'fear', 'violence', 'attack', 'dead', 'casualty'
]

def analizza_notizia(testo, lingua):
    testo = testo.lower()
    if lingua == "en":
        positive = PAROLE_POSITIVE_EN
        negative = PAROLE_NEGATIVE_EN
    else:
        positive = PAROLE_POSITIVE_IT
        negative = PAROLE_NEGATIVE_IT

    punteggio = 0
    for parola in positive:
        if parola in testo:
            punteggio += 1
    for parola in negative:
        if parola in testo:
            punteggio -= 2
    
    return punteggio > 0

print("Inizio scansione feed...")
notizie_filtrate = []
link_visti = set()

for feed_info in FEEDS:
    try:
        feed = feedparser.parse(feed_info['url'])
        for entry in feed.entries:
            link = entry.get('link', '')
            titolo = entry.get('title', '')

            # Evita duplicati o voci vuote
            if not link or link in link_visti:
                continue

            # I siti già focalizzati su notizie positive non richiedono filtro rigido
            is_positive_source = feed_info['nome'] in ["Positive News", "Good News Network"]

            if is_positive_source or analizza_notizia(titolo, feed_info['lingua']):
                notizie_filtrate.append({
                    "titolo": titolo,
                    "link": link,
                    "fonte": feed_info['nome']
                })
                link_visti.add(link)
    except Exception as e:
        print(f"Errore durante l'elaborazione di {feed_info['nome']}: {e}")

# Scrittura su file JSON
with open('notizie.json', 'w', encoding='utf-8') as f:
    json.dump(notizie_filtrate, f, ensure_ascii=False, indent=2)

print(f"Scansione terminata. Notizie raccolte: {len(notizie_filtrate)}")
