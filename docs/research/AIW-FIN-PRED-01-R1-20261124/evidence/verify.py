from pathlib import Path
import hashlib, json, os, subprocess, sys
from jsonschema_rs import Draft202012Validator, meta
root = Path(__file__).resolve().parents[1]
baseline = root.parent / 'AIW_FIN_PRED_01_20261121'
def jread(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def report(name, value):
    if not value:
        raise AssertionError(name)
    checks.append(name)
def rerun(name):
    cmd = [sys.executable, '-X', 'utf8', str(root / 'evidence' / name)]
    return json.loads(subprocess.check_output(cmd, encoding='utf-8'))
checks = []
prefix = 'AIW_FIN_PRED_01_R1_'
names = 'EXECUTIVE_DECISION RAMAN_SOURCE_ACQUISITION BIRTH_INPUT_AUDIT DASHA_BALANCE_RECONCILIATION NAVAMSA_DISCREPANCY VENUS_SUBPERIOD_SELECTION NINE_BHUKTI_COMPARISON INDEPENDENT_CHART_CONTROLS SOURCE_RULE_REGISTER BPHS_COMMENTARY_REVIEW MACHINE_FIXTURES IMPLEMENTATION_READINESS FINAL_DECISION'.split()
expected = {prefix+n+('.json' if n=='MACHINE_FIXTURES' else '.md') for n in names}
report('Thirteen requested root deliverables, exact names', expected=={p.name for p in root.iterdir() if p.is_file()})
j = jread(root / (prefix+'MACHINE_FIXTURES.json'))
old = jread(baseline / 'AIW_FIN_PRED_01_TEST_FIXTURES.json')
hashes = jread(root / 'evidence' / 'baseline.json')
report('Twelve original files unchanged', len(hashes)==12 and all(hashlib.sha256((baseline / n).read_bytes()).hexdigest()==r['localSHA256'].lower() for n,r in hashes.items()))
report('Original typed judgment schema preserved verbatim', j['schema']['$defs']['baselineJudgment']==old['outputRecordSchema'])
meta.validate(j['schema'])
validator = Draft202012Validator(j['schema'])
for item in j['schemaExamples']:
    validator.validate(item)
report('Draft 2020-12 metaschema and ten example records validated', len(j['schemaExamples'])==10)
flags = ('executionAllowed','financiallyValidated','marketDirectionAssigned')
report('Three flags false on packet and all ten records', all(r[k] is False for r in [j]+[r['judgment'] for r in j['schemaExamples']] for k in flags))
replay = rerun('replay.py')
report('Full independent chart and timing replay matches fixture', replay==j['modernAndManualReplays'])
report('1888 table coordinate reduction and balances match fixture',rerun('almanac.py')==j['almanacReplay'])
ages = replay['intervals']['44']
report('Nine contiguous half-open periods spanning seven 360-part years', len(ages)==9 and sum(v['parts'][1]-v['parts'][0] for v in ages.values())==2520 and all(a['parts'][1]==b['parts'][0] for a,b in zip(ages.values(),list(ages.values())[1:])))
report('Boundary passes from Venus to Sun on part 18257', all(next(k for k,v in ages.items() if v['parts'][0]<=int(n)<v['parts'][1])==r for n,r in j['tests']['knownAgeParts'].items()))
report('Five eligible children; three general-difficulty candidates',set(j['directEligible'])==set(replay['charts']['44']['eligible'])=={'Mercury','Venus','Moon','Saturn','Sun'} and set(j['starAdversity'])=={'Mercury','Venus','Moon'} and j['uniqueDebtSelector'] is None)
report('Rasi and D9 differences checked by date',replay['dateProfiles']['29']['rasiMismatch']==[] and replay['dateProfiles']['30']['rasiMismatch']==['Moon'] and set(replay['dateProfiles']['29']['d9Mismatch'])=={'Venus','Saturn'})
controls=list(j['controls'].values())
report('Controls counted directly against author lists',len(controls)==3 and sum(r['directSetMatches'] for r in controls)==1 and sum(r['directSetMatches'] or r.get('proxySetMatches',False) for r in controls)==2 and all((r['authorChild'] or r['authorParent']) in r['plateAndReplay']['eligible'] for r in controls) and all(not r['uniqueEventSelected'] for r in controls))
witness=j['schemaExamples'][-1]['judgment']
report('Retrospective baseline record preserved except normalized citations',all(witness[k]==v for k,v in old['exampleOutputRecord'].items() if k!='sourceRefs'))
report('No civil event or period timestamps asserted',all(all(x['judgment']['period'][k] is None for k in ('eventUTC','utcStart','utcEnd')) for x in j['schemaExamples']))
import re
links=[]
for p in root.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8-sig')):
        if '://' not in target and not target.startswith('#'):
            links.append((p.parent / target).is_file())
report('All Markdown local file links resolve',bool(links) and all(links))
print(json.dumps({'passed':checks,'schemaValidator':'jsonschema-rs 0.63.1 / Draft 2020-12'},indent=2))
