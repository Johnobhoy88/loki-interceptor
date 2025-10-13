import re

from modules.nda_uk.gates.protected_whistleblowing import ProtectedWhistleblowingGate
from modules.nda_uk.gates.protected_crime_reporting import ProtectedCrimeReportingGate
from modules.nda_uk.gates.protected_harassment import ProtectedHarassmentGate
from modules.nda_uk.gates.definition_specificity import DefinitionSpecificityGate
from modules.nda_uk.gates.public_domain_exclusion import PublicDomainExclusionGate
from modules.nda_uk.gates.prior_knowledge_exclusion import PriorKnowledgeExclusionGate
from modules.nda_uk.gates.duration_reasonableness import DurationReasonablenessGate
from modules.nda_uk.gates.permitted_disclosures import PermittedDisclosuresGate
from modules.nda_uk.gates.governing_law import GoverningLawGate
from modules.nda_uk.gates.consideration import ConsiderationGate
from modules.nda_uk.gates.return_destruction import ReturnDestructionGate
from modules.nda_uk.gates.gdpr_compliance import GdprComplianceGate
from modules.nda_uk.gates.parties_identified import PartiesIdentifiedGate
from modules.nda_uk.gates.permitted_purpose import PermittedPurposeGate


def test_protected_whistleblowing():
    g = ProtectedWhistleblowingGate()
    # PASS
    text = "This NDA: Nothing prevents making a protected disclosure under the Public Interest Disclosure Act."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL (blanket ban, no carveout)
    r = g.check("NDA: You shall not disclose to any third party under any circumstances.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("General memo", "memo")["status"] == "N/A"


def test_protected_crime_reporting():
    g = ProtectedCrimeReportingGate()
    # PASS (exception present)
    text = "Nothing prevents you from reporting criminal offences to police."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL (prohibition)
    r = g.check("You must not report incidents to authorities.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No NDA context", "memo")["status"] == "N/A"


def test_protected_harassment():
    g = ProtectedHarassmentGate()
    # PASS
    text = "Nothing prevents disclosure of harassment or discrimination under the Equality Act."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL
    r = g.check("Do not make any allegation about the employer.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No settlement terms", "memo")["status"] == "N/A"


def test_definition_specificity():
    g = DefinitionSpecificityGate()
    # PASS (specific categories)
    text = '"Confidential Information" means the items listed, including: trade secrets, financial data, and customer lists.'
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL (overbroad)
    r = g.check("Confidential information includes all information of any kind concerning business.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No confidentiality language", "memo")["status"] == "N/A"


def test_public_domain_exclusion():
    g = PublicDomainExclusionGate()
    # PASS
    text = "Confidential Information does not include information in the public domain or generally available to the public."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL
    r = g.check("Confidential information must remain secret at all times.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("Irrelevant text", "memo")["status"] == "N/A"


def test_prior_knowledge_exclusion():
    g = PriorKnowledgeExclusionGate()
    # PASS
    text = "Confidential Information excludes information already known by the Recipient prior to disclosure."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL
    r = g.check("Confidential information includes everything provided.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No confidentiality present", "memo")["status"] == "N/A"


def test_duration_reasonableness():
    g = DurationReasonablenessGate()
    # PASS (reasonable duration)
    assert g.check("Confidential obligations continue for 3 years.", "nda")["status"] == "PASS"
    # WARNING (perpetual)
    r = g.check("Confidentiality obligations apply indefinitely in perpetuity.", "nda")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No confidential context", "memo")["status"] == "N/A"


def test_permitted_disclosures():
    g = PermittedDisclosuresGate()
    # PASS
    text = "Recipient may disclose as required by law, court order, or regulatory authority."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL
    r = g.check("Confidential means never disclose for any reason.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No confidentiality terms", "memo")["status"] == "N/A"


def test_governing_law():
    g = GoverningLawGate()
    # PASS
    assert g.check("This Agreement shall be governed by the laws of England and Wales.", "nda")["status"] == "PASS"
    # FAIL
    r = g.check("This agreement shall be governed by applicable laws.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No agreement context here", "memo")["status"] == "N/A"


def test_consideration():
    g = ConsiderationGate()
    # PASS (English unilateral with deed)
    text = "This NDA is under England law and executed as a deed and signed in the presence of a witness."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL (English unilateral without deed or consideration)
    r = g.check("Under England law, unilateral NDA with disclosure only.", "nda")
    assert r["status"] == "FAIL"
    # N/A (Scotland)
    assert g.check("This NDA is governed by Scots law in Scotland.", "nda")["status"] == "N/A"


def test_return_destruction():
    g = ReturnDestructionGate()
    # PASS
    text = "Upon request, Recipient shall return or destroy all Confidential Information."
    assert g.check(text, "nda")["status"] == "PASS"
    # WARNING
    r = g.check("Confidential Information must be protected.", "nda")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No confidentiality here", "memo")["status"] == "N/A"


def test_gdpr_compliance():
    g = GdprComplianceGate()
    # PASS
    text = "Employee personal data will be processed in accordance with UK GDPR and data protection law."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL
    r = g.check("Employee personal data may be shared.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No personal data involved", "memo")["status"] == "N/A"


def test_parties_identified():
    g = PartiesIdentifiedGate()
    # PASS
    text = "This Agreement is made between ABC Ltd (12345) and XYZ Ltd (67890)."
    assert g.check(text, "nda")["status"] == "PASS"
    # FAIL
    r = g.check("This agreement is entered into on the date below.", "nda")
    assert r["status"] == "FAIL"
    # N/A
    assert g.check("No agreement terms", "memo")["status"] == "N/A"


def test_permitted_purpose():
    g = PermittedPurposeGate()
    # PASS
    text = "Recipient shall use Confidential Information solely for the purpose of evaluating a potential transaction."
    assert g.check(text, "nda")["status"] == "PASS"
    # WARNING (no purpose stated)
    r = g.check("Confidential Information must be kept secret.", "nda")
    assert r["status"] == "WARNING"
    # N/A
    assert g.check("No confidential info", "memo")["status"] == "N/A"

