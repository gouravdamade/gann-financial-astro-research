"""Offline research arithmetic only. No price or product modules. Prints JSON."""
import datetime as dt
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path
import swisseph as swe

packet = Path(__file__).resolve().parent
root = packet / "inputs"
if not all((root / name).is_file() for name in (
    "AIW_P0_MARS_12_CELL_REPRODUCTION.json",
    "AIW_P1_REAL_CHART_FIXTURES.json",
)):
    # Optional local-workspace fallback for the original accepted output layout.
    root = packet.parent / "AIW_P1_20261121"
files = [root / name for name in ("AIW_P0_MARS_12_CELL_REPRODUCTION.json", "AIW_P1_REAL_CHART_FIXTURES.json")]
p, b = [json.loads(f.read_bytes()) for f in files]
order = list(b["planets"])
sides = ["USD", "JPY"]
st = "2025-05-31T17:00:00Z"
def instant(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
def bv(c, planet, sign):
    return sum(1 + (sign - ref) % 12 in mask for ref, mask in
               zip(p["chartRecomputation"][c]["refs"], p["placesInclusive"][planet], strict=True))
def series(planet):
    v = b["planets"][planet]
    return [v["initial"]] + [x["sample"] for x in v["transitions"]]
rows = {k:series(k) for k in order}
for k, samples in rows.items():
    for s in samples:
        for c in sides:
            assert s["sides"][c]["status"] == "VALID"
            assert bv(c,k,s["transitSign"]) == s["sides"][c]["favorableCount"]
def states(t):
    signs = [next(s for s in reversed(rows[k]) if s["timestampUtc"] <= t)["transitSign"] for k in order]
    return {c:[bv(c,k,z) for k,z in zip(order, signs)] for c in sides}
def vector(lons,h=1):
    a = [math.radians(x*h) for x in lons]
    return [statistics.mean(f(t) for t in a) for f in (math.cos,math.sin)]
def dot(x,y):
    return sum(a*b for a,b in zip(x,y))
bodies = [swe.SUN,swe.MOON,swe.MARS,swe.MERCURY,swe.JUPITER,swe.VENUS,swe.SATURN,swe.URANUS,swe.NEPTUNE,swe.PLUTO]
def geometry(t):
    d=instant(t)
    jd=swe.julday(d.year,d.month,d.day,d.hour+d.minute/60+d.second/3600)
    flags=swe.FLG_MOSEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    vals=[swe.calc_ut(jd,h,flags) for h in bodies]
    assert all(ret & swe.FLG_MOSEPH for _,ret in vals)
    lon=[v[0] for v,_ in vals]
    T=vector(lon)
    nat={c:p["chartRecomputation"][c]["degrees"][:7] for c in sides}
    g={c:dot(T,vector(nat[c])) for c in sides}
    for c in sides:
        assert abs(g[c]-statistics.mean(math.cos(math.radians(x-y)) for x in lon for y in nat[c])) < 1e-12
    return dict(lon=lon,speed=[v[3] for v,_ in vals],T=T,R1=math.hypot(*T),R2=math.hypot(*vector(lon,2)),G=g,returnedFlags=[i for _,i in vals])
swe.set_sid_mode(swe.SIDM_RAMAN)
g=geometry(st)
assert all(int(g["lon"][i]//30)==next(s for s in reversed(rows[k]) if s["timestampUtc"]<=st)["transitSign"] for i,k in enumerate(order))
trans=[t for v in b["planets"].values() for t in v["transitions"]]
cuts=sorted({b["range"]["startInclusiveUtc"],b["range"]["endExclusiveUtc"]}|{t[k] for t in trans for k in ("firstNewSignWholeSecondUtc","lastOldSignWholeSecondUtc")})
amb={(t["lastOldSignWholeSecondUtc"],t["firstNewSignWholeSecondUtc"]) for t in trans}
tot=Counter()
for a,z in zip(cuts,cuts[1:]):
    dur=int((instant(z)-instant(a)).total_seconds())
    v=states(a)
    d=[u-j for u,j in zip(*[v[c] for c in sides])]
    label=("boundary" if (a,z) in amb else "mixed" if min(d)<0<max(d) else "tie" if max(d)==min(d)==0 else "strictUSD" if min(d)>0 else "strictJPY" if max(d)<0 else "weakUSD" if min(d)>=0 else "weakJPY")
    tot[label]+=dur
assert sum(tot.values()) == 365*86400
daily=[]
for n in range(365):
    t=(instant(b["range"]["startInclusiveUtc"])+dt.timedelta(days=n,hours=17)).strftime("%Y-%m-%dT%H:%M:%SZ")
    if any(aa<=t<zz for aa,zz in amb): continue
    v=states(t)
    gg=geometry(t)["G"]
    daily.append((sum(v["USD"])-sum(v["JPY"]),gg["USD"]-gg["JPY"]))
print(json.dumps(dict(hashes=[hashlib.sha256(f.read_bytes()).hexdigest() for f in files],order=order,utc=st,marks=states(st),aries={c:[bv(c,k,0) for k in order] for c in sides},geo=g,yearSeconds=dict(tot),dailyN=len(daily),dailyGeometryMarkCorrelation=statistics.correlation(*zip(*daily)), transitions=len(trans),sweVersion=swe.version),indent=2))
