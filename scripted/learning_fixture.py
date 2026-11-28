#!/usr/bin/env python3
"""A limited, model-free scenario fixture adapted from templates/scripted_learning.py.

Only LAB-LRN-01 and LAB-LRN-05 are validated with this fixture. It is not the frozen target or a general agent.

A scripted Learning agent: "book me on LD-nnn" (one or more courses in a message), with the two-round approval for fees above QAR 3,000.

SCRIPTED_MODE=good | eager (books at once with the first approver's id) | offers ("if you want, I can book it" instead of proposing)
| drops_second (only the first course of a message that names two)

    SCRIPTED_MODE=good python3 harness/run_scenarios.py --track learning --agent "python3 scripted/learning_fixture.py" \
        --scenarios scenarios/learning_public.jsonl --only LRN-04
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import scripted_base as base  # noqa: E402
from peoplehub import ApiError, learning as ln  # noqa: E402


def handle(user, message, history):
    ids = re.findall(r"LD-\d+", message)
    if not ids:
        return "done", "Tell me which course (for example LD-103) you want."
    cid, rest = ids[0], ids[1:]
    chk = ln.check_enrolment(user, cid, actor=user)
    if chk["mandatory"]:
        return "done", f"{cid} is a mandatory course: HR books it, I cannot."
    if not chk["eligible"]:
        return "done", f"I cannot book {cid}: " + "; ".join(r["code"] for r in chk["reasons"]) + "."
    sessions = [s for s in ln.list_sessions(cid, actor=user)["sessions"] if s["seats_left"] > 0]
    if not sessions:
        return "done", f"No session of {cid} has a seat left."
    approvers = [x["employee_id"] for x in chk["approvals_needed"]]
    if base.MODE == "offers":
        return "done", f"{cid} is possible. If you want, I can request it for you."
    if base.MODE == "eager":
        ln.request_enrolment(user, cid, sessions[0]["session_id"], actor=user, approved_by=approvers[0])
        return "done", f"Done: you are booked on {cid}."
    ask = {"tool": "request_enrolment", "args": {"employee_id": user, "course_id": cid, "session_id": sessions[0]["session_id"]},
           "rounds": [[a] for a in approvers], "text": f"Booking {cid} ({sessions[0]['session_id']}) needs approval."}
    if rest and base.MODE != "drops_second":
        ask["next"] = [f"book me on {c}" for c in rest]
    return "ask", ask


def execute(user, p, approved_by):
    for attempt in (1, 2):                                   # one retry for a temporary failure, with the same arguments
        try:
            ln.request_enrolment(**p["args"], actor=user, approved_by=approved_by, idempotency_key=f"scripted-{p['args']['course_id']}")
            return f"Done: you are booked on {p['args']['course_id']}."
        except ApiError as e:
            if not (e.retryable and attempt == 1):
                return f"I could not book it: {e.code}. Nothing was booked."


if __name__ == "__main__":
    base.run(handle, execute)
