"""Replay using September 1888 American Ephemeris table images with Raman's later appendix.
RA is in hours, declination in degrees. A negative degree signs the entire DMS value.
The obliquity of date is a declared modern coordinate reduction, held fixed over the day.
"""
import json
import math
import swisseph as swe

TABLES = {
    'MoonHourly': (((6,55,47.06),(21,31,5.0)),((6,57,58.86),(21,30,42.4))),
    'MoonNoons': (((6,31,44.97),(21,28,9.5)),((7,24,28.57),(21,17,40.4))),
    'VenusNoons': (((13,40,55.07),(-9,56,8.0)),((13,45,32.69),(-10,24,57.0))),
    'SaturnNoons': (((9,18,29.22),(16,30,50.9)),((9,18,52.90),(16,29,11.6))),
}
def dms(v):
    return math.copysign(abs(v[0])+v[1]/60+v[2]/3600,v[0])

def replay():
    jd=swe.julday(1888,9,28,23.6,swe.GREG_CAL)
    epsilon=swe.calc_ut(jd,swe.ECL_NUT,swe.FLG_MOSEPH)[0][0]
    e=math.radians(epsilon)
    offset=(1888-397)*(50+1/3)/3600
    out={}
    for name,points in TABLES.items():
        edges=[]
        for ra,dec in points:
            a=math.radians(15*dms(ra))
            dec=math.radians(dms(dec))
            edges.append(math.degrees(math.atan2(math.sin(a)*math.cos(e)+math.tan(dec)*math.sin(e), math.cos(a)))%360)
        frac=0.6 if name=='MoonHourly' else 11.6/24
        lam=edges[0]+(edges[1]-edges[0])*frac-offset
        entry={'RA_Dec_endpoints':points,'obliquityDeg':epsilon,'weight':frac,
               'tropicalEdgesDeg':edges,'siderealDeg':lam,'d9AriesZero':int(lam*9/30)%12}
        if name.startswith('Moon'):
            entry['angularYears']=(280/3-lam)*1.2
            entry['shortfallParts']=(13+50/360-entry['angularYears'])*360
        out[name]=entry
    return out

if __name__=='__main__':
    print(json.dumps(replay(),indent=2))

