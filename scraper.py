import feedparser
import json
from deep_translator import GoogleTranslator
from transformers import pipeline

print("Caricamento modello NLP in corso...")
# Inizializza il modello NLP multilingua
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# Fonti aggiornate (rimosse le testate specifiche di buone notizie)
FEEDS = [
    {"nome": "ANSA", "url": "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml", "lingua": "it"},
    {"nome": "Corriere della Sera", "url": "https://xml2.corriereobjects.it/rss/homepage.xml", "lingua": "it"},
    {"nome": "Repubblica", "url": "https://www.repubblica.it/rss/homepage/rss2.0.xml", "lingua": "it"},
    {"nome": "Focus", "url": "https://www.focus.it/rss/tutte-le-notizie", "lingua": "it"},
    {"nome": "Il Sole 24 Ore", "url": "https://www.ilsole24ore.com/rss/italia.xml", "lingua": "it"},
    {"nome": "Sky TG24", "url": "https://tg24.sky.it/rss/all.xml", "lingua": "it"},
    {"nome": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "lingua": "en"},
    {"nome": "The Guardian", "url": "https://www.theguardian.com/world/rss", "lingua": "en"}
]

def analizza_notizia_nlp(testo):
    try:
        risultato = sentiment_analyzer(testo[:512])[0] 
        label = risultato['label']
        stelle = int(label.split()[0])
        # Accetta solo notizie da 4 o 5 stelle
        return stelle >= 4
    except Exception as e:
        print(f"Errore NLP: {e}")
        return False

def estrai_immagine(entry):
    # Cerca l'immagine tra i vari formati possibili nei feed RSS
    if 'media_content' in entry:
        for media in entry.media_content:
            if 'url' in media and (media.get('medium') == 'image' or media.get('url', '').endswith(('.jpg', '.jpeg', '.png', '.webp'))):
                return media['url']
    if 'enclosures' in entry:
        for enclosure in entry.enclosures:
            if 'type' in enclosure and enclosure['type'].startswith('image/'):
                return enclosure['href']
    return None

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

            # Tutte le notizie ora devono passare il filtro AI
            if analizza_notizia_nlp(titolo_originale):
                
                titolo_da_salvare = titolo_originale
                if feed_info['lingua'] != 'it':
                    try:
                        titolo_da_salvare = GoogleTranslator(source='auto', target='it').translate(titolo_originale)
                    except Exception as e:
                        print(f"Errore di traduzione: {e}")
                
                # Estrazione immagine
                immagine = estrai_immagine(entry)
                
                notizie_filtrate.append({
                    "titolo": titolo_da_salvare,
                    "link": link,
                    "fonte": feed_info['nome'],
                    "immagine": immagine
                })
                link_visti.add(link)
    except Exception as e:
        print(f"Errore durante l'elaborazione di {feed_info['nome']}: {e}")

with open('notizie.json', 'w', encoding='utf-8') as f:
    json.dump(notizie_filtrate, f, ensure_ascii=False, indent=2)

print(f"Scansione terminata. Notizie raccolte: {len(notizie_filtrate)}")
