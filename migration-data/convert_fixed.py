import json

SRC = '/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/raw_original.json'
CAR_PREFIX = [11, 12, 14, 15, 17, 18]

with open(SRC, encoding='utf-8') as f:
    d = json.load(f)
master_raw = d['master']
repl_raw = d['repl']


def real_car(formation, m_pos):
    # m_pos like "M01".."M24" -> (car_index 0-5, tm 1-4) -> real car number e.g. "1711"
    n = int(str(m_pos).lstrip('Mm'))
    idx = (n - 1) // 4
    tm = (n - 1) % 4 + 1
    yy = str(formation)[-2:]
    car = f"{CAR_PREFIX[idx]}{yy}"
    return car, tm


def clean_master(v):
    if v in (None, '', '?'):
        return None
    return v


def clean_int_master(v):
    if v in (None, '', '?'):
        return None
    return int(v)


out_master = []
for m in master_raw:
    formation = str(m['편성'])
    status = m['상태']
    note = (m.get('비고') or '').strip() or None
    exch = (m.get('교환일자') or '').strip() or None
    if status == '운영중':
        car, tm = real_car(formation, m['위치'])
        location = f"{formation}-{car}-TM{tm}"
    else:
        location = None
    out_master.append({
        "serial": m['시리얼'],
        "formation": formation,
        "location": location,
        "status": status,
        "made_year": clean_int_master(m['제작년도']),
        "maker": clean_master(m['제조사']),
        "note": note,
        "exchange_date": exch,
    })

def clean(v):
    if v in (None, '', '-'):
        return None
    return v


def clean_int(v):
    if v in (None, '', '-'):
        return None
    return int(v)


out_repl = []
skipped_repl = []
for r in repl_raw:
    if r['일자'] == 'None' or not r['일자']:
        skipped_repl.append(r)
        continue
    formation = str(r['편성'])
    car = str(r['차호'])
    tm = r['위치']
    location = f"{formation}-{car}-TM{tm}"
    out_repl.append({
        "repair_date": r['일자'],
        "formation": formation,
        "car": car,
        "location": location,
        "removed_serial": clean(r['취거시리얼']),
        "removed_year": clean_int(r['취거제작년도']),
        "removed_maker": clean(r['취거제조사']),
        "installed_serial": clean(r['부착시리얼']),
        "installed_year": clean_int(r['부착제작년도']),
        "installed_maker": clean(r['부착제조사']),
        "fault_type": r['고장유형'],
        "fault_code": r['고장코드'],
        "severity": r['심각도'],
        "risk_score": r['위험점수'],
        "is_fault": r['고장성'],
        "detail": (r.get('세부내용') or '').strip() or None,
        "removed_condition": (r.get('취거품상태') or '').strip() or None,
        "review": r['검토'],
    })

with open('/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/fixed_master.json', 'w', encoding='utf-8') as f:
    json.dump(out_master, f, ensure_ascii=False)
with open('/tmp/claude-0/-home-user-jabascriptdemo/6dcd6a5a-6ff8-5a6c-882d-ddd89f5788c7/scratchpad/fixed_repl.json', 'w', encoding='utf-8') as f:
    json.dump(out_repl, f, ensure_ascii=False)

print('master', len(out_master), 'repl', len(out_repl), 'skipped_repl', len(skipped_repl))
# spot check against known example: 편성111 M18 -> should be car 1711 tm2
check = [x for x in out_master if x['formation'] == '111' and x['location'] and x['location'].startswith('111-1711-')]
print('check 편성111 car1711:', check)
# cross-check with repl raw sample RP-0001: 편성111 차호1711 위치2 -> matches which master serial?
print('sample repl:', out_repl[0])
# unique cars per formation in master
from collections import defaultdict
cars_by_formation = defaultdict(set)
for x in out_master:
    if x['location']:
        f_, c_, _ = x['location'].split('-')
        cars_by_formation[f_].add(c_)
for k in sorted(cars_by_formation):
    print(k, sorted(cars_by_formation[k]))
