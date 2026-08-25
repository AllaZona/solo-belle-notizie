import feedparser
import json
from deep_translator import GoogleTranslator
from transformers import pipeline

print("Caricamento modello NLP in corso...")
# Inizializza il modello NLP multilingua. Valuta il sentiment da 1 a 5 stelle.
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# Espansione fonti
FEEDS = [
    {"nome": "ANSA", "url": "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml", "lingua": "it"},
    {"nome": "Corriere della Sera", "url": "https://xml2.corriereobjects.it/rss/homepage.xml", "lingua": "it"},
    {"nome": "Repubblica", "url": "https://www.repubblica.it/rss/homepage/rss2.0.xml", "lingua": "it"},
    {"nome": "Focus", "url": "https://www.focus.it/rss/tutte-le-notizie", "lingua": "it"},
    {"nome": "Il Sole 24 Ore", "url": "https://www.ilsole24ore.com/rss/italia.xml", "lingua": "it"},
    {"nome": "Sky TG24", "url": "https://tg24.sky.it/rss/all.xml", "lingua": "it"},
    
    {"nome": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "lingua": "en"},
    {"nome": "The Guardian", "url": "https://www.theguardian.com/world/rss", "lingua": "en"},
    
    {"nome": "Positive News", "url": "https://www.positive.news/feed/", "lingua": "en"},
    {"nome": "Good News Network", "url": "https://www.goodnewsnetwork.org/feed/", "lingua": "en"}
]

def analizza_notizia_nlp(testo):
    try:
        # Tronca il testo a 512 token per limitazioni tecniche del modello base
        risultato = sentiment_analyzer(testo[:512])[0] 
        label = risultato['label']
        # Estrae il numero di stelle (es. "5 stars" -> 5)
        stelle = int(label.split()[0])
        return stelle >= 4
    except Exception as e:
        print(f"Errore NLP: {e}")
        return False

print("Inizio scansione feed...")
notizie_filtrate = []
link_visti = set()

for feed_info in FEEDS:
    try:
        feed = feedparser.parse(feed_info['url'])
        for entry in feed.entries:
            link = entry.get('link', '')
            titolo_originale = entry.get('title', '')

            if not link or link in link_visti:
                continue

            is_positive_source = feed_info['nome'] in ["Positive News", "Good News Network"]

            if is_positive_source or analizza_notizia_nlp(titolo_originale):
                
                titolo_da_salvare = titolo_originale
                if feed_info['lingua'] != 'it':
                    try:
                        titolo_da_salvare = GoogleTranslator(source='auto', target='it').translate(titolo_originale)
                    except Exception as e:
                        print(f"Errore di traduzione: {e}")
                
                notizie_filtrate.append({
                    "titolo": titolo_da_salvare,
                    "link": link,
                    "fonte": feed_info['nome']
                })
                link_visti.add(link)
    except Exception as e:
        print(f"Errore durante l'elaborazione di {feed_info['nome']}: {e}")

with open('notizie.json', 'w', encoding='utf-8') as f:
    json.dump(notizie_filtrate, f, ensure_ascii=False, indent=2)

print(f"Scansione terminata. Notizie raccolte: {len(notizie_filtrate)}")
