"""CLI for a local thesis workspace. Run with --help; no model API required."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile
from project_core import Project, read_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Thesis workspace, not the installed skill")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    imp = sub.add_parser("import")
    imp.add_argument("source", type=Path)
    imp.add_argument("--kind", choices=("file", "pasted"), default="file")
    imp.add_argument("--profile", type=Path)
    ctx = sub.add_parser("context")
    ctx.add_argument("--unit", required=True)
    ctx.add_argument("--task", required=True)
    ctx.add_argument("--mode", choices=("polish", "strengthen", "structure", "review"), default="polish")
    ctx.add_argument("--budget", type=int, default=24000)
    ctx.add_argument("--start", type=int)
    ctx.add_argument("--end", type=int)
    rec = sub.add_parser("record")
    action = rec.add_mutually_exclusive_group(required=True)
    action.add_argument("--context")
    action.add_argument("--note", type=Path)
    action.add_argument("--withdraw", help="Withdraw a candidate from active review without deleting history")
    rec.add_argument("--candidate", type=Path)
    rec.add_argument("--review", type=Path, help="JSON with checks and issues")
    rec.add_argument("--author-confirmed", action="store_true")
    rec.add_argument("--decision")
    sub.add_parser("status")
    sub.add_parser("resume")
    exp = sub.add_parser("export")
    exp.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    p = Project(args.project)
    try:
        if args.command == "init":
            result = p.init()
        else:
            with p.lock():
                if args.command == "import":
                    result = p.import_source(args.source, args.kind, args.profile)
                elif args.command == "context":
                    result = p.make_context(args.unit, args.task, args.mode, args.budget, args.start, args.end)
                    if "id" in result:
                        # Return locations and diagnostics; the full packet is on disk.
                        result = {k: v for k, v in result.items() if k != "packet"}
                        result["context_file"] = str(p.folder / "contexts" / (result["id"] + ".md"))
                elif args.command == "record":
                    if args.note:
                        result = p.record_note(read_json(args.note), args.author_confirmed)
                    elif args.withdraw:
                        result = p.withdraw(args.withdraw, args.decision)
                    else:
                        if not args.candidate:
                            raise ValueError("--candidate is required with --context")
                        review = read_json(args.review) if args.review else {}
                        if not isinstance(review, dict):
                            raise ValueError("Review must be an object")
                        result = p.record_revision(args.context, args.candidate.read_text(encoding="utf-8-sig"),
                                                   review.get("checks"), review.get("issues"),
                                                   args.author_confirmed, args.decision)
                elif args.command == "status":
                    result = p.status()
                elif args.command == "resume":
                    result = p.resume()
                else:
                    result = p.export(args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 3 if result.get("status") == "split_required" else 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
