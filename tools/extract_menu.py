# Lee la carta maestra (xlsx) y genera assets/menu-data.js con 4 idiomas y 2 canales.
import openpyxl, json, re, pathlib

SRC = r"C:/Users/Pablo/Downloads/BELLA CIAO _ CARTA MAESTRA CORPORATIVA _ CAT ES FR EN _ V1.xlsx"
OUT = pathlib.Path('assets/menu-data.js')


# Correcciones de nombres: el Excel mezcla idiomas en algunas filas.
NAME_FIXES = {
    'BC-032': {'ca': 'MARGHERITA', 'es': 'MARGHERITA', 'fr': 'MARGHERITA', 'en': 'MARGHERITA'},
    'BC-033': {'ca': 'PROSCIUTTO', 'es': 'PROSCIUTTO', 'fr': 'PROSCIUTTO', 'en': 'PROSCIUTTO'},
    'BC-022': {'es': 'TAGLIATELLE 4 QUESOS', 'fr': 'TAGLIATELLE AUX 4 FROMAGES', 'en': 'FOUR-CHEESE TAGLIATELLE'},
    'BC-027': {'es': 'FIOCCHI CON PERA Y RICOTTA', 'fr': 'FIOCCHI POIRE ET RICOTTA', 'en': 'PEAR AND RICOTTA FIOCCHI'},
    'BC-072': {'es': 'AGUA S. PELLEGRINO', 'fr': 'EAU S. PELLEGRINO', 'en': 'S. PELLEGRINO WATER'},
    'BC-071': {'es': 'VICHY CATALÁN'},
    'BC-011': {'ca': 'FORMATGE DE CABRA'},
    'BC-004': {'ca': "MANDONGUILLES D'ALBERGÍNIA"},
    'BC-SUP-004': {'ca': 'XAMPINYONS'},
    'BC-090': {'ca': 'GERRA'},
    'BC-074': {'fr': 'MARTINI / VERMOUTH', 'en': 'MARTINI / VERMOUTH'},
    'BC-082': {'fr': 'CUBA LIBRE', 'en': 'CUBA LIBRE'},
}

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb['MAESTRA']

def is_true(v): return str(v).strip().lower() == 'true'
def clean(s):
    s = re.sub(r'\s+', ' ', (s or '')).strip()
    return s[:-1] if s.endswith('.') else s

def price(p):
    try: p = float(p)
    except (TypeError, ValueError): p = 0.0
    return 's/m' if p <= 0 else f"{p:.2f}".replace('.', ',')

items = []
for r in ws.iter_rows(min_row=2, values_only=True):
    if not r[0]: continue
    name = {k: clean(v) for k, v in zip(('ca','es','fr','en'), (r[3], r[5], r[7], r[9]))}
    if not name['es']: continue
    if r[0] in NAME_FIXES:
        for k, v in NAME_FIXES[r[0]].items():
            name[k] = v
    items.append(dict(
        id=r[0], order=float(r[1] or 0), cat=r[2],
        name=name,
        desc={k: clean(v) for k, v in zip(('ca','es','fr','en'), (r[4], r[6], r[8], r[10]))},
        price=price(r[11]), priceDl=price(r[13]),
        rest=is_true(r[14]) and is_true(r[15]),
        dl=is_true(r[16]) and is_true(r[15]),
    ))

CAT = {
 'pizzes':          dict(es='Pizze clásicas', ca='Pizzes clàssiques', fr='Pizzas classiques', en='Classic pizzas'),
 'pizzes_blanques': dict(es='Pizze blancas',  ca='Pizzes blanques',   fr='Pizzas blanches',  en='White pizzas'),
 'entrants':        dict(es='Entrantes',      ca='Entrants',          fr='Entrées',          en='Starters'),
 'amanides':        dict(es='Ensaladas',      ca='Amanides',          fr='Salades',          en='Salads'),
 'sopes':           dict(es='Sopas',          ca='Sopes',             fr='Soupes',           en='Soups'),
 'carn':            dict(es='Carne',          ca='Carns',             fr='Viandes',          en='Meat'),
 'pasta':           dict(es='Pasta',          ca='Pasta',             fr='Pâtes',            en='Pasta'),
 'pasta_farcida':   dict(es='Rellenas y risotti', ca='Farcides i risottos', fr='Farcies et risottos', en='Stuffed & risotto'),
 'postres':         dict(es='Postres',        ca='Postres',           fr='Desserts',         en='Desserts'),
 'cafe_te':         dict(es='Cafés e infusiones', ca='Cafès i infusions', fr='Cafés et infusions', en='Coffee & tea'),
 'begudes':         dict(es='Refrescos y aguas', ca='Refrescos i aigües', fr='Boissons et eaux', en='Soft drinks & water'),
 'cerveses':        dict(es='Cervezas',       ca='Cerveses',          fr='Bières',           en='Beers'),
 'alcohol':         dict(es='Licores',        ca='Licors',            fr='Spiritueux',       en='Spirits'),
 'coctels':         dict(es='Cócteles',       ca='Còctels',           fr='Cocktails',        en='Cocktails'),
 'suplements':      dict(es='Extras',         ca='Extres',            fr='Suppléments',      en='Extras'),
}

BLOCKS = [
 dict(id='pizze', n='01', cats=['pizzes'], title=dict(es='Pizzas clásicas', ca='Pizzes clàssiques', fr='Pizzas classiques', en='Classic pizzas'),
      note=dict(es='Masa artesanal, integral o normal', ca='Massa artesanal, integral o normal', fr='Pâte artisanale, complète ou classique', en='Handmade dough, wholemeal or classic')),
 dict(id='pizze-bianche', n='02', cats=['pizzes_blanques'], title=dict(es='Pizzas blancas', ca='Pizzes blanques', fr='Pizzas blanches', en='White pizzas'),
      note=dict(es='Sin tomate, con base de queso', ca='Sense tomàquet, amb base de formatge', fr='Sans tomate, base fromage', en='No tomato, cheese base')),
 dict(id='entrantes', n='03', cats=['entrants'], title=dict(es='Entrantes', ca='Entrants', fr='Entrées', en='Starters'),
      note=dict(es='Para compartir, como en casa', ca='Per compartir, com a casa', fr='À partager, comme à la maison', en='To share, like at home')),
 dict(id='ensaladas', n='04', cats=['amanides','sopes'], title=dict(es='Ensaladas y sopas', ca='Amanides i sopes', fr='Salades et soupes', en='Salads & soups'),
      note=dict(es='Producto de temporada', ca='Producte de temporada', fr='Produits de saison', en='Seasonal produce'),
      groups={'amanides':dict(es='Ensaladas',ca='Amanides',fr='Salades',en='Salads'), 'sopes':dict(es='Sopas',ca='Sopes',fr='Soupes',en='Soups')}),
 dict(id='carne', n='05', cats=['carn'], title=dict(es='Carne', ca='Carns', fr='Viandes', en='Meat'),
      note=dict(es='Entrecot: precio por 100 g · mínimo 300 g', ca='Entrecot: preu per 100 g · mínim 300 g', fr='Entrecôte : prix aux 100 g · minimum 300 g', en='Entrecôte: price per 100 g · minimum 300 g')),
 dict(id='pasta', n='06', cats=['pasta','pasta_farcida'], title=dict(es='Pasta y risottos', ca='Pasta i risottos', fr='Pâtes et risottos', en='Pasta & risotto'),
      note=dict(es='Pasta fresca hecha cada día', ca='Pasta fresca feta cada dia', fr='Pâtes fraîches du jour', en='Fresh pasta made daily'),
      groups={'pasta':dict(es='Pasta',ca='Pasta',fr='Pâtes',en='Pasta'), 'pasta_farcida':dict(es='Rellenas y risottos',ca='Farcides i risottos',fr='Farcies et risottos',en='Stuffed pasta & risotto')}),
 dict(id='postres', n='07', cats=['postres'], title=dict(es='Postres', ca='Postres', fr='Desserts', en='Desserts'),
      note=dict(es='Todos caseros', ca='Tots casolans', fr='Tous faits maison', en='All homemade')),
 dict(id='cafes', n='08', cats=['cafe_te'], title=dict(es='Cafés e infusiones', ca='Cafès i infusions', fr='Cafés et infusions', en='Coffee & tea'),
      note=dict(es='También descafeinado y sin lactosa', ca='També descafeïnat i sense lactosa', fr='Aussi déca et sans lactose', en='Decaf and lactose-free available')),
 dict(id='bebidas', n='09', cats=['begudes','cerveses','alcohol','coctels'], title=dict(es='Bebidas', ca='Begudes', fr='Boissons', en='Drinks'),
      note=dict(es='s/m = según marca · caña 0,33 l · jarra 0,5 l', ca='s/m = segons marca · canya 0,33 l · gerra 0,5 l', fr='s/m = selon marque · 33 cl / 50 cl', en='s/m = by brand · 0.33 l / 0.5 l'),
      groups={'begudes':dict(es='Refrescos y aguas',ca='Refrescos i aigües',fr='Boissons et eaux',en='Soft drinks & water'),
              'cerveses':dict(es='Cervezas',ca='Cerveses',fr='Bières',en='Beers'),
              'alcohol':dict(es='Licores',ca='Licors',fr='Spiritueux',en='Spirits'),
              'coctels':dict(es='Cócteles',ca='Còctels',fr='Cocktails',en='Cocktails')}),
 dict(id='extras', n='10', cats=['suplements'], title=dict(es='Extras', ca='Extres', fr='Suppléments', en='Extras'),
      note=dict(es='Suplementos para pizza y pasta', ca='Suplements per a pizza i pasta', fr='Suppléments pour pizza et pâtes', en='Toppings for pizza and pasta')),
]

def build(channel):
    out = []
    for b in BLOCKS:
        cat_in_block = [c for c in b['cats']]
        groups = []
        for c in cat_in_block:
            its = [i for i in items if i['cat'] == c and (i['rest'] if channel == 'restaurant' else i['dl'])]
            if not its: continue
            groups.append(dict(cat=c, label=b['groups'][c] if 'groups' in b else None,
                               items=[dict(id=i['id'], name=i['name'], desc=i['desc'],
                                           price=(i['price'] if channel == 'restaurant' else i['priceDl'])) for i in sorted(its, key=lambda x: x['order'])]))
        if not groups: continue
        out.append(dict(id=b['id'], title=b['title'], note=b['note'], groups=groups))
    return out

data = dict(updated='Octubre 2026',
            categories=CAT,
            channels={c: dict(blocks=build(c)) for c in ('restaurant', 'delivery')})

js = 'window.BC=window.BC||{};window.BC.data=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
OUT.write_text(js, encoding='utf-8')
for c in ('restaurant','delivery'):
    n = sum(len(g['items']) for b in data['channels'][c]['blocks'] for g in b['groups'])
    print(c, 'bloques', len(data['channels'][c]['blocks']), 'platos', n)
print('bytes', len(js))
