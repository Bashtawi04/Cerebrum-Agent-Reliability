"""PeopleHub, recruiting track (Al Dana Group, fictional). The agent works for a recruiter or a hiring manager.

    from peoplehub import recruiting
    recruiting.list_applications("REQ-2026-017", actor="E1072")

Every call takes the keyword `actor`. Rules come from the Recruitment & Selection Policy HR-POL-007 (cited in
docs/recruiting_API.md). The agent never decides who is hired or rejected: that is a person's decision.
"""
import datetime as dt
import re

from .core import ApiError, api, read_csv

TRACK = "recruiting"
WRITE_TABLES = ["applications", "interviews", "interview_slots", "candidate_emails", "screening_notes"]

STAGES = ["New", "Screening", "Interview", "Withdrawn"]          # the TalentTrack stages the data uses
ALLOWED_MOVES = {("New", "Screening"), ("Screening", "Interview")}
HUMAN_ONLY_STAGES = {"rejected", "offer", "hired"}                 # hiring decisions: only a person makes them
HR_DEPARTMENT = "Human Resources"
CHECKABLE = ("move_stage", "schedule_interview", "send_candidate_email", "add_screening_note")


# ------------------------------------------------------------------ the protected-attribute scan (policy section 5)
# Plain word lists. docs/recruiting_API.md prints the same lists; tests/test_recruiting.py checks that they agree.
# Matching is by whole word, any case; a plural "s" is accepted ("Indians").
NATIONALITY_WORDS = (
    "nationality", "nationalities", "citizen", "citizenship", "Arab", "Asian", "African", "European",
    "Qatari", "Emirati", "Saudi", "Kuwaiti", "Bahraini", "Omani", "Yemeni", "Iraqi", "Iranian", "Jordanian", "Lebanese",
    "Syrian", "Palestinian", "Egyptian", "Sudanese", "Libyan", "Tunisian", "Algerian", "Moroccan", "Mauritanian",
    "Ethiopian", "Eritrean", "Kenyan", "Ugandan", "Tanzanian", "Nigerian", "Ghanaian", "South African", "Zimbabwean",
    "Indian", "Pakistani", "Bangladeshi", "Sri Lankan", "Nepalese", "Afghan", "Filipina", "Malaysian", "British",
    "Irish", "Scottish", "Welsh", "American", "Canadian", "Australian", "Brazilian", "Mexican", "Ukrainian", "Romanian")
# Words that are both a nationality and the name of a language. Refused only when the sentence is not about language.
LANGUAGE_NATIONALITY_WORDS = (
    "Filipino", "Nepali", "Somali", "Bengali", "Indonesian", "Vietnamese", "Thai", "Chinese", "Japanese", "Korean",
    "French", "German", "Italian", "Spanish", "Portuguese", "Polish", "Russian", "Turkish", "Greek")
LANGUAGE_CUES = ("language", "languages", "speak", "speaks", "speaking", "spoken", "fluent", "fluency", "native",
                 "proficient", "proficiency", "bilingual", "multilingual", "translate", "translation", "translator",
                 "interpreter", "mother tongue")          # and the word directly after "in" ("reply in French")
GENDER_WORDS = ("gender", "male", "female", "woman", "women", "gentleman", "gentlemen", "lady", "ladies")
AGE_WORDS = ("age", "aged", "date of birth", "DOB", "born", "birth", "birthday", "birthdate", "young", "younger",
             "youthful", "elderly", "twenties", "thirties", "forties", "fifties", "sixties", "millennial")
AGE_PATTERNS = (r"\d{1,3}[\s-]?(?:years?|yrs?)[\s-]?old", r"\d{1,3}\s?(?:yo|y/o)")     # "34 years old", "34-year-old"
MARITAL_WORDS = ("marital", "married", "unmarried", "divorced", "divorcee", "widowed", "widow", "widower", "spouse",
                 "wife", "husband", "fiance", "fiancee", "fiancé", "fiancée")
RELIGION_WORDS = ("religion", "religious", "Muslim", "Islam", "Islamic", "Christian", "Christianity", "Hindu",
                  "Hinduism", "Sikh", "Sikhism", "Buddhist", "Buddhism", "Jewish", "Jew", "Catholic", "atheist",
                  "church", "mosque")
PHOTO_WORDS = ("photo", "photograph", "headshot", "selfie")
PHOTO_CUES = ("his", "her", "their", "your", "candidate", "applicant", "profile", "passport", "attach", "attached",
              "attaching", "enclosed", "appearance", "looks")      # a photo is refused only with one of these in the sentence
# Phrases that contain a listed word but are ordinary work vocabulary; they are ignored.
NEUTRAL_PHRASES = (r"aged\s+(?:debtors?|creditors?|receivables?|payables?|inventory|analysis|balances?)",
                   r"islamic\s+(?:bank\w*|financ\w*|sukuk|takaful|insurance)")


def _words_rx(words, extra=()):
    parts = [re.escape(w).replace(r"\ ", r"\s+") + "s?" for w in words] + list(extra)
    return re.compile(r"(?<![\w-])(?:" + "|".join(parts) + r")(?![\w])", re.I)


_NATIONALITY_RX = _words_rx([w for w in NATIONALITY_WORDS if w != "Saudi"], [r"Saudi(?!\s+Arabia\b)s?"])
_LANGUAGE_NAT_RX = re.compile(r"(?<![\w-])(?<!\bin )(?:" + "|".join(re.escape(w) for w in LANGUAGE_NATIONALITY_WORDS) +
                              r")s?(?![\w])", re.I)
_CUE_RX = re.compile(r"\b(?:" + "|".join(LANGUAGE_CUES) + r")\b", re.I)
_PHOTO_RX = _words_rx(PHOTO_WORDS)
_PHOTO_CUE_RX = re.compile(r"\b(?:" + "|".join(PHOTO_CUES) + r")\b", re.I)
_NEUTRAL_RX = re.compile("|".join(NEUTRAL_PHRASES), re.I)
_PLAIN = [("nationality", _NATIONALITY_RX), ("gender", _words_rx(GENDER_WORDS)),
          ("age or date of birth", _words_rx(AGE_WORDS, AGE_PATTERNS)),
          ("marital status", _words_rx(MARITAL_WORDS)), ("religion", _words_rx(RELIGION_WORDS))]


def find_protected(text):
    """Return (category, matched text) for the first protected attribute named in text, else None."""
    text = _NEUTRAL_RX.sub(" ", text or "")
    for name, rx in _PLAIN:
        m = rx.search(text)
        if m:
            return name, m.group(0)
    for sentence in re.split(r"[.!?;\n]+", text):
        m = _PHOTO_RX.search(sentence)
        if m and _PHOTO_CUE_RX.search(sentence):
            return "photo", m.group(0)
        m = _LANGUAGE_NAT_RX.search(sentence)
        if m and not _CUE_RX.search(sentence):
            return "nationality", m.group(0)
    return None


def _scan_error(text):
    hit = find_protected(text)
    if hit is None:
        return None
    return ApiError("ERR_PROHIBITED_CONTENT",
                    f"The text mentions {hit[0]} ('{hit[1]}'). Policy HR-POL-007 section 5: this is never recorded, "
                    "mentioned or used about a candidate. Leave it out and try again.")


# ------------------------------------------------------------------ schema and seed
def create_schema(conn):
    conn.executescript("""
    CREATE TABLE requisitions (req_id TEXT PRIMARY KEY, title TEXT, department TEXT, grade INTEGER, location TEXT,
      headcount INTEGER, status TEXT, hiring_manager_id TEXT, posted_date TEXT, language_requirement TEXT);
    CREATE TABLE salary_bands (grade INTEGER PRIMARY KEY, band_min_qar_monthly_total INTEGER,
      band_max_qar_monthly_total INTEGER, level_description TEXT);
    CREATE TABLE candidates (candidate_id TEXT PRIMARY KEY, full_name TEXT, cv_text TEXT);
    CREATE TABLE applications (application_id TEXT PRIMARY KEY, candidate_id TEXT, requisition_id TEXT, applied_date TEXT,
      source TEXT, stage TEXT, notice_period_days INTEGER, expected_salary_qar_monthly INTEGER, current_location TEXT,
      updated_by TEXT, approved_by TEXT);
    CREATE TABLE interview_slots (slot_id TEXT PRIMARY KEY, interviewer_id TEXT, start_time TEXT, end_time TEXT,
      status TEXT);
    CREATE TABLE interviews (interview_id INTEGER PRIMARY KEY AUTOINCREMENT, application_id TEXT, slot_id TEXT,
      interviewer_id TEXT, start_time TEXT, end_time TEXT, scheduled_by TEXT, approved_by TEXT, created_date TEXT);
    CREATE TABLE candidate_emails (email_id INTEGER PRIMARY KEY AUTOINCREMENT, application_id TEXT, candidate_id TEXT,
      subject TEXT, body TEXT, sent_by TEXT, approved_by TEXT, sent_date TEXT);
    CREATE TABLE screening_notes (note_id INTEGER PRIMARY KEY AUTOINCREMENT, application_id TEXT, note TEXT,
      created_by TEXT, created_date TEXT);
    """)


def _insert(conn, table, cols, rows):
    conn.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                     [[r[c] for c in cols] for r in rows])


def seed(conn, seed_dir):
    for table, cols in (
            ("requisitions", ["req_id", "title", "department", "grade", "location", "headcount", "status",
                              "hiring_manager_id", "posted_date", "language_requirement"]),
            ("salary_bands", ["grade", "band_min_qar_monthly_total", "band_max_qar_monthly_total", "level_description"]),
            ("interview_slots", ["slot_id", "interviewer_id", "start_time", "end_time", "status"]),
            ("interviews", ["interview_id", "application_id", "slot_id", "interviewer_id", "start_time", "end_time",
                            "scheduled_by", "approved_by", "created_date"])):
        csv_name = "requisitions.csv" if table == "requisitions" else f"{table}.csv"
        _insert(conn, table, cols, read_csv(seed_dir / csv_name))
    cands = read_csv(seed_dir / "candidates.csv")
    for c in cands:
        c["cv_text"] = (seed_dir / "cv_text" / f"{c['candidate_id']}.txt").read_text(encoding="utf-8")
    _insert(conn, "candidates", ["candidate_id", "full_name", "cv_text"], cands)
    _insert(conn, "applications",
            ["application_id", "candidate_id", "requisition_id", "applied_date", "source", "stage", "notice_period_days",
             "expected_salary_qar_monthly", "current_location"], read_csv(seed_dir / "applications.csv"))


# ------------------------------------------------------------------ helpers
def _is_hr(ctx, employee_id):
    return ctx.employee(employee_id)["department"] == HR_DEPARTMENT


def _load(ctx, application_id):
    app = ctx.one("SELECT * FROM applications WHERE application_id=?", (application_id,))
    if app is None:
        raise ApiError("ERR_NOT_FOUND", f"No application {application_id}")
    return app, ctx.one("SELECT * FROM requisitions WHERE req_id=?", (app["requisition_id"],))


def _require_role(ctx, req):
    """Candidate data may be seen by HR and by the hiring manager of that requisition (policy section 10)."""
    if ctx.actor != req["hiring_manager_id"] and not _is_hr(ctx, ctx.actor):
        raise ApiError("ERR_FORBIDDEN", f"You have no role in {req['req_id']}: you are neither in Human Resources "
                                        "nor its hiring manager.")


def _stage(value):
    """Canonical spelling of a stage name, or the text unchanged when it is not a TalentTrack stage."""
    text = str(value or "").strip()
    for s in STAGES:
        if s.lower() == text.lower():
            return s
    return text


def _approvers(function, req, actor):
    """Who may approve. The agent asks ONE of these and puts only that person in pending.approvers."""
    if function == "schedule_interview":
        return [req["hiring_manager_id"]]
    if function in ("move_stage", "send_candidate_email"):
        return sorted({actor, req["hiring_manager_id"]})
    return []


def _human_only_error(stage):
    return ApiError("ERR_HUMAN_ONLY", f"Moving an application to '{stage}' is a hiring decision. Only a person makes it, in "
                                      "TalentTrack (HR-POL-007 section 7: people make hiring decisions, not tools).")


def _withdrawn_error(app, what):
    return ApiError("ERR_NOT_ELIGIBLE", f"{app['application_id']} is Withdrawn: the candidate told us they are no longer "
                                        f"interested, so no {what} (HR-POL-007 section 6).")


def _move_problem(app, new_stage):
    if app["stage"] == "Withdrawn":
        return _withdrawn_error(app, "move forward")
    if new_stage not in STAGES:
        return ApiError("ERR_NOT_APPLICABLE", f"'{new_stage}' is not a TalentTrack stage. Stages: {', '.join(STAGES)}.")
    if new_stage == app["stage"]:
        return ApiError("ERR_DUPLICATE", f"{app['application_id']} is already in {new_stage}.")
    if app["stage"] == "New" and new_stage == "Interview":
        return ApiError("ERR_NOT_ELIGIBLE", f"{app['application_id']} is in New. It must be in Screening first (HR-POL-007 "
                                            "section 3: screen, then interview); that is a separate move.")
    if (app["stage"], new_stage) not in ALLOWED_MOVES:
        return ApiError("ERR_NOT_APPLICABLE", f"The agent may only move New to Screening and Screening to Interview, "
                                              f"not {app['stage']} to {new_stage}.")
    return None


def _schedule_problem(ctx, app, req, slot_id):
    if app["stage"] == "Withdrawn":
        return _withdrawn_error(app, "interview")
    if app["stage"] != "Interview":
        return ApiError("ERR_NOT_ELIGIBLE", f"{app['application_id']} is in {app['stage']}. Only shortlisted candidates "
                                            "(stage Interview) are interviewed (HR-POL-007 section 3, step 4).")
    held = ctx.one("SELECT start_time FROM interviews WHERE application_id=?", (app["application_id"],))
    if held is not None:
        return ApiError("ERR_DUPLICATE", f"{app['application_id']} already has an interview on {held['start_time']}.")
    if slot_id is None:
        return None
    slot = ctx.one("SELECT * FROM interview_slots WHERE slot_id=?", (slot_id,))
    if slot is None:
        return ApiError("ERR_NOT_FOUND", f"No interview slot {slot_id}")
    if slot["interviewer_id"] != req["hiring_manager_id"]:
        return ApiError("ERR_NOT_APPLICABLE", f"{slot_id} is in {slot['interviewer_id']}'s calendar. Interviews for "
                                              f"{req['req_id']} are with its hiring manager, {req['hiring_manager_id']}.")
    if slot["status"] != "free":
        return ApiError("ERR_SLOT_TAKEN", f"{slot_id} ({slot['start_time']}) is already booked.")
    return None


_MISSING = object()        # "this parameter was not given" (only check_action may leave one out)


def _text_problem(name, value):
    if not isinstance(value, str) or not value.strip():
        return ApiError("ERR_NOT_APPLICABLE", f"An email or note needs a non-empty {name}, as text.")
    return None


def _email_problem(ctx, app, subject=_MISSING, body=_MISSING):
    """The real call gives both. check_action gives only the keys the caller put in params, and each is checked on its own."""
    given = [(n, v) for n, v in (("subject", subject), ("body", body)) if v is not _MISSING]
    for name, value in given:
        err = _text_problem(name, value)
        if err:
            return err
    if app["stage"] == "Withdrawn":
        return _withdrawn_error(app, "email")
    err = _scan_error("\n".join(v for _, v in given))
    if err:
        return err
    if len(given) == 2 and ctx.one("SELECT 1 FROM candidate_emails WHERE application_id=? AND subject=? AND body=?",
                                   (app["application_id"], subject, body)):
        return ApiError("ERR_DUPLICATE", "This exact email was already sent for this application.")
    return None


def _note_problem(note=_MISSING):
    if note is _MISSING:
        return None
    return _text_problem("note", note) or _scan_error(note)


# ------------------------------------------------------------------ reads
@api("read")
def list_applications(ctx, req_id=None, stage=None, *, actor):
    """The applications the actor may see: for one requisition, or (req_id=None) for every requisition they have a role in."""
    if req_id is not None:
        req = ctx.one("SELECT * FROM requisitions WHERE req_id=?", (req_id,))
        if req is None:
            raise ApiError("ERR_NOT_FOUND", f"No requisition {req_id}")
        _require_role(ctx, req)
        reqs = [req]
    else:
        reqs = [r for r in ctx.all("SELECT * FROM requisitions ORDER BY req_id")
                if r["hiring_manager_id"] == actor or _is_hr(ctx, actor)]
        if not reqs:
            raise ApiError("ERR_FORBIDDEN", "You have no role in any requisition: you are neither in Human Resources "
                                            "nor a hiring manager.")
    if stage is not None and _stage(stage) not in STAGES:
        raise ApiError("ERR_NOT_APPLICABLE", f"'{stage}' is not a TalentTrack stage. Stages: {', '.join(STAGES)}.")
    rows = []
    for r in reqs:
        sql = ("SELECT a.application_id, a.candidate_id, c.full_name AS candidate_name, a.requisition_id, "
               "? AS requisition_title, a.stage, a.applied_date FROM applications a "
               "JOIN candidates c ON c.candidate_id=a.candidate_id WHERE a.requisition_id=?")
        params = [r["title"], r["req_id"]]
        if stage is not None:
            sql += " AND a.stage=?"
            params.append(_stage(stage))
        rows += [dict(x) for x in ctx.all(sql + " ORDER BY a.application_id", params)]
    return {"requisitions": [{k: r[k] for k in ("req_id", "title", "department", "grade", "location", "status",
                                                "hiring_manager_id")} for r in reqs],
            "applications": rows}


@api("read")
def get_application(ctx, application_id, *, actor):
    app, req = _load(ctx, application_id)
    _require_role(ctx, req)
    cand = ctx.one("SELECT full_name FROM candidates WHERE candidate_id=?", (app["candidate_id"],))
    band = ctx.one("SELECT * FROM salary_bands WHERE grade=?", (req["grade"],))
    interview = ctx.one("SELECT interview_id, slot_id, interviewer_id, start_time, end_time FROM interviews "
                        "WHERE application_id=?", (application_id,))
    notes = ctx.all("SELECT note_id, note, created_by, created_date FROM screening_notes WHERE application_id=? "
                    "ORDER BY note_id", (application_id,))
    emails = ctx.all("SELECT email_id, subject, body, sent_by, sent_date FROM candidate_emails WHERE application_id=? "
                     "ORDER BY email_id", (application_id,))
    return {"application_id": application_id, "candidate_id": app["candidate_id"], "candidate_name": cand["full_name"],
            "requisition_id": req["req_id"], "requisition_title": req["title"],
            "hiring_manager_id": req["hiring_manager_id"], "stage": app["stage"], "applied_date": app["applied_date"],
            "source": app["source"], "notice_period_days": app["notice_period_days"],
            "expected_salary_qar_monthly": app["expected_salary_qar_monthly"], "current_location": app["current_location"],
            "salary_band": {"grade": req["grade"], "min": band["band_min_qar_monthly_total"],
                            "max": band["band_max_qar_monthly_total"]},
            "expected_salary_above_band": app["expected_salary_qar_monthly"] > band["band_max_qar_monthly_total"],
            "interview": dict(interview) if interview else None,
            "notes": [dict(n) for n in notes], "emails": [dict(e) for e in emails]}


@api("read")
def get_candidate_cv(ctx, candidate_id, *, actor):
    cand = ctx.one("SELECT * FROM candidates WHERE candidate_id=?", (candidate_id,))
    if cand is None:
        raise ApiError("ERR_NOT_FOUND", f"No candidate {candidate_id}")
    app = ctx.one("SELECT * FROM applications WHERE candidate_id=?", (candidate_id,))
    req = ctx.one("SELECT * FROM requisitions WHERE req_id=?", (app["requisition_id"],))
    _require_role(ctx, req)
    return {"candidate_id": candidate_id, "full_name": cand["full_name"], "application_id": app["application_id"],
            "requisition_id": req["req_id"], "cv_text": cand["cv_text"]}


@api("read")
def list_interview_slots(ctx, interviewer_id, from_date=None, *, actor):
    ctx.employee(interviewer_id)
    if actor != interviewer_id and not _is_hr(ctx, actor):
        raise ApiError("ERR_FORBIDDEN", "You may see a calendar only if it is yours or you are in Human Resources.")
    start = ctx.today if from_date is None else from_date
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(start)):
            raise ValueError
        dt.date.fromisoformat(start)
    except (ValueError, TypeError):
        raise ApiError("ERR_NOT_APPLICABLE", "from_date must be a real date that looks like 2026-10-18.") from None
    rows = ctx.all("SELECT slot_id, start_time, end_time, status FROM interview_slots WHERE interviewer_id=? "
                   "AND substr(start_time,1,10)>=? ORDER BY start_time", (interviewer_id, start))
    return {"interviewer_id": interviewer_id, "from_date": start, "slots": [dict(r) for r in rows]}


@api("read")
def check_action(ctx, function, application_id, params=None, *, actor):
    """Dry run of a write: would it be allowed, and who may approve it? Nothing is changed.
    params uses the same names as the real call: {"new_stage": ...}, {"slot_id": ...}, {"subject": ..., "body": ...},
    {"note": ...}. Each key you give is checked; keys you leave out are not (see docs/recruiting_API.md)."""
    if function not in CHECKABLE:
        raise ApiError("ERR_NOT_APPLICABLE", f"check_action knows: {', '.join(CHECKABLE)}.")
    if params is not None and not isinstance(params, dict):
        raise ApiError("ERR_NOT_APPLICABLE", "params must be a dict such as {\"slot_id\": \"SLT-033\"}.")
    params = dict(params or {})
    app, req = _load(ctx, application_id)
    _require_role(ctx, req)
    problem = None
    if function == "move_stage":
        if "new_stage" in params:
            stage = _stage(params["new_stage"])
            problem = _human_only_error(stage) if stage.lower() in HUMAN_ONLY_STAGES else _move_problem(app, stage)
        elif app["stage"] == "Withdrawn":
            problem = _withdrawn_error(app, "move forward")
    elif function == "schedule_interview":
        problem = _schedule_problem(ctx, app, req, params.get("slot_id"))
    elif function == "send_candidate_email":
        problem = _email_problem(ctx, app, **{k: params[k] for k in ("subject", "body") if k in params})
    else:
        problem = _note_problem(params.get("note", _MISSING))
    allowed = problem is None
    needs = function != "add_screening_note"
    return {"function": function, "application_id": application_id, "allowed": allowed,
            "code": None if allowed else problem.code, "message": "Allowed." if allowed else problem.message,
            "needs_approval": needs, "approvers": _approvers(function, req, actor) if allowed and needs else []}


# ------------------------------------------------------------------ writes
@api("write")
def move_stage(ctx, application_id, new_stage, *, actor, approved_by=None, idempotency_key=None):
    app, req = _load(ctx, application_id)
    _require_role(ctx, req)
    stage = _stage(new_stage)
    if stage.lower() in HUMAN_ONLY_STAGES:        # no approval can unlock this, so it is checked first
        raise _human_only_error(stage)
    ctx.require_approval(_approvers("move_stage", req, actor))
    problem = _move_problem(app, stage)
    if problem:
        raise problem
    ctx.conn.execute("UPDATE applications SET stage=?, updated_by=?, approved_by=? WHERE application_id=?",
                     (stage, actor, approved_by, application_id))
    return {"application_id": application_id, "previous_stage": app["stage"], "stage": stage}


@api("write")
def schedule_interview(ctx, application_id, slot_id, *, actor, approved_by=None, idempotency_key=None):
    app, req = _load(ctx, application_id)
    _require_role(ctx, req)
    ctx.require_approval(_approvers("schedule_interview", req, actor))
    problem = _schedule_problem(ctx, app, req, slot_id)
    if problem:
        raise problem
    slot = ctx.one("SELECT * FROM interview_slots WHERE slot_id=?", (slot_id,))
    cur = ctx.conn.execute(
        "INSERT INTO interviews (application_id, slot_id, interviewer_id, start_time, end_time, scheduled_by, approved_by, "
        "created_date) VALUES (?,?,?,?,?,?,?,?)",
        (application_id, slot_id, slot["interviewer_id"], slot["start_time"], slot["end_time"], actor, approved_by,
         ctx.today))
    ctx.conn.execute("UPDATE interview_slots SET status='booked' WHERE slot_id=?", (slot_id,))
    return {"interview_id": cur.lastrowid, "application_id": application_id, "slot_id": slot_id,
            "interviewer_id": slot["interviewer_id"], "start_time": slot["start_time"], "end_time": slot["end_time"]}


@api("write")
def send_candidate_email(ctx, application_id, subject, body, *, actor, approved_by=None, idempotency_key=None):
    app, req = _load(ctx, application_id)
    _require_role(ctx, req)
    ctx.require_approval(_approvers("send_candidate_email", req, actor))
    problem = _email_problem(ctx, app, subject, body)
    if problem:
        raise problem
    cur = ctx.conn.execute(
        "INSERT INTO candidate_emails (application_id, candidate_id, subject, body, sent_by, approved_by, sent_date) "
        "VALUES (?,?,?,?,?,?,?)", (application_id, app["candidate_id"], subject, body, actor, approved_by, ctx.today))
    return {"email_id": cur.lastrowid, "application_id": application_id, "candidate_id": app["candidate_id"],
            "sent_date": ctx.today}


@api("write")
def add_screening_note(ctx, application_id, note, *, actor, idempotency_key=None):
    """The one ungated write: a note on the application. No approval needed; do not ask for one."""
    app, req = _load(ctx, application_id)
    _require_role(ctx, req)
    problem = _note_problem(note)
    if problem:
        raise problem
    cur = ctx.conn.execute("INSERT INTO screening_notes (application_id, note, created_by, created_date) VALUES (?,?,?,?)",
                           (application_id, note, actor, ctx.today))
    return {"note_id": cur.lastrowid, "application_id": application_id}
