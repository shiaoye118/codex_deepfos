#!/usr/bin/env python3
"""Read-only, project-local DeepFOS knowledge helper for portable agents."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
from collections import Counter
from importlib import metadata, util
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = "1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_ROOT = PROJECT_ROOT / "agent"
MANIFEST_PATH = AGENT_ROOT / "manifest.json"
KB_ROOT = Path(os.environ.get("DEEPFOS_KB_ROOT", str(PROJECT_ROOT / "deepfos-knowledge"))).expanduser().resolve()
INDEX_PATH = KB_ROOT / "deepfos-index.sqlite"
USAGE_PATH = KB_ROOT / "usage-patterns.jsonl"
VERSION_CACHE_PATH = KB_ROOT / "version-cache.json"


class AgentError(Exception):
    """Expected CLI failure with a stable error code and process exit status."""

    def __init__(self, code: str, message: str, exit_code: int = 5) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code


class JsonArgumentParser(argparse.ArgumentParser):
    """Argument parser that returns the public JSON error contract on misuse."""

    def error(self, message: str) -> None:
        raise AgentError("E_USAGE", message, 2)


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise AgentError("E_NOT_FOUND", "File not found: {}".format(path), 4)
    except json.JSONDecodeError as exc:
        raise AgentError("E_INVALID_JSON", "Invalid JSON in {}: {}".format(path, exc), 4)
    if not isinstance(value, dict):
        raise AgentError("E_INVALID_JSON", "Expected a JSON object in {}".format(path), 4)
    return value


def _manifest() -> Dict[str, Any]:
    return _read_json(MANIFEST_PATH)


def _sdk_root() -> Optional[Path]:
    configured = os.environ.get("DEEPFOS_SDK_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    try:
        spec = util.find_spec("deepfos")
    except (ImportError, ValueError):
        spec = None
    if spec and spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations))).resolve()
    candidates = [
        PROJECT_ROOT / ".venv" / "lib" / "python{}.{}".format(sys.version_info.major, sys.version_info.minor) / "site-packages" / "deepfos",
        Path.home() / ".venv" / "lib" / "python{}.{}".format(sys.version_info.major, sys.version_info.minor) / "site-packages" / "deepfos",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    return None


def _connect() -> sqlite3.Connection:
    if not INDEX_PATH.is_file():
        raise AgentError("E_INDEX_MISSING", "Knowledge index missing: {}".format(INDEX_PATH), 4)
    try:
        con = sqlite3.connect(str(INDEX_PATH))
        con.row_factory = sqlite3.Row
        return con
    except sqlite3.Error as exc:
        raise AgentError("E_INDEX_OPEN", "Cannot open knowledge index: {}".format(exc), 4)


def _fts_query(text: str) -> str:
    parts = re.findall(r"[\w\u4e00-\u9fff]+", text, flags=re.UNICODE)
    if not parts:
        return '""'
    return " AND ".join('"{}"'.format(part.replace('"', '""')) for part in parts)


def _normalize_text(value: Any, limit: int = 1000) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


def _installed_sdk_version() -> str:
    try:
        return metadata.version("deepfos")
    except metadata.PackageNotFoundError:
        return "unknown"


def _cache_versions() -> Tuple[Optional[str], Optional[str]]:
    if not VERSION_CACHE_PATH.is_file():
        return None, None
    try:
        data = json.loads(VERSION_CACHE_PATH.read_text(encoding="utf-8"))
        versions = data.get("versions") or []
        return (str(versions[0]) if versions else None, data.get("fetched_at"))
    except (OSError, ValueError, TypeError):
        return None, None


def cmd_describe(_: argparse.Namespace) -> Dict[str, Any]:
    manifest = _manifest()
    sdk_root = _sdk_root()
    return {
        "manifest": manifest,
        "runtime": {
            "project_root": str(PROJECT_ROOT),
            "knowledge_root": str(KB_ROOT),
            "index_path": str(INDEX_PATH),
            "usage_path": str(USAGE_PATH),
            "sdk_root": str(sdk_root) if sdk_root else None,
            "sdk_available": bool(sdk_root and sdk_root.is_dir()),
            "python": sys.version.split()[0],
            "platform": sys.platform,
        },
    }


def cmd_doctor(_: argparse.Namespace) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str, critical: bool = True) -> None:
        checks.append({"name": name, "ok": bool(ok), "critical": critical, "detail": detail})

    add("project_root", PROJECT_ROOT.is_dir(), str(PROJECT_ROOT))
    add("manifest", MANIFEST_PATH.is_file(), str(MANIFEST_PATH))

    manifest: Dict[str, Any] = {}
    manifest_ok = False
    if MANIFEST_PATH.is_file():
        try:
            manifest = _manifest()
            manifest_ok = manifest.get("schema_version") == SCHEMA_VERSION
        except AgentError as exc:
            add("manifest_contract", False, exc.message)
        else:
            add("manifest_contract", manifest_ok, "schema_version={}".format(manifest.get("schema_version")))
    else:
        add("manifest_contract", False, "manifest missing")

    add("knowledge_root", KB_ROOT.is_dir(), str(KB_ROOT))
    add("knowledge_index", INDEX_PATH.is_file(), str(INDEX_PATH))

    docs_count = 0
    symbols_count = 0
    if INDEX_PATH.is_file():
        try:
            con = _connect()
            tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
            schema_ok = {"docs_meta", "docs_fts", "symbols_meta", "symbols_fts"}.issubset(tables)
            add("index_schema", schema_ok, "required docs/symbol tables")
            if schema_ok:
                docs_count = int(con.execute("SELECT COUNT(*) FROM docs_meta").fetchone()[0])
                symbols_count = int(con.execute("SELECT COUNT(*) FROM symbols_meta").fetchone()[0])
            con.close()
        except (AgentError, sqlite3.Error) as exc:
            add("index_query", False, str(exc))
        else:
            add("docs_content", docs_count > 0, "{} documents".format(docs_count))
            add("symbols_content", symbols_count > 0, "{} symbols".format(symbols_count))
    else:
        add("index_schema", False, "index missing")
        add("docs_content", False, "index missing")
        add("symbols_content", False, "index missing")

    skill_info = manifest.get("skill") if isinstance(manifest, dict) else None
    skill_rel = skill_info.get("path") if isinstance(skill_info, dict) else None
    skill_path = PROJECT_ROOT / skill_rel if skill_rel else None
    add("project_skill", bool(skill_path and skill_path.is_file()), str(skill_path) if skill_path else "manifest skill path missing")

    sdk_root = _sdk_root()
    add("sdk_source", bool(sdk_root and sdk_root.is_dir()), str(sdk_root) if sdk_root else "set DEEPFOS_SDK_ROOT if needed", critical=False)
    add("ripgrep", shutil.which("rg") is not None, shutil.which("rg") or "optional; Python fallback is used", critical=False)
    add("network_policy", True, "all built-in commands are read-only and make no network calls")

    critical_ok = all(item["ok"] for item in checks if item["critical"])
    warnings = [item["name"] for item in checks if not item["ok"] and not item["critical"]]
    return {
        "healthy": critical_ok,
        "checks": checks,
        "warnings": warnings,
        "stats": {"documents": docs_count, "symbols": symbols_count},
    }


def cmd_docs(args: argparse.Namespace) -> Dict[str, Any]:
    con = _connect()
    query = args.query.strip()
    if not query:
        raise AgentError("E_USAGE", "docs query cannot be empty", 2)
    rows: List[sqlite3.Row] = []
    if len(query) >= 3:
        try:
            rows = con.execute(
                """
                SELECT m.route, m.title, m.path,
                       snippet(docs_fts, 4, '[', ']', ' … ', 28) AS excerpt
                FROM docs_fts JOIN docs_meta m ON m.id = docs_fts.rowid
                WHERE docs_fts MATCH ?
                ORDER BY bm25(docs_fts)
                LIMIT ?
                """,
                (_fts_query(query), args.limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    if not rows:
        tokens = re.findall(r"[\w\u4e00-\u9fff]+", query, flags=re.UNICODE) or [query]
        clauses: List[str] = []
        params: List[Any] = []
        for token in tokens:
            like = "%{}%".format(token)
            clauses.append("(title LIKE ? OR body LIKE ? OR path LIKE ?)")
            params.extend([like, like, like])
        params.append(args.limit)
        rows = con.execute(
            """
            SELECT route, title, path, substr(body, 1, 420) AS excerpt
            FROM docs_meta
            WHERE {}
            ORDER BY length(body)
            LIMIT ?
            """.format(" AND ".join(clauses)),
            params,
        ).fetchall()
    con.close()
    results = [
        {
            "title": row["title"],
            "route": row["route"],
            "path": row["path"],
            "excerpt": _normalize_text(row["excerpt"], 900),
        }
        for row in rows
    ]
    return {"query": query, "count": len(results), "results": results, "source": str(INDEX_PATH)}


def cmd_symbols(args: argparse.Namespace) -> Dict[str, Any]:
    con = _connect()
    query = args.query.strip()
    if not query:
        raise AgentError("E_USAGE", "symbols query cannot be empty", 2)
    rows = con.execute(
        """
        SELECT * FROM symbols_meta
        WHERE qualified_name = ? OR name = ?
        ORDER BY CASE WHEN qualified_name = ? THEN 0 ELSE 1 END
        LIMIT ?
        """,
        (query, query, query, args.limit),
    ).fetchall()
    if not rows:
        try:
            rows = con.execute(
                """
                SELECT m.* FROM symbols_fts JOIN symbols_meta m ON m.id = symbols_fts.rowid
                WHERE symbols_fts MATCH ?
                ORDER BY bm25(symbols_fts)
                LIMIT ?
                """,
                (_fts_query(query), args.limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    if not rows:
        like = "%{}%".format(query)
        rows = con.execute(
            "SELECT * FROM symbols_meta WHERE qualified_name LIKE ? OR name LIKE ? OR args LIKE ? LIMIT ?",
            (like, like, like, args.limit),
        ).fetchall()
    con.close()
    results = [
        {
            "kind": row["kind"],
            "qualified_name": row["qualified_name"],
            "name": row["name"],
            "module": row["module"],
            "args": row["args"],
            "is_async": bool(row["is_async"]),
            "doc": _normalize_text(row["doc"], 1000),
        }
        for row in rows
    ]
    return {"query": query, "count": len(results), "results": results, "source": str(INDEX_PATH)}


def _iter_python_files(root: Path):
    ignored = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}
    for current, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [name for name in dirnames if name not in ignored]
        for filename in filenames:
            if filename.endswith(".py"):
                yield Path(current) / filename


def _source_search(root: Path, term: str, remaining: int, max_per_file: int) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    if not root.is_dir() or remaining <= 0:
        return matches
    for path in _iter_python_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        per_file = 0
        for line_number, line in enumerate(text.splitlines(), 1):
            if term in line:
                matches.append(
                    {
                        "root": str(root),
                        "path": str(path),
                        "line": line_number,
                        "text": line.strip()[:500],
                    }
                )
                per_file += 1
                remaining -= 1
                if per_file >= max_per_file or remaining <= 0:
                    break
        if remaining <= 0:
            break
    return matches


def cmd_source(args: argparse.Namespace) -> Dict[str, Any]:
    query = args.query.strip()
    if not query:
        raise AgentError("E_USAGE", "source query cannot be empty", 2)
    roots: List[Path] = []
    sdk_root = _sdk_root()
    if sdk_root:
        roots.append(sdk_root)
    project_root = Path(os.environ.get("DEEPFOS_PROJECT_ROOT", str(PROJECT_ROOT))).expanduser().resolve()
    if args.project:
        roots.append(project_root)
    results: List[Dict[str, Any]] = []
    for root in roots:
        results.extend(_source_search(root, query, args.limit - len(results), args.max_per_file))
        if len(results) >= args.limit:
            break
    return {
        "query": query,
        "count": len(results),
        "results": results,
        "roots": [str(root) for root in roots],
        "note": "Only SDK source is searched unless --project is supplied; business-code roots are never scanned implicitly.",
    }


def cmd_review(_: argparse.Namespace) -> Dict[str, Any]:
    counts: Counter = Counter()
    examples: Dict[str, str] = {}
    if USAGE_PATH.is_file():
        for line in USAGE_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            pattern = str(item.get("pattern") or "uncategorized")
            counts[pattern] += 1
            examples.setdefault(pattern, _normalize_text(item.get("summary"), 300))
    results = []
    for pattern, count in counts.most_common():
        results.append(
            {
                "pattern": pattern,
                "count": count,
                "example": examples.get(pattern, ""),
                "suggest_skill": count >= 3,
            }
        )
    return {"count": len(results), "results": results, "source": str(USAGE_PATH)}


def cmd_version(_: argparse.Namespace) -> Dict[str, Any]:
    latest, fetched_at = _cache_versions()
    sdk_root = _sdk_root()
    return {
        "installed_sdk": _installed_sdk_version(),
        "latest_cached_documentation": latest,
        "cache_fetched_at": fetched_at,
        "sdk_root": str(sdk_root) if sdk_root else None,
        "sdk_available": bool(sdk_root and sdk_root.is_dir()),
        "authority": "Use the installed SDK and current project code for runtime behavior; cached documentation is context only.",
        "network_called": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description="Read-only DeepFOS agent CLI with a stable JSON contract.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("describe", help="Describe the project adapter and runtime paths").set_defaults(func=cmd_describe, name="describe")
    sub.add_parser("doctor", help="Validate portable project prerequisites").set_defaults(func=cmd_doctor, name="doctor")

    docs = sub.add_parser("docs", help="Search local product documentation")
    docs.add_argument("query")
    docs.add_argument("--limit", type=int, default=5)
    docs.set_defaults(func=cmd_docs, name="docs")

    symbols = sub.add_parser("symbols", help="Search local SDK symbol signatures")
    symbols.add_argument("query")
    symbols.add_argument("--limit", type=int, default=5)
    symbols.set_defaults(func=cmd_symbols, name="symbols")

    source = sub.add_parser("source", help="Search installed SDK source; opt in to project source")
    source.add_argument("query")
    source.add_argument("--limit", type=int, default=80)
    source.add_argument("--max-per-file", type=int, default=3)
    source.add_argument("--project", action="store_true")
    source.set_defaults(func=cmd_source, name="source")

    sub.add_parser("review", help="Review reusable workflow patterns").set_defaults(func=cmd_review, name="review")
    sub.add_parser("version", help="Show local SDK and cached documentation versions").set_defaults(func=cmd_version, name="version")
    return parser


def _emit(payload: Dict[str, Any], pretty: bool) -> None:
    if pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def main(argv: Optional[List[str]] = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    pretty = "--pretty" in raw
    raw = [item for item in raw if item not in {"--json", "--pretty"}]
    try:
        args = build_parser().parse_args(raw)
        if getattr(args, "limit", 1) < 1:
            raise AgentError("E_USAGE", "--limit must be at least 1", 2)
        if getattr(args, "max_per_file", 1) < 1:
            raise AgentError("E_USAGE", "--max-per-file must be at least 1", 2)
        data = args.func(args)
        _emit({"ok": True, "data": data, "error": None}, pretty)
        return 0
    except AgentError as exc:
        _emit(
            {
                "ok": False,
                "data": None,
                "error": {"code": exc.code, "message": exc.message},
            },
            pretty,
        )
        return exc.exit_code
    except KeyboardInterrupt:
        _emit({"ok": False, "data": None, "error": {"code": "E_INTERRUPTED", "message": "Interrupted"}}, pretty)
        return 130
    except Exception as exc:
        _emit(
            {
                "ok": False,
                "data": None,
                "error": {"code": "E_INTERNAL", "message": "{}: {}".format(type(exc).__name__, exc)},
            },
            pretty,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
