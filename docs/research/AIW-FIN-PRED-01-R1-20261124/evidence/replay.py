"""Independent research replay. Run with pyswisseph, using Swiss Ephemeris 2.10.03.
Reads no historical outcomes or baseline fixture. Prints JSON to standard output.
Sign indices below start with Aries=0. Conventional Y/M/D use 360/30 parts.
"""
import json
import math
from itertools import combinations
import swisseph as swe

SIGNS = 'Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces'.split()
ORDER = 'Ketu Venus Sun Moon Mars Rahu Jupiter Saturn Mercury'.split()
YEARS = dict(zip(ORDER, (7,20,6,10,7,18,16,19,17)))
OWNERS = 'Mars Venus Mercury Moon Sun Mercury Venus Mars Jupiter Saturn Saturn Jupiter'.split()
NAMES = 'Sun Moon Mercury Venus Mars Jupiter Saturn Rahu Ketu Asc'.split()
ASPECTS = {p: {7} for p in NAMES[:7]}
ASPECTS.update(Mars={4,7,8}, Jupiter={5,7,9}, Saturn={3,7,10})
# Read directly from the fixed-sign plates, independent of the prose.
PLATES = {
    '38': [6,9,6,7,5,1,5,11,5,5],
    '40': [7,7,7,6,7,3,6,10,4,6],
    '41': [9,10,9,10,9,7,8,7,1,8],
    '44': [5,2,6,6,7,7,3,3,9,4],
}
D9_PRINT = [1,0,8,7,9,6,11,4,10,8]

def house(source, target):
    return 1+(target-source)%12

def geometry(vector):
    s=dict(zip(NAMES,vector))
    wealth=(s['Asc']+1)%12
    owner=OWNERS[wealth]
    def aspectors(target):
        return [p for p,places in ASPECTS.items() if house(s[p],target) in places]
    routes={'A':[owner],'B':aspectors(wealth),
            'C':[p for p in ORDER if s[p]==wealth],
            'D':aspectors(s[owner]),
            'E':[p for p in ORDER if p!=owner and s[p]==s[owner]],
            'F':[OWNERS[(s['Moon']+1)%12]]}
    return {'signs':s,'routes':routes,
            'eligible':[p for p in ORDER if any(p in g for g in routes.values())]}

def positions(jd):
    ids = list(range(7))+[swe.MEAN_NODE]
    flags=swe.FLG_MOSEPH|swe.FLG_SIDEREAL
    bodies={}
    for p,num in zip(NAMES,ids):
        xx,returned=swe.calc_ut(jd,num,flags)
        assert returned & swe.FLG_MOSEPH and returned & swe.FLG_SIDEREAL
        bodies[p]=xx[0]
    bodies['Ketu']=(bodies['Rahu']+180)%360
    bodies['Asc']=swe.houses_ex(jd,26.5,74.75,b'W',swe.FLG_SIDEREAL)[1][0]
    return bodies

def cross(fn,angle,a,b):
    assert fn(a)<=angle<=fn(b)
    for _ in range(55):
        m=(a+b)/2
        if fn(m)<angle:a=m
        else:b=m
    return (a+b)/2

def age(parts):
    y,rest=divmod(parts,360)
    m,d=divmod(rest,30)
    return [y,m,d]

def quarters(parent,start):
    i=ORDER.index(parent)
    ages={}
    for p in ORDER[i:]+ORDER[:i]:
        end=start+YEARS[parent]*YEARS[p]*3
        ages[p]={'parts':[start,end],'age':[age(start),age(end)]}
        start=end
    return ages

def replay():
    swe.set_sid_mode(swe.SIDM_RAMAN)
    flags=swe.FLG_MOSEPH
    geo={k:geometry(v) for k,v in PLATES.items()}
    birth=swe.julday(1888,9,29,4+35/60-74.75/15,swe.GREG_CAL)
    tests={}
    for day,jd in [(29,birth),(30,birth+1)]:
        lon=positions(jd)
        rasi={p:SIGNS[int(v//30)] for p,v in lon.items()}
        d9={p:SIGNS[int(v*9//30)%12] for p,v in lon.items()}
        tests[day]={'jdUT':jd,'longitude':lon,'rasi':rasi,'d9':d9,
                    'rasiMismatch':[p for i,p in enumerate(NAMES) if rasi[p]!=SIGNS[PLATES['44'][i]]],
                    'd9Mismatch':[p for i,p in enumerate(NAMES) if d9[p]!=SIGNS[D9_PRINT[i]]],
                    'birthStarIndex1':1+int(lon['Moon']/(40/3))}
    def native(t):return swe.calc_ut(t,swe.MOON,flags|swe.FLG_SIDEREAL)[0][0]
    offset=(1888-397)*(50+1/3)/3600
    def manual(p,t,linear=False):
        def trop(j):return swe.calc_ut(j,p,flags)[0][0]
        if not linear:return (trop(t)-offset)%360
        j=math.floor(t)
        change=(trop(j+1)-trop(j)+180)%360-180
        return (trop(j)+(t-j)*change-offset)%360
    clock={}
    printed=13+50/360
    for key,fn in [('modern',native),('manualAtBirth',lambda t:manual(swe.MOON,t)),
                   ('manualNoonLinear',lambda t:manual(swe.MOON,t,True))]:
        lo=cross(fn,80,birth-1,birth);hi=cross(fn,280/3,birth,birth+2)
        angle=16*(280/3-fn(birth))/(40/3)
        time=16*(hi-birth)/(hi-lo)
        clock[key]={'lambda':fn(birth),'crossingJD':[lo,hi],'angularYears':angle,'timeYears':time,
                    'shortfallPartsAngle':360*(printed-angle),'shortfallPartsTime':360*(printed-time)}
    alternate={p:[manual(num,birth),manual(num,birth,True)] for p,num in [('Venus',swe.VENUS),('Saturn',swe.SATURN)]}
    intervals={k:quarters(parent,start) for k,parent,start in [
        ('44','Ketu',49*360+50),('38','Saturn',38*360+2*30+14),
        ('40','Ketu',35*360+2*30+18)]}
    rows={}
    chart=geo['44']
    star=tests[29]['birthStarIndex1']
    starRulers={ORDER[(star-1+k-1)%9]:k for k in (3,5,7)}
    for p in ORDER:
        sign=chart['signs'][p]
        dist=house(chart['signs']['Ketu'],sign)
        rows[p]={'channels':[k for k,g in chart['routes'].items() if p in g],
                 'parentDirect': 'Ketu' in chart['eligible'],
                 'owned':[house(chart['signs']['Asc'],i) for i,v in enumerate(OWNERS) if v==p],
                 'occupies':house(chart['signs']['Asc'],sign),'fromParent':dist,
                 'joined':[q for q in ORDER if q!=p and chart['signs'][q]==sign],
                 'incomingFull':[q for q,g in ASPECTS.items() if house(chart['signs'][q],sign) in g],
                 'HPA13starOrdinal':starRulers.get(p),'HPA14adverseGeometry':dist in (2,6,8,12),
                 'age':intervals['44'][p]['age']}
    def adjacent(places):
        return [a+'/'+b for a,b in combinations(NAMES[:-1],2) if (places[a]-places[b])%12 in (1,11)]
    modernD9={p:SIGNS.index(s) for p,s in tests[29]['d9'].items()}
    return dict(engine=swe.version,binding=swe.__version__,charts=geo,dateProfiles=tests,
                clocks=clock,annualOffset=offset,alternateD9Input=alternate,
                printedD9=dict(zip(NAMES,map(SIGNS.__getitem__,D9_PRINT))),
                d9Adjacent={'printed':adjacent(dict(zip(NAMES,D9_PRINT))),'modern':adjacent(modernD9)},
                subperiods=rows,intervals=intervals,
                chart41MercuryMajor=[age(24*360+152),age(41*360+152)])
if __name__=='__main__':
    print(json.dumps(replay(),ensure_ascii=False,indent=2))

