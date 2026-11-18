"""resume, end to end: approval, re-check, write, and what happens when the process dies half-way."""
import contextlib
import io
import json
from argparse import Namespace
from unittest import mock

from helpers import FreshDB

import agent_cli
from agent import approval, executor, policy, state as store

BOOK = {"employee_id": "E1012", "course_id": "LD-103", "session_id": "LD-103-S1"}


class Crash(BaseException):
    """The process dies here. BaseException, so no `except Exception` in our code can catch it."""


class TestResume(FreshDB):
    def open_request(self, thread="T1", user="E1012"):
        """A saved conversation with a request waiting on round 0, as `start` would leave it."""
        st = store.new(user)
        st["pending"] = approval.open_request(policy.plan("request_enrolment", BOOK, user))
        store.save(thread, st)

    def resume(self, by, decision="approve", thread="T1"):
        """Run `resume` like the CLI does and return the one JSON object it prints."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            agent_cli.resume(Namespace(thread=thread, decision=decision, by=by, edit=None))
        return json.loads(out.getvalue())

    def bookings(self):
        return self.sql("SELECT approved_by FROM enrolments WHERE status='booked'")

    # ---------------------------------------------------------------- the happy path, for reference
    def test_approve_books_once(self):
        self.open_request()
        reply = self.resume("E1008")
        self.assertEqual(reply["status"], "done")
        self.assertEqual(self.bookings(), [{"approved_by": "E1008"}])

    # ---------------------------------------------------------------- issue 1: interrupted execution
    def test_crash_before_the_write_then_resume_books_once(self):
        self.open_request()
        with mock.patch.object(executor, "execute", side_effect=Crash):
            with self.assertRaises(Crash):
                self.resume("E1008")
        self.assertEqual(self.bookings(), [])  # the process died before PeopleHub saw anything

        reply = self.resume("E1008")  # the same command, run again
        self.assertEqual(reply["status"], "done")
        self.assertIn("booked", reply["message"])
        self.assertEqual(self.bookings(), [{"approved_by": "E1008"}])
        self.assertIsNone(store.load("T1")["pending"])

    def test_crash_after_the_write_then_resume_reports_the_booking(self):
        self.open_request()
        real_execute = executor.execute

        def write_then_die(*args, **kwargs):
            real_execute(*args, **kwargs)  # PeopleHub commits the booking...
            raise Crash                   # ...and we die before saving that we know it

        with mock.patch.object(executor, "execute", side_effect=write_then_die):
            with self.assertRaises(Crash):
                self.resume("E1008")
        self.assertEqual(len(self.bookings()), 1)

        reply = self.resume("E1008")
        self.assertEqual(reply["status"], "done")
        self.assertIn("booked", reply["message"])
        self.assertNotIn("Nothing was booked", reply["message"])
        self.assertEqual(len(self.bookings()), 1)  # still one: the same key was reused
        st = store.load("T1")
        self.assertIsNone(st["pending"])
        self.assertEqual(st["writes"], 1)

    # ---------------------------------------------------------------- issue 2: approvers change
    def test_new_manager_is_asked_when_the_manager_changes(self):
        self.open_request()                                     # waiting on E1008
        self.sql("UPDATE employees SET manager_id='E1010' WHERE employee_id='E1012'")

        reply = self.resume("E1008")                            # the OLD manager says yes
        self.assertEqual(reply["status"], "awaiting_approval")
        self.assertEqual(reply["pending"]["approvers"], ["E1010"])
        self.assertEqual(self.bookings(), [])
        self.assertEqual(self.audit("request_enrolment"), [])  # PeopleHub was never asked to refuse

        reply = self.resume("E1010")                            # the NEW manager says yes
        self.assertEqual(reply["status"], "done")
        self.assertEqual(self.bookings(), [{"approved_by": "E1010"}])