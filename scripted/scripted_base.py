"""The command-line contract in about 80 lines, for scripted (model-free) agents. The three scripted_<track>.py files use it.

You write two small functions and call run(handle, execute):

    handle(user, message, history) -> ("done", text)
                                   or ("ask", {"tool": ..., "args": {...}, "rounds": [[ids who may approve round 1], [round 2], ...],
                                               "text": "what to tell the user", "next": ["another request from the same message", ...]})
    execute(user, pending, approved_by) -> text       # called once every round is approved; do the real write here

`next` is for a message that asks for several things: after the first is approved and done, the base feeds the next one back to handle().
SCRIPTED_MODE (an environment variable) lets one file hold a correct agent and wrong variants: read base.MODE in your handlers.
See harness/README.md for the contract itself.
"""
import argparse
import json
import os
import sys
from pathlib import Path

MODE = os.environ.get("SCRIPTED_MODE", "good")
STATE_DIR = Path(os.environ.get("AGENT_STATE_DIR", ".agent_state"))


def out(status, message, pending=None):
    print(json.dumps({"status": status, "message": message, "pending": pending}))
    sys.exit(0)


def _file(thread):
    return STATE_DIR / f"{thread}.json"


def load(thread):
    return json.loads(_file(thread).read_text()) if _file(thread).exists() else None


def save(thread, state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _file(thread).write_text(json.dumps(state))


def _ask(state, thread, ask, prefix=""):
    p = {**ask, "round": 0, "approved": [], "next": ask.get("next", [])}   # keeps any extra keys your handler put in `ask`
    state["pending"] = p
    save(thread, state)
    out("awaiting_approval", (prefix + " " + ask["text"]).strip(),
        {"tool": p["tool"], "args": p["args"], "approvers": p["rounds"][0], "summary": ask["text"]})


def _step(handle, thread, state, message, prefix=""):
    res = handle(state["user"], message, state["history"])
    if res[0] == "ask":
        _ask(state, thread, res[1], prefix)
    state["pending"] = None
    save(thread, state)
    out("done", (prefix + " " + res[1]).strip())


def run(handle, execute):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["start", "say", "resume"])
    ap.add_argument("--thread", required=True)
    ap.add_argument("--user")
    ap.add_argument("--message")
    ap.add_argument("--decision")
    ap.add_argument("--by")
    ap.add_argument("--edit")
    a = ap.parse_args()
    if a.cmd in ("start", "say"):
        state = load(a.thread) if a.cmd == "say" else None
        if a.cmd == "say" and state is None:
            out("error", "No conversation with this id; use start first.")
        if a.cmd == "say" and state.get("pending"):
            out("error", "A request in this conversation is still waiting for approval.")
        state = state or {"user": a.user, "history": [], "pending": None}
        state["history"].append(a.message)
        _step(handle, a.thread, state, a.message)
    state = load(a.thread)
    p = state.get("pending") if state else None
    if not p:
        out("error", "Nothing is waiting for approval in this conversation.")
    if a.decision == "reject":
        state["pending"] = None
        save(a.thread, state)
        out("done", "Understood, nothing was changed.")
    if a.by not in p["rounds"][p["round"]]:
        out("awaiting_approval", f"{a.by} may not approve this step.", {"tool": p["tool"], "args": p["args"], "approvers": p["rounds"][p["round"]],
                                                                       "summary": p["text"]})
    if a.decision == "modify" and a.edit:
        p["args"].update(json.loads(a.edit))
    p["approved"].append(a.by)
    p["round"] += 1
    if p["round"] < len(p["rounds"]):
        save(a.thread, state)
        out("awaiting_approval", f"{a.by} approved. One more approval is needed.",
            {"tool": p["tool"], "args": p["args"], "approvers": p["rounds"][p["round"]], "summary": p["text"]})
    text = execute(state["user"], p, ",".join(p["approved"]))
    nxt = p.get("next", [])
    state["pending"] = None
    if nxt:
        state["history"].append(nxt[0])
        res = handle(state["user"], nxt[0], state["history"])
        if res[0] == "ask":
            res[1]["next"] = nxt[1:] + res[1].get("next", [])
            _ask(state, a.thread, res[1], text)
        text = (text + " " + res[1]).strip()
    save(a.thread, state)
    out("done", text)
