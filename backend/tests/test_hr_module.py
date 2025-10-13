import re

from modules.hr_scottish.gates.accompaniment import AccompanimentGate
from modules.hr_scottish.gates.evidence import EvidenceGate
from modules.hr_scottish.gates.appeal import AppealGate
from modules.hr_scottish.gates.allegations import AllegationsGate
from modules.hr_scottish.gates.dismissal import DismissalGate
from modules.hr_scottish.gates.meeting_notice import MeetingNoticeGate
from modules.hr_scottish.gates.investigation import InvestigationGate
from modules.hr_scottish.gates.witness_statements import WitnessStatementsGate
from modules.hr_scottish.gates.meeting_notes import MeetingNotesGate
from modules.hr_scottish.gates.suspension import SuspensionGate
from modules.hr_scottish.gates.previous_warnings import PreviousWarningsGate
from modules.hr_scottish.gates.outcome_reasons import OutcomeReasonsGate
from modules.hr_scottish.gates.representation_choice import RepresentationChoiceGate
from modules.hr_scottish.gates.timeframes import TimeframesGate
from modules.hr_scottish.gates.consistency import ConsistencyGate


def test_accompaniment():
    g = AccompanimentGate()
    # PASS
    text = "Disciplinary hearing invitation. You have the right to be accompanied by a trade union representative."
    assert g.check(text, "letter")["status"] == "PASS"
    # FAIL (relevant but missing right)
    text = "You are invited to attend a disciplinary meeting."
    r = g.check(text, "letter")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("General memo about office", "memo")["status"] == "N/A"


def test_evidence():
    g = EvidenceGate()
    # PASS
    text = "You are invited to a disciplinary hearing; evidence is enclosed."
    assert g.check(text, "letter")["status"] == "PASS"
    # FAIL
    r = g.check("You are invited to a disciplinary hearing.", "letter")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("This is unrelated content", "memo")["status"] == "N/A"


def test_appeal():
    g = AppealGate()
    # PASS
    text = "The decision is final, but you have the right to appeal this outcome."
    assert g.check(text, "outcome")["status"] == "PASS"
    # FAIL
    r = g.check("Outcome: decision concluded with a final warning.", "outcome")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No outcome here", "memo")["status"] == "N/A"


def test_allegations():
    g = AllegationsGate()
    # PASS (has date)
    text = "Disciplinary allegations include conduct on 01/02/2024 at the office."
    assert g.check(text, "notice")["status"] == "PASS"
    # FAIL (vague terms, no dates)
    r = g.check("Disciplinary allegation: poor attitude and unacceptable behaviour.", "notice")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("General policy update", "memo")["status"] == "N/A"


def test_dismissal():
    g = DismissalGate()
    # PASS when no serious misconduct
    assert g.check("Disciplinary matter unrelated to gross misconduct.", "notice")["status"] == "PASS"
    # FAIL when gross misconduct without dismissal warning
    r = g.check("Disciplinary gross misconduct alleged for theft.", "notice")
    assert r["status"] == "FAIL"
    # PASS when gross misconduct with dismissal warning
    text = "Gross misconduct (theft). Potential outcome includes summary dismissal."
    assert g.check(text, "notice")["status"] == "PASS"


def test_meeting_notice():
    g = MeetingNoticeGate()
    # PASS (no short notice)
    assert g.check("Disciplinary hearing scheduled in two weeks.", "notice")["status"] == "PASS"
    # WARNING (very short notice)
    r = g.check("Disciplinary meeting is today; please attend immediately.", "notice")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No meetings discussed", "memo")["status"] == "N/A"


def test_investigation():
    g = InvestigationGate()
    # PASS
    text = "Disciplinary allegation of misconduct; following an investigation we found..."
    assert g.check(text, "notice")["status"] == "PASS"
    # FAIL (relevant but no investigation)
    r = g.check("Disciplinary allegation of breach in policy.", "notice")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("Unrelated newsletter", "memo")["status"] == "N/A"


def test_witness_statements():
    g = WitnessStatementsGate()
    # PASS
    text = "Disciplinary—manager observed the event; a witness statement is provided."
    assert g.check(text, "notice")["status"] == "PASS"
    # WARNING (no statements mentioned)
    r = g.check("Disciplinary matter reported by colleague.", "notice")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No disciplinary context", "memo")["status"] == "N/A"


def test_meeting_notes():
    g = MeetingNotesGate()
    # PASS
    assert g.check("A disciplinary hearing will have minutes recorded.", "notice")["status"] == "PASS"
    # WARNING (no notes mention)
    r = g.check("You are invited to a meeting regarding disciplinary matters.", "notice")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("General memo", "memo")["status"] == "N/A"


def test_suspension():
    g = SuspensionGate()
    # PASS
    assert g.check("You are suspended on full pay pending investigation.", "notice")["status"] == "PASS"
    # FAIL
    r = g.check("You are suspended without pay effective immediately.", "notice")
    assert r["status"] == "FAIL"
    # WARNING (unclear pay status)
    r = g.check("You are suspended pending investigation.", "notice")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No suspension", "memo")["status"] == "N/A"


def test_previous_warnings():
    g = PreviousWarningsGate()
    # PASS (gross misconduct -> warnings not required)
    assert g.check("Termination for gross misconduct.", "outcome")["status"] == "PASS"
    # PASS (previous warnings referenced)
    assert g.check("Dismissal following previous warning and earlier warning.", "outcome")["status"] == "PASS"
    # WARNING (no prior warnings referenced)
    r = g.check("Dismissal for misconduct.", "outcome")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No dismissal discussed", "memo")["status"] == "N/A"


def test_outcome_reasons():
    g = OutcomeReasonsGate()
    # PASS
    text = "Outcome decision: following investigation we found that policy was breached."
    assert g.check(text, "outcome")["status"] == "PASS"
    # FAIL
    r = g.check("Outcome decision: final warning issued.", "outcome")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No outcome noted", "memo")["status"] == "N/A"


def test_representation_choice():
    g = RepresentationChoiceGate()
    # PASS
    assert g.check("You may bring a representative of your choice.", "notice")["status"] == "PASS"
    # WARNING (restriction present)
    r = g.check("Representative must be HR approved.", "notice")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No companion reference", "memo")["status"] == "N/A"


def test_timeframes():
    g = TimeframesGate()
    # PASS reasonable timeframe
    assert g.check("You may appeal within 7 working days.", "outcome")["status"] == "PASS"
    # WARNING very short timeframe
    r = g.check("You must appeal within 24 hours.", "outcome")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No appeal mentioned", "memo")["status"] == "N/A"


def test_consistency():
    g = ConsistencyGate()
    # PASS
    assert g.check("In accordance with our disciplinary procedure.", "notice")["status"] == "PASS"
    # WARNING
    r = g.check("A disciplinary meeting is scheduled.", "notice")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No HR matters here", "memo")["status"] == "N/A"

