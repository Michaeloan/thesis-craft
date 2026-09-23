"""Read-only DOCX object inventory; does not render, edit or certify preservation."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
PART = re.compile(r"word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$")
TAGS = {
    f"{{{W}}}p": "paragraphs",
    f"{{{W}}}tbl": "tables",
    f"{{{M}}}oMath": "equations",
    f"{{{W}}}bookmarkStart": "bookmarks",
    f"{{{W}}}fldSimple": "simple_fields",
    f"{{{W}}}drawing": "drawings",
    f"{{{W}}}pict": "legacy_pictures",
    f"{{{W}}}ins": "insertions",
    f"{{{W}}}del": "deletions",
    f"{{{W}}}moveFrom": "moves_from",
    f"{{{W}}}moveTo": "moves_to",
    f"{{{W}}}comment": "comments",
    f"{{{W}}}sectPr": "sections",
    f"{{{W}}}altChunk": "alt_chunks",
}


def inspect(path: Path) -> dict:
    totals = Counter({v: 0 for v in TAGS.values()})
    totals["complex_fields"] = 0
    parts = {}
    with zipfile.ZipFile(path) as package:
        names = package.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP member names; inventory is ambiguous")
        if "word/document.xml" not in names:
            raise ValueError("Not a supported DOCX: word/document.xml is absent")
        selected = [n for n in names if PART.fullmatch(n)]
        if sum(package.getinfo(n).file_size for n in selected) > 32 * 1024 * 1024:
            raise ValueError("XML inventory exceeds the 32 MiB inspection limit")
        for name in sorted(selected):
            root = ET.fromstring(package.read(name))
            counts = Counter()
            for node in root.iter():
                if node.tag in TAGS:
                    counts[TAGS[node.tag]] += 1
                if node.tag == f"{{{W}}}fldChar" and node.get(f"{{{W}}}fldCharType") == "begin":
                    counts["complex_fields"] += 1
            parts[name] = dict(counts)
            totals.update(counts)
        media = [n for n in names if n.startswith("word/media/") and not n.endswith("/")]
    return {
        "file": str(path.resolve()),
        "status": "inventory_only",
        "parts": parts,
        "totals": dict(totals),
        "media_files": len(media),
        "limitations": [
            "No page rendering, content comparison or relationship integrity verification.",
            "Counts do not prove objects are unchanged or correctly displayed.",
            "Alternate chunks, embedded files and unsupported XML vocabularies are not traversed.",
            "Paragraphs include text boxes and other nested paragraphs in selected parts.",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.resolve() == args.docx.resolve():
            raise ValueError("Report output must not overwrite the document")
        report = inspect(args.docx)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
