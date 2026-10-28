# Compara la carta maestra (xlsx) con lo que publica la web (assets/menu-data.js)
import openpyxl, json, pathlib, sys

SRC = r"C:/Users/Pablo/Downloads/BELLA CIAO _ CARTA MAESTRA CORPORATIVA _ CAT ES FR EN _ V1.xlsx"
raw = pathlib.Path('assets/menu-data.js').read_text(encoding='utf-8')
key = 'window.BC.data='
web = json.loads(raw[raw.index(key)+len(key):raw.rindex('}')+1])

def is_true(v): return str(v).strip().lower() == 'true'
def fmt(p):
    try: p = float(p)
    except (TypeError, ValueError): p = 0.0
    return 's/m' if p <= 0 else f"{p:.2f}".replace('.', ',')

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb['MAESTRA']

excel = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    if not r[0]:
        continue
    excel[r[0]] = dict(
        id=r[0], cat=r[2], name_es=(r[5] or '').strip(), name_cat=(r[3] or '').strip(),
        price=fmt(r[11]), price_dl=fmt(r[13]),
        rest=is_true(r[14]) and is_true(r[15]), dl=is_true(r[16]) and is_true(r[15]))

web_idx = {}
for ch, chobj in web['channels'].items():
    for b in chobj['blocks']:
        for g in b['groups']:
            for it in g['items']:
                web_idx.setdefault(it['id'], {})[ch] = it

problems = []
for pid, e in excel.items():
    w = web_idx.get(pid)
    if not w:
        problems.append(('FALTA EN LA WEB', pid, e['name_es'] or e['name_cat'], 'flags rest=%s dl=%s' % (e['rest'], e['dl'])))
        continue
    if e['rest'] and 'restaurant' not in w:
        problems.append(('FALTA EN RESTAURANTE', pid, e['name_es'], ''))
    if e['dl'] and 'delivery' not in w:
        problems.append(('FALTA EN DELIVERY', pid, e['name_es'], ''))
    if not e['rest'] and 'restaurant' in w:
        problems.append(('SOBRA EN RESTAURANTE', pid, e['name_es'], 'Web=False'))
    if not e['dl'] and 'delivery' in w:
        problems.append(('SOBRA EN DELIVERY', pid, e['name_es'], 'Delivery=False'))
    if 'restaurant' in w and w['restaurant']['price'] != e['price']:
        problems.append(('PRECIO DISTINTO', pid, e['name_es'], '%s vs %s' % (w['restaurant']['price'], e['price'])))
    if 'restaurant' in w and (w['restaurant']['name']['es'] or '').strip() != e['name_es']:
        problems.append(('NOMBRE DISTINTO', pid, e['name_es'], w['restaurant']['name']['es']))

for pid in web_idx:
    if pid not in excel:
        problems.append(('ID DESCONOCIDO EN LA WEB', pid, '', ''))

def total(ch):
    return sum(len(g['items']) for b in web['channels'][ch]['blocks'] for g in b['groups'])

print('EXCEL: %d productos (%d restaurante / %d delivery)'
      % (len(excel), sum(1 for e in excel.values() if e['rest']), sum(1 for e in excel.values() if e['dl'])))
print('WEB:   %d productos (%d restaurante / %d delivery)' % (sum(len(v) for v in web_idx.values()), total('restaurant'), total('delivery')))
print()
if not problems:
    print('✔ Sin diferencias: todos los productos del Excel están en la web con su nombre y precio.')
else:
    print('Diferencias (%d):' % len(problems))
    for p in problems:
        print('  -', ' | '.join(str(x) for x in p if x != ''))
