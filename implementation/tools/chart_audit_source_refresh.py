"""Read-only source extraction for the 2026-09-11 chart-audit refresh.

All generated material goes to the audit report directory.  Filename/post
associations are candidates until a human/vision review confirms them.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "sources/x-raw-2026-09-11"
OUT = ROOT / "implementation/reports/phase1-live/chart-audit/source-recheck-2026-09-11"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pixel_identity(data):
    with Image.open(io.BytesIO(data)) as image:
        rgb = image.convert("RGB")
        return {"size": list(rgb.size), "rgb_sha256": sha(rgb.tobytes())}


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    candidates = []
    posts = []
    for pdf in sorted(RAW.glob("*.pdf")):
        doc = fitz.open(pdf)
        folder = OUT / "new-source-figures" / pdf.stem
        folder.mkdir(parents=True, exist_ok=True)
        current_post = None
        for pno, page in enumerate(doc, 1):
            blocks = sorted(page.get_text("dict")["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            text = page.get_text(sort=True)
            (folder / f"p{pno:03d}.txt").write_text(text)
            page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(folder / f"p{pno:03d}.png")
            image_number = 0
            for bi, block in enumerate(blocks):
                if block["type"] == 0:
                    block_text = "\n".join("".join(s["text"] for s in line["spans"]) for line in block["lines"])
                    if "PART C — Remaining cached charts" in block_text:
                        current_post = None
                    patterns = [r"GMT[^\n]*?·\s*id\s+(\d{15,})"] if pdf.stem.startswith("JJumbo") else [r"(?:^|\n)id:\s*(\d{15,})"]
                    for pattern in patterns:
                        for match in re.finditer(pattern, block_text):
                            current_post = match.group(1)
                            posts.append({"pdf": str(pdf.relative_to(ROOT)), "page": pno, "post_id": current_post})
                    continue
                if block["type"] != 1:
                    continue
                image_number += 1
                artifact = folder / f"p{pno:03d}-i{image_number:02d}.{block['ext']}"
                artifact.write_bytes(block["image"])
                following_text = []
                for nb in blocks[bi + 1:]:
                    if nb["type"] == 1:
                        break
                    t = "\n".join("".join(s["text"] for s in line["spans"]) for line in nb.get("lines", []))
                    following_text.append(t)
                names = re.findall(r"(?<![/\w-])([\w-]+\.(?:png|jpg|jpeg))\b", "\n".join(following_text))
                captions = list(dict.fromkeys(names))
                row = {"pdf": str(pdf.relative_to(ROOT)), "page": pno, "image": image_number,
                       "post_id_candidate": current_post, "caption_candidates": captions,
                       "bbox": block["bbox"], "artifact": str(artifact.relative_to(ROOT)),
                       "sha256": sha(block["image"]), **pixel_identity(block["image"]),
                       "reviewed": False}
                candidates.append(row)
    zip_path = RAW / "JJumboFX_media_v2.zip"
    zip_rows = []
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            data = archive.read(member)
            source = RAW / "JJumboFX_media_v2" / member.filename
            row = {"zip_member": member.filename, "sha256": sha(data), "size": len(data),
                   "unpacked_file": str(source.relative_to(ROOT)),
                   "unpacked_equal": source.exists() and sha(source.read_bytes()) == sha(data)}
            if Path(member.filename).suffix.lower() in {".png", ".jpg", ".jpeg"}:
                row.update(pixel_identity(data))
                row["caption_matches"] = [{"pdf": c["pdf"], "page": c["page"], "image": c["image"],
                    "post_id_candidate": c["post_id_candidate"], "pixel_exact": c["rgb_sha256"] == row["rgb_sha256"],
                    "source_size": row["size"], "pdf_image_size": c["size"]}
                    for c in candidates if Path(member.filename).name in c["caption_candidates"]]
            zip_rows.append(row)
    (OUT / "new_figure_candidates.json").write_text(json.dumps(candidates, indent=2) + "\n")
    (OUT / "new_post_boundaries.json").write_text(json.dumps(posts, indent=2) + "\n")
    (OUT / "zip_caption_candidates.json").write_text(json.dumps(zip_rows, indent=2) + "\n")
    print(json.dumps({"figures": len(candidates), "post_boundaries": len(posts), "zip_files": len(zip_rows),
                      "unpacked_identical": sum(r["unpacked_equal"] for r in zip_rows),
                      "image_files": sum("caption_matches" in r for r in zip_rows),
                      "exact_caption_image_matches": sum(any(m["pixel_exact"] for m in r.get("caption_matches", [])) for r in zip_rows)}, indent=2))


if __name__ == "__main__":
    prepare()
