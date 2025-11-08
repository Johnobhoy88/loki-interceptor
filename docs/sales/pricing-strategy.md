# LOKI Pricing Strategy

**Highland AI Ltd** | November 2025 | Confidential

---

## Pricing Overview

**Model:** Usage-based SaaS subscription (tiered)
**Currency:** GBP (UK market primary)
**Billing:** Monthly or Annual (17% discount)
**Free Trial:** 14 days, 20 documents

---

## Pricing Tiers

| Tier | Monthly | Annual | Documents/Month | Users | Support | Target Customer |
|------|---------|--------|-----------------|-------|---------|----------------|
| **Starter** | £199 | £2,388 | 100 | 1 | Email (24hr) | Solo practitioners, startups |
| **Professional** | £499 | £5,988 | 500 | 5 | Email + Chat (8hr) | Growing firms, teams |
| **Enterprise** | Custom | Custom | Unlimited | Unlimited | Dedicated + Phone (4hr) | Large organizations |

**Overage Pricing:** £0.75/document above tier limit

---

## Feature Matrix

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| **Core Modules** | | | |
| FCA UK | ✓ | ✓ | ✓ |
| GDPR UK | ✓ | ✓ | ✓ |
| Tax UK | ✓ | ✓ | ✓ |
| NDA UK | ✓ | ✓ | ✓ |
| HR Scottish | ✓ | ✓ | ✓ |
| **Platform** | | | |
| Desktop App | ✓ | ✓ | ✓ |
| Web App | Q1 2026 | ✓ | ✓ |
| REST API | ✗ | ✓ | ✓ |
| Batch Processing | ✗ | ✓ (50 docs) | ✓ (unlimited) |
| **Integrations** | | | |
| SharePoint | ✗ | ✗ | ✓ |
| Salesforce | ✗ | ✗ | ✓ |
| Custom Integrations | ✗ | ✗ | ✓ |
| **Support & Training** | | | |
| Email Support | ✓ (24hr) | ✓ (8hr) | ✓ (4hr) |
| Phone Support | ✗ | ✗ | ✓ |
| Onboarding Webinar | ✓ | ✓ | ✓ + Custom |
| Dedicated CSM | ✗ | ✗ | ✓ |
| **Security & Compliance** | | | |
| SOC 2 Type II | Q2 2026 | Q2 2026 | ✓ |
| SSO (SAML, OAuth) | ✗ | ✗ | ✓ |
| Custom SLA | ✗ | ✗ | ✓ (99.9%) |
| **Analytics** | | | |
| Basic Reports | ✓ | ✓ | ✓ |
| Advanced Analytics | ✗ | ✗ | ✓ |
| API Access to Audit Logs | ✗ | ✓ | ✓ |

---

## Pricing Rationale

**Cost Structure:**
- Anthropic API (Claude): £0.15/document
- Infrastructure (AWS): £0.05/document
- Support & Overhead: £0.10/document
- **Total Variable Cost:** £0.30/document

**Gross Margin:**
- Starter: 85% (£199 - £30 COGS)
- Professional: 85% (£499 - £75 COGS)
- Enterprise: 80-85%

**Pricing Philosophy:**
1. **Value-Based:** Customers save £100-500/doc (manual review cost)
2. **Land-and-Expand:** Start low (Starter), upsell to Professional/Enterprise
3. **Volume Incentive:** Lower per-doc cost at higher tiers
4. **Competitive:** 10-20x cheaper than LawGeex, 200-1,000x cheaper than manual

---

## Competitive Pricing Comparison

| Provider | Model | Effective Cost/Doc | Our Advantage |
|----------|-------|-------------------|---------------|
| **LOKI Starter** | £199/month (100 docs) | £1.99 | Baseline |
| **LOKI Professional** | £499/month (500 docs) | £1.00 | 50% discount vs Starter |
| **LawGeex** | Per-doc pricing | £5-10 | **5-10x more expensive** |
| **Peninsula** | Consultancy fee | £100-500 | **100-500x more expensive** |
| **BrightHR** | £5-10/user/month | N/A (different model) | Different (HR only) |
| **Manual Review** | £100-500/doc | £100-500 | **100-500x more expensive** |

---

## Customer Acquisition Economics

**Starter Tier:**
- ARPU: £2,388/year
- CAC: £500 (digital marketing)
- LTV: £7,164 (3-year retention)
- LTV:CAC: 14:1
- Payback: 2 months

**Professional Tier:**
- ARPU: £5,988/year
- CAC: £1,200 (outbound sales)
- LTV: £23,952 (4-year retention)
- LTV:CAC: 20:1
- Payback: 2 months

**Enterprise Tier:**
- ARPU: £24,000/year (average)
- CAC: £4,000 (field sales, demos)
- LTV: £120,000 (5-year retention)
- LTV:CAC: 30:1
- Payback: 2 months

---

## Discounting Policy

**Annual Prepayment:** 17% discount (2 months free)
- Starter: £2,388 (vs £2,388 monthly)
- Professional: £4,990 (vs £5,988 monthly)

**Volume Discounts (Enterprise):**
- 100-500 users: 10%
- 500-1,000 users: 20%
- 1,000+ users: 25-30% (custom)

**Partner/Reseller Discounts:**
- 20% margin for channel partners
- 30% for white-label integrations (Farsight)

**Educational/Nonprofit:**
- 50% discount (verified .ac.uk or charity registration)

**Startup Program:**
- Free Starter tier for YC/Techstars portfolio (first 6 months)

---

## Revenue Projections

| Tier | Year 1 Customers | Year 2 | Year 3 | Y3 ARR |
|------|-----------------|--------|--------|--------|
| **Starter** | 200 | 600 | 1,200 | £2.9M |
| **Professional** | 100 | 500 | 1,500 | £9.0M |
| **Enterprise** | 20 | 80 | 200 | £4.8M |
| **Partner (Farsight)** | 100 | 300 | 600 | £1.8M |
| **TOTAL** | 420 | 1,480 | 3,500 | **£18.5M** |

**Average Revenue Per Account (ARPA):**
- Year 1: £2,286
- Year 2: £3,108 (upsell)
- Year 3: £5,286 (more Enterprise)

---

## Upgrade Paths

**Starter → Professional:**
- Trigger: Hit 100 docs/month limit consistently (3 months)
- Message: "Upgrade to Professional to get 500 docs/month + API access + priority support"
- Success Rate: 40% (estimated)

**Professional → Enterprise:**
- Trigger: 500 docs/month limit, request for SSO/SharePoint, >10 users
- Message: "Let's discuss Enterprise custom pricing for unlimited docs and dedicated support"
- Success Rate: 25% (estimated)

**Churn Mitigation:**
- Downgrade option: Professional → Starter (keep customer, reduce revenue)
- Pause subscription: 3-month pause available (seasonal businesses)

---

## International Pricing (Future)

**EU Market (2026):**
- EUR pricing: Add 20% for currency risk
- Starter: €239/month
- Professional: €599/month
- Enterprise: Custom

**US Market (2027):**
- USD pricing: Add 15%
- Starter: $229/month
- Professional: $579/month
- Enterprise: Custom

---

## Conclusion

LOKI's pricing strategy balances:
1. **Affordability:** 10-500x cheaper than alternatives
2. **Scalability:** Tiered model supports all business sizes
3. **Profitability:** 80-85% gross margins, strong unit economics
4. **Competitiveness:** Positioned below LawGeex, far below Peninsula/manual

**Recommended Messaging:**
"Save 86% on compliance costs. From £199/month."

---

*Last Updated: November 2025*
