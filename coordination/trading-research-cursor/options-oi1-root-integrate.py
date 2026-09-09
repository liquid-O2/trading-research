from pathlib import Path
import ast,json,hashlib,shutil
root=Path('/workspace/trading-research')
work=Path('/workspace/coordination/trading-research-cursor/worktrees/options-oi1')
coord=work.parents[1]
names=['src/trading_research/research/options_oi_measurements.py','src/trading_research/research/options_oi_statistics.py','tests/test_options_oi_measurements.py']
backup=coord/'options-oi1-before-root-review';backup.mkdir(exist_ok=True)
for name in names: shutil.copy2(work/name,backup/Path(name).name)
p=work/names[0];s=p.read_text()
s=s.replace('        self.open = {}\n','        self.open = {}\n        self.request_midnights = {}\n',1)
s=s.replace('            self.pending.append(item)\n','            if item[3] not in self.request_midnights:\n                self.request_midnights[item[3]] = cut_ns_on(item[3], "00:00")\n            self.pending.append(item)\n',1)
start=s.index('        applied.sort(',s.index('class AsofTimeline:'));end=s.index('        return closed\n',start)
s=s[:start]+'''        # A later request can repeat an older source clock. Its eligibility starts
        # at request midnight; it cannot rewrite an earlier interval or replace a
        # newer clock. Resolve same-clock conflicts across request files as well.
        def availability(event):
            return max(event[1], self.request_midnights[event[3]])
        applied.sort(key=lambda e: (availability(e), e[0], e[1], e[3], e[4], e[5]))
        closed = []
        i = 0
        while i < len(applied):
            j = i + 1
            first = applied[i]
            start_at = availability(first)
            while (j < len(applied) and applied[j][0] == first[0]
                   and applied[j][1] == first[1] and availability(applied[j]) == start_at):
                j += 1
            group = applied[i:j]
            cid, ts = first[0], first[1]
            prev = self.open.get(cid)
            if prev is not None and ts < prev["ts_event_ns"]:
                i = j
                continue
            pick = min(group, key=lambda item: (item[3], item[4], item[5]))
            values = {item[2] for item in group}
            ambiguous = len(values) != 1
            if prev is not None and ts == prev["ts_event_ns"]:
                ambiguous = ambiguous or prev["ambiguous"] or prev["open_interest"] not in values
                if not ambiguous:
                    i = j
                    continue
            if prev is not None:
                self.open.pop(cid)
                start_at = max(start_at, prev["valid_from_ns"])
                prev["valid_to_ns"] = start_at
                closed.append(prev)
            state = {
                "contract_id": cid, "chain": self.chain,
                "open_interest": None if ambiguous else pick[2],
                "ts_event_ns": ts, "request_date": pick[3],
                "file_id": pick[4], "row_index": pick[5],
                "ambiguous": ambiguous, "valid_from_ns": start_at, "valid_to_ns": None,
                "expiration": pick[6], "causal_feature_eligible": False,
            }
            self.open[cid] = dict(state)
            self.live[cid] = {
                "oi": state["open_interest"], "ts": ts, "request_date": pick[3],
                "ambiguous": ambiguous, "expiration": pick[6],
            }
            i = j
''' + s[end:]
s=s.replace('        interval_w.append(list(asof.open.values()))','        # Persist pending future-clock observations too; no selected cut can see\n        # an interval before its valid_from/request-date predicate.\n        interval_w.append(asof.apply_through(9223372036854775807, "9999-12-31"))\n        interval_w.append(list(asof.open.values()))',1)
s=s.replace('    "Late observations stay pending until a later cut. "','    "Late observations stay pending until a later cut. valid_from_ns is the later of "\n    "the source clock and request midnight; older reobserved clocks never replace a newer state. "',1)
# Empty markers have no Arrow schema entry in the actual admitted source registry.
s=s.replace('                    if type(schema_str) is not str:\n                        raise IntegrityError("admitted schema_id is not in schemas")\n                    table, meta = read_admitted_source(protocol, record)','                    table, meta = read_admitted_source(protocol, record)\n                    if meta["empty_marker"]:\n                        schema_str = str(table.schema)\n                    elif type(schema_str) is not str:\n                        raise IntegrityError("admitted schema_id is not in schemas")',1)
# Do not retain every chain\'s historical identity keys after the chain finishes.
s=s.replace('        self.expiration = {}\n','        self.expiration = {}\n        self.next_id = 0\n',1)
s=s.replace('                cid = len(self._key_to_id)\n','                cid = self.next_id\n                self.next_id += 1\n',1)
s=s.replace('        interval_w.append(list(asof.open.values()))\n    return finish_measurement_outputs(','        interval_w.append(list(asof.open.values()))\n        identities._key_to_id.clear()\n        identities.expiration.clear()\n    return finish_measurement_outputs(',1)
p.write_text(s)
p=work/names[1];s=p.read_text()
s=s.replace('            life["censor_boundary"][day] = life_acc.get("n_censor_boundary", 0) / attempts\n','',1)
s=s.replace('                         "censor_boundary_fraction", "first_observed_fraction"):', '                         "first_observed_fraction"):',1)
needle='        for cut, payload in row.get("asof", {}).items():'
s=s.replace(needle,'''        # Source boundaries have their own endpoint population; do not double
        # the denominator of the ordinary adjacent-date changes.
        boundary = row.get("lifecycle_boundary", {}).get(policy, {}).get("n_attempts", 0)
        if boundary:
            life["censor_boundary"][day] = 1.0
            events["censor_boundary_fraction"][day] = boundary
'''+needle,1)
s=s.replace('        "Contract observations are not additional independent dates.",','        "Contract observations are not additional independent dates. "\n        "censor_boundary_fraction uses only the separately retained source-boundary endpoint population; "\n        "its event support reports that boundary count.",',1)
# The full projection is owned by the registered supervisor and actual admitted total rows.
a=s.index('    scale = max(files_read or 1, rows_read or 1, intended_units or 1)');b=s.index('    refs = {',a);s=s[:a]+s[b:]
a=s.index('            "full_gate_projection": {');b=s.index('        },\n        "source_dates_processed"',a)
s=s[:a]+'''            "full_gate_projection": "computed by registered supervisor from admitted full rows/files/dates and measured pilot; not inferred from this selection",
'''+s[b:]
p.write_text(s)
# Add independent literals for the remaining root review corrections.
p=work/names[2];s=p.read_text();pos=s.index('\n\nif __name__')
s=s[:pos]+'''

class RootReviewTests(unittest.TestCase):
    def test_reobserved_older_clock_does_not_rewind_current_state(self):
        from trading_research.research.options_oi_measurements import AsofTimeline
        timeline = AsofTimeline("NDX")
        a = cut_ns_on("2020-01-02", "06:30")
        older = a - 100
        timeline.add([1], [a], [100], ["2020-01-02"], [1], [0], ["2020-01-17"])
        closed = timeline.apply_through(cut_ns_on("2020-01-02", "15:00"), "2020-01-02")
        timeline.add([1], [older], [50], ["2020-01-03"], [2], [0], ["2020-01-17"])
        closed += timeline.apply_through(cut_ns_on("2020-01-03", "09:30"), "2020-01-03")
        ledger = closed + list(timeline.open.values())
        for day in ["2020-01-02", "2020-01-03"]:
            visible = reconstruct_asof_intervals(ledger, cut_ns_on(day, "09:30"), day)
            self.assertEqual([r["open_interest"] for r in visible], [100])

    def test_same_clock_conflict_on_later_request_preserves_prior_cut(self):
        from trading_research.research.options_oi_measurements import AsofTimeline
        timeline = AsofTimeline("NDX")
        ts = cut_ns_on("2020-01-02", "06:30")
        timeline.add([1], [ts], [100], ["2020-01-02"], [1], [0], ["2020-01-17"])
        closed = timeline.apply_through(cut_ns_on("2020-01-02", "15:00"), "2020-01-02")
        timeline.add([1], [ts], [120], ["2020-01-03"], [2], [0], ["2020-01-17"])
        closed += timeline.apply_through(cut_ns_on("2020-01-03", "09:30"), "2020-01-03")
        ledger = closed + list(timeline.open.values())
        first = reconstruct_asof_intervals(ledger, cut_ns_on("2020-01-02", "09:30"), "2020-01-02")
        last = reconstruct_asof_intervals(ledger, cut_ns_on("2020-01-03", "09:30"), "2020-01-03")
        self.assertEqual(first[0]["open_interest"], 100)
        self.assertEqual(len(last), 1)
        self.assertTrue(last[0]["ambiguous"])
        self.assertEqual(last[0]["valid_from_ns"], cut_ns_on("2020-01-03", "00:00"))

    def test_admitted_empty_marker_without_schema_is_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "data"
            path = root / "empty.json"
            root.mkdir()
            raw = b"{}"
            path.write_bytes(raw)
            record = _admit(1, "empty.json", "NDX", "open_interest", "2020-01-02", "oi", "empty_marker",
                            {"size_bytes": 2, "sha256": hashlib.sha256(raw).hexdigest()})
            record.update(format=".json", rows=0, marker={})
            protocol = dict(PROTOCOL, data_root=str(root))
            admitted = {"kind": "options_oi_admitted_sources_v1", "source_files": 1, "sources": [record], "schemas": {}}
            outputs = BoundedOutputs(Path(folder)/"out", maximum_total_bytes=32*1024**2, maximum_file_bytes=16*1024**2)
            result = run(protocol=protocol, admitted=admitted, outputs=outputs, selected_dates=["2020-01-02"])
            import pyarrow.parquet as pq
            coverage = pq.read_table(result["refs"]["coverage"]["path"]).to_pylist()
            ndx = next(row for row in coverage if row["chain"] == "NDX")
            self.assertEqual(ndx["oi_status"], "empty_marker")
            self.assertIsNone(ndx["oi_count"])
            self.assertEqual(result["counts"]["source_files_read"], 1)
''' + s[pos:];p.write_text(s)
for name in names:
    p=work/name;ast.parse(p.read_text());dest=root/name
    if dest.exists(): raise RuntimeError('new isolated files only: '+str(dest))
    shutil.copy2(p,dest)
report={'reviewed_files':names,'static_parse':'passed','root_corrections':['future pending ledger preserved','late older-clock reobservations cannot rewind latest state','same-clock later-request conflicts preserve earlier intervals','empty admission marker schema','per-chain identity map lifetime','boundary statistic uses separate population','remove invalid internal full projection'], 'candidate_execution':'only through registered runner next','worker_run':'20260909T000320Z-d5341ec6','hashes':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}}
(coord/'options-oi1-integration.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
