"""Build portable skill and source archives, excluding local thesis data and runtime files."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def archive(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for source, target in sorted(entries, key=lambda pair: pair[1]):
            info = zipfile.ZipInfo(target, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, source.read_bytes())
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise RuntimeError("Archive integrity check failed")
    return {"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "files": len(entries), "bytes": path.stat().st_size}


def build():
    skill = ROOT / "skills/thesis-craft"
    version = re.search(r'version:\s*"([^"]+)"', (skill / "SKILL.md").read_text(encoding="utf-8")).group(1)
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Unexpected version format")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    ignored = {"__pycache__", ".thesis-craft", ".validation-deps", "outputs", "local", ".git", ".venv", "dist"}
    allowed_roots = {"skills", "tools"}
    allowed_files = {"README.md", ".gitignore", "LICENSE", "NOTICE.md"}
    allowed_docs = {"docs/R09_VALIDATION_PUBLIC.md", "docs/SOURCES.md", "docs/VALIDATION_STATUS.json"}
    source_entries, skill_entries = [], []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if not path.is_file() or path.is_symlink() or set(rel.parts) & ignored:
            continue
        if path.name.endswith((".pyc", ".codex-write")) or path.name.startswith((".env", "~$")):
            continue
        if rel.parts[0] in allowed_roots or str(rel) in allowed_files or rel.as_posix() in allowed_docs:
            source_entries.append((path, "thesis-craft-project/" + rel.as_posix()))
        if path.is_relative_to(skill):
            skill_entries.append((path, "thesis-craft/" + path.relative_to(skill).as_posix()))
    reports = [archive(dist / f"thesis-craft-{version}.zip", skill_entries),
               archive(dist / f"thesis-craft-{version}-source.zip", source_entries)]
    status_file = ROOT / "docs" / "VALIDATION_STATUS.json"
    evaluation = json.loads(status_file.read_text(encoding="utf-8")) if status_file.exists() else {}
    if evaluation.get("version") != version:
        evaluation = {}
    manifest = {"version": version, "archives": reports,
                "model_comparison": evaluation.get("model_comparison", "not_run"),
                "evaluation_report": evaluation.get("report")}
    (dist / f"manifest-{version}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
