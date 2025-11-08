import re


class WorkingTimeRegulationsGate:
    """
    Working Time Regulations 1998 (as amended 2025)
    Covers: Maximum working hours, rest breaks, annual leave, night work, record-keeping
    """
    def __init__(self):
        self.name = "working_time_regulations"
        self.severity = "critical"
        self.legal_source = "Working Time Regulations 1998 (amended 2025)"

    def _is_relevant(self, text):
        """Check if document relates to working time"""
        text_lower = text.lower()
        keywords = [
            'working time', 'working hours', 'hours of work', 'work hours',
            'rest break', 'rest period', 'annual leave', 'holiday',
            'night work', 'night shift', 'overtime',
            'maximum hours', '48 hours', 'opt-out', 'opt out'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to working time',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. MAXIMUM 48-HOUR WORKING WEEK (averaged over 17 weeks)
        max_hours_patterns = [
            r'(?:maximum|up\s+to|no\s+more\s+than)\s+(\d+)\s+hours?\s+(?:per\s+)?week',
            r'(\d+)[\s-]hour\s+(?:working\s+)?week',
            r'work(?:ing)?\s+hours?.*(\d+)\s+hours?\s+per\s+week',
            r'average.*(\d+)\s+hours?'
        ]

        hours_mentioned = []
        for pattern in max_hours_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for m in matches:
                try:
                    hours = int(re.search(r'\d+', m.group()).group())
                    hours_mentioned.append(hours)

                    if hours > 48:
                        # Check for opt-out
                        context_start = max(0, m.start() - 150)
                        context_end = min(len(text), m.end() + 150)
                        context = text[context_start:context_end].lower()

                        has_opt_out = any(phrase in context for phrase in [
                            'opt-out', 'opt out', 'voluntary', 'agreement', 'consent',
                            'choose to work', 'elect to work'
                        ])

                        if not has_opt_out:
                            spans.append({
                                'type': 'excessive_hours_no_opt_out',
                                'start': m.start(),
                                'end': m.end(),
                                'text': m.group(),
                                'severity': 'critical'
                            })
                            issues.append(f'CRITICAL: {hours}-hour week exceeds 48-hour maximum without valid opt-out')
                        else:
                            spans.append({
                                'type': 'excessive_hours_with_opt_out',
                                'start': m.start(),
                                'end': m.end(),
                                'text': m.group(),
                                'severity': 'medium'
                            })
                except:
                    pass

        # Check for 48-hour reference
        forty_eight_patterns = [
            r'(?:48|forty[\s-]eight)\s+hours?',
            r'WTR.*48',
            r'Working\s+Time\s+Regulations.*maximum'
        ]

        has_48_hour_ref = any(re.search(p, text, re.IGNORECASE) for p in forty_eight_patterns)

        # Check for averaging period
        averaging_patterns = [
            r'(?:averaged|average)\s+(?:over|across)\s+(\d+)\s+weeks?',
            r'(?:17|seventeen)[\s-]week\s+(?:reference\s+)?period',
            r'reference\s+period'
        ]

        has_averaging = any(re.search(p, text, re.IGNORECASE) for p in averaging_patterns)

        if has_48_hour_ref and not has_averaging:
            warnings.append('48-hour week should reference 17-week averaging period (26 weeks for certain sectors)')

        # 2. OPT-OUT AGREEMENT (voluntary right to work more than 48 hours)
        opt_out_patterns = [
            r'opt[\s-]out',
            r'working\s+time\s+opt[\s-]out',
            r'agree.*work\s+(?:more\s+than\s+)?48\s+hours',
            r'voluntary\s+agreement.*exceed.*48'
        ]

        has_opt_out = any(re.search(p, text, re.IGNORECASE) for p in opt_out_patterns)

        if has_opt_out:
            # Check opt-out is voluntary and in writing
            voluntary_patterns = [
                r'voluntary',
                r'choose\s+to',
                r'elect\s+to',
                r'no\s+(?:obligation|requirement)',
                r'optional',
                r'freely\s+agree'
            ]

            has_voluntary = any(re.search(p, text, re.IGNORECASE) for p in voluntary_patterns)
            if not has_voluntary:
                issues.append('CRITICAL: Opt-out must be voluntary - no pressure or detriment for refusing')

            # Check for written agreement
            written_patterns = [
                r'(?:in\s+)?writing',
                r'written\s+(?:agreement|consent)',
                r'signed\s+(?:agreement|opt[\s-]out)'
            ]

            has_written = any(re.search(p, text, re.IGNORECASE) for p in written_patterns)
            if not has_written:
                warnings.append('Opt-out agreement must be in writing and signed by employee')

            # Check for right to cancel opt-out
            cancel_patterns = [
                r'(?:cancel|withdraw|terminate)\s+(?:the\s+)?opt[\s-]out',
                r'(?:7|seven)\s+days?\s+notice',
                r'(?:3|three)\s+months?\s+notice',
                r'end\s+(?:the\s+)?agreement'
            ]

            has_cancel = any(re.search(p, text, re.IGNORECASE) for p in cancel_patterns)
            if not has_cancel:
                warnings.append('Opt-out agreement should specify right to cancel with notice (7 days to 3 months)')

            # Check employer records requirement
            records_patterns = [
                r'(?:keep|maintain|retain)\s+records?',
                r'record.*working\s+(?:time|hours)',
                r'evidence.*compliance'
            ]

            has_records = any(re.search(p, text, re.IGNORECASE) for p in records_patterns)
            if not has_records and has_opt_out:
                warnings.append('Employer must keep records of employees who opt out of 48-hour week')

        # 3. REST BREAKS
        break_patterns = [
            r'rest\s+break',
            r'break',
            r'lunch\s+break',
            r'coffee\s+break',
            r'rest\s+period'
        ]

        has_breaks = any(re.search(p, text, re.IGNORECASE) for p in break_patterns)

        if has_breaks:
            # Check for 20-minute break for 6+ hour shifts
            twenty_min_patterns = [
                r'(?:20|twenty)[\s-]minute\s+break',
                r'break.*(?:20|twenty)\s+minutes?',
                r'(?:at\s+least|minimum\s+of)\s+20\s+minutes?'
            ]

            has_20_min = any(re.search(p, text, re.IGNORECASE) for p in twenty_min_patterns)

            six_hour_patterns = [
                r'(?:6|six)\s+hours?',
                r'shifts?\s+(?:of\s+)?(?:6|six)\s+hours?\s+or\s+(?:more|longer)',
                r'work(?:ing)?\s+(?:more\s+than\s+)?(?:6|six)\s+hours?'
            ]

            has_6_hour_ref = any(re.search(p, text, re.IGNORECASE) for p in six_hour_patterns)

            if has_6_hour_ref and not has_20_min:
                warnings.append('Workers working 6+ hours are entitled to 20-minute uninterrupted rest break')

            # Check break is uninterrupted
            uninterrupted_patterns = [
                r'uninterrupted',
                r'continuous',
                r'without\s+(?:being\s+)?(?:disturbed|interrupted)',
                r'away\s+from\s+(?:work\s+)?(?:station|desk)'
            ]

            has_uninterrupted = any(re.search(p, text, re.IGNORECASE) for p in uninterrupted_patterns)
            if has_20_min and not has_uninterrupted:
                warnings.append('Rest break must be uninterrupted and away from workstation')

        else:
            warnings.append('Should specify rest break entitlements (20 minutes for 6+ hour shifts)')

        # 4. DAILY REST - 11 consecutive hours between working days
        daily_rest_patterns = [
            r'daily\s+rest',
            r'(?:11|eleven)\s+(?:consecutive\s+)?hours?\s+(?:rest|between\s+(?:shifts|work))',
            r'rest\s+(?:period\s+)?(?:of\s+)?(?:11|eleven)\s+hours?',
            r'(?:at\s+least|minimum)\s+11\s+hours?\s+(?:off|rest)'
        ]

        has_daily_rest = any(re.search(p, text, re.IGNORECASE) for p in daily_rest_patterns)

        if not has_daily_rest and has_breaks:
            warnings.append('Should reference 11 consecutive hours daily rest between working days')

        # 5. WEEKLY REST - 24 hours per week (or 48 hours per fortnight)
        weekly_rest_patterns = [
            r'weekly\s+rest',
            r'(?:24|twenty[\s-]four)\s+hours?\s+(?:per\s+week|weekly)',
            r'(?:48|forty[\s-]eight)\s+hours?\s+(?:per\s+fortnight|every\s+two\s+weeks)',
            r'(?:1|one)\s+day\s+off\s+(?:per\s+week|weekly)',
            r'rest\s+day'
        ]

        has_weekly_rest = any(re.search(p, text, re.IGNORECASE) for p in weekly_rest_patterns)

        if not has_weekly_rest and has_daily_rest:
            warnings.append('Should reference weekly rest period (24 hours per week or 48 hours per fortnight)')

        # 6. ANNUAL LEAVE - 5.6 weeks (28 days for full-time)
        annual_leave_patterns = [
            r'annual\s+leave',
            r'holiday\s+entitlement',
            r'paid\s+(?:holiday|leave|time\s+off)',
            r'vacation'
        ]

        has_annual_leave = any(re.search(p, text, re.IGNORECASE) for p in annual_leave_patterns)

        if has_annual_leave:
            # Check for 5.6 weeks / 28 days
            leave_amount_patterns = [
                r'(?:5\.6|5\s+6/10)\s+weeks?',
                r'(?:28|twenty[\s-]eight)\s+days?',
                r'(?:4|four)\s+weeks?.*(?:8|eight)\s+(?:bank\s+)?holidays',
                r'(?:20|twenty)\s+days?\s+(?:plus|and)\s+(?:8|eight)\s+(?:bank\s+)?holidays'
            ]

            has_leave_amount = any(re.search(p, text, re.IGNORECASE) for p in leave_amount_patterns)

            # Check if amount is less than statutory
            days_match = re.search(r'(\d+)\s+days?\s+(?:annual\s+leave|holiday|paid\s+leave)', text, re.IGNORECASE)
            if days_match:
                days = int(days_match.group(1))
                if days < 28:
                    # Check if part-time (pro-rata)
                    context_start = max(0, days_match.start() - 100)
                    context_end = min(len(text), days_match.end() + 100)
                    context = text[context_start:context_end].lower()

                    is_pro_rata = any(phrase in context for phrase in [
                        'pro-rata', 'pro rata', 'part-time', 'part time',
                        'proportionate', 'calculated'
                    ])

                    if not is_pro_rata:
                        issues.append(f'CRITICAL: {days} days annual leave is below statutory minimum of 28 days (5.6 weeks) for full-time workers')

            if not has_leave_amount:
                warnings.append('Should specify annual leave entitlement (statutory minimum 5.6 weeks / 28 days for full-time)')

            # Check for carry over provisions (2025 update)
            carry_over_patterns = [
                r'carry\s+(?:over|forward)',
                r'unused\s+(?:holiday|leave)',
                r'roll\s+over',
                r'(?:next\s+)?(?:holiday\s+)?year'
            ]

            has_carry_over = any(re.search(p, text, re.IGNORECASE) for p in carry_over_patterns)
            # Good practice to clarify carry-over policy

            # Check payment on termination
            termination_pay_patterns = [
                r'(?:payment|pay)\s+(?:for|of)\s+(?:unused|accrued|outstanding)\s+(?:holiday|leave)',
                r'(?:holiday|leave)\s+pay.*(?:termination|leaving|end\s+of\s+employment)',
                r'accrued\s+but\s+untaken'
            ]

            has_termination_pay = any(re.search(p, text, re.IGNORECASE) for p in termination_pay_patterns)
            if not has_termination_pay:
                warnings.append('Should clarify payment for accrued but untaken holiday on termination')

        # 7. NIGHT WORK - Special provisions for night workers
        night_work_patterns = [
            r'night\s+(?:work|shift|worker)',
            r'work(?:ing)?\s+at\s+night',
            r'(?:11\s*pm|23:00).*(?:6\s*am|7\s*am|06:00|07:00)',
            r'night\s+time'
        ]

        has_night_work = any(re.search(p, text, re.IGNORECASE) for p in night_work_patterns)

        if has_night_work:
            # Check for maximum 8-hour average for night workers
            night_hours_patterns = [
                r'(?:8|eight)\s+hours?.*(?:average|per\s+24)',
                r'maximum.*night\s+work.*(?:8|eight)\s+hours?',
                r'(?:no\s+more\s+than|up\s+to)\s+8\s+hours?.*night'
            ]

            has_night_hours = any(re.search(p, text, re.IGNORECASE) for p in night_hours_patterns)
            if not has_night_hours:
                warnings.append('Night workers should not work more than 8 hours in any 24-hour period (on average)')

            # Check for health assessments
            health_patterns = [
                r'health\s+(?:assessment|check|examination)',
                r'medical\s+(?:assessment|check|screening)',
                r'free\s+health\s+assessment'
            ]

            has_health = any(re.search(p, text, re.IGNORECASE) for p in health_patterns)
            if not has_health:
                warnings.append('Night workers are entitled to free health assessments')

            # Check for transfer to day work if health issues
            transfer_patterns = [
                r'transfer\s+to\s+day\s+work',
                r'alternative\s+work',
                r'if\s+(?:health|medical)\s+(?:issues|problems|grounds)'
            ]

            has_transfer = any(re.search(p, text, re.IGNORECASE) for p in transfer_patterns)
            # Good practice to mention

        # 8. RECORD KEEPING (2025 requirement)
        records_patterns = [
            r'(?:keep|maintain|retain)\s+records?',
            r'record.*(?:working\s+(?:time|hours)|hours\s+worked)',
            r'time\s+(?:sheets|records|tracking)',
            r'attendance\s+records?'
        ]

        has_records = any(re.search(p, text, re.IGNORECASE) for p in records_patterns)

        if not has_records and hours_mentioned:
            warnings.append('Employer must keep adequate records of working hours to demonstrate WTR compliance')

        # 9. UNMEASURED WORKING TIME (Exemptions)
        unmeasured_patterns = [
            r'unmeasured\s+working\s+time',
            r'autonomous\s+decision[\s-]?making',
            r'managerial\s+(?:employees|staff|workers)',
            r'senior\s+executives?'
        ]

        has_unmeasured = any(re.search(p, text, re.IGNORECASE) for p in unmeasured_patterns)

        if has_unmeasured:
            # Check this is appropriate exemption
            warnings.append('Unmeasured working time exemption only applies to autonomous decision-makers (senior executives)')

        # 10. ENFORCEMENT AND PENALTIES (2025 updates)
        enforcement_patterns = [
            r'(?:breach|violation|non[\s-]compliance)',
            r'(?:penalty|fine|prosecution)',
            r'health\s+and\s+safety\s+executive',
            r'\bHSE\b',
            r'enforcement'
        ]

        has_enforcement = any(re.search(p, text, re.IGNORECASE) for p in enforcement_patterns)

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Working time provisions violate statutory requirements',
                'legal_source': self.legal_source,
                'suggestion': 'Address critical breaches: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 4:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Working time provisions need strengthening',
                'legal_source': self.legal_source,
                'suggestion': 'Key improvements: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Minor improvements recommended for working time compliance',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Working time provisions appear compliant with regulations',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_working_time_regulations_gate():
    gate = WorkingTimeRegulationsGate()

    # Test 1: Excessive hours without opt-out
    test1 = """
    EMPLOYMENT CONTRACT

    Your normal working hours will be 60 hours per week.
    You will be expected to work overtime as required.
    """
    result1 = gate.check(test1, "employment_contract")
    assert result1['status'] == 'FAIL'
    assert '48' in str(result1).lower() or 'opt-out' in str(result1).lower()

    # Test 2: Inadequate annual leave
    test2 = """
    HOLIDAY ENTITLEMENT

    You are entitled to 20 days of annual leave per year.
    """
    result2 = gate.check(test2, "employment_contract")
    assert result2['status'] == 'FAIL'
    assert '28' in str(result2).lower() or '5.6' in str(result2).lower()

    # Test 3: Compliant working time provisions
    test3 = """
    WORKING TIME

    Normal working hours: 37.5 hours per week (average over 17 weeks)

    Rest Breaks:
    - 20-minute uninterrupted break for shifts of 6+ hours
    - 11 consecutive hours daily rest between shifts
    - 24 hours weekly rest (1 day off per week)

    Annual Leave: 28 days (5.6 weeks) including bank holidays
    Payment for accrued but untaken holiday on termination.

    We maintain records of working hours to demonstrate compliance.
    """
    result3 = gate.check(test3, "employment_contract")
    assert result3['status'] in ['PASS', 'WARNING']

    # Test 4: Opt-out agreement compliant
    test4 = """
    WORKING TIME OPT-OUT AGREEMENT

    I voluntarily agree to work more than 48 hours per week on average.
    This is optional - there is no obligation or detriment for refusing.

    I understand I can cancel this agreement with 7 days' notice.
    The employer will keep records of this opt-out agreement.

    Signed: _______________
    """
    result4 = gate.check(test4, "opt_out_agreement")
    assert result4['status'] in ['PASS', 'WARNING']

    # Test 5: Night work provisions
    test5 = """
    NIGHT SHIFT TERMS

    Night work is defined as work between 11pm and 6am.

    Night workers will not work more than 8 hours in any 24-hour period (on average).
    Free health assessments are provided for all night workers.
    If health issues arise, we will consider transfer to day work.
    """
    result5 = gate.check(test5, "night_shift_policy")
    assert result5['status'] in ['PASS', 'WARNING']

    print("All working time regulations gate tests passed!")


if __name__ == "__main__":
    test_working_time_regulations_gate()
