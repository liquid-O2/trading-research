"""Restore losslessly compressed/split export files; does not run research."""
from pathlib import Path
import gzip
import hashlib
import json
import os

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'EXPORT_MANIFEST.json').read_text())
for record in manifest['compressed'] + manifest['split_files']:
    destination = (root / record['path']).resolve()
    if not destination.is_relative_to(root):
        raise ValueError('Destination is outside this repository')
    digest = hashlib.sha256()
    temporary = destination.with_name(destination.name + '.restore-tmp')
    with temporary.open('wb') as output:
        sources = record.get('parts', [record.get('stored_path')])
        for source in sources:
            source_path = (root / source).resolve()
            if not source_path.is_relative_to(root):
                raise ValueError('Source is outside this repository')
            opener = gzip.open if 'stored_path' in record else open
            with opener(source_path, 'rb') as stream:
                while chunk := stream.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
    if digest.hexdigest() != record['restored_sha256']:
        temporary.unlink()
        raise ValueError('Checksum mismatch: ' + record['path'])
    os.replace(temporary, destination)
    print('Restored', record['path'])
