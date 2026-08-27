import feedparser
import json
import random
import re
import html
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from time import mktime, sleep
from deep_translator import GoogleTranslator

# Fonti dedicate a buone notizie, scienza, ambiente, animali e innovazione
FEEDS = [
    # Fonti Italiane Tematiche
    {"nome": "ANSA Scienza", "url": "https://www.ansa.it/canale_scienza_tecnica/notizie/scienza_tecnica_rss.xml", "lingua": "it"},
    {"nome": "ANSA Ambiente", "url": "https://www.ansa.it/canale_ambiente/notizie/ambiente_rss.xml", "lingua": "it"},
    {"nome": "Focus", "url": "https://www.focus.it/rss/tutte-le-notizie", "lingua": "it"},
    {"nome": "Wired Italia", "url": "https://www.wired.it/feed/rss", "lingua": "it"},
    {"nome": "GreenMe", "url": "https://www.greenme.it/feed/", "lingua": "it"},
    {"nome": "Rinnovabili.it", "url": "https://www.rinnovabili.it/feed/", "lingua": "it"},
    
    # Fonti Internazionali di Notizie Positive e Costruttive
    {"nome": "Good News Network", "url": "https://www.goodnewsnetwork.org/feed/", "lingua": "en"},
    {"nome": "Positive News", "url": "https://www.positive.news/feed/", "lingua": "en"},
    {"nome": "Optimist Daily", "url": "https://www.optimistdaily.com/feed/", "lingua": "en"},
    {"nome": "Good Good Good", "url": "https://www.goodgoodgood.co/articles?format=rss", "lingua": "en"},
    {"nome": "Science Daily", "url": "https://www.sciencedaily.com/rss/top/science.xml", "lingua": "en"},
    {"nome": "BBC Science", "url": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "lingua": "en"}
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

# Parole positive rigorose (rimossi termini ambigui come 'aiuto', 'accordo', 'crescita', 'speranza')
PAROLE_POSITIVE_IT = [
    'scoperta', 'successo', 'guarigione', 'vittoria', 'innovazione', 
    'progresso', 'traguardo', 'solidarietà', 'miracolo', 'donazione', 
    'rinascita', 'cucciolo', 'amore', 'felicità', 'matrimonio', 'nozze', 
    'riciclo', 'salvato', 'salvata', 'tutela', 'biodiversità', 'sostenibile'
]

PAROLE_NEGATIVE_IT = [
    'mort', 'decess', 'uccis', 'vittim', 'strag', 'omicid', 'femminicid', 
    'annega', 'incidente', 'tragedia', 'crisi', 'croll', 'paura', 'violenz', 
    'attacc', 'armi', 'missil', 'guerra', 'bomba', 'ucrain', 'russi', 'putin', 
    'zelensk', 'israel', 'gaza', 'hamas', 'conflitt', 'politic', 'elezion', 
    'govern', 'parlament', 'partit', 'vot', 'sindac', 'ministr', 'premier', 
    'senat', 'candidat', 'trump', 'biden', 'harris', 'meloni', 'schlein', 
    'salvini', 'conte', 'lega', 'vannacci', 'destra', 'sinistra', 'arrest', 
    'carcer', 'process', 'condann', 'truff', 'sanzion', 'multa', 'tass', 
    'banc', 'inflazion', 'dipendenz', 'drog', 'sequestr', 'abuso', 'danni', 
    'preoccupaz', 'disoccupaz', 'falliment', 'scompars', 'malatti', 'tumore', 'cancro'
]

PAROLE_POSITIVE_EN = [
    'breakthrough', 'discovery', 'success', 'healing', 'victory', 
    'innovation', 'progress', 'milestone', 'award', 'recovery', 
    'donation', 'charity', 'puppy', 'love', 'happiness', 'wedding', 
    'rescued', 'renewable', 'clean energy', 'restoration', 'conservation'
]

PAROLE_NEGATIVE_EN = [
    'death', 'dead', 'kill', 'casualt', 'murder', 'drown', 'traged', 
    'accident', 'crisis', 'collapse', 'fear', 'violen', 'attack', 'weapon', 
    'missil', 'war', 'bomb', 'ukrain', 'russia', 'putin', 'zelensk', 
    'israel', 'gaza', 'hamas', 'conflict', 'politic', 'election', 'govern', 
    'parliament', 'party', 'vote', 'mayor', 'minister', 'senat', 'candidat', 
    'trump', 'biden', 'harris', 'democrat', 'republican', 'arrest', 'prison', 
    'jail', 'court', 'trial', 'condemn', 'fraud', 'sanction', 'fine', 
    'tax', 'bank', 'inflation', 'addiction', 'drug', 'kidnap', 'abuse', 
    'damage', 'concern', 'unemployment', 'bankruptcy', 'missing', 'disease', 'cancer'
]

CATEGORIE = {
    "Scienza & Tech": ["scoperta", "innovazione", "ricerca", "spazio", "tecnologia", "studio", "scienziat", "intelligenza artificiale", "medicina", "scienza", "astronomia", "energia"],
    "Animali": ["cucciol", "cane", "cani", "gatto", "gatti", "animal", "fauna", "specie", "natura", "selvatic", "uccell", "biodiversit"],
    "Salute": ["guarigione", "salute", "benessere", "cura", "terapia", "medico"],
    "Società": ["solidarietà", "donazione", "beneficenza", "volontari", "comunità", "matrimonio", "nozze", "sostenibil", "riciclo"]
}

def analizza_notizia(testo, lingua):
    testo = testo.lower()
    if lingua == "en":
        positive, negative = PAROLE_POSITIVE_EN, PAROLE_NEGATIVE_EN
    else:
        positive, negative = PAROLE_POSITIVE_IT, PAROLE_NEGATIVE_IT

    # Blocco immediato se presente qualsiasi parola negativa
    for parola in negative:
        if re.search(rf'\b{parola}', testo):
            return False

    # Accettazione se presente almeno una parola esplicitamente positiva
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
    except Exception:
        pass

    try:
        trad = GoogleTranslator(source='auto', target='it').translate(testo)
        if trad and "Error 500" not in trad: 
            return trad
    except Exception:
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
    testo_pulito = re.sub(r'<[^>]+>', '', testo)
    testo_pulito = html.unescape(testo_pulito)
    testo_pulito = testo_pulito.strip()
    return testo_pulito

print("Inizio scansione feed tematici...")
notizie_salvate = []
link_visti = set()
limite_temporale = datetime.now(timezone.utc) - timedelta(days=7)

if os.path.exists('notizie.json'):
    try:
        with open('notizie.json', 'r', encoding='utf-8') as f:
            dati_salvati = json.load(f)
            lista_vecchia = dati_salvati.get('notizie', []) if isinstance(dati_salvati, dict) else dati_salvati
            
            for notiz in lista_vecchia:
                data_str = notiz.get('data', 'Data sconosciuta')
                mantieni = True
                if data_str != 'Data sconosciuta':
                    try:
                        dt_notizia = datetime.strptime(data_str, "%d/%m/%Y").replace(tzinfo=timezone.utc)
                        if dt_notizia < limite_temporale:
                            mantieni = False
                    except Exception:
                        pass
                
                if mantieni:
                    notizie_salvate.append(notiz)
                    link_visti.add(notiz.get('link', ''))
    except Exception as e:
        pass

nuove_notizie = []

for feed_info in FEEDS:
    try:
        feed = feedparser.parse(feed_info['url'])
        for entry in feed.entries:
            link = entry.get('link', '')
            titolo_originale = entry.get('title', '')
            sommario_originale = entry.get('summary', entry.get('description', ''))
            
            testo_completo = titolo_originale + " " + sommario_originale

            if not link or link in link_visti: 
                continue

            data_formattata = "Data sconosciuta"
            data_pubblicazione_str = entry.get('published_parsed') or entry.get('updated_parsed')
            if data_pubblicazione_str:
                try:
                    dt_pubblicazione = datetime.fromtimestamp(mktime(data_pubblicazione_str), timezone.utc)
                    if dt_pubblicazione < limite_temporale: 
                        continue
                    data_formattata = dt_pubblicazione.strftime("%d/%m/%Y")
                except Exception:
                    pass

            if analizza_notizia(testo_completo, feed_info['lingua']):
                titolo_tradotto = traduci_testo_sicuro(titolo_originale, feed_info['lingua'])
                categoria = assegna_categoria(titolo_tradotto)
                sleep(1)
                
                sommario_pulito = pulisci_anteprima(sommario_originale)
                if len(sommario_pulito) > 160:
                    sommario_pulito = sommario_pulito[:157] + "..."
                
                sommario_tradotto = traduci_testo_sicuro(sommario_pulito, feed_info['lingua'])
                if feed_info['lingua'] != 'it': 
                    sleep(1.5)
                
                immagine = estrai_immagine(entry)
                if not immagine: 
                    immagine = random.choice(IMMAGINI_FALLBACK)
                
                nuove_notizie.append({
                    "titolo": titolo_tradotto,
                    "link": link,
                    "fonte": feed_info['nome'],
                    "immagine": immagine,
                    "data": data_formattata,
                    "categoria": categoria,
                    "sommario": sommario_tradotto
                })
                link_visti.add(link)
    except Exception as e:
        print(f"Errore su feed {feed_info['nome']}: {e}")

notizie_totali = nuove_notizie + notizie_salvate

dati_finali = {
    "citazione": random.choice(CITAZIONI),
    "curiosita": random.choice(CURIOSITA),
    "notizie": notizie_totali
}

with open('notizie.json', 'w', encoding='utf-8') as f:
    json.dump(dati_finali, f, ensure_ascii=False, indent=2)

print(f"Scansione terminata. Nuove: {len(nuove_notizie)}. Totali: {len(notizie_totali)}")
