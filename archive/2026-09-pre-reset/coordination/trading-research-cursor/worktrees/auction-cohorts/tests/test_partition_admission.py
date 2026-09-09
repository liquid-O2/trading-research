from dataclasses import replace
import multiprocessing
import os
from pathlib import Path
import tempfile
import unittest

from trading_research.data.events import decode_fields
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from tests.test_market_data import SCENARIO, event


def _crash_worker(store_path, path, kwargs):
    from trading_research.data.partitions import PartitionStore
    def stop(stage):
        if stage == "after_chunk":
            os._exit(77)
    PartitionStore(store_path).ingest_parquet(path, fault_hook=stop, **kwargs)


class PartitionAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            raise unittest.SkipTest("pinned Arrow dependency unavailable")
        cls.pa, cls.pq = pa, pq

    def setup_partition(self, folder, *, bad_row=False, empty=False):
        from trading_research.data.partitions import PartitionBudget, PartitionStore
        root = Path(folder)
        path = root / "input.parquet"
        rows = [decode_fields(event(i, at=10, action="T", side="B", flags=0, size=2).raw_fields) for i in range(5)]
        for i, row in enumerate(rows):
            row["correction_sequence"] = i + 10
        table = self.pa.Table.from_pylist(rows)
        schema = table.schema
        if bad_row:
            rows[2]["t"] = None
            table = self.pa.Table.from_pylist(rows, schema=schema)
        if empty:
            table = table.slice(0, 0)
        self.pq.write_table(table, path, row_group_size=3)
        budget = PartitionBudget(max_source_bytes=1<<20, max_rows=16, max_output_bytes=2<<20, chunk_rows=2)
        store = PartitionStore(root / "accepted")
        kwargs = dict(data_root=root, dataset_id="fixture/mbp", acquisition_version="v1",
                      expected_schema=schema, scenario=SCENARIO, budget=budget)
        return path, rows, store, kwargs

    def test_crash_after_data_and_before_manifest_exposes_no_partial_partition_then_restart_matches(self):
        for fault in ("after_chunk", "before_manifest"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as folder:
                path, rows, store, kwargs = self.setup_partition(folder)
                def crash(stage):
                    if stage == fault:
                        raise InterruptedError("injected process interruption")
                with self.assertRaises(InterruptedError):
                    store.ingest_parquet(path, fault_hook=crash, **kwargs)
                self.assertEqual(store.manifests(), [])
                admitted = store.ingest_parquet(path, **kwargs)
                self.assertEqual(store.manifests(), [admitted])
                self.assertEqual([decode_fields(e.raw_fields) for e in store.events(admitted)], rows)
                self.assertEqual(store.ingest_parquet(path, **kwargs), admitted)
                self.assertEqual(store.manifests(), [admitted])

    def test_verified_aliases_and_different_chunk_sizes_preserve_every_event_and_correction_field(self):
        with tempfile.TemporaryDirectory() as folder:
            path, rows, store, kwargs = self.setup_partition(folder)
            first = store.ingest_parquet(path, **kwargs)
            alias = path.with_name("alias.parquet"); alias.write_bytes(path.read_bytes())
            same = store.ingest_parquet(alias, **kwargs)
            self.assertEqual(first, same)
            alternate = store.ingest_parquet(alias, **{**kwargs,"budget":replace(kwargs["budget"],chunk_rows=3)})
            a, b = list(store.events(first)), list(store.events(alternate))
            self.assertEqual([e.id for e in a], [e.id for e in b])
            self.assertEqual([decode_fields(e.raw_fields) for e in b], rows)
            self.assertEqual(len(store.locators(first)), 2)
            self.assertEqual([e.address.row for e in a], [0,1,2,0,1])

    def test_process_death_leaves_no_admission_and_restart_recovers_exact_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path, rows, store, kwargs = self.setup_partition(folder)
            process = multiprocessing.get_context("spawn").Process(target=_crash_worker,args=(store.root,path,kwargs))
            process.start()
            process.join(15)
            if process.is_alive():
                process.kill(); process.join(5)
                self.fail("bounded crash fixture did not finish")
            self.assertEqual(process.exitcode, 77)
            self.assertEqual(store.manifests(), [])
            restarted = store.ingest_parquet(path, **kwargs)
            self.assertEqual([decode_fields(e.raw_fields) for e in store.events(restarted)], rows)

    def test_rejected_row_keeps_physical_address_and_counts_and_quarantines_consumers(self):
        with tempfile.TemporaryDirectory() as folder:
            path, rows, store, kwargs = self.setup_partition(folder, bad_row=True)
            reference = store.ingest_parquet(path, **kwargs)
            manifest = store.manifest(reference)
            self.assertEqual((manifest["source_rows"],manifest["accepted_rows"],manifest["rejected_rows"]), (5,4,1))
            self.assertEqual(manifest["status"], "quarantined")
            rejected = store.rejections(reference)
            self.assertEqual([(r["row_group"],r["row"]) for r in rejected], [(0,2)])
            self.assertEqual(rejected[0]["reason_code"], "decode_contract_violation")
            self.assertTrue(rejected[0]["raw_arrow_row"])
            from trading_research.operations.artifacts import artifact_ref
            arrow_row = store.artifacts.read(artifact_ref(rejected[0]["raw_arrow_row"]))
            with self.pa.ipc.open_stream(arrow_row) as stream:
                self.assertEqual(stream.read_all().to_pylist(), [rows[2]])
            with self.assertRaises(DependencyUnavailable):
                list(store.events(reference))

    def test_schema_budget_and_partial_download_fail_without_manifest_and_empty_partition_is_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            path, _, store, kwargs = self.setup_partition(folder)
            with self.assertRaises(ContractError):
                store.ingest_parquet(path, **{**kwargs,"expected_schema":kwargs["expected_schema"].remove(0)})
            for budget in (replace(kwargs["budget"],max_source_bytes=1),replace(kwargs["budget"],max_rows=2),
                           replace(kwargs["budget"],max_output_bytes=16)):
                with self.subTest(budget=budget), self.assertRaises(DependencyUnavailable):
                    store.ingest_parquet(path, **{**kwargs,"budget":budget})
            partial = path.with_name("input.parquet.part");partial.write_bytes(path.read_bytes())
            with self.assertRaises(ContractError):
                store.ingest_parquet(partial, **kwargs)
            self.assertEqual(store.manifests(), [])
        with tempfile.TemporaryDirectory() as folder:
            path, _, store, kwargs = self.setup_partition(folder, empty=True)
            empty = store.ingest_parquet(path, **kwargs)
            self.assertEqual((store.manifest(empty)["source_rows"],store.manifest(empty)["status"]), (0,"accepted"))
            self.assertEqual(list(store.events(empty)), [])

    def test_corrupt_later_chunk_is_detected_before_any_event_is_exposed(self):
        with tempfile.TemporaryDirectory() as folder:
            path, _, store, kwargs = self.setup_partition(folder)
            reference = store.ingest_parquet(path, **kwargs)
            from trading_research.operations.artifacts import artifact_ref
            chunks = store.manifest(reference)["chunks"]
            last = store.artifacts.path(artifact_ref(chunks[-1]))
            last.write_bytes(b"corrupt")
            stream = store.events(reference)
            with self.assertRaises(IntegrityError):
                next(stream)

    def test_same_numeric_columns_with_changed_correction_field_is_a_new_partition(self):
        with tempfile.TemporaryDirectory() as folder:
            path, rows, store, kwargs = self.setup_partition(folder)
            first = store.ingest_parquet(path, **kwargs)
            rows[0]["correction_sequence"] = 999
            self.pq.write_table(self.pa.Table.from_pylist(rows,schema=kwargs["expected_schema"]),path,row_group_size=3)
            changed = store.ingest_parquet(path, **kwargs)
            self.assertNotEqual(first, changed)
            self.assertNotEqual(list(store.events(first))[0].id, list(store.events(changed))[0].id)
            self.assertEqual(decode_fields(list(store.events(first))[0].raw_fields)["correction_sequence"],10)
            self.assertEqual(decode_fields(list(store.events(changed))[0].raw_fields)["correction_sequence"],999)

    def test_partial_manifest_and_omitted_correction_field_fail_independent_source_checks(self):
        from dataclasses import asdict
        from trading_research.data.events import encode_fields
        from trading_research.operations.artifacts import artifact_ref, canonical_json, publish_new
        with tempfile.TemporaryDirectory() as folder:
            path, _, store, kwargs = self.setup_partition(folder)
            good = store.ingest_parquet(path, **kwargs)
            manifest = store.manifest(good)
            partial = {**manifest,"source_rows":2,"row_group_sizes":[2],"accepted_rows":2,"chunks":manifest["chunks"][:1]}
            ref = store.artifacts.put_json(partial,kind="partition_manifest")
            publish_new(store.index/f"{ref.sha256}.json",canonical_json(asdict(ref)))
            with self.assertRaises(IntegrityError):
                next(store.events(ref))
            first_rows = store.artifacts.read_json(artifact_ref(manifest["chunks"][0]))
            fields = decode_fields(bytes.fromhex(first_rows[0]["raw_fields"]))
            del fields["correction_sequence"]
            first_rows[0]["raw_fields"] = encode_fields(fields).hex()
            changed_chunk = store.artifacts.put_json(first_rows,kind="partition_rows")
            omitted = {**manifest,"chunks":[asdict(changed_chunk),*manifest["chunks"][1:]]}
            ref = store.artifacts.put_json(omitted,kind="partition_manifest")
            publish_new(store.index/f"{ref.sha256}.json",canonical_json(asdict(ref)))
            with self.assertRaisesRegex(IntegrityError,"raw fields"):
                next(store.events(ref))

    def test_availability_configuration_is_versioned_and_old_code_cannot_be_reused(self):
        from dataclasses import asdict
        from trading_research.operations.artifacts import canonical_json, publish_new
        with tempfile.TemporaryDirectory() as folder:
            path, _, store, kwargs = self.setup_partition(folder)
            first = store.ingest_parquet(path, **kwargs)
            changed = store.ingest_parquet(path, **{**kwargs,"scenario":replace(SCENARIO,id="plus-five",delay_ns=5)})
            self.assertNotEqual(first, changed)
            self.assertEqual([e.clocks.known_at for e in store.events(first)], [12]*5)
            self.assertEqual([e.clocks.known_at for e in store.events(changed)], [15]*5)
            stale = {**store.manifest(first),"code_version":"0"*64}
            ref = store.artifacts.put_json(stale,kind="partition_manifest")
            publish_new(store.index/f"{ref.sha256}.json",canonical_json(asdict(ref)))
            with self.assertRaises(ContractError):
                next(store.events(ref))
