"""Build a reviewable cross-reference, not a trading implementation or source summary.

Source-specific dispositions are carried verbatim from the reviewed findings; routing
combines explicit conversation destinations with observable mechanism tags. Generated
routes are checked in the final design review, and every source row retains its own
future fixture ID. No source claim is promoted to empirical evidence by this file.
"""
from pathlib import Path
import json,re,collections

ROOT=Path('/workspace/planning/trading-model')
OUT=ROOT/'traceability';OUT.mkdir(exist_ok=True)
components={}
for p in sorted((ROOT/'components').glob('*.md')):
    for line_no,line in enumerate(p.read_text().splitlines(),1):
        m=re.match(r'## ([FCMOLXGPRV]\d{2}) — (.*)',line)
        if m:components[m[1]]={'path':str(p),'line':line_no,'title':m[2]}

def clink(cid):
    v=components[cid];return f"[{cid}]({v['path']}:{v['line']})"
def linkset(ids):return ', '.join(clink(x) for x in sorted(set(ids)))

prefix={
'JSS':'C01 C06 L04','JTR':'C01 C02 C03 L01 L02','JXA':'C01 C03 L01 L02','JFN':'C01 C03 V07',
'INV':'F01 F06 F07','IMG':'O09 O10 O11 X06','AM1':'C07 C08 L05','VP2':'M04 L05 C07',
'TP3':'M06 L07 C07','VX4':'C15 C16 G02','DM5':'M09 M10 R01 R05','DM6':'M09 R02 R03 R05',
'DM7':'M09 R05 R06','FP8':'M13 R08 L09','FP9':'M13 R07 R09 R10','VW10':'M07 M01 L11',
'CD1':'C07 C22 L17','CD2':'P02 P03 P08','CD3':'P01 P03 P08','DEN':'V01 V03 V07',
'EMO':'V03 P04 P08','GXF':'O05 O09 O13 C15','MAV':'M04 M06 C07 L05 L07',
'MAT':'C07 G04 G05 V01','RVP':'M04 C07 L05','RDL':'M05 M11 R15 P03',
'ALM':'C07 C08 L05','WIC':'R01 R11 R17 C18','YMA':'R02 R10 R14 L05',
'RFE':'L19 L17 R05 P05','OFM':'L19 R12 R13 R19','K10':'L05 P02 P03 V07',
'K18':'M05 L19 P03 P04','F23':'C07 L19 P03 V07','CCS':'C08 L05 L19 R12',
'ALS':'L17 P03 P04 P08','NYA':'R03 R17 P03 P11','SRE':'R14 R17 P04',
'TBR':'L05 L06 C19 R17','OBT':'M02 L19 R02 R13','AUT':'V01 V03 P08 P09',
'MVF':'C18 L19 M13','OSF':'M08 L08 L10 R20',
}
explicit={}
def routes(block):
    for l in block.strip().splitlines():
        k,v=l.split(':',1);explicit[k.strip()]=v.split()
routes('''
DTM-A01: F04 F11 G01 P01 P07 P08 V07
DTM-A02: C01 C03 L01 L02 P05 V07
DTM-A03: C09 C10 C11 C12 C13 C14 C23 C24 G02 G04 G05
DTM-A04: C05 C06 L05 L16 L17 L18 G07 G08
DTM-A05: O01 O03 O04 O06 O07 O08 O09 O10 O13
DTM-A06: X02 X03 X04 X05 X06 L15
DTM-A07: F05 F06 V06 R11 R12 R14
DTM-A08: P08 P09 P11 V04
DTM-A09: M02 M11 C17 X08
DTM-A10: C18 C19 P06 G09
DTM-A11: M04 M05 M07 M12 L05 L06 L11 L12 L17 L18 G08
DTM-A12: M09 M10 R02 R05 R14
DTM-A13: C07 R11 R12 R15
DTM-A14: X05 G01 R19
DTM-A15: V01 P05 G05 G06
DTM-A16: P01 P02 P03 P04 P05 P08 P09
DTM-A17: V02 V03 V04 V06 V07
DTM-A18: X05 L15 G08 V01
JCV-U01: C05 C06 M04 M05 L04 L05 L06 V07
JCV-U02: C05 C06 C10 M09 L05 L06 G08
JCV-U03: C05 C19 M09 P05 R06 F12 V08
JCV-U04: M09 R05 R06
JCV-U05: G01 G08 V03 V04 V07
JCV-U06: R06 P05 V08
JCV-A01: C01 C03 M05 L05 L06
JCV-A02: M11 R11 R12 R15 P05 V07
JCV-A03: F05 M09 P05 R06 V02
JCV-A04: C01 C05 C06 V03
JCV-A05: C09 C10 C11 C12 C13 C14 C17 X07 G02
JCV-A06: M09 M10 R01 R05 R11 G08
JCV-A07: R02 R06 P05 G08
JCV-A08: C19 M11 G08 P03 R19
JCV-A09: R06 P05 V04 V08
JCV-A10: V03 V04 P11
CEX-01: V01 V07 G01 C22
CEX-02: C01 C03 V01 V03 P05
CEX-03: C05 C06 C21 L04
CEX-04: C03 C07 C20 C21 G01
CEX-05: F07 M01 M02 M13 C18 G09
CEX-06: C09 C10 C11 C12 C13 C14 C15 C19 C23 C24 G02
CEX-07: M03 X01 X07
CEX-08: P03 P08 P09 P10
CEX-09: O09 O13 C07 C15
CEX-10: F01 F07 O01 O06 O21 V08
CEX-11: O04 O05 O18 O19 C16 M12
CEX-12: X09 P12
CEX-13: X02 X05 X06 L15
CEX-14: L16 L18 G08 V07
CEX-15: G10 V03 V05 P06
CEX-16: F02 X02 X03 X04
CEX-17: O06 O07 O08 O15 O16 O20
CEX-18: O09 O10 O11 X06 V01
CEX-19: O12 O13 O14 O17 X06
CEX-20: F12 O17 V08
CEX-21: O05 O09 O17 M07 L11 L14
CEX-22: F01 F06 F12 V08
CEX-23: F02 F07 O01 O21
CEX-24: F04 F05 F07 O03 V06
CEX-25: X09 O19 C16 C17 X08
CEX-26: F01 F03 F08 V06
CEX-27: V01 V03
CRL-01: M04 M05 L05 L06 V07
CRL-02: C05 C06 M09 R06 P05
CRL-03: V04 V07 L18 G08
CRL-04: C01 C05 L12 V03
CRL-05: C15 C16 O04 O19 L01
CRL-06: M04 M05 M07 M08 M12 O18 L05 L06 L11
CRL-07: R02 R05 R11 R12 R14 R15 R19
CRL-08: C07 C20 R01 R14 R21 V03
CRL-09: G10 V05 P06
CRL-10: C17 X08 X10
CRL-11: C18 L16 L18 G08
CRL-12: R02 R05 R10 R14 L05
CRL-13: M05 M11 R02 R15 R21
CRL-14: R01 R02 R05 R06 R10 R11 R12 R15
CRL-15: M02 M10 R01 R03 V01
CRL-16: R14 R22 V01
CRL-17: G01 G03 G09 G10 V05
CRL-18: M13 C18 L19 G09
CRL-19: M11 L16 L17 L18 G08
CRL-20: V01 V03
DRF-U01: O05 O09 O21 G05 G06 L13
DRF-U02: O06 O07
DRF-U03: O11 O22 L13 L16 G08
DRF-U04: O02 O04 O05 C15
DRF-U05: O10 O11 O13 O17 X06
DRF-U06: O06 O07 O08 G10
DRF-U07: C03 C22 L01 L13 G08
DRF-U08: C05 C06 L16 L17 G03
DRF-U09: X02 X05 L15
DRF-U10: V03 V07 L18 G08
DRF-U11: C22 G08 R19
DRF-U12: V01 V07 V04 G01
DRF-A01: O06 O08 O09 O10
DRF-A02: F05 O03 O20 M02
DRF-A03: F01 F07 V08
DRF-A04: O06 O07 O08 O20
DRF-A05: O22 G05 C19
DRF-A06: F02 O02 O05 O06
DRF-A07: O09 O11 F10 V01
DRF-A08: O11 O13 O14 L13 L14
DRF-A09: O22 G04 G05 L13
DRF-A10: G04 G05 G06 G07 G08
DRF-A11: X02 O21
DRF-A12: C09 C10 C11 C12 C13 C14 C15 C16 G02
DRF-A13: O04 O05 O10 C15
DRF-A14: O21 G09 V05
DRF-A15: O10 O12 O13 O22 R21
DRF-A16: O10 O11 O13 O17 R22
DRF-A17: O06 O15 O16 O18 O20
DRF-A18: O07 O08 O22 V01
DRF-A19: O11 O12 O13 L13 G08
DRF-A20: C22 L01 L05 L13 G01
DRF-A21: G01 G03 G08
DRF-A22: L18 G08 V03 V07
DRF-A23: X05 L15
DRF-A24: C22 G08 R19
DRF-A25: V01 V03 V07
DRF-A26: F11 V06 V07
DRF-A27: V02 V03 V04
DRF-A28: V01 V06 V07
DRF-A29: G01 C22 V07
''')

# Mechanism tags add distinct owners to compound rows. Causal/source-row tests
# remain mandatory even when a tag does not apply.
tags=[
(r'cvd|cumulative.?delta|cumulative.?volume','M01 M02 M03 R10'),
(r'delta.?profile|signed.?profile|weekly.?delta','M05 L06'),
(r'volume.?profile|\bvp\b|minor.?node|\bhvn\b|\blvn\b|shel(f|ves)|ledge|\bpoc\b','M04 L05'),
(r'profile.?anchor|dealing.?range|yearly.?composite|leg.?profile','M04 M05 L05 L06'),
(r'\btpo\b|single.?print|poor.?extreme|initial.?balance','M06 L07'),
(r'vwap|anchored.?dispersion','M07 L11'),
(r'\bsmt\b|divergence','M03 X07'),
(r'06.?00.?09|6.?9|single.?break|double.?break|quadrant|25.?50.?75','C01 C02 C03 L01 L02'),
(r'p.?zone|adaptive.?range|learned.?range|window.?discovery','C05 C06 L04'),
(r'remaining.?range|remaining.?session|runway|target.?room','C19 G05 G06'),
(r'volatility|variance|\bgk\b|yang.?zhang|\bhar\b','C09 C10 C11 C12 C13 G02'),
(r'parkinson','C23'),(r'garch|\barch\b','C24'),
(r'\bvix\b|\bvx\b|vvix|vxn','C16'),
(r'skew|surface|implied|\biv\b','O02 O04 C15'),
(r'gamma|gex|vanna|vega|charm|volga|kg1','O05 O09 O21'),
(r'open.?interest|\boi\b|next.?report','O06 O07 O08'),
(r'options?.?flow|premium|multi.?leg|sweep.?trade','O03 O15 O16 O20'),
(r'king|gatekeeper|heatmap|whipsaw|rainbow|rug.?pull|air.?pocket|trinity','O11 O12 O13 X06'),
(r'ndx|ndxp|qqq','X02 X03'),(r'spx|spxw|spy','X02 X04'),
(r'no.?local.?touch|without.?local|cross.?asset|source.?event|transmission','X05 L15'),
(r'joint|multi.?chain|multi.?asset','X06'),
(r'copper|silver|nikkei|nkd|usdjpy|usdcny|\bhg\b|\bsi\b|\brty\b|\bym\b','X09'),
(r'earnings|constituent','X08 C17'),(r'macro|cftc|cot\b|shfe|slv|vintage','C17 X10'),
(r'absorption|absorbed|high.?effort|stopping.?volume','M10 R02 R04'),
(r'exhaust|quiet.?failure|diminish|tape.?slows','R03 R13'),
(r'refill|reload|refresh|replenish|resilien','M09 R05'),
(r'iceberg|spoof|layering|off.?touch|mbp.?10|\bmbo\b|remote.?depth','R06 P05'),
(r'footprint|diagonal|stacked.?imbalance','M13 R08'),
(r'poc.?flip|mode.?relocat','R09'),
(r'no.?retest|break.?retest|failed.?retest|failed.?traverse','R11'),
(r'squeeze|origin.?of.?the.?move|\bofm\b','L19 R12'),
(r'protected|control.?switch|rewarded.?side','M11 R15'),
(r'second.?retest|repeated.?touch|retest.?count','L17 R17'),
(r'order.?block|rejection.?block','L10 R18'),
(r'cisd|fvg|pivot|fractal|sweep','M08 L08 L09 R20'),
(r'wait|confirm.*late|delay.*entry|remaining.*payoff','G07 R19'),
(r'rank|competing|select.*level|candidate.*density|nearer|deeper','L18 G08'),
(r'mixture|\bmoe\b|softmax|ensemble|gate','G01 G03 G09'),
(r'calibrat','G03'),(r'retrain|adaptation|decay|drift','G10 V05'),
(r'partial|pyramid|sizing|two.?contracts|multi.?account|cop(y|ied|ier)','P01 P08 P11'),
(r're.?entr|retry|re.?enter','P04'),
(r'trail|breakeven|\bbe\b|target.?exten|giveback','P03'),
(r'stop|risk.?reward|\brr\b|bracket','P02 P08'),
(r'fill|slippage|passive|queue|marketable|stop.?limit','P05 P06'),
(r'daily.?loss|daily.?stop|loss.?budget','P08'),
(r'prop|funded|payout|tradeify|lucid|consistency|account.?floor','P09 P11'),
(r'dst|time.?zone|midnight|clock|holiday|boundary','F03 P10'),
(r'roll|settlement|expiry.?clock|multiplier|sentinel','F02 F08 M12'),
(r'lookahead|repaint|backdat|future|as.?of|receipt|publication','F04 V06'),
(r'leak|oos|out.?of.?sample|purge|embargo|train.*test','V02 V03'),
(r'placebo|selected.*example|hindsight|screenshot|drawing|unverified.*result','V01 V03 V07'),
]

# Manual domain routing after the second semantic review. Each source case retains
# all clause-level assertions; these are destinations, not independent votes.
source_prefix_refined={
'JSS':'C01 C06 L04 V01', 'JTR':'C01 C02 C03 L01 L02 V01',
'JXA':'C01 C02 C03 L01 L02 V01', 'JFN':'C01 C03 L01 L02 V07',
'INV':'F01 F02 F04 F05 F06 F07 V08', 'IMG':'O09 O10 O11 O12 O13 X06 V01',
'AM1':'M04 M06 C07 C08 L05 L07', 'VP2':'M04 C07 L05 L17',
'TP3':'M06 C07 L07', 'VX4':'C15 C16 G02 L04',
'DM5':'M01 M09 M10 R01 R02 R03 R05', 'DM6':'M09 M10 R02 R03 R05 R06',
'DM7':'M09 R02 R05 R06 P05', 'FP8':'M13 L09 R02 R07 R08',
'FP9':'M01 M03 M13 R07 R09 R10', 'VW10':'M07 M01 L11 C07',
'CD1':'C07 C22 L17 R19 P04 V03', 'CD2':'P02 P03 P04 P08 P09 V04',
'CD3':'C18 R01 R02 R03 R05 R07 R10 P01 P03 P08',
'DEN':'F05 M01 M09 M13 R06 V01 V03 V07', 'EMO':'P01 P04 P08 V03 V05',
'GXF':'O05 O09 O13 O21 C15 L13 L14 V01',
'MAV':'M04 M06 C07 C08 L05 L07 L17', 'MAT':'M04 C07 C08 L05 G04 G05 V01',
'RVP':'M04 C07 C08 L05 L16 L17', 'RDL':'M05 M11 L06 L19 R15 R16 P03',
'ALM':'C07 C08 L05 L17 R11', 'WIC':'C18 R01 R02 R03 R11 R14 R15 R17',
'YMA':'M03 M10 L05 R02 R10 R14 R21', 'RFE':'M09 L19 L17 R05 R14 R15 P05 V01 V02',
'OFM':'M11 L19 R03 R05 R12 R13 R19 P02 P03 P04',
'K10':'M04 C07 L05 L19 R02 R11 P02 P03 V07',
'K18':'M05 L06 L19 R14 R15 P03 P04 V07',
'F23':'C07 C08 L05 L19 R02 R11 P03 V07',
'CCS':'M04 C08 L05 L19 R05 R12 R15 P03',
'ALS':'C19 L17 R19 P03 P04 P08 V07',
'NYA':'R03 R13 R17 P03 P04 P11 V07',
'SRE':'R14 R17 P04 P05 V01', 'TBR':'M05 L05 L06 C19 R15 R17 P04',
'OBT':'M02 M11 L19 R02 R03 R13 P04', 'AUT':'V01 V03 P04 P08 P09 P11',
'MVF':'M02 M04 M05 M13 C18 L16 L19 G01 G09',
'OSF':'F09 M08 L08 L09 L10 R18 R20 V06'}
pin_domains={}
def pin_map(nums,ids):
    for n in nums:pin_domains[n]=ids.split()
pin_map([1,2,12,21,24,44,75], 'C01 C02 C03 C05 C21 L01 L02 V03')
pin_map([3,4], 'C01 C02 C03 C04 C17 C21 L01 L02 L03')
pin_map([5], 'L12 L16 L18 G08 V03')
pin_map([6,7,14,16,45,52,55,57,62,63,65,67,68,70,83], 'C01 C06 C09 C19 L01 L02 L04 G03 V03')
pin_map([8,9,17,33], 'C09 C12 C18 C20 R20 G01 G09 V03')
pin_map([10,22,23,35,71], 'M08 C02 L08 L09 L10 R18 R20')
pin_map([11,20,34,50,72,79], 'M03 C18 C20 R20 G01 G09 G10 V03')
pin_map([13,15,25,39,40,41,42,46,47,49,54,61,64,73,74,76,80,81,82], 'M12 C01 C02 C04 C06 C21 L01 L02 L03 L12 G03 V03')
pin_map([18], 'C15 C16 G02 L04 V03')
pin_map([19], 'M08 C01 C06 C20 L04 L09 R20 V03')
pin_map([26,27,28,29,30,43,48,58,59,78], 'C01 C02 C04 C06 C21 M06 L01 L02 L04 L07 G03 V03')
pin_map([31,36,37,56,60], 'C01 C02 C06 M08 L01 L02 L08 R20 G03 V03')
pin_map([32,38,51], 'M08 L08 L10 L12 R20')
pin_map([53], 'F01 V01 V03')
pin_map([66,77], 'M04 M05 M12 O06 C07 L05 L06 L12')
pin_map([69], 'M07 C07 L11 G03 V03')
assert set(pin_domains)==set(range(1,84))
source_extra={
'JTR-02':'M12 L12', 'JTR-03':'C05 F03', 'JTR-04':'C19 P02 P03',
'JTR-06':'C04 C19 L03', 'JTR-07':'M03 X07', 'JTR-08':'C21 P03',
'JTR-09':'C17 C21', 'JTR-10':'C04 F09', 'JTR-11':'M13 R07 R18',
'JTR-12':'C19 G05', 'JTR-13':'C17 C21', 'JTR-14':'C17 P04 P08',
'JTR-15':'P01 P02 P05 P06 P07 P08', 'JTR-16':'L10 R18 P02 P05',
'JTR-17':'L10 R18 P02', 'JTR-18':'V03 V04', 'JTR-19':'G03 V03',
'JTR-20':'M10 M13 R02 R07', 'JTR-21':'M04 M05 C04 L03 L09',
'JTR-22':'M04 M05 C04 L03 L09', 'JTR-23':'C21', 'JTR-24':'R18 P03 P04 P08',
'RDL-06':'R16', 'CRL-06':'L03 L08 L12', 'CEX-04':'C04',
'JCV-U01':'L03', 'DTM-A04':'L03', 'DTM-A11':'L03',
'JXA-05':'M06 L07', 'JXA-06':'C04 C19', 'JXA-08':'M11 L19 R15',
'JXA-09':'M04 M05 L03 L05 L06', 'JXA-13':'C04 C19',
'JXA-15':'M04 M05 M11 L03 L05 L06 L19 R15',
'JXA-16':'M04 M05 M08 L03 L05 L06 L08',
'JXA-19':'C06 L04', 'JXA-20':'M08 L08', 'JXA-22':'C06 L04',
'JXA-23':'M03 X07', 'JFN-04':'C04 L03', 'JFN-08':'M04 M05 L03 L05 L06',
'JFN-10':'C04 L03', 'JFN-07':'C06 L04'}

# Additional clause-specific destinations confirmed against original visual/account findings.
source_prefix_refined['IMG']='O06 O07 O08 O09 O10 O11 O12 O13 X06 L13 L14 V01'
source_prefix_refined['GXF']+=' C16'
source_extra.update({
'JXA-02':'P03 P04 V07', 'JXA-03':'C04 L03 R02 R11 R14',
'JXA-07':'C04 G03 V03', 'JXA-09':'M04 M05 L03 L05 L06 P03 G07',
'JXA-10':'C04 L03 L12 M12 C21', 'JXA-11':'C06 L04 P09 V04',
'JXA-12':'P03 P04 C19 C21', 'JXA-13':'C04 C19 M02 M10 M13 R02 R07',
'JXA-15':'M02 M04 M05 M11 L03 L05 L06 L19 R02 R15',
'JXA-16':'M04 M05 M08 L03 L05 L06 L08 P03',
'JXA-17':'C17 C19 C21 R14 P03', 'JXA-18':'C19 C21 G04 G05',
'JXA-21':'X09 F03 C21', 'JXA-22':'C05 C06 C20 L04 L17 X09',
'JXA-23':'C04 L03 M03 X07', 'JXA-24':'M13 L09 R08 R18 P01 P11',
'JXA-25':'C17 C21 V03', 'JXA-26':'M08 L09 R20 V03',
'JFN-05':'C04 C20 G01', 'JFN-06':'P01 L05 G05',
'JFN-09':'C17 C19 C21 M03 X07', 'JFN-10':'C04 L03 L17 P03 P04 G08',
'JFN-11':'C06 L04', 'JFN-12':'V01 V03',
'RFE-11':'P08 P09 P11 V04', 'RFE-12':'P08 P09 P11 V04',
'RFE-13':'P09 P11 V04', 'RFE-14':'V03 V04',
'K10-06':'P09 P11 V04', 'K18-08':'P09 P11 V04',
'F23-07':'P09 P11 V04', 'NYA-06':'P09 P11 V04'})

# Clause-level supplements from the complete final routing pass.
for _id,_extra in {'AM1-07': 'C20', 'AM1-08': 'C04', 'AM1-09': 'C04 L03 L12', 'AM1-10': 'C20 L18 G08', 'VP2-05': 'M07 L11 R02', 'TP3-04': 'P12', 'TP3-06': 'P02 R11', 'TP3-07': 'L05 R14', 'VX4-03': 'P01 P02 P03', 'VX4-04': 'P02 P08', 'VX4-05': 'C19', 'VX4-07': 'C17', 'VX4-08': 'P08', 'VX4-09': 'C07 R21', 'DM5-04': 'R14', 'DM6-05': 'R04', 'DM7-02': 'R14', 'FP8-02': 'P05 P06', 'FP8-05': 'M04 M07 R01', 'FP9-05': 'R04', 'CD1-02': 'X05 L15', 'CD1-03': 'X05 L15 M06', 'CD3-04': 'C07 L05 L07 R11', 'CD3-05': 'M04 L05 V03', 'DEN-03': 'C09 C20 X10', 'DEN-04': 'C17 X08 X10', 'DEN-05': 'P08 V04', 'GXF-02': 'X02 X03 X04', 'GXF-03': 'X02', 'GXF-05': 'C17 C20', 'GXF-07': 'O11 O23 L13 L14', 'GXF-08': 'O06 C17', 'GXF-13': 'R21 P02 P08', 'MAV-03': 'C04 G04 G05', 'MAV-04': 'C20', 'MAV-05': 'R11', 'MAV-06': 'R11', 'MAV-07': 'C04 C18', 'MAV-08': 'L03 L12 G04', 'MAV-09': 'C04 L01', 'MAV-10': 'C06 L07 L12 M12 V03', 'MAV-12': 'C04 L03 L12', 'MAV-13': 'C09', 'MAT-02': 'M09 M10 C18 R02 R05', 'MAT-03': 'M09 M10 R02 R03 R05 R13', 'MAT-05': 'C20 G01 R21', 'MAT-09': 'R21', 'RVP-03': 'R11', 'RVP-07': 'R11 R21', 'YMA-03': 'M04 M05 L06 R16', 'OFM-08': 'P08 P09 P11 V04', 'OFM-09': 'V01 V02 V03', 'K10-01': 'P09 P11 V04', 'K10-02': 'O21 O22 L13 C19', 'K18-01': 'P09 P11 V04', 'K18-02': 'M04 L05 C07 C08 O21', 'K18-05': 'P01 P08', 'F23-01': 'P09 P11 V04', 'F23-02': 'M13 R08 R15 L12', 'F23-04': 'P02 R15', 'F23-05': 'P04 P08', 'F23-06': 'P09 P11', 'CCS-01': 'P11', 'CCS-03': 'M05 L06', 'CCS-04': 'O21 R21 P09 P11', 'CCS-05': 'P02 P04', 'CCS-06': 'R16', 'SRE-06': 'P08 P09 V04', 'TBR-05': 'P02 G06', 'TBR-06': 'P11 P12', 'TBR-07': 'F04 V06 R22', 'OBT-02': 'M13 R07 R08', 'OBT-03': 'R12', 'OBT-04': 'M04 M07 L05 L11 R16', 'OBT-05': 'M04 L05 R16', 'OBT-07': 'R21 O21', 'OBT-08': 'R21 P03', 'OBT-09': 'P02 P03', 'OBT-10': 'P09 P11 V04', 'AUT-03': 'P02', 'AUT-04': 'G07 G08 L18', 'AUT-06': 'C04 C07 M06 L07 R08 R11 R21 G07', 'AUT-07': 'R22 V07', 'AUT-08': 'R14', 'AUT-09': 'R01 R02 M10 L05 G05'}.items():
    source_extra[_id]=' '.join(sorted(set(source_extra.get(_id,'').split()) | set(_extra.split())))

for _id,_extra in {'PIN005-02': 'M08 R20', 'PIN005-03': 'M08 R20', 'PIN005-04': 'M08 L09 R20', 'PIN005-05': 'M08 L09 R20', 'PIN011-03': 'L16 L04 C09', 'PIN011-07': 'P03', 'PIN012-02': 'M12 L12', 'PIN022-03': 'X01 X09', 'PIN023-02': 'M12 L12', 'PIN032-02': 'C01 C19', 'PIN032-03': 'C01 M12', 'PIN034-01': 'P03', 'PIN035-02': 'C04 C06', 'PIN035-03': 'C20 G01', 'PIN036-01': 'M12 L12', 'PIN037-01': 'M12 L12', 'PIN075-01': 'C06 L04', 'PIN075-02': 'C06 L04', 'PIN001-01': 'C19', 'PIN001-02': 'C19', 'PIN001-03': 'C19', 'PIN001-04': 'C19', 'PIN024-01': 'C19', 'PIN024-02': 'C19'}.items():
    source_extra[_id]=' '.join(sorted(set(source_extra.get(_id,'').split()) | set(_extra.split())))

rows=[]
for lineno,line in enumerate((ROOT/'SOURCE_FINDINGS_AND_CONFLICTS.md').read_text().splitlines(),1):
    if not line.startswith('|'):continue
    cells=[x.strip() for x in re.split(r'(?<!\\)\|',line)[1:-1]]
    m=re.match(r'([A-Z][A-Z0-9]*(?:-[A-Z]*\d+)+)',cells[0])
    if not m:continue
    sid=m[1];pre=sid.split('-')[0];alltext=' '.join(cells[1:]);lower=alltext.lower()
    if sid in explicit:owners=set(explicit[sid])
    elif pre.startswith('PIN'):owners=set(pin_domains[int(pre[3:])]) | {'F09','V06','V01'}
    else:owners=set(source_prefix_refined[pre].split())
    owners.update(source_extra.get(sid,'').split())
    # Only literal, bounded cross-cutting semantic matches supplement manual domains.
    if sid not in explicit:
        if re.search(r'\bDST\b|timezone|time.?zone|midnight|clock',alltext,re.I):owners.add('F03')
        if re.search(r'lookahead|repaint|receipt|publication|known_at|backdat',alltext,re.I):owners.update(['F04','V06'])
        if re.search(r'\bSMT\b|cross.?index',alltext,re.I):owners.update(['M03','X07'])
        if re.search(r'\bCVD\b|cumulative.?delta',alltext,re.I):owners.update(['M01','M02','M03'])
    if pre in ('DTM','JCV') or sid.startswith('DRF-U'):
        provenance=cells[1];idea=cells[2];rationale=cells[-1]
    elif pre in ('CEX','CRL'):
        provenance=cells[1];idea=cells[3];rationale=cells[5]+'; '+cells[4]+'; validation: '+cells[7]
    elif sid.startswith('DRF-A'):
        provenance=cells[1];idea=cells[2];rationale='; '.join(cells[3:])
    elif pre in ('JSS','JTR'):
        provenance=cells[1];idea=cells[2];rationale=cells[3]
    else:
        provenance=cells[0][len(sid):].strip() or 'Exact pages/lines in linked finding'
        idea=cells[1];rationale=cells[2]
    statuses=[]
    for pat,label in [(r'retain|preserve','Retained hypothesis/reference'),(r'modif|improv|correct|replace|merge|extend','Modified/merged'),(r'benchmark','Benchmark comparison'),(r'reject|exclude|not.*authoriz','Rejected clause/exclusion'),(r'defer|unavailable|unprovided|missing|absent|unidentif','Dependency/unresolved'),(r'unverified|unproven|not.*evidence|unsupported|claim','Unvalidated claim')]:
        if re.search(pat,rationale.lower()):statuses.append(label)
    if any(x.startswith('R') for x in owners):statuses.append('Detailed Response later')
    if not statuses:statuses=['Source-specific disposition in rationale']
    fixture='T-SRC-'+sid
    rows.append(dict(id=sid,source_line=lineno,provenance=provenance,idea=idea,rationale=rationale,components=sorted(owners),statuses=statuses,fixture=fixture))
assert len(rows)==712 and len({r['id'] for r in rows})==712
assert all(x in components for r in rows for x in r['components'])
(ROOT/'review/source_design_routing.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')

def clean(s):return s.replace('|','\\|').replace('\n',' ')
lines=['# Supplied source-to-design matrix','','This is the detailed appendix to REQUIREMENTS_TRACEABILITY.md. All 712 stable table findings are included individually. Each row retains the full reviewed source-specific disposition/correction and its precise evidence link; a compound row can retain an observable mechanism, reject an identity/performance claim and defer an unavailable variant at the same time. Status tags are an index to those clauses, not approval of an entire narrative. The rationale governs.','','Every row owns a future `T-SRC-<finding-ID>` fixture/review case. That case must name separate assertions for each rule, exception, ordering, arithmetic error, missing input and evidence limitation in the linked finding. It is not satisfied by a test merely named after the source. Referenced component cards add their CC-07 unit/property/synthetic/integration/predictive/economic/ablation tests as applicable. For evidence-only claims the fixture is provenance/arithmetic/non-adoption review, not an invented predictive experiment. No proposed test is claimed run.','','C/L-compatible measurements and locations are in current scope. R-series sequence development is deferred as specified, while its measurement/logging and common-opportunity dependencies remain explicit. Observed author performance, hidden formulas and unsupported causal identities never become empirical priors simply because a mechanism has a destination.','','| Finding and exact source location | Original idea/observation | Final clause disposition and rationale | Component destinations | Required source case |','|---|---|---|---|---|']
for r in rows:
    sl=f"[{r['id']}]({ROOT}/SOURCE_FINDINGS_AND_CONFLICTS.md:{r['source_line']}) — {clean(r['provenance'])}"
    lines.append(f"| {sl} | {clean(r['idea'])} | {clean(r['rationale'])} | {linkset(r['components'])} | `{r['fixture']}`; component tests |")
lines+=['',f"Reconciliation: {len(rows)} reviewed source table IDs, {len(rows)} matrix rows, {len(rows)} distinct source-case IDs. The five DTM-U bullet requirements and seventeen active USR clarifications are separately mapped in the parent traceability file. No row is omitted because its source formula is wrong, its result unverified or its author an earlier assistant."]
(OUT/'SOURCE_TO_DESIGN.md').write_text('\n'.join(lines)+'\n')

ext=[]
ext_text=(ROOT/'EXTERNAL_RESEARCH.md').read_text()
for m in re.finditer(r'^### (EXT-\d+) — (.*?)\n(.*?)(?=^#{2,3} |\Z)',ext_text,re.M|re.S):
    body=m[3]; source=next(x.removeprefix('Source: ') for x in body.splitlines() if x.startswith('Source: '))
    owners=set('F12 O21'.split())
    for pat,ids in tags:
        if re.search(pat,body.lower()):owners.update(ids.split())
    ext.append(dict(id=m[1],line=ext_text[:m.start()].count('\n')+1,source=source,finding=body,components=sorted(owners)))
for lineno,l in enumerate(ext_text.splitlines(),1):
    m=re.match(r'\| (EXT-\d+|TECH-\d+) \|',l)
    if not m:continue
    c=[x.strip() for x in re.split(r'(?<!\\)\|',l)[1:-1]];sid=m[1]
    owners=set('F12 O21'.split()) if sid.startswith('EXT') else set('V03 V04'.split())
    for pat,ids in tags:
        if re.search(pat,' '.join(c[1:]).lower()):owners.update(ids.split())
    ext.append(dict(id=sid,line=lineno,source=c[1],finding=c[2],components=sorted(owners)))
tech={1:'C13 G02',2:'C11',3:'C10',4:'C12 C14',5:'O02 O04 O05',6:'M09 P06',7:'G01 G09 R21',8:'O14 X06',9:'G03',10:'V03 V04',11:'G06 G07 P05 V04',12:'F04 C17 X10',13:'F04 O06 O07',14:'F07 O01 O02',15:'O03 F05 F07',16:'F01 F02 F05',17:'C23 G02',18:'C24 G02'}
# Explicit page-level routes reviewed against the retained mechanism, including
# operational-only and deferred data dependencies. Avoid lexical false matches
# such as an options sweep being sent to a price-sweep detector.
ext_routes = {}
def emap(nums, ids):
    for n in nums:
        assert n not in ext_routes, n
        ext_routes[n] = ids.split()
emap([1,2,3,5,14,23,24,25,26,27,28,79,80,81,82,84,93,95], 'F02 F12 V03 V08')
emap([4], 'O09 O10 O11 O13 O21 O22 X06 L13')
emap([6], 'O09 O10 O11 O12 O13 O21 O22 L13 G05 G08 P04')
emap([7], 'F10 F12 O01 O09 O21')
emap([8], 'O13 O22 X03 X04 X05 X06 L15 G08')
emap([9], 'C19 O09 O11 O13 X05 X06 L15 G05 G06 G08')
emap([10], 'F04 O01 O21 C17 R12 G09')
emap([11], 'O11 O22 L13 P02 P04 P08')
emap([12], 'O11 O13 O22 L13 G08')
emap([13], 'F02 O10 O12 O13 X05 X06 V01 V03 V07')
emap([15], 'O11 O13 O22 G04 G05 G07')
emap([16], 'O11 O13 O21 O22 G08 G09')
emap([17], 'O11 O13 O22 G04 G05 G07 G08 P01 P03')
emap([18], 'C19 O11 O12 O13 O21 O22 G04 G05')
emap([19], 'O10 O11 O12 O13 O22')
emap([20], 'O10 O11 O13 O22 X05 X06 L15')
emap([21], 'C22 O13 G08 V01 V07')
emap([22], 'O11 O12 O13 O14 O22 X06')
emap([29], 'F04 F12 O01 O09 O11 O21')
emap([30], 'F04 F12 O09 O10 O12 O21 V06')
emap([31], 'F04 F06 F11 F12 O10 O12 O21')
emap([32], 'F04 F07 O03 O06 O15 O16 O18 O20 X08')
emap([33], 'F04 F07 O03 O15 O18 O20')
emap([34,35], 'F04 O03 O15 O18')
emap([36,37], 'F04 O18 G03')
emap([38], 'O14 O15 O18')
emap([39], 'F04 O18 V02 V03')
emap([40,41,42,43], 'F02 F04 O03 O15 O18 X06 X08')
emap([44], 'F04 F05 O15 O20')
emap([45], 'O03 O15 O18 G01 G03')
emap([46], 'O06 O07 O08 O18 O21')
emap([47], 'O14 O18 O20')
emap([48], 'F05 O03 O18 O20 G03')
emap([49,50,51,52], 'F02 O03 O15 O18')
emap([53,54], 'F02 F07 O01')
emap([55,56,57,58], 'F04 O03 O15 O18')
emap([59], 'F04 F09 O15 O18 X08')
emap([60], 'F04 F05 O03 O15 O16 O18 O20')
emap([61], 'O06 O14 O15 O18 O23')
emap([62], 'O01 O14 O15 O18')
emap([63], 'F02 F07 O01')
emap([64], 'F04 F07 O01 O02 O04 O21')
emap([65], 'F03 F04 F08 O18 X08')
emap([66,69,76], 'F03 F04 O14 O18')
emap([67,68], 'F04 O01 O18 O20 V03')
emap([70], 'F04 O06 O07 O08 O18')
emap([71,72], 'F04 F07 O01 O06 O15 O18')
emap([73], 'F04 F09 O02 O03 O15 O16 O18')
emap([74], 'F04 F05 O03 O15 O16 O20')
emap([75], 'F04 O02 O06 O07 O15 O18')
emap([77,78], 'F04 F05 F12 X08 L12 V01')
emap([83], 'F12 O03 O13 O20 X06 V01')
emap([85], 'F09 F10 F12 O10 O11 O13 O21 X02 L13')
emap([86], 'F10 L01 L02 V03')
emap([87], 'O17 L14 X02')
emap([88], 'M07 L11 X02')
emap([89], 'M01 M02 F09')
emap([90], 'M04 M05 L05 L06')
emap([91], 'M06 L07')
emap([92], 'F09 M01 M02 F12')
emap([94], 'F02 F03 F12')
emap([96], 'F04 F06 F12')
assert set(ext_routes) == set(range(1,97))
for r in ext:
    n=int(r['id'].split('-')[1])
    r['components']=tech[n].split() if r['id'].startswith('TECH') else ext_routes[n]
assert len(ext)==114 and len(set(r['id'] for r in ext))==114
assert all(c in components for r in ext for c in r['components'])
(ROOT/'review/external_design_routing.json').write_text(json.dumps(ext,indent=2,ensure_ascii=False)+'\n')
lines=['# External research-to-design matrix','','All 96 Skylit page findings and 18 focused primary-method/provider findings have destinations below. Exact visit/read scope, retained mechanisms/corrections and unavailable text are recorded in the linked EXTERNAL_RESEARCH.md finding and SOURCE_REVIEW_LEDGER.md. Public docs describe mechanisms/capabilities, not verified access or profitable edge. Each row has a future `T-EXT-<ID>` semantic/provenance case plus applicable component tests. Official firm rules map separately to P09/P10/P11 and T-ACCOUNT in the parent matrix.','','| Research finding and disposition | Exact source | Component destinations | Verification |','|---|---|---|---|']
for r in ext:
    lines.append(f"| [{r['id']}]({ROOT}/EXTERNAL_RESEARCH.md:{r['line']}) | {r['source']} | {linkset(r['components'])} | `T-EXT-{r['id']}` |")
(OUT/'EXTERNAL_TO_DESIGN.md').write_text('\n'.join(lines)+'\n')
(ROOT/'review/component_registry.json').write_text(json.dumps(components,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'components':len(components),'source_findings':len(rows),'external_findings':len(ext),'source_components_minmax':[min(len(r['components']) for r in rows),max(len(r['components']) for r in rows)]}))
