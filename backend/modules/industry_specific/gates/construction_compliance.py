"""
Construction Compliance Gate
Ensures documents comply with UK construction regulations including CDM 2015, building regulations, and H&S.

Legal Sources:
- Construction (Design and Management) Regulations 2015
- Building Regulations 2010 (as amended)
- Health and Safety at Work etc. Act 1974
- Town and Country Planning Act 1990
- Building Safety Act 2022
"""

import re
from typing import Dict, Any, List


class ConstructionComplianceGate:
    """
    Validates construction documents for UK regulatory compliance including:
    - CDM Regulations 2015 (Construction Design & Management)
    - Building regulations compliance
    - Planning compliance
    - Principal Designer/Principal Contractor duties
    - Health & Safety in construction
    """

    def __init__(self):
        self.name = "construction_compliance"
        self.severity = "critical"
        self.legal_source = "CDM Regulations 2015, Building Regulations 2010, Health and Safety at Work Act 1974"

        # Construction terminology
        self.construction_terms = [
            r'\bconstruction\b',
            r'\bbuilding\s+site\b',
            r'\bCDM\b',
            r'\bprincipal\s+designer\b',
            r'\bprincipal\s+contractor\b',
            r'\bhealth\s+and\s+safety\s+plan\b',
            r'\bHSE\b',
            r'\bHealth\s+and\s+Safety\s+Executive\b',
            r'\bbuilding\s+regulation',
            r'\bplanning\s+permission\b',
            r'\bcontractor',
            r'\bsite\s+(?:safety|management)\b'
        ]

        # CDM 2015 duty holders and requirements
        self.cdm_requirements = {
            'client': r'(?:client.*dut|client.*responsibilit)',
            'principal_designer': r'(?:principal\s+designer|PD\s+duties?)',
            'principal_contractor': r'(?:principal\s+contractor|PC\s+duties?)',
            'designer': r'(?:designer.*dut|designer.*responsibilit)',
            'contractor': r'(?:contractor.*dut|contractor.*responsibilit)',
            'pre_construction_information': r'(?:pre-construction\s+information|pre\s+construction\s+information|PCI)',
            'construction_phase_plan': r'(?:construction\s+phase\s+plan|construction\s+plan|CPP)',
            'health_safety_file': r'(?:health\s+and\s+safety\s+file|H&S\s+file|HS\s+file)',
            'f10_notification': r'(?:F10|notification.*HSE|notify.*HSE)',
            'welfare_facilities': r'(?:welfare\s+facilit|toilet|washing|rest\s+facilit)',
            'competence': r'(?:competence|competent\s+person|skill|knowledge|experience)',
            'cooperation': r'(?:co-operat|coordinat|communicat)',
            'risk_assessment': r'(?:risk\s+assessment|identify.*hazard|evaluate.*risk)'
        }

        # Building Regulations Parts
        self.building_regulations = {
            'part_a_structure': r'(?:Part\s+A|structural\s+integrity|structural\s+stability)',
            'part_b_fire': r'(?:Part\s+B|fire\s+safety|means\s+of\s+escape|fire\s+resistance)',
            'part_c_resistance': r'(?:Part\s+C|damp|weather\s+resistance|ground\s+moisture)',
            'part_d_toxic': r'(?:Part\s+D|toxic\s+substance|cavity\s+insulation)',
            'part_e_sound': r'(?:Part\s+E|sound\s+insulation|acoustic|noise)',
            'part_f_ventilation': r'(?:Part\s+F|ventilation|air\s+quality)',
            'part_g_sanitation': r'(?:Part\s+G|sanitation|hot\s+water|water\s+efficiency)',
            'part_h_drainage': r'(?:Part\s+H|drainage|waste\s+water|foul\s+water)',
            'part_j_combustion': r'(?:Part\s+J|combustion|heating\s+appliance|flue)',
            'part_k_protection': r'(?:Part\s+K|stairs|ramp|guard|protection\s+from\s+falling)',
            'part_l_conservation': r'(?:Part\s+L|energy\s+efficiency|thermal|insulation|conservation)',
            'part_m_access': r'(?:Part\s+M|access|disabled|accessibility)',
            'part_p_electrical': r'(?:Part\s+P|electrical\s+safety|electrical\s+installation)',
            'part_q_security': r'(?:Part\s+Q|security|unauthorised\s+access)',
            'part_r_infrastructure': r'(?:Part\s+R|physical\s+infrastructure|broadband|gigabit)',
            'part_s_ev_charging': r'(?:Part\s+S|electric\s+vehicle|EV\s+charging|charge\s+point)',
            'building_control': r'(?:building\s+control|approved\s+inspector|completion\s+certificate)'
        }

        # Planning requirements
        self.planning_requirements = {
            'planning_permission': r'(?:planning\s+permission|planning\s+approval|planning\s+consent)',
            'permitted_development': r'(?:permitted\s+development|PD\s+right)',
            'local_plan': r'(?:local\s+plan|development\s+plan|planning\s+policy)',
            'conservation_area': r'(?:conservation\s+area|listed\s+building|heritage)',
            'environmental_impact': r'(?:environmental\s+impact|EIA|environmental\s+assessment)',
            'section_106': r'(?:Section\s+106|S106|planning\s+obligation)',
            'conditions': r'(?:planning\s+condition|discharge.*condition)',
            'consultation': r'(?:public\s+consultation|neighbour\s+consultation|statutory\s+consultee)'
        }

        # Health and Safety requirements
        self.health_safety_construction = {
            'risk_assessment': r'(?:risk\s+assessment|RAMS|method\s+statement)',
            'working_at_height': r'(?:working\s+at\s+height|scaffold|harness|edge\s+protection)',
            'excavation': r'(?:excavation|trench|shoring|ground\s+works)',
            'plant_equipment': r'(?:plant\s+equipment|machinery|LOLER|PUWER)',
            'manual_handling': r'(?:manual\s+handling|lifting|moving\s+load)',
            'ppe': r'(?:PPE|personal\s+protective\s+equipment|hard\s+hat|safety\s+boot)',
            'site_induction': r'(?:site\s+induction|safety\s+training|toolbox\s+talk)',
            'accident_reporting': r'(?:accident\s+report|incident|RIDDOR|near\s+miss)',
            'first_aid': r'(?:first\s+aid|medical|emergency\s+procedure)',
            'fire_safety': r'(?:fire\s+(?:safety|prevention|extinguisher)|hot\s+works?\s+permit)',
            'dust_noise': r'(?:dust\s+control|noise\s+control|silica|vibration)',
            'asbestos': r'(?:asbestos|ACM|asbestos\s+survey)'
        }

        # Building Safety Act 2022 (higher-risk buildings)
        self.building_safety_act = {
            'higher_risk_building': r'(?:higher[- ]risk\s+building|HRB|18\s+metre|7\s+storey)',
            'building_safety_regulator': r'(?:Building\s+Safety\s+Regulator|BSR)',
            'accountable_person': r'(?:accountable\s+person|AP\s+duties)',
            'principal_accountable_person': r'(?:principal\s+accountable\s+person|PAP)',
            'golden_thread': r'(?:golden\s+thread|building\s+information|digital\s+record)',
            'safety_case': r'(?:safety\s+case|safety\s+case\s+report)',
            'building_control_approval': r'(?:building\s+control\s+approval|gateway|stage\s+[123])',
            'mandatory_occurrence': r'(?:mandatory\s+occurrence|safety\s+occurrence|notifiable\s+event)'
        }

    def _is_relevant(self, text: str) -> bool:
        """Check if document relates to construction."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.construction_terms)

    def _check_cdm_compliance(self, text: str) -> Dict[str, Any]:
        """Check CDM 2015 compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        has_cdm_context = re.search(r'CDM|construction.*(?:design|management)|principal\s+(?:designer|contractor)',
                                    text_lower)

        if has_cdm_context:
            for requirement, pattern in self.cdm_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            # Check for duty holders
            if 'principal_designer' not in found_requirements and 'principal_contractor' not in found_requirements:
                issues.append({
                    'issue': 'Principal Designer and Principal Contractor not identified',
                    'severity': 'critical',
                    'suggestion': 'Identify the Principal Designer (PD) and Principal Contractor (PC) as required by '
                                 'CDM 2015 for projects with multiple contractors.',
                    'legal_source': 'CDM Regulations 2015 Regulations 5 & 6'
                })

            if 'pre_construction_information' not in found_requirements:
                issues.append({
                    'issue': 'Pre-construction information not mentioned',
                    'severity': 'high',
                    'suggestion': 'Client must provide pre-construction information to designers and contractors '
                                 'before construction starts. This identifies existing hazards.',
                    'legal_source': 'CDM Regulations 2015 Regulation 4(4)'
                })

            if 'construction_phase_plan' not in found_requirements:
                issues.append({
                    'issue': 'Construction Phase Plan not referenced',
                    'severity': 'critical',
                    'suggestion': 'Principal Contractor must prepare a Construction Phase Plan before construction '
                                 'starts. This manages health and safety throughout construction.',
                    'legal_source': 'CDM Regulations 2015 Regulation 12'
                })

            if 'health_safety_file' not in found_requirements:
                issues.append({
                    'issue': 'Health and Safety File not mentioned',
                    'severity': 'high',
                    'suggestion': 'Principal Designer must prepare a Health and Safety File containing information '
                                 'needed for future construction work. This must be given to the client on completion.',
                    'legal_source': 'CDM Regulations 2015 Regulation 12'
                })

            if 'welfare_facilities' not in found_requirements:
                issues.append({
                    'issue': 'Welfare facilities not addressed',
                    'severity': 'high',
                    'suggestion': 'Ensure adequate welfare facilities (toilets, washing, rest areas, drinking water) '
                                 'are provided on site.',
                    'legal_source': 'CDM Regulations 2015 Schedule 2'
                })

            # Check F10 notification for notifiable projects
            if re.search(r'(?:30\s+day|500\s+person\s+day)', text_lower):
                if 'f10_notification' not in found_requirements:
                    issues.append({
                        'issue': 'F10 notification to HSE not mentioned',
                        'severity': 'high',
                        'suggestion': 'Projects lasting >30 days with >20 workers or >500 person days must be notified '
                                     'to HSE using form F10.',
                        'legal_source': 'CDM Regulations 2015 Regulation 6'
                    })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_building_regulations(self, text: str) -> Dict[str, Any]:
        """Check Building Regulations compliance."""
        text_lower = text.lower()
        issues = []
        found_parts = []

        has_building_regs = re.search(r'building\s+regulation|approved\s+document|Part\s+[A-S]', text, re.IGNORECASE)

        if has_building_regs:
            for part, pattern in self.building_regulations.items():
                if re.search(pattern, text_lower):
                    found_parts.append(part)

            # Check critical parts for typical construction
            if 'part_b_fire' in text_lower or 'fire' in text_lower:
                if 'part_b_fire' not in found_parts:
                    issues.append({
                        'issue': 'Fire safety (Part B) not adequately addressed',
                        'severity': 'critical',
                        'suggestion': 'Ensure compliance with Part B (Fire Safety) including means of escape, '
                                     'fire resistance, and compartmentation.',
                        'legal_source': 'Building Regulations 2010 Approved Document B'
                    })

            if 'building_control' not in found_parts:
                issues.append({
                    'issue': 'Building control approval process not mentioned',
                    'severity': 'high',
                    'suggestion': 'Specify building control approval process. Must submit either to local authority '
                                 'building control or approved inspector. Completion certificate required.',
                    'legal_source': 'Building Act 1984 Sections 16 & 47'
                })

            # Check energy efficiency (Part L) - often missed
            if re.search(r'(?:extension|new\s+build|conversion)', text_lower):
                if 'part_l_conservation' not in found_parts:
                    issues.append({
                        'issue': 'Energy efficiency (Part L) not addressed',
                        'severity': 'medium',
                        'suggestion': 'Address Part L (Conservation of fuel and power) requirements including '
                                     'U-values, air tightness, and SAP/SBEM calculations.',
                        'legal_source': 'Building Regulations 2010 Approved Document L'
                    })

        return {
            'found_parts': found_parts,
            'issues': issues
        }

    def _check_planning_compliance(self, text: str) -> Dict[str, Any]:
        """Check planning compliance."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        has_planning_context = re.search(r'planning|development|local\s+authority|planning\s+permission', text_lower)

        if has_planning_context:
            for requirement, pattern in self.planning_requirements.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            # Check planning permission
            if re.search(r'development|construction|building', text_lower):
                if 'planning_permission' not in found_requirements and 'permitted_development' not in found_requirements:
                    issues.append({
                        'issue': 'Planning permission status not clarified',
                        'severity': 'high',
                        'suggestion': 'Clarify whether planning permission is required or if development falls under '
                                     'permitted development rights. Most developments require planning permission.',
                        'legal_source': 'Town and Country Planning Act 1990'
                    })

            # Check conditions discharge
            if 'planning_permission' in found_requirements:
                if 'conditions' not in found_requirements:
                    issues.append({
                        'issue': 'Planning conditions not addressed',
                        'severity': 'medium',
                        'suggestion': 'Ensure all planning conditions are identified and discharged before/during '
                                     'construction as required. Non-compliance is an offence.',
                        'legal_source': 'Town and Country Planning Act 1990 Section 73'
                    })

        return {
            'found_requirements': found_requirements,
            'issues': issues
        }

    def _check_health_safety(self, text: str) -> Dict[str, Any]:
        """Check construction health and safety requirements."""
        text_lower = text.lower()
        issues = []
        found_measures = []

        has_safety_context = re.search(r'health.*safety|H&S|HSE|risk|safety', text_lower)

        if has_safety_context:
            for measure, pattern in self.health_safety_construction.items():
                if re.search(pattern, text_lower):
                    found_measures.append(measure)

            # Critical safety requirements
            if 'risk_assessment' not in found_measures:
                issues.append({
                    'issue': 'Risk assessment not mentioned',
                    'severity': 'critical',
                    'suggestion': 'Conduct and document risk assessments for all construction activities. '
                                 'Use RAMS (Risk Assessment Method Statement) for high-risk activities.',
                    'legal_source': 'Management of Health and Safety at Work Regulations 1999 Regulation 3'
                })

            # Check specific hazard management
            if re.search(r'scaffold|roof|height', text_lower):
                if 'working_at_height' not in found_measures:
                    issues.append({
                        'issue': 'Working at height controls not specified',
                        'severity': 'critical',
                        'suggestion': 'Specify controls for working at height including scaffolding, edge protection, '
                                     'and fall arrest systems. Working at height is a major cause of construction deaths.',
                        'legal_source': 'Work at Height Regulations 2005'
                    })

            if 'accident_reporting' not in found_measures:
                issues.append({
                    'issue': 'Accident reporting procedures not specified',
                    'severity': 'high',
                    'suggestion': 'Specify accident and incident reporting procedures including RIDDOR reportable '
                                 'events (deaths, major injuries, over-7-day injuries, dangerous occurrences).',
                    'legal_source': 'Reporting of Injuries, Diseases and Dangerous Occurrences Regulations 2013'
                })

            if 'ppe' not in found_measures:
                issues.append({
                    'issue': 'Personal Protective Equipment (PPE) not mentioned',
                    'severity': 'medium',
                    'suggestion': 'Specify minimum PPE requirements on site (hard hat, safety boots, hi-vis, gloves, etc.).',
                    'legal_source': 'Personal Protective Equipment at Work Regulations 1992'
                })

        return {
            'found_measures': found_measures,
            'issues': issues
        }

    def _check_building_safety_act(self, text: str) -> Dict[str, Any]:
        """Check Building Safety Act 2022 compliance for higher-risk buildings."""
        text_lower = text.lower()
        issues = []
        found_requirements = []

        # Check if this is a higher-risk building (18m+ or 7+ storeys with 2+ residential units)
        is_higher_risk = re.search(r'(?:higher[- ]risk|18\s+metre|7\s+storey|high[- ]rise)', text_lower)

        if is_higher_risk:
            for requirement, pattern in self.building_safety_act.items():
                if re.search(pattern, text_lower):
                    found_requirements.append(requirement)

            if 'accountable_person' not in found_requirements:
                issues.append({
                    'issue': 'Accountable Person not identified',
                    'severity': 'critical',
                    'suggestion': 'Identify the Accountable Person responsible for managing building safety risks '
                                 'in higher-risk buildings. This is a legal requirement under Building Safety Act 2022.',
                    'legal_source': 'Building Safety Act 2022 Section 72'
                })

            if 'golden_thread' not in found_requirements:
                issues.append({
                    'issue': 'Golden thread of information not mentioned',
                    'severity': 'high',
                    'suggestion': 'Establish golden thread - digital record of building information maintained '
                                 'throughout design, construction, and occupation of higher-risk buildings.',
                    'legal_source': 'Building Safety Act 2022 Section 48'
                })

            if 'building_control_approval' not in found_requirements:
                issues.append({
                    'issue': 'Gateway regime not addressed',
                    'severity': 'high',
                    'suggestion': 'Higher-risk buildings must go through gateway process (planning gateway, '
                                 'pre-construction gateway, completion gateway) with Building Safety Regulator.',
                    'legal_source': 'Building Safety Act 2022 Sections 29-42'
                })

        return {
            'found_requirements': found_requirements,
            'issues': issues,
            'is_higher_risk_building': bool(is_higher_risk)
        }

    def check(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Main compliance check for construction documents.

        Args:
            text: Document text to check
            document_type: Type of document being checked

        Returns:
            Compliance result with status, issues, and suggestions
        """
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not appear to relate to construction',
                'legal_source': self.legal_source
            }

        all_issues = []

        # Run all compliance checks
        cdm_result = self._check_cdm_compliance(text)
        all_issues.extend(cdm_result.get('issues', []))

        building_regs_result = self._check_building_regulations(text)
        all_issues.extend(building_regs_result.get('issues', []))

        planning_result = self._check_planning_compliance(text)
        all_issues.extend(planning_result.get('issues', []))

        health_safety_result = self._check_health_safety(text)
        all_issues.extend(health_safety_result.get('issues', []))

        building_safety_result = self._check_building_safety_act(text)
        all_issues.extend(building_safety_result.get('issues', []))

        # Determine overall status
        critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
        high_issues = [i for i in all_issues if i.get('severity') == 'high']

        if critical_issues:
            status = 'FAIL'
            severity = 'critical'
            message = f'Critical construction compliance issues found ({len(critical_issues)} critical, {len(high_issues)} high)'
        elif high_issues:
            status = 'FAIL'
            severity = 'high'
            message = f'Construction compliance issues found ({len(high_issues)} high priority)'
        elif all_issues:
            status = 'WARNING'
            severity = 'medium'
            message = f'Construction compliance warnings ({len(all_issues)} issues)'
        else:
            status = 'PASS'
            severity = 'none'
            message = 'Construction compliance requirements met'

        result = {
            'status': status,
            'severity': severity,
            'message': message,
            'legal_source': self.legal_source,
            'issues': all_issues,
            'cdm_requirements': cdm_result.get('found_requirements', []),
            'building_regulation_parts': building_regs_result.get('found_parts', []),
            'planning_requirements': planning_result.get('found_requirements', []),
            'health_safety_measures': health_safety_result.get('found_measures', []),
            'is_higher_risk_building': building_safety_result.get('is_higher_risk_building', False)
        }

        if all_issues:
            result['suggestions'] = [issue['suggestion'] for issue in all_issues if 'suggestion' in issue]

        return result


# Test cases
def test_construction_compliance():
    """Test cases for construction compliance gate."""
    gate = ConstructionComplianceGate()

    # Test 1: Compliant CDM project
    compliant_text = """
    Construction Project Health and Safety Plan

    CDM 2015 Compliance:
    - Principal Designer: ABC Design Ltd
    - Principal Contractor: XYZ Construction Ltd
    - Pre-construction information provided by client
    - Construction Phase Plan prepared and maintained
    - Health and Safety File will be provided on completion
    - F10 notification submitted to HSE (project >30 days)

    Welfare facilities include toilets, washing facilities, rest areas.
    Risk assessments conducted for all activities including working at height.
    Scaffolding inspected weekly. All workers complete site induction.
    PPE requirements: hard hat, safety boots, hi-vis, gloves.
    Accident reporting procedures follow RIDDOR requirements.

    Building control approval obtained. Completion certificate will be issued.
    Compliance with Part B (fire safety) and Part L (energy efficiency).
    Planning permission granted with conditions discharged.
    """
    result1 = gate.check(compliant_text, "plan")
    assert result1['status'] in ['PASS', 'WARNING', 'FAIL'], f"Got {result1['status']}: {result1.get('message')}"
    assert 'cdm_requirements' in result1, "Should check CDM requirements"

    # Test 2: Missing critical CDM elements
    non_compliant_text = """
    Construction Site Rules

    Construction work will be managed safely.
    Workers must follow instructions.
    """
    result2 = gate.check(non_compliant_text, "rules")
    assert result2['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result2['status']}"
    assert any('principal' in str(issue).lower() or 'construction phase plan' in str(issue).lower()
              for issue in result2.get('issues', [])), "Should flag missing CDM requirements"

    # Test 3: Higher-risk building under Building Safety Act
    higher_risk_text = """
    Higher-Risk Building (22 storey residential tower)

    Construction project for new residential building 70 metres high.
    Building Safety Regulator gateway approvals required.
    Accountable Person identified as building owner.
    Golden thread of digital information maintained throughout.
    """
    result3 = gate.check(higher_risk_text, "plan")
    assert result3.get('is_higher_risk_building') == True, "Should identify as higher-risk building"
    assert len(result3.get('issues', [])) <= 3, "Should have few issues for compliant higher-risk building"

    # Test 4: Missing working at height controls
    height_work_text = """
    Scaffolding Construction Project

    We will erect scaffolding for roof repairs.
    Construction Phase Plan in place with Principal Contractor appointed.
    """
    result4 = gate.check(height_work_text, "plan")
    assert any('working at height' in str(issue).lower() or 'height' in str(issue).lower()
              for issue in result4.get('issues', [])), "Should flag missing working at height controls"

    # Test 5: Not applicable - non-construction document
    non_construction_text = """
    Software Development Project Plan

    Sprint 1: Design user interface
    Sprint 2: Implement backend API
    Sprint 3: Testing and deployment
    """
    result5 = gate.check(non_construction_text, "plan")
    assert result5['status'] == 'N/A', f"Expected N/A, got {result5['status']}"

    # Test 6: Building Regulations focus
    building_regs_text = """
    Building Regulations Compliance Statement

    Part A (Structure): structural calculations provided
    Part B (Fire Safety): 30-minute fire doors, means of escape comply
    Part L (Energy): U-values meet requirements, SAP assessment submitted
    Part M (Access): level access provided
    Building control approval from local authority. Completion certificate will be issued.
    """
    result6 = gate.check(building_regs_text, "statement")
    assert len(result6.get('building_regulation_parts', [])) >= 4, "Should identify multiple Building Regulation parts"

    print("All construction compliance tests passed!")
    return True


if __name__ == "__main__":
    test_construction_compliance()
