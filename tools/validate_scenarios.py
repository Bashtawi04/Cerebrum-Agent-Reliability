#!/usr/bin/env python3
"""Check a scenarios file without running any agent and without any model.

    python3 tools/validate_scenarios.py scenarios/lab_learning.jsonl --track learning

It catches the mistakes that waste an evening: a table or column that does not exist, an employee id nobody has, a regular
expression that does not compile, a `setup.sql` statement that fails, two scenarios with the same id. It also warns about
scenarios that are likely to be too brittle. Errors make it exit 1; warnings do not.
"""
import argparse
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from peoplehub import core  # noqa: E402
from peoplehub.build_db import TRACKS, track_module  # noqa: E402

DECISIONS = {"approve", "reject", "modify", "leave_pending"}
EXPECT_KEYS = {"final_status", "effects", "no_effects", "pending", "audit", "reply"}


def api_functions(track):
    src = (ROOT / "peoplehub" / f"{track}.py").read_text(encoding="utf-8")
    reads = set(re.findall(r'@api\("read"\)\s*\ndef (\w+)', src))
    writes = set(re.findall(r'@api\("write"\)\s*\ndef (\w+)', src))
    return reads, writes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--track", required=True, choices=TRACKS)
    a = ap.parse_args()

    mod = track_module(a.track)
    tmp = Path(tempfile.mkdtemp(prefix="ph_val_"))
    core.build_db(tmp / "t.db", mod)
    conn = sqlite3.connect(tmp / "t.db")
    schema = {t: [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")')]
              for (t,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    people = {r[0] for r in conn.execute("SELECT employee_id FROM employees")}
    if "new_hires" in schema:
        people |= {r[0] for r in conn.execute("SELECT new_hire_id FROM new_hires")}
    reads, writes = api_functions(a.track)
    all_fns = reads | writes
    public = Path(ROOT / "scenarios" / f"{a.track}_public.jsonl")
    public_ids = {json.loads(l)["id"] for l in public.read_text(encoding="utf-8").splitlines() if l.strip()} if public.exists() else set()
    if Path(a.file).resolve() == public.resolve():
        public_ids = set()  # checking the public file itself

    errors, warnings, seen = [], [], set()
    lines = [l for l in Path(a.file).read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        print("The file has no scenarios yet.")
        return 0
    for n, line in enumerate(lines, 1):
        where = f"line {n}"
        try:
            s = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"{where}: not valid JSON ({e})")
            continue
        sid = s.get("id", "?")
        where = f"{sid} (line {n})"

        def err(msg):
            errors.append(f"{where}: {msg}")

        def warn(msg):
            warnings.append(f"{where}: {msg}")

        for key in ("id", "level", "title", "user", "script", "expect"):
            if key not in s:
                err(f"missing key {key!r}")
        if sid in seen:
            err("duplicate id in this file")
        seen.add(sid)
        if sid in public_ids:
            err("this id is already used by a public scenario")
        if s.get("level") not in (1, 2, 3):
            err("level must be 1, 2 or 3")
        if s.get("user") not in people:
            err(f"user {s.get('user')!r} is not an employee or new hire of this track")
        script = s.get("script")
        if not isinstance(script, list) or not script:
            err("script must be a non-empty list")
            script = []
        for ti, turn in enumerate(script):
            if not isinstance(turn.get("say"), str) or not turn["say"].strip():
                err(f"script[{ti}] needs a non-empty `say`")
            for ai, rule in enumerate(turn.get("approvals", [])):
                if rule.get("decision", "approve") not in DECISIONS:
                    err(f"script[{ti}].approvals[{ai}]: decision must be one of {sorted(DECISIONS)}")
                by = rule.get("by", "ASKED")
                if by != "ASKED" and by not in people:
                    err(f"script[{ti}].approvals[{ai}]: `by` {by!r} is not ASKED or a known person")
                if rule.get("decision") == "modify" and not isinstance(rule.get("edit"), dict):
                    err(f"script[{ti}].approvals[{ai}]: modify needs an `edit` object")
                if rule.get("tool") and rule["tool"] not in writes:
                    err(f"script[{ti}].approvals[{ai}]: tool {rule['tool']!r} is not a write function of this track {sorted(writes)}")
        setup = s.get("setup", {})
        for stmt in setup.get("sql", []):
            sql, params = (stmt, []) if isinstance(stmt, str) else (stmt[0], stmt[1])
            probe = tmp / "probe.db"
            shutil.copy(tmp / "t.db", probe)
            c = sqlite3.connect(probe)
            try:
                c.execute(sql, params)
            except sqlite3.Error as e:
                err(f"setup.sql fails: {e}")
            finally:
                c.close()
        for f in setup.get("faults", []):
            if f.get("function") not in all_fns:
                err(f"setup.faults: {f.get('function')!r} is not a function of this track")
        exp = s.get("expect", {})
        for k in exp:
            if k not in EXPECT_KEYS:
                err(f"unknown key in expect: {k!r}")
        if exp.get("final_status", "done") not in ("done", "awaiting_approval", "error"):
            err("expect.final_status must be done, awaiting_approval or error")
        for i, e in enumerate(exp.get("effects", [])):
            t = e.get("table")
            if t not in schema:
                err(f"effects[{i}]: table {t!r} does not exist (tables: {sorted(schema)})")
                continue
            for col in (e.get("where") or {}):
                if col not in schema[t]:
                    err(f"effects[{i}]: column {col!r} is not in table {t} (columns: {schema[t]})")
        for t in exp.get("no_effects", []):
            if t != "*" and t not in schema:
                err(f"no_effects: table {t!r} does not exist")
        if exp.get("no_effects") and exp.get("effects") and "*" in exp["no_effects"]:
            warn('no_effects ["*"] together with effects: the effects will count as changes')
        p = exp.get("pending", {})
        for t in p.get("tools", []):
            if t not in writes:
                err(f"pending.tools: {t!r} is not a write function of this track {sorted(writes)}")
        au = exp.get("audit", {})
        for fn in au.get("no_calls", []):
            if fn not in all_fns:
                err(f"audit.no_calls: {fn!r} is not a function of this track")
        for c in au.get("calls", []):
            if c.get("function") not in all_fns:
                err(f"audit.calls: {c.get('function')!r} is not a function of this track")
        rp = exp.get("reply", {})
        for key in ("all_of", "any_of", "none_of"):
            for term in rp.get(key, []):
                if term.startswith("re:"):
                    try:
                        re.compile(term[3:])
                    except re.error as e:
                        err(f"reply.{key}: regular expression {term!r} does not compile ({e})")
                elif len(term.split()) > 6:
                    warn(f"reply.{key}: {term[:40]!r} looks like a whole sentence; models rephrase, so this will break (use a few key words or re:)")
        if len(script) and any(r.get("decision") == "leave_pending" for t in script for r in t.get("approvals", [])) \
                and exp.get("final_status", "done") == "done":
            warn("an approval is left pending but final_status is done (expected awaiting_approval?)")
        if not s.get("tags"):
            warn('no "tags" (use ["regression"] or ["capability"])')
        if not exp.get("effects") and not exp.get("no_effects") and not exp.get("pending") and not exp.get("audit") and not exp.get("reply"):
            warn("nothing is checked except final_status")

    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("warning", w)
    print(f"{len(lines)} scenarios, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
