from pathlib import Path
import ast,hashlib,json,shutil
W=Path('/workspace/coordination/trading-research-cursor/worktrees/crossmarket1');R=Path('/workspace/trading-research');C=W.parent.parent
files=['src/trading_research/research/cross_market_alignment.py','src/trading_research/research/cross_market_descriptive.py','tests/test_cross_market_descriptive.py']
backup=C/'crossmarket1-before-root';backup.mkdir(exist_ok=True)
for f in files:shutil.copy2(W/f,backup/Path(f).name)
def sub(s,a,b):
 assert a in s,a[:100]
 return s.replace(a,b)
p=W/files[0];s=p.read_text()
s=sub(s,'    np = _np()\n    n = len(unit)\n    if unit.instrument_kind', '    np = _np()\n    if unit._contract_keys is not None:\n        return unit._contract_keys\n    n = len(unit)\n    if unit.instrument_kind')
s=sub(s,'        return out\n    prefix = unit.symbol + ":"\n    return np.asarray([prefix + str(int(code)) for code in unit.instrument_id], dtype=object)', '        unit._contract_keys = out\n        return out\n    prefix = unit.symbol + ":"\n    codes, inverse = np.unique(unit.instrument_id, return_inverse=True)\n    names = np.asarray([prefix + str(int(code)) for code in codes], dtype=object)\n    unit._contract_keys = names[inverse]\n    return unit._contract_keys')
s=sub(s,'    _clocks: dict | None = field(default=None, repr=False, compare=False)','    _clocks: dict | None = field(default=None, repr=False, compare=False)\n    _contract_keys: object = field(default=None, repr=False, compare=False)')
s=sub(s,'    while i >= 0 and j >= 0:\n        se = int(src_end[i])','    lower_end = int(cash_close_ns) - MAX_SOURCE_AGE_NS\n    while i >= 0 and j >= 0:\n        if int(src_end[i]) < lower_end or int(rcv_end[j]) < lower_end:\n            break\n        se = int(src_end[i])')
s=sub(s,'    if row is None:\n        return None\n    return {\n        "ratio":', '    if row is None or row["bar_end_ns"] < int(cash.open_at):\n        return None\n    return {\n        "ratio":')
s=sub(s,'        status = np.full(n, 1, dtype=np.int8)','        status = np.full(n, 2, dtype=np.int8)')
s=sub(s,'    def prior_rth_scale(self, current_contract_key=None):\n        for day in reversed(self.dates):','    def prior_rth_scale(self, current_contract_key=None, prior_intended=None):\n        days = self.dates if prior_intended is None else prior_intended[-1:]\n        for day in reversed(days):')
s=sub(s,'            if row is None or not row["rth_complete"] or row["rth_sqrt_rv"] is None:\n                continue','            if row is None or not row["rth_complete"] or row["rth_sqrt_rv"] is None:\n                if prior_intended is not None:\n                    return None\n                continue')
p.write_text(s)
p=W/files[1];s=p.read_text()
a=s.index('    if not src_known and not rcv_known:',s.index('def _breach_state'));b=s.index('    source = bool(',a)
s=s[:a]+'    if not src_known or not rcv_known:\n        return "unknown"\n'+s[b:]
s=sub(s,'    for cash in cash_days:\n        intended_dates.append', '    prior_calendar_days = [date.fromisoformat(d) for d in intended_dates]\n    history_days = sorted(set(prior_calendar_days + intended_day_list))\n    previous_by_day = {d: history_days[i - 1] if i else None for i, d in enumerate(history_days)}\n    for cash in cash_days:\n        next_label_id = label_ids.get("_next", 1)\n        label_ids.clear()\n        label_ids["_next"] = next_label_id\n        prior_dates = history_days[max(0, history_days.index(cash.day) - 20):history_days.index(cash.day)]\n        intended_dates.append')
s=sub(s,'                prior_dates = [item for item in intended_day_list if item < cash.day]\n','')
s=sub(s,'scale = carry_unit.prior_rth_scale(prep.contract_key[index])','scale = carry_unit.prior_rth_scale(prep.contract_key[index], prior_dates)')
s=sub(s,'writers, groups, carry, intended_day_list)','writers, groups, carry, previous_by_day)')
s=sub(s,'    prior_day = previous_intended_date(intended_days, cash.day)','    prior_day = intended_days.get(cash.day) if isinstance(intended_days, dict) else previous_intended_date(intended_days, cash.day)')
s=sub(s,'or ref_start is None or ref_start >= event_start','or ref_start is None or ref_start >= event_known')
s=sub(s,'formed + 2 * MINUTE))','formed + 3 * MINUTE))')
s=sub(s,'and form_i != mid_i) else None','and form_i != mid_i\n                            and rcv_prep.run_id[form_i] == rcv_prep.run_id[mid_i]\n                            and rcv_prep.contract_key[form_i] == rcv_prep.contract_key[mid_i]) else None')
s=sub(s,'and (ref_start is None or ref_start < event_known)) else None','and ref_i is not None\n                            and rcv_prep.run_id[mid_i] == rcv_prep.run_id[ref_i]\n                            and rcv_prep.contract_key[mid_i] == ref_key\n                            and (ref_start is None or ref_start < event_known)) else None')
s=sub(s,'                            window = {"status": "no_receiver", "reasons": ("no_receiver",),\n                                      "high": None, "low": None, "close": None, "index": None,\n                                      "contract_key": None, "instrument_id": None}\n                            if not no_ref:\n                                window = lookup_future_window(\n                                    receiver, rcv_prep.futures, label_start, horizon,\n                                    reference_contract_key=ref_key)', '                            raw_window = lookup_future_window(receiver, rcv_prep.futures, label_start, horizon)\n                            window = dict(raw_window)\n                            if no_ref:\n                                window.update(status="no_receiver", high=None, low=None, close=None)\n                            elif raw_window.get("contract_key") != ref_key:\n                                window.update(status="roll", high=None, low=None, close=None)')
s=sub(s,'label_id = len(label_ids) + 1\n                                label_ids[label_key] = label_id','label_id = label_ids["_next"]\n                                label_ids["_next"] = label_id + 1\n                                label_ids[label_key] = label_id')
a=s.index('                                writers["receiver_labels"].add({');b=s.index('                            bundle =',a)
s=s[:a]+s[a:b].replace('window[','raw_window[').replace('window.get(','raw_window.get(')+s[b:]
s=sub(s,'if src_known and src["close"] and sph and src["close"] > 0 and sph > 0:\n                                excursion = math.log(src["close"] / sph) if src_h else (\n                                    math.log(sph / src["close"]) if src_l else 0.0)', 'if src_known:\n                                high_excursion = max(0.0, math.log(src["high"] / sph)) if src_h and sph and sph > 0 else 0.0\n                                low_excursion = max(0.0, math.log(spl / src["low"])) if src_l and spl and src["low"] > 0 else 0.0\n                                excursion = max(high_excursion, low_excursion)')
s=sub(s,'                            src_known = src["priced"] and src_idx is not None\n                            rcv_known = rcv["priced"] and rcv_idx is not None', '                            src_known = src["priced"] and src_idx is not None and bool(src_prep.running[length]["defined"][src_idx]) and (int(src_prep.pivot["high_known_end_ns"][src_idx]) >= 0 and int(src_prep.pivot["low_known_end_ns"][src_idx]) >= 0)\n                            rcv_known = rcv["priced"] and rcv_idx is not None and bool(rcv_prep.running[length]["defined"][rcv_idx]) and (int(rcv_prep.pivot["high_known_end_ns"][rcv_idx]) >= 0 and int(rcv_prep.pivot["low_known_end_ns"][rcv_idx]) >= 0)')
s=s.replace('or int(src_p["low_known_end_ns"]','and int(src_p["low_known_end_ns"]').replace('or int(rcv_p["low_known_end_ns"]','and int(rcv_p["low_known_end_ns"]')
s=sub(s,'            if not row.get("in_primary_cohort"):', '            if not row.get("in_primary_cohort"):') if '            if not row.get("in_primary_cohort"):' in s else s
s=sub(s,'        if not row.get("in_primary_cohort"):\n            continue','        if not row.get("in_primary_cohort") or int(row["date"][:4]) not in years:\n            continue')
s=sub(s,'    _add_cell(groups, group_key(metric="zero_reaction", **base), day, 1.0 if row.get("zero_reaction") else 0.0)', '    if ci_ok and row.get("terminal_log") is not None:\n        _add_cell(groups, group_key(metric="zero_reaction", **base), day, 1.0 if row.get("zero_reaction") else 0.0)')
s=sub(s,'    _add_cell(groups, group_key(metric="zero_receiver", **base), day, 1.0 if concord == "zero_receiver" else 0.0)', '    if ci_ok and row.get("terminal_log") is not None:\n        _add_cell(groups, group_key(metric="zero_receiver", **base), day, 1.0 if concord == "zero_receiver" else 0.0)')
s=sub(s,'                f"lag={key[10] if isinstance(key, tuple) else None} "','                f"variants={key[3:5] if isinstance(key, tuple) else None} "\n                f"year/stage/session={key[5:8] if isinstance(key, tuple) else None} "\n                f"kind={key[9] if isinstance(key, tuple) else None} "\n                f"lag={key[10] if isinstance(key, tuple) else None} "')
p.write_text(s)
p=W/files[2];s=p.read_text()
s=sub(s,'cut = int(unit.end_ns[0]) + 180 * NS','cut = int(unit.end_ns[0]) + 240 * NS')
s=sub(s,'self.assertTrue(all(row["source_own_breach_high"] is None for row in unknown))','self.assertTrue(all(row["source_own_breach_high"] is None or row["receiver_own_breach_high"] is None for row in unknown))')
s=sub(s,'            self.assertGreaterEqual(sum(1 for row in joints if row.get("no_receiver") is False), 5)', '            self.assertGreaterEqual(sum(1 for row in joints if row.get("no_receiver") is False), 5)\n            primary = [r for r in joints if r["source_start_ns"] == start + 20 * MINUTE and r["event_kind"] == "running_high" and r["lag_s"] == 60]\n            self.assertEqual(len(primary), 5)\n            self.assertTrue(all(r["terminal_log"] == 0.0 and r["future_status"] == "complete" for r in primary))\n            self.assertTrue(all(r["receiver_ref_start_ns"] == start + 20 * MINUTE for r in primary))')
s += '''\nclass RootReviewRegression(unittest.TestCase):
    def test_missing_opposition_cannot_establish_source_only(self):
        from trading_research.research.cross_market_descriptive import _breach_state
        self.assertEqual(_breach_state(True, False, True, False, False, False), 'unknown')
        self.assertEqual(_breach_state(False, True, False, False, True, False), 'unknown')
        self.assertEqual(_breach_state(True, True, True, False, False, False), 'source_only')

    def test_mapping_missing_current_day_does_not_reuse_older_close(self):
        from trading_research.research.cross_market_alignment import freeze_previous_closing_ratio
        first = date(2020, 1, 6)
        start = local_timestamp(first, time(15, 50), NY)
        source = _bars('QQQ', start, [10.] * 10)
        receiver = _bars('NQ', start, [100.] * 10)
        cal = CashCalendar(CALENDAR)
        missing_day = date(2020, 1, 7)
        cash = cal.resolve(missing_day, cut=local_timestamp(missing_day, time(0), NY))
        self.assertIsNone(freeze_previous_closing_ratio(source, receiver, cash))

    def test_prior_rth_scale_does_not_compress_missing_day(self):
        carry=PriorCarry()
        carry.push_day(date(2020,1,6), {}, .2, True, 'NQ:1')
        carry.push_day(date(2020,1,7), {}, None, False, 'NQ:1')
        self.assertIsNone(carry.prior_rth_scale('NQ:1', [date(2020,1,7)]))
'''
p.write_text(s)
for f in files:
 p=W/f;ast.parse(p.read_text());dest=R/f;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,dest)
(C/'crossmarket1-root-integration.json').write_text(json.dumps({'files':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in files},'review':'Root read all corrected source/tests; fixed decision-reference rejection, unknown SMT, low excursion, year-stable calendar history, prior close freshness, compact label independence/IDs/bounded state, same-contract past paths, pivot formation end, missing future status, report group identities, invalid stale fixture.'},indent=2)+'\n')
print('integrated',len(files))
