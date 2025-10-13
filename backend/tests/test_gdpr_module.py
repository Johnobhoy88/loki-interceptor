import re

from modules.gdpr_uk.gates.consent import ConsentGate
from modules.gdpr_uk.gates.purpose import PurposeGate
from modules.gdpr_uk.gates.retention import RetentionGate
from modules.gdpr_uk.gates.rights import RightsGate
from modules.gdpr_uk.gates.security import SecurityGate
from modules.gdpr_uk.gates.lawful_basis import LawfulBasisGate
from modules.gdpr_uk.gates.data_minimisation import DataMinimisationGate
from modules.gdpr_uk.gates.third_party_sharing import ThirdPartySharingGate
from modules.gdpr_uk.gates.international_transfer import InternationalTransferGate
from modules.gdpr_uk.gates.automated_decisions import AutomatedDecisionsGate
from modules.gdpr_uk.gates.children_data import ChildrenDataGate
from modules.gdpr_uk.gates.breach_notification import BreachNotificationGate
from modules.gdpr_uk.gates.dpo_contact import DpoContactGate
from modules.gdpr_uk.gates.cookies_tracking import CookiesTrackingGate
from modules.gdpr_uk.gates.withdrawal_consent import WithdrawalConsentGate


def test_consent():
    g = ConsentGate()
    # PASS
    text = "We collect personal data. By using this service you consent to processing."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("We process personal data for our services.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No data matters here", "memo")["status"] == "N/A"


def test_purpose():
    g = PurposeGate()
    # PASS
    text = "We process data for the following purposes: account management and support."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("We process user data.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("Nothing about processing here", "memo")["status"] == "N/A"


def test_retention():
    g = RetentionGate()
    # PASS
    text = "We retain data for 12 months and then delete it."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("Our privacy policy describes data handling.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No retention mentioned", "memo")["status"] == "N/A"


def test_rights():
    g = RightsGate()
    # PASS (list several rights)
    text = "Privacy notice: You have the right to access, rectification, erasure, and data portability."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL (insufficient rights mentioned)
    r = g.check("Privacy: you may contact us for help.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No privacy policy", "memo")["status"] == "N/A"


def test_security():
    g = SecurityGate()
    # PASS
    text = "We protect personal data with encryption and access controls."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("Data protection is important to us.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No security context", "memo")["status"] == "N/A"


def test_lawful_basis():
    g = LawfulBasisGate()
    # PASS
    text = "We process personal information where necessary for contract performance."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("We process data for our services.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No processing mentioned", "memo")["status"] == "N/A"


def test_data_minimisation():
    g = DataMinimisationGate()
    # PASS
    text = "We collect data and only the minimum necessary for the purpose."
    assert g.check(text, "privacy")["status"] == "PASS"
    # WARNING (no minimisation statement)
    r = g.check("We collect user data for service.", "privacy")
    assert r["status"] in ("WARNING",)
    # N/A
    assert g.check("No collection here", "memo")["status"] == "N/A"


def test_third_party_sharing():
    g = ThirdPartySharingGate()
    # PASS (no 3rd parties)
    assert g.check("Privacy policy without sharing.", "privacy")["status"] == "PASS"
    # FAIL (mentions sharing but no disclosure)
    r = g.check("We share data with third parties.", "privacy")
    assert r["status"] == "FAIL"
    # PASS (disclosed)
    text = "We share data with third parties including: service providers."
    assert g.check(text, "privacy")["status"] == "PASS"
    # N/A
    assert g.check("No privacy", "memo")["status"] == "N/A"


def test_international_transfer():
    g = InternationalTransferGate()
    # PASS (no transfers)
    assert g.check("No international transfers of data are made.", "privacy")["status"] == "PASS"
    # FAIL (mention transfer without safeguards)
    r = g.check("We transfer data outside the UK.", "privacy")
    assert r["status"] == "FAIL"
    # PASS (with safeguards)
    text = "We transfer data outside the EU with standard contractual clauses."
    assert g.check(text, "privacy")["status"] == "PASS"
    # N/A
    assert g.check("No transfers discussed", "memo")["status"] == "N/A"


def test_automated_decisions():
    g = AutomatedDecisionsGate()
    # PASS (disclosure)
    text = "We use AI profiling; automated decisions are applied in credit checks."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL (AI mentioned without disclosure)
    r = g.check("Our service uses AI and machine learning.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No automation here", "memo")["status"] == "N/A"


def test_children_data():
    g = ChildrenDataGate()
    # PASS
    text = "Children under 16 require parental consent and age verification."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("This service is for children.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("Adults only", "memo")["status"] == "N/A"


def test_breach_notification():
    g = BreachNotificationGate()
    # PASS
    text = "In case of a data breach we will notify the ICO."
    assert g.check(text, "privacy")["status"] == "PASS"
    # WARNING
    r = g.check("Our privacy commitments are outlined.", "privacy")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No privacy matters", "memo")["status"] == "N/A"


def test_dpo_contact():
    g = DpoContactGate()
    # PASS
    text = "Contact our Data Protection Officer at dpo@company.com."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("See our privacy policy.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No privacy here", "memo")["status"] == "N/A"


def test_cookies_tracking():
    g = CookiesTrackingGate()
    # PASS (no cookies)
    assert g.check("Our website discusses content only.", "privacy")["status"] == "PASS"
    # WARNING (cookies mentioned without controls)
    r = g.check("We use cookies and analytics on our website.", "privacy")
    assert r["status"] == "WARNING"
    # PASS (with controls)
    text = "We use cookies; you can manage cookie settings and opt out."
    assert g.check(text, "privacy")["status"] == "PASS"
    # N/A
    assert g.check("No website info", "memo")["status"] == "N/A"


def test_withdrawal_consent():
    g = WithdrawalConsentGate()
    # PASS
    text = "You can withdraw consent at any time by unsubscribing."
    assert g.check(text, "privacy")["status"] == "PASS"
    # FAIL
    r = g.check("This page discusses consent.", "privacy")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No consent here", "memo")["status"] == "N/A"

