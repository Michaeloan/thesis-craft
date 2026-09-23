"""Read-only lexical comparison. No semantic or bibliographic verdicts."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import unicodedata

CITATION = re.compile(r"\[(?:\d+\s*(?:[-–—,，]\s*\d+\s*)*)\]")
# Deliberately finite unit vocabulary. Not a general scientific parser.
UNITS = (
    r"kWh/kWp(?:/a)?|元/kWh|元/W|kg\s*CO2/kWh|Mt\s*CO2(?:/a)?|"
    r"kWh(?:/a)?|MWh(?:/a)?|GWh(?:/a)?|TWh(?:/a)?|"
    r"kWp|MWp|GWp|kW|MW|GW|km2|m2|km²|m²|Mt|kg|"
    r"°C|°|%|元"
)
QUANTITY = re.compile(
    r"(?<![A-Za-z0-9_])[-+−]?(?:\d{1,3}(?:,\d{3})+|\d+)"
    r"(?:\.\d+)?(?:[eE][+-]?\d+)?(?:\s*(?:" + UNITS + r"))?"
)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).replace("−", "-")


def citations(text: str) -> Counter:
    return Counter(re.sub(r"\s+", "", m.group()) for m in CITATION.finditer(normalize(text)))


def quantities(text: str) -> Counter:
    text = CITATION.sub("", normalize(text))
    return Counter(re.sub(r"\s+", "", m.group()) for m in QUANTITY.finditer(text))


def changes(before: Counter, after: Counter) -> dict:
    return {"removed": dict(before - after), "added": dict(after - before)}


def audit(before: str, after: str, profile: dict | None = None) -> dict:
    if profile is None:
        profile = {}
    if not isinstance(profile, dict):
        raise ValueError("Profile must be a JSON object")
    phrases = profile.get("protected_phrases", [])
    if not isinstance(phrases, list) or any(not isinstance(p, str) or not p.strip() for p in phrases):
        raise ValueError("protected_phrases must be a list of non-empty strings")
    phrase_changes = [
        {"phrase": p, "before": before.count(p), "after": after.count(p)}
        for p in dict.fromkeys(phrases) if before.count(p) != after.count(p)
    ]
    numbers = changes(quantities(before), quantities(after))
    refs = changes(citations(before), citations(after))
    changed = bool(phrase_changes or any(numbers.values()) or any(refs.values()))
    return {
        "status": "review_needed" if changed else "no_lexical_changes",
        "quantity_changes": numbers,
        "citation_changes": refs,
        "protected_phrase_changes": phrase_changes,
        "length": {"before": len(before), "after": len(after)},
        "limitations": [
            "No semantic, factual, source-support or denominator validation.",
            "Matching quantities can still be assigned to different subjects.",
            "Unit vocabulary is finite; equivalent unit conversions may be flagged.",
            "Citation ranges are compared literally, not expanded.",
            "Protected phrases are literal occurrence counts, not immutable facts.",
            "Length is informational; it is not a quality score."
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON report; never overwrite an input")
    args = parser.parse_args(argv)
    try:
        inputs = {p.resolve() for p in (args.before, args.after, args.profile) if p is not None}
        if args.output and args.output.resolve() in inputs:
            raise ValueError("Report output must not overwrite an input")
        profile = json.loads(args.profile.read_text(encoding="utf-8-sig")) if args.profile else None
        report = audit(args.before.read_text(encoding="utf-8-sig"),
                       args.after.read_text(encoding="utf-8-sig"), profile)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 1 if report["status"] == "review_needed" else 0
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
