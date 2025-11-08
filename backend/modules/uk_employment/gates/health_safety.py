import re


class HealthSafetyGate:
    """
    Health and Safety at Work Act 1974 + RIDDOR 2013 (2025 updates)
    Covers: Risk assessments, H&S policies, RIDDOR compliance, employer duties
    """
    def __init__(self):
        self.name = "health_safety"
        self.severity = "critical"
        self.legal_source = "Health and Safety at Work Act 1974, RIDDOR 2013, Management of H&S at Work Regulations 1999"

    def _is_relevant(self, text):
        """Check if document relates to health and safety"""
        text_lower = text.lower()
        keywords = [
            'health and safety', 'health & safety', 'h&s', 'h and s',
            'risk assessment', 'hazard', 'accident', 'injury',
            'riddor', 'reportable', 'incident', 'near miss',
            'ppe', 'personal protective equipment',
            'safe working', 'safety policy', 'safety procedure'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to health and safety',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. EMPLOYER'S GENERAL DUTIES (HSWA 1974 s.2)
        duty_patterns = [
            r'employer.*(?:duty|obligation|responsibility)',
            r'so\s+far\s+as\s+(?:is\s+)?reasonably\s+practicable',
            r'ensure.*health.*safety.*employees',
            r'provide.*safe\s+(?:system|place)\s+of\s+work'
        ]

        has_duty = any(re.search(p, text, re.IGNORECASE) for p in duty_patterns)

        if has_duty:
            # Check for "so far as is reasonably practicable" (SFAIRP)
            sfairp_patterns = [
                r'so\s+far\s+as\s+(?:is\s+)?reasonably\s+practicable',
                r'SFAIRP',
                r'reasonably\s+practicable'
            ]

            has_sfairp = any(re.search(p, text, re.IGNORECASE) for p in sfairp_patterns)
            # Good practice to include SFAIRP qualifier

        # 2. HEALTH AND SAFETY POLICY (required for 5+ employees)
        policy_patterns = [
            r'health\s+and\s+safety\s+policy',
            r'h&s\s+policy',
            r'safety\s+policy\s+statement'
        ]

        has_policy = any(re.search(p, text, re.IGNORECASE) for p in policy_patterns)

        if has_policy:
            # Check for three parts of policy
            policy_components = {
                'statement': r'(?:general\s+)?(?:policy\s+)?statement',
                'organisation': r'organisation.*(?:responsibilities|roles)',
                'arrangements': r'arrangements.*(?:implementing|practice|procedures)'
            }

            missing_components = []
            for component, pattern in policy_components.items():
                if not re.search(pattern, text, re.IGNORECASE):
                    missing_components.append(component)

            if len(missing_components) >= 2:
                warnings.append('H&S policy should include: statement of intent, organisation/responsibilities, arrangements for implementation')

            # Check for review date
            review_patterns = [
                r'review(?:ed)?\s+(?:date|annually|yearly|on)',
                r'last\s+review(?:ed)?',
                r'next\s+review\s+date',
                r'review\s+(?:at\s+least\s+)?(?:annually|yearly|every\s+year)'
            ]

            has_review = any(re.search(p, text, re.IGNORECASE) for p in review_patterns)
            if not has_review:
                warnings.append('H&S policy should be reviewed regularly (at least annually)')

            # Check for signature
            signature_patterns = [
                r'signed',
                r'signature',
                r'(?:managing\s+director|CEO|director).*(?:date|signed)'
            ]

            has_signature = any(re.search(p, text, re.IGNORECASE) for p in signature_patterns)
            if not has_signature:
                warnings.append('H&S policy should be signed by senior management')

        # 3. RISK ASSESSMENTS (Management of H&S at Work Regulations 1999 Reg 3)
        risk_assessment_patterns = [
            r'risk\s+assessment',
            r'assess.*risks?',
            r'hazard.*(?:identification|assessment)',
            r'identify.*hazards?'
        ]

        has_risk_assessment = any(re.search(p, text, re.IGNORECASE) for p in risk_assessment_patterns)

        if has_risk_assessment:
            # Check for 5 steps of risk assessment
            five_steps = {
                'identify_hazards': r'identify(?:ing)?\s+(?:the\s+)?hazards?',
                'who_harmed': r'who\s+(?:might|could)\s+be\s+harmed',
                'evaluate': r'evaluat(?:e|ing)\s+(?:the\s+)?risks?',
                'controls': r'(?:control\s+measures?|precautions?|mitigat)',
                'review': r'review\s+(?:and\s+)?(?:update|revise)'
            }

            steps_found = 0
            for step, pattern in five_steps.items():
                if re.search(pattern, text, re.IGNORECASE):
                    steps_found += 1

            if steps_found < 3:
                warnings.append('Risk assessment should follow 5 steps: identify hazards, who could be harmed, evaluate risks, control measures, review')

            # Check for recording requirement (5+ employees)
            recording_patterns = [
                r'record(?:ed|ing)?.*(?:risk\s+assessment|findings)',
                r'written\s+record',
                r'document(?:ed|ation)'
            ]

            has_recording = any(re.search(p, text, re.IGNORECASE) for p in recording_patterns)
            if not has_recording:
                warnings.append('Risk assessments must be recorded in writing (employers with 5+ employees)')

            # Check for significant findings
            findings_patterns = [
                r'significant\s+(?:findings|risks?|hazards?)',
                r'high\s+risk',
                r'priority\s+(?:actions?|risks?)'
            ]

            has_findings = any(re.search(p, text, re.IGNORECASE) for p in findings_patterns)

            # Check for control measures hierarchy
            hierarchy_patterns = [
                r'hierarchy\s+of\s+controls?',
                r'eliminat(?:e|ion)',
                r'substitut(?:e|ion)',
                r'engineering\s+controls?',
                r'administrative\s+controls?',
                r'PPE\b|personal\s+protective\s+equipment'
            ]

            control_mentions = sum(1 for p in hierarchy_patterns if re.search(p, text, re.IGNORECASE))
            if control_mentions >= 3:
                # Good - mentions hierarchy of controls
                pass

        else:
            warnings.append('Must conduct suitable and sufficient risk assessments for workplace hazards')

        # 4. SPECIFIC RISK ASSESSMENTS
        # DSE (Display Screen Equipment) Risk Assessment
        dse_patterns = [
            r'\bDSE\b',
            r'display\s+screen\s+equipment',
            r'computer\s+(?:workstation|screen)',
            r'VDU\b'
        ]

        has_dse = any(re.search(p, text, re.IGNORECASE) for p in dse_patterns)

        if has_dse:
            dse_requirements = [
                r'(?:eye|eyesight)\s+test',
                r'breaks?.*screen',
                r'workstation\s+assessment',
                r'adjustable\s+(?:chair|desk|screen)'
            ]

            dse_compliant = sum(1 for p in dse_requirements if re.search(p, text, re.IGNORECASE))
            if dse_compliant < 2:
                warnings.append('DSE assessments should cover: workstation setup, breaks, eye tests, adjustable equipment')

        # Manual Handling Risk Assessment
        manual_handling_patterns = [
            r'manual\s+handling',
            r'lifting',
            r'carrying',
            r'TILE\b'  # Task, Individual, Load, Environment
        ]

        has_manual_handling = any(re.search(p, text, re.IGNORECASE) for p in manual_handling_patterns)

        if has_manual_handling:
            tile_factors = [
                r'task',
                r'individual\s+(?:capability|capacity)',
                r'load',
                r'environment'
            ]

            tile_found = sum(1 for p in tile_factors if re.search(p, text, re.IGNORECASE))
            if tile_found < 3:
                warnings.append('Manual handling assessment should consider TILE: Task, Individual, Load, Environment')

        # COSHH (Control of Substances Hazardous to Health)
        coshh_patterns = [
            r'\bCOSHH\b',
            r'hazardous\s+substances?',
            r'chemical\s+(?:risk|hazard|safety)',
            r'safety\s+data\s+sheet',
            r'\bSDS\b'
        ]

        has_coshh = any(re.search(p, text, re.IGNORECASE) for p in coshh_patterns)

        if has_coshh:
            coshh_requirements = [
                r'assessment',
                r'control\s+measures?',
                r'exposure\s+limits?',
                r'(?:storage|handling)\s+procedures?',
                r'emergency\s+procedures?'
            ]

            coshh_compliant = sum(1 for p in coshh_requirements if re.search(p, text, re.IGNORECASE))
            if coshh_compliant < 2:
                warnings.append('COSHH assessment should cover: identification, exposure control, storage, emergency procedures')

        # 5. RIDDOR (Reporting of Injuries, Diseases and Dangerous Occurrences Regulations 2013)
        riddor_patterns = [
            r'\bRIDDOR\b',
            r'reportable\s+(?:injury|incident|disease|occurrence)',
            r'report(?:ing)?.*(?:HSE|Health\s+and\s+Safety\s+Executive)',
            r'notif(?:y|ication).*(?:serious|major)\s+(?:injury|incident)'
        ]

        has_riddor = any(re.search(p, text, re.IGNORECASE) for p in riddor_patterns)

        if has_riddor:
            # Check for types of reportable incidents
            reportable_types = {
                'death': r'death|fatal(?:ity)?',
                'major_injury': r'major\s+injury|fracture|amputation',
                'over_7_days': r'(?:over|more\s+than)\s+(?:7|seven)\s+days?',
                'dangerous_occurrence': r'dangerous\s+occurrence',
                'occupational_disease': r'occupational\s+disease|work[\s-]related\s+(?:illness|disease)'
            }

            types_mentioned = sum(1 for p in reportable_types.values() if re.search(p, text, re.IGNORECASE))

            if types_mentioned < 2:
                warnings.append('RIDDOR reportable incidents include: deaths, major injuries, 7+ day injuries, dangerous occurrences, occupational diseases')

            # Check for reporting timeframes
            timeframe_patterns = [
                r'(?:immediately|forthwith|without\s+delay)',
                r'(?:within\s+)?(?:10|ten)\s+days?',
                r'(?:within\s+)?(?:15|fifteen)\s+days?',
                r'as\s+soon\s+as\s+(?:possible|practicable)'
            ]

            has_timeframe = any(re.search(p, text, re.IGNORECASE) for p in timeframe_patterns)
            if not has_timeframe:
                warnings.append('RIDDOR reports must be made: immediately for deaths/major injuries, within 10 days for 7+ day injuries, within 15 days for diseases')

            # Check for HSE contact information
            hse_patterns = [
                r'HSE\b',
                r'Health\s+and\s+Safety\s+Executive',
                r'(?:report|notify).*(?:online|phone|telephone)',
                r'RIDDOR\s+(?:hotline|reporting)'
            ]

            has_hse_info = any(re.search(p, text, re.IGNORECASE) for p in hse_patterns)
            if not has_hse_info:
                warnings.append('Should provide HSE contact details for RIDDOR reporting (online or 0345 300 9923)')

        # 6. ACCIDENT BOOK / INCIDENT RECORDING
        accident_book_patterns = [
            r'accident\s+book',
            r'incident\s+(?:log|record|register)',
            r'record(?:ing)?.*(?:accidents?|incidents?|near\s+miss)',
            r'BI\s+510'  # Standard accident book reference
        ]

        has_accident_book = any(re.search(p, text, re.IGNORECASE) for p in accident_book_patterns)

        if has_accident_book:
            # Check for data protection compliance
            gdpr_patterns = [
                r'(?:GDPR|data\s+protection)',
                r'confidential(?:ity)?',
                r'personal\s+data',
                r'privacy',
                r'removable\s+pages?'
            ]

            has_gdpr = any(re.search(p, text, re.IGNORECASE) for p in gdpr_patterns)
            if not has_gdpr:
                warnings.append('Accident book must comply with GDPR (use BI 510 with removable pages to protect personal data)')

        else:
            warnings.append('Must maintain accident book to record workplace injuries and incidents')

        # 7. TRAINING AND INFORMATION
        training_patterns = [
            r'(?:health\s+and\s+safety\s+)?training',
            r'induction',
            r'instruction',
            r'information.*employees',
            r'competent\s+person'
        ]

        has_training = any(re.search(p, text, re.IGNORECASE) for p in training_patterns)

        if has_training:
            # Check for adequate training provision
            training_types = [
                r'induction\s+training',
                r'job[\s-]specific\s+training',
                r'refresher\s+training',
                r'emergency\s+procedures?',
                r'first\s+aid'
            ]

            training_coverage = sum(1 for p in training_types if re.search(p, text, re.IGNORECASE))
            # Good if covers multiple types

        # 8. PPE (Personal Protective Equipment)
        ppe_patterns = [
            r'\bPPE\b',
            r'personal\s+protective\s+equipment',
            r'protective\s+equipment',
            r'safety\s+(?:equipment|glasses|boots|helmet|gloves)'
        ]

        has_ppe = any(re.search(p, text, re.IGNORECASE) for p in ppe_patterns)

        if has_ppe:
            # Check PPE is last resort (after elimination, substitution, engineering controls)
            last_resort_patterns = [
                r'last\s+resort',
                r'when.*other\s+(?:measures?|controls?)\s+(?:not|cannot)',
                r'after.*(?:eliminat|engineer|other\s+controls?)',
                r'hierarchy\s+of\s+controls?'
            ]

            has_last_resort = any(re.search(p, text, re.IGNORECASE) for p in last_resort_patterns)
            if not has_last_resort:
                warnings.append('PPE should be last resort after other control measures (elimination, substitution, engineering controls)')

            # Check for provision and maintenance
            provision_patterns = [
                r'provid(?:e|ed)\s+free',
                r'at\s+no\s+cost',
                r'employer.*provide',
                r'maintain(?:ed|ance)',
                r'replace(?:d|ment)'
            ]

            has_provision = any(re.search(p, text, re.IGNORECASE) for p in provision_patterns)
            if not has_provision:
                warnings.append('Employer must provide PPE free of charge and maintain it')

            # Check for training on PPE use
            ppe_training_patterns = [
                r'(?:training|instruction).*(?:use|wearing|using)\s+PPE',
                r'how\s+to\s+(?:use|wear)',
                r'proper\s+use'
            ]

            has_ppe_training = any(re.search(p, text, re.IGNORECASE) for p in ppe_training_patterns)
            if not has_ppe_training:
                warnings.append('Employees must be trained in correct PPE use')

        # 9. CONSULTATION WITH EMPLOYEES
        consultation_patterns = [
            r'consult(?:ation)?.*(?:employees|workers|staff)',
            r'safety\s+representative',
            r'safety\s+committee',
            r'employee\s+(?:involvement|participation)'
        ]

        has_consultation = any(re.search(p, text, re.IGNORECASE) for p in consultation_patterns)

        if has_consultation:
            # Check for safety representatives
            rep_patterns = [
                r'safety\s+representative',
                r'union\s+(?:rep|representative)',
                r'elected\s+representative'
            ]

            has_reps = any(re.search(p, text, re.IGNORECASE) for p in rep_patterns)
            # Good practice

        # 10. FIRST AID
        first_aid_patterns = [
            r'first\s+aid',
            r'first[\s-]aider',
            r'appointed\s+person',
            r'first\s+aid\s+(?:kit|box|equipment)'
        ]

        has_first_aid = any(re.search(p, text, re.IGNORECASE) for p in first_aid_patterns)

        if has_first_aid:
            # Check for adequate provision
            provision_requirements = [
                r'first\s+aid\s+kit',
                r'trained\s+first[\s-]aider',
                r'appointed\s+person',
                r'first\s+aid\s+(?:room|facility)'
            ]

            first_aid_coverage = sum(1 for p in provision_requirements if re.search(p, text, re.IGNORECASE))
            if first_aid_coverage < 2:
                warnings.append('First aid provision should include: trained first-aider or appointed person, first aid kit, appropriate facilities')

        # 11. FIRE SAFETY
        fire_patterns = [
            r'fire\s+(?:safety|risk|assessment|precautions?)',
            r'fire\s+(?:drill|evacuation|alarm)',
            r'emergency\s+(?:exit|evacuation|procedures?)',
            r'assembly\s+point'
        ]

        has_fire = any(re.search(p, text, re.IGNORECASE) for p in fire_patterns)

        if has_fire:
            fire_requirements = [
                r'fire\s+risk\s+assessment',
                r'fire\s+drill',
                r'emergency\s+(?:exit|evacuation)',
                r'assembly\s+point',
                r'fire\s+(?:warden|marshal)'
            ]

            fire_coverage = sum(1 for p in fire_requirements if re.search(p, text, re.IGNORECASE))
            if fire_coverage < 2:
                warnings.append('Fire safety should cover: risk assessment, evacuation procedures, drills, assembly points')

        # 12. NEW AND EXPECTANT MOTHERS
        pregnancy_patterns = [
            r'pregnant',
            r'new.*mother',
            r'expectant\s+mother',
            r'maternity',
            r'breastfeeding'
        ]

        has_pregnancy = any(re.search(p, text, re.IGNORECASE) for p in pregnancy_patterns)

        if has_pregnancy:
            pregnancy_requirements = [
                r'risk\s+assessment',
                r'adjust(?:ment|ed)\s+(?:duties|work)',
                r'suitable\s+alternative\s+work',
                r'suspend(?:ed|sion)\s+(?:on\s+full\s+pay)?',
                r'rest\s+(?:facilities|area)'
            ]

            pregnancy_coverage = sum(1 for p in pregnancy_requirements if re.search(p, text, re.IGNORECASE))
            if pregnancy_coverage < 2:
                warnings.append('Must assess risks to new and expectant mothers, adjust work or provide alternatives, suspend on full pay if necessary')

        # 13. YOUNG WORKERS (under 18)
        young_worker_patterns = [
            r'young\s+workers?',
            r'under\s+18',
            r'(?:16|17)[\s-]year[\s-]old',
            r'child\s+employment'
        ]

        has_young_workers = any(re.search(p, text, re.IGNORECASE) for p in young_worker_patterns)

        if has_young_workers:
            young_worker_requirements = [
                r'risk\s+assessment',
                r'(?:parent|guardian).*inform(?:ed|ation)',
                r'training.*supervision',
                r'prohibited\s+(?:work|activities?)',
                r'working\s+time\s+(?:limits?|restrictions?)'
            ]

            young_worker_coverage = sum(1 for p in young_worker_requirements if re.search(p, text, re.IGNORECASE))
            if young_worker_coverage < 2:
                warnings.append('Young workers require: specific risk assessment, parental notification, training/supervision, working time restrictions')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Health and safety provisions have serious compliance issues',
                'legal_source': self.legal_source,
                'suggestion': 'Address critical issues: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Health and safety provisions need strengthening',
                'legal_source': self.legal_source,
                'suggestion': 'Priority improvements: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Minor health and safety improvements recommended',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Health and safety provisions appear compliant',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_health_safety_gate():
    gate = HealthSafetyGate()

    # Test 1: Complete H&S policy
    test1 = """
    HEALTH AND SAFETY POLICY

    Statement: We are committed to ensuring the health, safety and welfare of all employees
    so far as is reasonably practicable.

    Organisation: The Managing Director has overall responsibility. Department managers
    are responsible for day-to-day implementation.

    Arrangements: We will conduct risk assessments, provide training, maintain equipment,
    and consult with employees on H&S matters.

    Signed: _________________ Date: _________
    Review Date: Annually
    """
    result1 = gate.check(test1, "hs_policy")
    assert result1['status'] in ['PASS', 'WARNING']

    # Test 2: RIDDOR compliance
    test2 = """
    RIDDOR REPORTING PROCEDURE

    Reportable incidents include:
    - Deaths
    - Major injuries (fractures, amputations)
    - Over 7-day injuries
    - Dangerous occurrences
    - Occupational diseases

    Report immediately to HSE for deaths/major injuries (0345 300 9923).
    Report within 10 days for 7+ day injuries.
    Report within 15 days for occupational diseases.
    """
    result2 = gate.check(test2, "riddor_procedure")
    assert result2['status'] in ['PASS', 'WARNING']

    # Test 3: Risk assessment
    test3 = """
    RISK ASSESSMENT PROCEDURE

    5-Step Process:
    1. Identify the hazards
    2. Decide who might be harmed and how
    3. Evaluate the risks and decide on control measures
    4. Record the findings (required for 5+ employees)
    5. Review and update regularly

    Control measures follow the hierarchy:
    - Elimination
    - Substitution
    - Engineering controls
    - Administrative controls
    - PPE (last resort)
    """
    result3 = gate.check(test3, "risk_assessment")
    assert result3['status'] in ['PASS', 'WARNING']

    # Test 4: PPE policy
    test4 = """
    PERSONAL PROTECTIVE EQUIPMENT (PPE)

    PPE is provided as a last resort when other control measures are not sufficient.
    All PPE is provided free of charge by the employer.
    We maintain and replace PPE as needed.
    Employees receive training on correct use of PPE.
    """
    result4 = gate.check(test4, "ppe_policy")
    assert result4['status'] in ['PASS', 'WARNING']

    print("All health and safety gate tests passed!")


if __name__ == "__main__":
    test_health_safety_gate()
