# LOKI Compliance Platform - Getting Started Guide

**Document Version:** 1.0
**Last Updated:** November 2025
**Estimated Reading Time:** 15 minutes

---

## Welcome to LOKI

Thank you for choosing LOKI Interceptor, the UK's premier AI-powered compliance validation platform. This guide will help you get up and running in under 15 minutes.

**What You'll Learn:**
- How to install and configure LOKI
- Process your first document
- Understand validation results
- Apply automatic corrections
- Export compliant documents

---

## Quick Start Checklist

Before you begin, ensure you have:

- [ ] LOKI installer downloaded from your account portal
- [ ] Anthropic API key (provided during onboarding, or obtain from anthropic.com)
- [ ] Windows 10+, macOS 10.15+, or Ubuntu 20.04+
- [ ] 4GB RAM minimum (8GB recommended)
- [ ] Active internet connection
- [ ] Sample documents ready for testing

---

## Installation

### Step 1: Download LOKI

**Option A: Desktop Application (Recommended for New Users)**

1. Log in to your account at: https://portal.loki-compliance.com
2. Navigate to **Downloads** section
3. Select your operating system:
   - **Windows:** Download `LOKI-Setup-1.0.0.exe`
   - **macOS:** Download `LOKI-1.0.0.dmg`
   - **Linux:** Download `LOKI-1.0.0.AppImage`

**Option B: API Server (For Developers/Integration)**

```bash
git clone https://github.com/HighlandAI/loki-interceptor.git
cd loki-interceptor
```

### Step 2: Install LOKI

**Windows:**
```powershell
# Run the installer
.\LOKI-Setup-1.0.0.exe

# Follow installation wizard
# Default location: C:\Program Files\LOKI Interceptor
```

**macOS:**
```bash
# Open the DMG file
open LOKI-1.0.0.dmg

# Drag LOKI to Applications folder
# If prompted, allow installation from identified developer
```

**Linux:**
```bash
# Make AppImage executable
chmod +x LOKI-1.0.0.AppImage

# Run the application
./LOKI-1.0.0.AppImage
```

### Step 3: First Launch

1. **Launch LOKI** from your Applications folder or Start menu
2. **Accept License Agreement** (MIT License)
3. **Choose Installation Type:**
   - **Typical:** Recommended for most users (default modules)
   - **Custom:** Select specific compliance modules
   - **Enterprise:** Full installation with API server

4. **Complete Initial Setup** (approximately 2 minutes)

---

## Configuration

### Setting Up Your API Key

LOKI requires an Anthropic API key for AI-powered semantic analysis.

**Option 1: Via Setup Wizard (First Launch)**

1. When prompted, paste your Anthropic API key
2. Click **Validate Key**
3. Wait for confirmation (green checkmark)
4. Click **Continue**

**Option 2: Manual Configuration**

1. Open LOKI Settings (Gear icon or Ctrl+, / Cmd+,)
2. Navigate to **API Configuration**
3. Paste your API key in the **Anthropic API Key** field
4. Click **Save & Test Connection**

**Option 3: Environment Variable (Advanced)**

```bash
# Windows (Command Prompt)
setx ANTHROPIC_API_KEY "sk-ant-api03-..."

# macOS/Linux (add to ~/.bashrc or ~/.zshrc)
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### Obtaining an Anthropic API Key

**If you don't have an API key:**

1. Visit: https://console.anthropic.com/
2. Sign up for an account (free tier available)
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-api03-`)
6. Paste into LOKI configuration

**Note:** Highland AI Enterprise customers receive pre-provisioned API keys with usage included in subscription.

### Module Selection

Choose which compliance modules to enable:

**Default Configuration (Recommended):**
- [x] FCA UK (Financial Services)
- [x] GDPR UK (Data Protection)
- [x] Tax UK (HMRC Compliance)
- [x] NDA UK (Non-Disclosure Agreements)
- [x] HR Scottish (Employment Law)

**Custom Configuration:**

1. Go to **Settings > Modules**
2. Toggle modules on/off based on your needs
3. Click **Save Configuration**

**Module Recommendations by Industry:**

| Industry | Recommended Modules |
|----------|-------------------|
| Financial Services | FCA UK, GDPR UK, Tax UK |
| HR/Recruitment | HR Scottish, GDPR UK, NDA UK |
| SaaS/Tech | GDPR UK, NDA UK, Tax UK |
| Legal Firms | All modules |
| Accountancy | Tax UK, GDPR UK, NDA UK |

---

## Your First Document Validation

### Step 1: Prepare Your Document

**Supported Formats:**
- Plain text (.txt)
- Markdown (.md)
- HTML (text extracted automatically)

**Recommended First Test:**
Use one of these sample scenarios:

**Sample Financial Promotion:**
```
Investment Opportunity - Guaranteed 15% Returns!

Our innovative fund has delivered consistent 15% annual returns
for the past 3 years. This zero-risk investment is suitable for
everyone. Limited time offer - invest before midnight tonight!

Contact us to start earning guaranteed passive income.
```

**Sample Privacy Notice:**
```
Privacy Notice

We collect your data for various purposes. By using our website,
you agree to our data collection practices. We may share your
information with trusted third parties. Data is stored securely.
```

### Step 2: Upload Document

**Method A: Drag-and-Drop (Easiest)**
1. Open LOKI Desktop App
2. Drag your document file into the upload area
3. Document automatically loads

**Method B: File Picker**
1. Click **Upload Document** button
2. Browse to your document location
3. Select file and click **Open**

**Method C: Paste Text**
1. Click **Paste Text** tab
2. Copy document content (Ctrl+C / Cmd+C)
3. Paste into text area (Ctrl+V / Cmd+V)
4. Click **Validate**

### Step 3: Select Compliance Modules

After uploading, select which modules to apply:

**For Financial Document:**
- [x] FCA UK
- [x] GDPR UK (if includes data collection)
- [ ] Tax UK
- [ ] NDA UK
- [ ] HR Scottish

**Quick Preset Selection:**
- **Financial Services:** FCA + GDPR + Tax
- **HR Documents:** HR Scottish + GDPR + NDA
- **Legal Contracts:** NDA + GDPR
- **All Modules:** Comprehensive check

### Step 4: Run Validation

1. Click the **Validate Document** button
2. Wait 2-5 seconds for analysis
3. Review results dashboard

---

## Understanding Validation Results

### Results Dashboard

Your validation report contains four key sections:

#### 1. Overall Status

**PASS (Green):**
- All compliance gates passed
- Document is compliant
- No critical violations detected

**FAIL (Red):**
- One or more compliance violations detected
- Document requires corrections
- Review gate-specific failures

**NEEDS REVIEW (Yellow):**
- Ambiguous cases requiring human judgment
- Context-specific decisions needed
- Legal review recommended

#### 2. Module Breakdown

Example output:

```
FCA UK: FAIL (3 critical violations)
├─ Fair, Clear, Not Misleading: FAIL - Critical
│  └─ Misleading guarantee detected: "guaranteed 15% returns"
├─ Risk Warning: FAIL - Critical
│  └─ Missing mandatory risk warning
└─ Pressure Tactics: FAIL - High
   └─ Urgency manipulation: "limited time offer"

GDPR UK: PASS (0 violations)
└─ All gates passed

Tax UK: NOT APPLICABLE
```

#### 3. Violation Details

Each violation shows:

**Violation Card:**
```
[CRITICAL] Misleading Guarantee
Gate: Fair, Clear, Not Misleading (COBS 4.2.1)
Module: FCA UK

Detected Pattern: "Guaranteed 15% returns"
Location: Line 1, paragraph 1
Reason: Financial guarantees are prohibited under FCA rules.
  Investment returns cannot be guaranteed.

Recommended Action:
- Remove guarantee language
- Add risk warning
- Use balanced statement (e.g., "Targeted returns...")

Regulation: FCA COBS 4.2.1(1)R - A firm must ensure that
  a financial promotion is fair, clear and not misleading.
```

**Severity Levels:**

| Severity | Icon | Meaning | Action Required |
|----------|------|---------|----------------|
| CRITICAL | 🔴 | Immediate legal violation | Must fix |
| HIGH | 🟠 | Significant compliance risk | Should fix |
| MEDIUM | 🟡 | Best practice deviation | Recommended |
| LOW | 🟢 | Minor improvement | Optional |

#### 4. Correction Summary

```
Corrections Available: 5
├─ Automatic (Deterministic): 4
│  ├─ Add risk warning template
│  ├─ Remove guarantee language
│  ├─ Remove pressure tactics
│  └─ Add regulatory disclaimer
└─ Manual (Suggestions): 1
   └─ Consider rewriting investment claims
```

---

## Applying Automatic Corrections

### Step 1: Review Proposed Corrections

1. Click **View Corrections** button
2. See before/after comparison for each correction

**Example Correction Preview:**

```diff
Before:
- Investment Opportunity - Guaranteed 15% Returns!

After:
+ Investment Opportunity - Targeted 15% Returns

+ RISK WARNING: Capital at risk. The value of investments
+ can go down as well as up. Past performance is not indicative
+ of future results. You may not get back the amount invested.
```

### Step 2: Accept/Reject Corrections

**Option A: Accept All (Recommended for New Users)**
1. Click **Accept All Corrections**
2. All automatic corrections applied instantly
3. Skip to Export step

**Option B: Selective Acceptance**
1. Review each correction individually
2. Click **Accept** (✓) or **Reject** (✗) for each
3. Click **Apply Selected Corrections**

**Best Practice:** Accept all CRITICAL and HIGH severity corrections, review MEDIUM/LOW individually.

### Step 3: Manual Review

Some violations cannot be autocorrected:

**Manual Review Required:**
```
[HIGH] Unsuitable Investment Advice
This document appears to provide investment advice without
mentioning FCA authorization status.

Suggestion: Add one of the following:
- "We are authorized and regulated by the FCA (FRN: 123456)"
- "This is not financial advice. Seek independent advice."

Reason: Cannot determine FCA authorization status automatically.
```

**Action Steps:**
1. Review suggestion
2. Manually edit document in LOKI editor
3. Re-run validation to confirm fix

---

## Exporting Corrected Documents

### Step 1: Choose Export Format

**Available Formats:**
- **Plain Text (.txt):** Original format, corrected content
- **Markdown (.md):** With formatting preserved
- **HTML (.html):** Web-ready version
- **Audit Report (JSON):** Technical audit trail
- **Compliance Report (PDF):** Professional report (Enterprise only)

### Step 2: Export Options

**Quick Export:**
1. Click **Export** button
2. Document saves to Downloads folder
3. Filename: `[original-name]-corrected.txt`

**Custom Export:**
1. Click **Export Options ▼**
2. Select export format
3. Choose export location
4. Enable **Include Audit Report** (optional)
5. Click **Export**

### Step 3: Review Exported Files

**Corrected Document:**
- Contains all accepted corrections
- Maintains original formatting
- Ready for distribution

**Audit Report (if enabled):**
```json
{
  "document_id": "abc123",
  "processed_at": "2025-11-08T10:30:00Z",
  "original_hash": "a3b2c1...",
  "corrected_hash": "d4e5f6...",
  "corrections_applied": 4,
  "validation_status": "PASS",
  "modules_checked": ["fca_uk", "gdpr_uk"],
  "corrections": [
    {
      "pattern": "misleading_guarantee",
      "before": "Guaranteed 15% returns",
      "after": "Targeted 15% returns with risk warning",
      "reason": "FCA COBS 4.2.1 - Misleading guarantee",
      "severity": "CRITICAL"
    }
  ]
}
```

---

## Working with Batch Documents

### Processing Multiple Documents

**Step 1: Prepare Batch**
1. Place all documents in a single folder
2. Ensure consistent format (all .txt or all .md)

**Step 2: Batch Upload**
1. Click **Batch Processing** tab
2. Click **Select Folder**
3. Choose your document folder
4. Configure batch settings:
   - Select modules to apply
   - Choose correction mode (Auto/Manual Review)
   - Set export location

**Step 3: Process Batch**
1. Click **Start Batch Processing**
2. Monitor progress bar
3. Review batch summary report

**Batch Summary:**
```
Processed: 47/50 documents
├─ Passed: 23 (48%)
├─ Corrected: 21 (44%)
├─ Needs Review: 3 (6%)
└─ Failed: 0 (0%)

Processing Time: 3 minutes 24 seconds
Average: 4.1 seconds/document
```

### Enterprise Features

**Professional/Enterprise Plans Only:**

**Scheduled Processing:**
- Set recurring batch jobs
- Folder monitoring (auto-process new files)
- Email notifications on completion

**Advanced Filtering:**
- Process only documents modified since last run
- Exclude specific file patterns
- Priority queue management

---

## Advanced Configuration

### Fine-Tuning Validation

**Sensitivity Levels:**

**Strict Mode (Default):**
- Detects all violations including low severity
- Recommended for regulatory submissions
- Zero tolerance for compliance deviations

**Balanced Mode:**
- Focuses on CRITICAL and HIGH severity
- Filters out minor suggestions
- Recommended for internal documents

**Permissive Mode:**
- Only CRITICAL violations flagged
- Use for early-stage drafts
- Not recommended for final documents

**Configuration:**
```
Settings > Validation > Sensitivity Level > [Select Mode]
```

### Custom Rule Configuration

**Enterprise Only:**

1. Navigate to **Settings > Custom Rules**
2. Click **Add Rule**
3. Configure rule parameters:
   - **Pattern:** Regex pattern to detect
   - **Replacement:** Correction template
   - **Severity:** CRITICAL/HIGH/MEDIUM/LOW
   - **Module:** Which compliance module
   - **Reason:** Explanation for correction

**Example Custom Rule:**
```json
{
  "pattern": "contact us on \\d{11}",
  "replacement": "contact us on +44 (0) [formatted number]",
  "severity": "LOW",
  "module": "gdpr_uk",
  "reason": "Phone numbers should include country code for international compliance"
}
```

### Performance Optimization

**For Large Documents (50+ pages):**

1. **Enable Chunk Processing:**
   - Settings > Performance > Enable Chunk Processing
   - Process document in 10-page segments
   - Reduces memory usage

2. **Disable Low Severity Checks:**
   - Settings > Validation > Skip Low Severity
   - Speeds up validation by 30-40%

3. **Cache Validation Results:**
   - Settings > Performance > Enable Result Cache
   - Avoid re-validating unchanged documents

---

## Integration with Your Workflow

### Email Integration

**Outlook/Gmail Plugin (Planned Q1 2026):**
- Validate emails before sending
- One-click compliance check
- Inline correction suggestions

**Current Workaround:**
1. Copy email content
2. Paste into LOKI
3. Validate and correct
4. Copy corrected text back to email

### Document Management Systems

**SharePoint Integration (Q1 2026):**
- Auto-validate documents uploaded to SharePoint
- Compliance status badges
- Automated correction workflows

**Current Workaround:**
1. Download document from SharePoint
2. Process through LOKI
3. Upload corrected version

### API Integration

**For Developers:**

**REST API Example:**
```bash
curl -X POST https://api.loki-compliance.com/v1/validate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here",
    "modules": ["fca_uk", "gdpr_uk"],
    "document_type": "financial_promotion"
  }'
```

**See API Reference documentation for complete integration guide.**

---

## Troubleshooting

### Common Issues

#### Issue 1: API Key Invalid

**Symptoms:**
- "Invalid API key" error
- Validation fails immediately

**Solutions:**
1. Verify key starts with `sk-ant-api03-`
2. Check for extra spaces (copy-paste error)
3. Ensure key is active (not expired)
4. Test key at console.anthropic.com

#### Issue 2: Slow Validation

**Symptoms:**
- Validation takes >30 seconds
- Application freezes

**Solutions:**
1. Check internet connection (AI requires API access)
2. Reduce document size (split large documents)
3. Disable low severity checks (Settings > Validation)
4. Close other applications using bandwidth

#### Issue 3: No Corrections Available

**Symptoms:**
- Validation shows violations
- No automatic corrections offered

**Possible Reasons:**
1. Violation requires manual judgment (e.g., FCA authorization status unknown)
2. Context-specific correction (cannot be automated)
3. Suggestion-only guidance (no deterministic fix)

**Action:**
- Review manual suggestions
- Consult legal/compliance team for complex issues

#### Issue 4: Application Won't Launch

**Windows:**
1. Run as Administrator (right-click > Run as Administrator)
2. Check antivirus isn't blocking LOKI
3. Reinstall application

**macOS:**
1. Allow in Security & Privacy settings
   - System Preferences > Security & Privacy
   - Click "Open Anyway" for LOKI
2. Grant necessary permissions (File Access)

**Linux:**
1. Ensure AppImage has execute permissions
   ```bash
   chmod +x LOKI-1.0.0.AppImage
   ```
2. Install required dependencies
   ```bash
   sudo apt install libfuse2
   ```

---

## Getting Help

### Support Resources

**1. Documentation:**
- Full Documentation: https://docs.loki-compliance.com
- Video Tutorials: https://tutorials.loki-compliance.com
- API Reference: https://api-docs.loki-compliance.com

**2. Community:**
- Community Forum: https://community.loki-compliance.com
- GitHub Issues: https://github.com/HighlandAI/loki-interceptor/issues

**3. Direct Support:**

**Email Support (All Plans):**
- support@highlandai.com
- Response time: 24-48 hours

**Priority Support (Professional/Enterprise):**
- priority@highlandai.com
- Response time: 4 hours (business hours)
- Phone support: +44 (0) 131 XXX XXXX

**Enterprise Support:**
- Dedicated account manager
- 24/7 emergency support hotline
- Slack integration

### Training & Onboarding

**Free Webinars (Monthly):**
- Every first Thursday, 2:00 PM GMT
- Register: https://training.loki-compliance.com
- Topics: Getting Started, Advanced Features, Integration

**Certification Program:**
- LOKI Compliance Analyst Certification
- 4-hour online course
- Exam and certificate
- Cost: £99 (free for Enterprise customers)

**Custom Training (Enterprise):**
- On-site or virtual training
- Customized to your workflows
- Train-the-trainer programs
- Included with Enterprise subscription

---

## Next Steps

Now that you've completed the getting started guide:

**1. Process Your Real Documents**
- Start with low-risk internal documents
- Build confidence with the platform
- Gradually move to regulatory submissions

**2. Explore Advanced Features**
- Read the Admin Manual for advanced configuration
- Review API Reference for integration opportunities
- Explore batch processing for efficiency

**3. Join the Community**
- Share your experience in the community forum
- Request features and vote on roadmap
- Connect with other compliance professionals

**4. Schedule Training**
- Book a free onboarding webinar
- Consider certification program
- Request custom training (Enterprise)

---

## Quick Reference Card

### Essential Keyboard Shortcuts

| Action | Windows | macOS |
|--------|---------|-------|
| Upload Document | Ctrl+O | Cmd+O |
| Validate | Ctrl+Enter | Cmd+Enter |
| Accept All Corrections | Ctrl+Shift+A | Cmd+Shift+A |
| Export | Ctrl+E | Cmd+E |
| Settings | Ctrl+, | Cmd+, |
| Help | F1 | F1 |

### Validation Workflow

```
1. Upload → 2. Select Modules → 3. Validate →
4. Review Results → 5. Apply Corrections → 6. Export
```

### Support Contact

**Email:** support@highlandai.com
**Phone:** +44 (0) 131 XXX XXXX (Enterprise)
**Docs:** https://docs.loki-compliance.com

---

**Welcome to compliant, confident document creation with LOKI.**

---

*Last Updated: November 2025*
*Version: 1.0*
*For LOKI v1.0.0 and later*
