import feedparser
import json
import random
import re
import html
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from time import mktime, sleep
from deep_translator import GoogleTranslator

FEEDS = [
    {"nome": "ANSA", "url": "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml", "lingua": "it"},
    {"nome": "Corriere della Sera", "url": "https://xml2.corriereobjects.it/rss/homepage.xml", "lingua": "it"},
    {"nome": "Repubblica", "url": "https://www.repubblica.it/rss/homepage/rss2.0.xml", "lingua": "it"},
    {"nome": "Focus", "url": "https://www.focus.it/rss/tutte-le-notizie", "lingua": "it"},
    {"nome": "Il Sole 24 Ore", "url": "https://www.ilsole24ore.com/rss/italia.xml", "lingua": "it"},
    {"nome": "Sky TG24", "url": "https://tg24.sky.it/rss/all.xml", "lingua": "it"},
    {"nome": "La Stampa", "url": "https://www.lastampa.it/rss/italia", "lingua": "it"},
    {"nome": "Il Messaggero", "url": "https://www.ilmessaggero.it/rss/italia.xml", "lingua": "it"},
    {"nome": "Il Post", "url": "https://www.ilpost.it/feed/", "lingua": "it"},
    {"nome": "Wired Italia", "url": "https://www.wired.it/feed/rss", "lingua": "it"},
    {"nome": "AGI", "url": "https://www.agi.it/rss", "lingua": "it"},
    {"nome": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "lingua": "en"},
    {"nome": "The Guardian", "url": "https://www.theguardian.com/world/rss", "lingua": "en"},
    {"nome": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "lingua": "en"},
    {"nome": "Washington Post", "url": "https://feeds.washingtonpost.com/rss/world", "lingua": "en"},
    {"nome": "CNN", "url": "http://rss.cnn.com/rss/edition_world.rss", "lingua": "en"},
    {"nome": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "lingua": "en"},
    {"nome": "Le Monde", "url": "https://www.lemonde.fr/international/rss_full.xml", "lingua": "fr"},
    {"nome": "El Pais", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional/portada", "lingua": "es"},
    {"nome": "Der Spiegel", "url": "https://www.spiegel.de/international/index.rss", "lingua": "en"}
]

CITAZIONI = [
    "Fai un respiro profondo. Tutto andrà bene. 🌿",
    "Sii gentile con te stesso oggi. Te lo meriti. ✨",
    "Il sorriso è la curva che raddrizza ogni cosa. 😊",
    "Ogni giorno è una nuova opportunità. 🌅",
    "Prenditi una pausa. Il mondo può aspettare. ☕"
]

CURIOSITA = [
    "Sapevi che le mucche hanno migliori amiche e si rilassano quando sono vicine?",
    "Le lontre di mare si tengono per mano mentre dormono per non separarsi.",
    "Il battito cardiaco di due persone che si amano si sincronizza se si guardano negli occhi.",
    "In Svezia esiste la 'Fika': prendersi una pausa caffè per godersi le cose belle della vita.",
    "I macachi giapponesi fanno le palle di neve solo per il gusto di giocarci."
]

IMMAGINI_FALLBACK = [
    "https://images.unsplash.com/photo-1470071131384-001b85755536?w=800&q=80",
    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80",
    "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=800&q=80",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80"
]

PAROLE_POSITIVE_IT = ['scoperta', 'successo', 'crescita', 'guarigione', 'salvataggio', 'vittoria', 'innovazione', 'aiuto', 'progresso', 'pace', 'accordo', 'svolta', 'traguardo', 'solidarietà', 'miracolo', 'donazione', 'rinascita', 'cucciolo', 'amore', 'felicità']
PAROLE_NEGATIVE_IT = ['morti', 'crisi', 'tragedia', 'incidente', 'guerra', 'omicidio', 'arrest', 'croll', 'paura', 'violenz', 'attacc', 'uccis', 'vittim', 'condann', 'truff', 'sanzion', 'armi', 'missil', 'abus', 'ferit', 'decess', 'strag', 'carcer', 'process', 'scompars', 'malatti', 'drog', 'sequestr', 'ucrain', 'russi', 'putin', 'zelensk', 'israel', 'gaza', 'hamas', 'conflitt']

PAROLE_POSITIVE_EN = ['breakthrough', 'discovery', 'success', 'healing', 'rescue', 'victory', 'innovation', 'progress', 'peace', 'milestone', 'hope', 'award', 'recovery', 'donation', 'charity', 'puppy', 'love', 'happiness']
PAROLE_NEGATIVE_EN = ['death', 'kill', 'crisis', 'traged', 'accident', 'war', 'murder', 'arrest', 'collaps', 'fear', 'violen', 'attack', 'dead', 'casualt', 'fraud', 'sanction', 'weapon', 'missil', 'abus', 'missing', 'prison', 'jail', 'court', 'trial', 'kidnap', 'disease', 'ukrain', 'russia', 'putin', 'zelensk', 'israel', 'gaza', 'hamas', 'conflict']

PAROLE_POSITIVE_ES = ['descubrimiento', 'éxito', 'curación', 'rescate', 'victoria', 'innovación', 'progreso', 'paz', 'esperanza', 'premio', 'amor', 'felicidad']
PAROLE_NEGATIVE_ES = ['muert', 'asesinat', 'crisis', 'tragedia', 'accident', 'guerra', 'arrest', 'violencia', 'ataqu', 'víctim', 'desaparecid', 'prisión', 'cárcel', 'juici', 'enfermedad', 'ucrani', 'rusi', 'zelensk', 'putin', 'israel', 'gaza', 'hamas', 'conflict', 'armas', 'misil', 'tropas', 'ejércit', 'precio']

PAROLE_POSITIVE_FR = ['découverte', 'succès', 'guérison', 'sauvetage', 'victoire', 'innovation', 'progrès', 'paix', 'espoir', 'prix', 'amour', 'bonheur']
PAROLE_NEGATIVE_FR = ['mort', 'crise', 'tragédie', 'accident', 'guerre', 'meurtre', 'arrestation', 'violence', 'attaque', 'victimes', 'disparu', 'prison', 'procès', 'maladie', 'ukraine', 'russie', 'zelensky', 'putin', 'israël', 'gaza', 'hamas', 'conflit']

CATEGORIE = {
    "Scienza & Tech": ["scoperta", "innovazione", "ricerca", "spazio", "tecnologia", "studio", "scienziat", "intelligenza artificiale", "medicina", "scienza", "astronomia"],
    "Animali": ["cucciol", "cane", "cani", "gatto", "gatti", "animal", "fauna", "specie", "natura", "selvatic", "uccell"],
    "Salute": ["guarigione", "salute", "benessere", "cura", "ospedale", "terapia", "medico", "pazient"],
    "Società": ["solidarietà", "donazione", "beneficenza", "aiuto", "volontari", "comunità", "salvataggio", "diritti", "pace", "sociale"]
}

def analizza_notizia(testo, lingua):
    testo = testo.lower()
    if lingua == "en":
        positive, negative = PAROLE_POSITIVE_EN, PAROLE_NEGATIVE_EN
    elif lingua == "es":
        positive, negative = PAROLE_POSITIVE_ES, PAROLE_NEGATIVE_ES
    elif lingua == "fr":
        positive, negative = PAROLE_POSITIVE_FR, PAROLE_NEGATIVE_FR
    else:
        positive, negative = PAROLE_POSITIVE_IT, PAROLE_NEGATIVE_IT

    for parola in negative:
        if re.search(rf'\b{parola}', testo):
            return False

    for parola in positive:
        if re.search(rf'\b{parola}\b', testo):
            return True
    return False

def assegna_categoria(testo):
    testo_lower = testo.lower()
    for cat, parole in CATEGORIE.items():
        for p in parole:
            if re.search(rf'\b{p}', testo_lower):
                return cat
    return "Mondo"

def traduci_testo_sicuro(testo, lingua_origine):
    if not testo or lingua_origine == 'it': 
        return testo
    
    try:
        testo_codificato = urllib.parse.quote(testo)
        url = f"https://api.mymemory.translated.net/get?q={testo_codificato}&langpair={lingua_origine}|it&de=belle.notizie.app@gmail.com"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if data['responseStatus'] == 200:
            traduzione = data['responseData']['translatedText']
            if traduzione and "MYMEMORY WARNING" not in traduzione:
                return traduzione
    except Exception as e:
        pass

    try:
        trad = GoogleTranslator(source='auto', target='it').translate(testo)
        if trad and "Error 500" not in trad: 
            return trad
    except Exception as e:
        pass
        
    return testo

def estrai_immagine(entry):
    if 'media_content' in entry:
        for media in entry.media_content:
            if 'url' in media and (media.get('medium') == 'image' or media.get('url', '').endswith(('.jpg', '.jpeg', '.png', '.webp'))):
                return media['url']
    if 'enclosures' in entry:
        for enclosure in entry.enclosures:
            if 'type' in enclosure and enclosure['type'].startswith('image/'):
                return enclosure['href']
    return None

def pulisci_anteprima(testo):
    if not testo: return ""
    # Rimuove tutti i tag HTML (es. <div>, <p>, <img>, <a>)
    testo_pulito = re.sub(r'<[^>]+>', '', testo)
    # Converte le entità speciali (es. &quot; in ")
    testo_pulito = html.unescape(testo_pulito)
    # Rimuove gli spazi in eccesso all'inizio e alla fine
    testo_pulito = testo_pulito.strip()
    return testo_pulito

print("Inizio scansione feed...")
notizie_filtrate = []
link_visti = set()
limite_temporale = datetime.now(timezone.utc) - timedelta(days=7)

for feed_info in FEEDS:
    try:
        feed = feedparser.parse(feed_info['url'])
        for entry in feed.entries:
            link = entry.get('link', '')
            titolo_originale = entry.get('title', '')

            if not link or link in link_visti: continue

            data_formattata = "Data sconosciuta"
            data_pubblicazione_str = entry.get('published_parsed') or entry.get('updated_parsed')
            if data_pubblicazione_str:
                try:
                    dt_pubblicazione = datetime.fromtimestamp(mktime(data_pubblicazione_str), timezone.utc)
                    if dt_pubblicazione < limite_temporale: continue
                    data_formattata = dt_pubblicazione.strftime("%d/%m/%Y")
                except Exception:
                    pass

            if analizza_notizia(titolo_originale, feed_info['lingua']):
                # Traduce il titolo
                titolo_tradotto = traduci_testo_sicuro(titolo_originale, feed_info['lingua'])
                categoria = assegna_categoria(titolo_tradotto)
                sleep(1) # Breve pausa API
                
                # Estrae, pulisce e taglia il sommario (anteprima) a massimo 160 caratteri
                sommario_originale = entry.get('summary', entry.get('description', ''))
                sommario_pulito = pulisci_anteprima(sommario_originale)
                if len(sommario_pulito) > 160:
                    sommario_pulito = sommario_pulito[:157] + "..."
                
                # Traduce l'anteprima se necessario
                sommario_tradotto = traduci_testo_sicuro(sommario_pulito, feed_info['lingua'])
                if feed_info['lingua'] != 'it': 
                    sleep(1.5) # Pausa API se c'è stata una traduzione
                
                immagine = estrai_immagine(entry)
                if not immagine: immagine = random.choice(IMMAGINI_FALLBACK)
                
                notizie_filtrate.append({
                    "titolo": titolo_tradotto,
                    "link": link,
                    "fonte": feed_info['nome'],
                    "immagine": immagine,
                    "data": data_formattata,
                    "categoria": categoria,
                    "sommario": sommario_tradotto # Aggiunta del nuovo dato
                })
                link_visti.add(link)
    except Exception as e:
        print(f"Errore su feed {feed_info['nome']}: {e}")

dati_finali = {
    "citazione": random.choice(CITAZIONI),
    "curiosita": random.choice(CURIOSITA),
    "notizie": notizie_filtrate
}

with open('notizie.json', 'w', encoding='utf-8') as f:
    json.dump(dati_finali, f, ensure_ascii=False, indent=2)
