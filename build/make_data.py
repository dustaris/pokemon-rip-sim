# Builds data.js: TCGdex card list + rarity, joined with TCGplayer market prices/images via tcgcsv.com.
# Refresh prices: python3 build/make_data.py --fetch
import json, glob, os, re, sys, urllib.request, datetime
os.chdir(os.path.dirname(os.path.abspath(__file__)))
MAIN, CLASSIC = 24722, 24837
def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})))
if '--fetch' in sys.argv:
    for g in (MAIN, CLASSIC):
        json.dump(get(f'https://tcgcsv.com/tcgplayer/3/{g}/products'), open(f'prod_{g}.json', 'w'))
        json.dump(get(f'https://tcgcsv.com/tcgplayer/3/{g}/prices'), open(f'price_{g}.json', 'w'))

def load(g):
    prods = json.load(open(f'prod_{g}.json'))['results']
    price = {}
    for q in json.load(open(f'price_{g}.json'))['results']:
        if q['marketPrice'] is not None:
            price[q['productId']] = max(price.get(q['productId'], 0), q['marketPrice'])
    ed = lambda p, k: next((e['value'] for e in p['extendedData'] if e['name'] == k), None)
    return [dict(id=p['productId'], name=p['name'], num=ed(p, 'Number'), url=p['url'], price=price.get(p['productId'])) for p in prods]

main = {p['num'].split('/')[0]: p for p in load(MAIN) if p['num']}
classic = [p for p in load(CLASSIC)]

def dl(pid, dest):
    if not os.path.exists(dest):
        urllib.request.urlretrieve(f'https://tcgplayer-cdn.tcgplayer.com/product/{pid}_in_600x600.jpg', dest)

R = {'Common':'C','Rare':'R','Double rare':'DR','Pikachu Rare':'PK','Illustration rare':'IR',
     'Special illustration rare':'SIR','Futuristic Rare':'FUR'}
cards, used = [], set()
for f in sorted(glob.glob('cards/*.json')):
    d = json.load(open(f))
    if d['id'].startswith('30th-c-'):
        m = next(p for p in classic if p['id'] not in used and p['name'].lower().startswith(d['name'].lower()))
        used.add(m['id'])
        img = f"img/c/cc{d['localId']}.jpg"; dl(m['id'], '../' + img)
        cards.append({'n': d['localId'], 'o': m['num'], 'name': d['name'], 'r': 'CC', 'img': img, 'p': m['price'], 'u': m['url']})
    else:
        m = main.get(d['localId'])
        cards.append({'n': d['localId'], 'name': d['name'], 'r': R[d['rarity']], 'img': f"img/c/{d['localId']}.jpg",
                      'p': m and m['price'], 'u': m and m['url']})
for p in load(MAIN):
    if p['num'] and p['num'].endswith('/RGB'):
        c = p['num'][0]; img = f'img/c/rgb{c}.jpg'; dl(p['id'], '../' + img)
        cards.append({'n': c, 'name': p['name'].split(' - ')[0] + f' ({ {"R":"Red","G":"Green","B":"Blue"}[c] })', 'r': 'RGB', 'img': img, 'p': p['price'], 'u': p['url']})
pack = next((p['price'] for p in load(MAIN) if p['name'] == '30th Celebration Booster Pack'), None)
asof = datetime.date.fromtimestamp(os.path.getmtime(f'price_{MAIN}.json')).isoformat()
open('../data.js', 'w').write('window.CARDS=' + json.dumps(cards, separators=(',', ':')) +
    f';\nwindow.PRICES={{asOf:"{asof}",pack:{json.dumps(pack)}}};\n')
missing = [c['name'] for c in cards if c['p'] is None]
print(len(cards), 'cards; pack', pack, 'as of', asof, '; no price:', missing)
