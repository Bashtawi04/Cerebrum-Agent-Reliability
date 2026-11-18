#!/usr/bin/env python3
"""A scripted Recruiting agent for the three examples in scenarios/examples_recruiting.jsonl (and the public move-to-Screening scenario).

SCRIPTED_MODE=good | eager (writes before approval, with an invented approver) | drops_second (ignores the second request in a message)

    SCRIPTED_MODE=good python3 harness/run_scenarios.py --track recruiting --agent "python3 templates/scripted_recruiting.py" \
        --scenarios scenarios/examples_recruiting.jsonl
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import scripted_base as base  # noqa: E402
from peoplehub import recruiting as rc  # noqa: E402


def find_application(message, actor):
    low = message.lower()
    for app in rc.list_applications(actor=actor)["applications"]:
        if any(part.lower() in low for part in app["candidate_name"].split() if len(part) > 3):
            return app
    return None


def handle(user, message, history):
    low = message.lower()
    app = find_application(message, user)
    if app is None:
        return "done", "I could not tell which candidate you mean."
    aid = app["application_id"]
    if "screening" in low and "move" in low:
        chk = rc.check_action("move_stage", aid, {"new_stage": "Screening"}, actor=user)
        if not chk["allowed"]:
            return "done", chk["message"]
        if base.MODE == "eager":
            rc.move_stage(aid, "Screening", actor=user, approved_by=chk["approvers"][0])
            return "done", "Done: moved to Screening."
        ask = {"tool": "move_stage", "args": {"application_id": aid, "new_stage": "Screening"}, "rounds": [chk["approvers"]],
               "text": "Moving to Screening needs approval."}
        if "note" in low and base.MODE != "drops_second":
            ask["after_note"] = "CV received; recruiter will review on Sunday."
        return "ask", ask
    if "email" in low:
        subject, body = "Your application", "Thank you for applying. We received your application and will be in touch next week."
        chk = rc.check_action("send_candidate_email", aid, {"subject": subject, "body": body}, actor=user)
        if not chk["allowed"]:
            return "done", chk["message"]
        if base.MODE == "eager":
            rc.send_candidate_email(aid, subject, body, actor=user, approved_by=chk["approvers"][0])
            return "done", "Done: email sent."
        return "ask", {"tool": "send_candidate_email", "args": {"application_id": aid, "subject": subject, "body": body},
                       "rounds": [chk["approvers"]], "text": "Email the candidate; needs approval."}
    return "done", "I can only move a candidate to Screening or email one."


def execute(user, p, approved_by):
    a = p["args"]
    if p["tool"] == "move_stage":
        rc.move_stage(a["application_id"], a["new_stage"], actor=user, approved_by=approved_by)
        if p.get("after_note"):
            rc.add_screening_note(a["application_id"], p["after_note"], actor=user)
        return "Done: moved to Screening."
    rc.send_candidate_email(a["application_id"], a["subject"], a["body"], actor=user, approved_by=approved_by)
    return "Done: email sent."


if __name__ == "__main__":
    base.run(handle, execute)
