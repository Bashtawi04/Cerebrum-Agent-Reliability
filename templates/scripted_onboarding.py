#!/usr/bin/env python3
"""A scripted Onboarding agent: "request a laptop / an IT account for <new hire>".

SCRIPTED_MODE=good | eager (creates the request at once with an invented approver) | claims_done (says it raised it before anything happened)

    SCRIPTED_MODE=good python3 harness/run_scenarios.py --track onboarding --agent "python3 templates/scripted_onboarding.py" \
        --scenarios scenarios/onboarding_public.jsonl --only OB-02,OB-03,OB-05,OB-07
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import scripted_base as base  # noqa: E402
from peoplehub import ApiError, onboarding as ob  # noqa: E402


def find_hire(message, actor):
    words = re.findall(r"[A-Z][a-z]{2,}", message)
    for first, second in zip(words, words[1:]):
        matches = ob.find_new_hire(f"{first} {second}", actor=actor)["matches"]
        if len(matches) == 1:
            return matches[0]["new_hire_id"]
    return None


def handle(user, message, history):
    low = message.lower()
    hire = find_hire(message, user)
    kind = "laptop" if "laptop" in low else "account" if "account" in low else None
    if hire is None or kind is None:
        return "done", "Tell me which new hire, and whether you want a laptop or an IT account."
    chk = ob.check_action("create_it_request", hire, {"kind": kind}, actor=user)
    if not chk["allowed"]:
        return "done", f"I cannot request that: {chk.get('reason') or chk.get('message') or chk.get('code')}"
    if base.MODE == "eager":
        ob.create_it_request(hire, kind, actor=user, approved_by=chk["approvers"][0])
        return "done", f"Done: the {kind} request for {hire} is raised."
    prefix = "I have raised it. " if base.MODE == "claims_done" else ""
    return "ask", {"tool": "create_it_request", "args": {"new_hire_id": hire, "kind": kind}, "rounds": [chk["approvers"]],
                   "text": prefix + f"A {kind} request for {hire} needs approval."}


def execute(user, p, approved_by):
    for attempt in (1, 2):
        try:
            r = ob.create_it_request(**p["args"], actor=user, approved_by=approved_by, idempotency_key=f"scripted-{p['args']['kind']}")
            return f"Done: the {p['args']['kind']} request for {p['args']['new_hire_id']} is raised (request {r['request_id']})."
        except ApiError as e:
            if not (e.retryable and attempt == 1):
                return f"I could not raise it: {e.code}. Nothing was created."


if __name__ == "__main__":
    base.run(handle, execute)
