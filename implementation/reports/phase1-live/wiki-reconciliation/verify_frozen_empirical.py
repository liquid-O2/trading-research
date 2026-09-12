"""Verify the accepted run against its exact frozen documentation context.

Run from /workspace with the implementation virtual environment. This keeps
the public live-input drift checks intact. Only the definition-file root is
bound to an independently hash-checked historical snapshot; validators, rule
bodies, code, market artifacts and assertions are unchanged. The canonical
verifier's output is saved here without rewriting historical acceptance.
"""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
from pathlib import Path, PurePosixPath
import runpy
import sys
import tarfile
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EMPIRICAL = HERE.parent / 'empirical'
sys.path.insert(0, str(ROOT / 'implementation/src'))


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def materialize(snapshot_dir, manifest, registry):
    archive = HERE / manifest['archive']
    assert digest(archive.read_bytes()) == manifest['archive_sha256'], 'snapshot archive changed'
    assert manifest['files'] == registry['input_identities'], 'snapshot is not the frozen registry input set'
    seen = set()
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            name = member.name
            relative = PurePosixPath(name)
            assert member.isfile() and not relative.is_absolute() and '..' not in relative.parts
            assert name in manifest['files'] and name not in seen, 'foreign or duplicate snapshot member'
            payload = tar.extractfile(member).read()
            assert digest(payload) == manifest['files'][name], f'frozen input changed: {name}'
            target = snapshot_dir.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            seen.add(name)
    assert seen == set(manifest['files']), 'incomplete snapshot'


def main():
    from trading_research.research.method_pack import empirical_registry as registry_module
    from trading_research.research.method_pack import empirical_protocol as protocol_module

    manifest = json.loads((HERE / 'FROZEN_DEFINITIONS.json').read_text())
    registry_path = EMPIRICAL / 'registry/CANDIDATE_REGISTRY.json'
    registry = json.loads(registry_path.read_text())
    assert digest(registry_path.read_bytes()) == manifest['registry_file_sha256']
    assert registry['registry_sha256'] == manifest['registry_sha256']
    run = json.loads((EMPIRICAL / 'RUN_MANIFEST.json').read_text())
    assert protocol_module.implementation_identity(ROOT) == run['implementation'], 'current executable inputs changed'

    changed = {}
    for relative, expected in manifest['files'].items():
        path = ROOT / relative
        actual = digest(path.read_bytes()) if path.is_file() else None
        if actual != expected:
            assert relative.startswith('planning/phase-1-live/wiki/'), f'non-wiki definition changed: {relative}'
            changed[relative] = {'frozen_sha256': expected, 'current_sha256': actual}
    current_wiki = {str(p.relative_to(ROOT)): digest(p.read_bytes())
                    for p in sorted((ROOT / 'planning/phase-1-live/wiki').glob('*.md'))}
    added = sorted(set(current_wiki) - set(manifest['files']))
    original_signature = registry_module._definition_signature
    original_identities = registry_module.input_identities
    original_write = protocol_module.write_json

    with tempfile.TemporaryDirectory(prefix='phase1-frozen-definitions-') as temporary:
        snapshot_dir = Path(temporary)
        materialize(snapshot_dir, manifest, registry)

        def frozen_signature(root='/workspace'):
            return original_signature(snapshot_dir)

        def frozen_identities(root='/workspace'):
            return original_identities(snapshot_dir)

        def save_verification(path, value):
            assert Path(path) == EMPIRICAL / 'validation/FINAL_VERIFICATION.json', 'unexpected verifier write'
            return original_write(HERE / 'FROZEN_RUN_VERIFICATION.json', value)

        with ExitStack() as stack:
            stack.enter_context(patch.object(registry_module, '_definition_signature', frozen_signature))
            stack.enter_context(patch.object(registry_module, 'input_identities', frozen_identities))
            stack.enter_context(patch.object(protocol_module, 'write_json', save_verification))
            assert registry_module.input_identities() == registry['input_identities']
            runpy.run_path(str(EMPIRICAL / 'validation/verify_completed_run.py'), run_name='__main__')

    assert digest((HERE / 'FROZEN_RUN_VERIFICATION.json').read_bytes()) == digest(
        (EMPIRICAL / 'validation/FINAL_VERIFICATION.json').read_bytes()), 'historical verification result changed'
    assert current_wiki == {str(p.relative_to(ROOT)): digest(p.read_bytes())
                            for p in sorted((ROOT / 'planning/phase-1-live/wiki').glob('*.md'))}, 'wiki changed during verification'
    record = {'schema': 'phase1-wiki-reconciliation-verification-v1', 'status': 'pass',
              'verification_context': 'exact frozen definition files; current unchanged executable and market inputs',
              'registry_sha256': registry['registry_sha256'], 'run_manifest_sha256': run['manifest_sha256'],
              'snapshot_manifest_sha256': digest((HERE / 'FROZEN_DEFINITIONS.json').read_bytes()),
              'verifier_sha256': digest(Path(__file__).read_bytes()),
              'frozen_result_sha256': digest((HERE / 'FROZEN_RUN_VERIFICATION.json').read_bytes()),
              'changed_wiki': changed, 'added_wiki': added, 'current_wiki': current_wiki,
              'live_validation': 'old registry deliberately rejects changed live definition files; use this frozen-context check for this historical run'}
    original_write(HERE / 'VERIFICATION.json', record)
    print(json.dumps({'wiki_changed': len(changed), 'wiki_added': len(added), 'frozen_verification': 'pass'}))


if __name__ == '__main__':
    main()
