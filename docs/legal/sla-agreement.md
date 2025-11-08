# LOKI Service Level Agreement (SLA)

**Highland AI Ltd**
**Effective Date:** November 8, 2025
**SLA Version:** 1.0

---

## 1. Scope

This Service Level Agreement applies to **Enterprise Plan customers** only. Starter and Professional plans do not include SLA guarantees (best-effort support).

---

## 2. Uptime Commitment

**Target Uptime:** 99.9% per calendar month

**Uptime Calculation:**
```
Uptime % = (Total Minutes in Month - Downtime Minutes) / Total Minutes in Month × 100
```

**Excluded from Downtime:**
- Scheduled maintenance (announced 72 hours in advance)
- Force majeure events (natural disasters, war, terrorism, internet backbone failures)
- Third-party service failures (Anthropic Claude API, AWS outages)
- Customer-caused issues (invalid API requests, DDoS attacks on customer infrastructure)
- Planned downtime for security patches (max 4 hours/month)

---

## 3. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Response Time** | <500ms (P95) | 95th percentile of all API requests |
| **Document Validation Time** | <5 seconds | Standard 5-page document |
| **Support Response Time** | <4 hours | Enterprise support tickets (business hours) |
| **Critical Issue Resolution** | <24 hours | Service-impacting bugs |

**Business Hours:** Monday-Friday, 9:00-17:00 GMT (excluding UK bank holidays)

---

## 4. Service Credits

If uptime falls below 99.9% in a calendar month, you receive service credits:

| Monthly Uptime | Service Credit |
|----------------|----------------|
| 99.0% - 99.8% | 10% of monthly fee |
| 95.0% - 98.9% | 25% of monthly fee |
| <95.0% | 50% of monthly fee |

**Service Credit Terms:**
- Credits applied to next month's invoice (not cash refunds)
- Maximum credit: 50% of monthly fee
- Must request credit within 30 days of incident
- Credits are sole remedy for SLA breaches (no other damages)

**Requesting Credit:**
1. Email sla@highlandai.com with subject "SLA Credit Request"
2. Include: Month affected, incident details, downtime duration
3. We will investigate and respond within 10 business days
4. Credit issued if claim validated

---

## 5. Scheduled Maintenance

**Frequency:** Maximum once per month
**Duration:** Maximum 4 hours
**Notice:** 72 hours advance notice via email
**Window:** Typically Saturday 02:00-06:00 GMT (minimal customer impact)

**Emergency Maintenance:**
- Critical security patches may require <72 hours notice
- We will provide maximum advance notice possible
- Exempt from SLA if <4 hours and security-related

---

## 6. Support Response Times (Enterprise Only)

| Priority | Initial Response | Resolution Target |
|----------|-----------------|-------------------|
| **Critical** (Service down) | 1 hour | 4 hours |
| **High** (Major feature broken) | 4 hours | 24 hours |
| **Medium** (Minor issue) | 8 hours | 72 hours |
| **Low** (Question, feature request) | 24 hours | Best effort |

**Support Channels:**
- Email: support@highlandai.com (monitored 24/7 for Enterprise)
- Phone: +44 (0) 131 XXX YYYY (business hours + emergency on-call)
- Slack: Dedicated Enterprise channel (optional)

**Escalation:**
If response time exceeded, contact: escalations@highlandai.com or phone emergency line.

---

## 7. Data Backup and Recovery

**Backup Frequency:** Every 6 hours
**Backup Retention:** 30 days
**Recovery Point Objective (RPO):** 6 hours (max data loss)
**Recovery Time Objective (RTO):** 4 hours (max downtime for restore)

**Data Recovery Request:**
- Email: support@highlandai.com
- Provide: Date/time of data loss, affected resources
- We will restore from nearest backup (may lose up to 6 hours of data)

---

## 8. Security Incident Response

**Detection:** 24/7 automated monitoring + security alerts
**Response Time:** Immediate (no SLA - best effort to respond ASAP)
**Notification:** Affected customers notified within 72 hours (GDPR requirement)
**Resolution:** Varies by incident severity, but prioritized above all other work

**Security Contact:** security@highlandai.com

---

## 9. Limitations of Liability

**Service Credits:** Sole remedy for SLA breaches. We are not liable for:
- Consequential damages (lost profits, business interruption)
- Regulatory fines or penalties you incur
- Damages beyond service credits

**Maximum Liability:** Total amount you paid in past 12 months (even with SLA breach).

---

## 10. Monitoring and Reporting

**Status Page:** https://status.loki-compliance.com
- Real-time uptime status
- Historical uptime data
- Scheduled maintenance calendar
- Subscribe to updates (email, SMS, Slack)

**Monthly SLA Report:**
- Delivered within 5 business days of month end
- Includes: Uptime %, incidents, performance metrics
- Available in portal: portal.loki-compliance.com > SLA Reports

---

## 11. SLA Exclusions

This SLA does not apply to:
- Beta features (marked "Beta" in product)
- Third-party integrations (Anthropic, AWS outages beyond our control)
- Starter or Professional plans (no SLA)
- Free trials
- Accounts in suspended state (payment overdue)

---

## 12. Changes to SLA

We may modify this SLA with 90 days' notice to Enterprise customers. Material changes require customer approval (opt-out with refund).

---

## 13. Termination

If we fail to meet SLA for 3 consecutive months, you may terminate contract with:
- 30 days' notice
- Pro-rated refund of prepaid fees
- Full data export

---

## Contact

**SLA Questions:** sla@highlandai.com
**SLA Credit Requests:** sla@highlandai.com
**Emergency Support:** +44 (0) 131 XXX YYYY

---

**Highland AI Ltd**
Registered in Scotland: SC123456
Last Updated: November 8, 2025
