# eQMS Document Management System — Complete Knowledge Base
## Arni Medica Diagnostics | Medical Device eQMS
### Source: DeepSeek Training Conversation + Document Lifecycle Specification
### Date: February 2026

---

## TABLE OF CONTENTS
1. Foundational Concepts & Regulatory Landscape
2. Core Document Management Workflow (4 Phases)
3. Specific Document Types & Workflows
4. Document Control Admin's 360-Degree View
5. Complete Document Lifecycle — Creation to Obsoletion
6. Versioning, Attachments & Document Relationships
7. Workflow Diagram (All Stages & Back-and-Forth)
8. User Checklists by Role
9. SOP-042 Narrative Example
10. Workflow Verification & Improvements
11. Stage-by-Stage Configuration Guide
12. Regulatory References by Stage
13. Validation Test Scripts
14. Comprehensive Workflows with Rejection Loops
15. Tailored Workflow (Author → Primary Reviewer → Secondary Reviewer → Approver)
16. Superseded Documents — Complete Explanation

---

## 1. FOUNDATIONAL CONCEPTS & REGULATORY LANDSCAPE

### What is an eQMS?
An eQMS (electronic Quality Management System) is the **digital tool** that manages a company's QMS (Quality Management System) — the **framework** of policies, processes, and procedures. For medical device companies, it's not optional — it's a **regulatory requirement**.

### Key Regulations:
| Regulation | Scope | Key Clause |
|---|---|---|
| **ISO 13485:2016** | International QMS for medical devices | Clause 4.2.3 — Document Control |
| **FDA 21 CFR Part 820** | US FDA Quality System Regulation | 820.40 — Document Controls |
| **FDA 21 CFR Part 11** | Electronic records & signatures | 11.10 — Controls for closed systems |
| **EU MDR 2017/745** | European Medical Device Regulation | Article 10(9) — QMS requirements |
| **ISO 14971** | Risk Management | Integrated with document workflows |

### Core Principle
> "The right person has the right version of the right document at the right time."

### Signs You Need an eQMS:
- Using paper-based or file-share document control
- Documents scattered across SharePoint/Google Drive
- No audit trail for document changes
- Manual training tracking
- Difficulty preparing for regulatory audits

---

## 2. CORE DOCUMENT MANAGEMENT WORKFLOW (4 PHASES)

### Phase 1: Document Creation & Initial Review
1. **Initiation**: Authorized user creates document from controlled template
2. **Auto-ID**: System generates unique Document Number (e.g., SOP-042)
3. **Version Start**: Born as Draft v0.1 (the "0" means not yet released)
4. **Authoring**: Author works using TipTap editor, system tracks all changes
5. **Metadata**: Author fills title, department, document type, regulatory requirement
6. **Initial Review**: Optional peer/subject matter expert review before formal submission

### Phase 2: The Review & Approval Workflow
1. **Submit for Review**: Author clicks "Submit" — document locks for editing
2. **Reviewer Assignment**: System assigns reviewers based on document type and department
3. **Review Options**: Approve, Reject (return to author), Request Changes
4. **Approval Gate**: After reviewers approve, moves to formal approvers
5. **Electronic Signature**: 21 CFR Part 11 compliant — username + password + meaning
6. **Multi-level Approval**: Sequential or parallel based on configuration

### Phase 3: Publication, Distribution & Training
1. **Training Assignment**: System auto-assigns training to affected personnel
2. **Training Gate**: Users must complete "Read & Understand" before accessing the effective document
3. **Effective Date**: Configurable delay (e.g., 7 days) to allow training completion
4. **Controlled Distribution**: System manages who gets access
5. **Watermarking**: "Uncontrolled Copy if Printed" on all printed versions

### Phase 4: Document Maintenance & Archiving
1. **Periodic Review**: Automated reminders at configured intervals (e.g., every 24 months)
2. **Review Outcomes**: No changes needed, Minor revision, Major revision, Make obsolete
3. **Revision Cycle**: Creates new draft version, repeats workflow
4. **Superseding**: New version replaces old (old marked "Superseded")
5. **Obsolescence**: Document withdrawn from use entirely
6. **Archiving**: Retained for regulatory retention period (typically 7+ years)

---

## 3. SPECIFIC DOCUMENT TYPES & WORKFLOWS

### Standard Operating Procedures (SOPs)
- **Template**: Header with doc ID, title, version, effective date, department
- **Review**: Department Manager (technical) → Plant Head/Director (strategic) → QA Manager (compliance)
- **Training**: Mandatory "Read & Understand" for all affected personnel
- **Review Period**: Typically every 2 years

### Work Instructions (WIs)
- **Parent**: Always linked to a controlling SOP
- **Review**: Subject Matter Expert → Department Manager
- **Training**: Hands-on demonstration may be required
- **Review Period**: Aligned with parent SOP

### Forms & Templates
- **Version Control**: Forms themselves are controlled documents
- **Filled Forms = Records**: Once filled, they become quality records (not editable)
- **Review**: QA review for regulatory alignment

### Policies
- **Highest Level**: Govern all SOPs and WIs beneath them
- **Approval**: Senior Management / Quality Director
- **Impact**: Changes cascade to all child documents
- **Review Period**: Annually or on regulatory change

### Specifications
- **Types**: Product specs, material specs, test method specs
- **Review**: Engineering + QA + Regulatory
- **Change Impact**: May require design control assessment

### Validation Protocols & Reports
- **Lifecycle**: Protocol → Execution → Report → Approval
- **Special**: Requires IQ/OQ/PQ stages
- **Retention**: Lifetime of device + regulatory period

---

## 4. DOCUMENT CONTROL ADMIN'S 360-DEGREE VIEW

### 1. User Management & Access Control
- Assign roles: Author, Reviewer, Approver, Read-Only
- Configure department-based access matrices
- Set up approval chains by document type
- Manage training requirements per role

### 2. Template Governance
- Create and maintain controlled document templates
- Lock template formatting to prevent unauthorized changes
- Version templates independently from documents
- Map templates to document types (SOP → SOP template)

### 3. Workflow Configuration & Troubleshooting
- Configure review/approval workflows per document type
- Set SLA timers for each stage (e.g., 5 days for review)
- Configure escalation rules (notify manager if overdue)
- Handle edge cases: reassign if reviewer on leave

### 4. Audit Trail Monitoring ("The Sherlock Holmes Work")
- Review all document access events
- Verify electronic signatures are valid
- Check for unauthorized access attempts
- Generate audit reports for regulatory inspections

### 5. The "Read & Understood" Enforcement
- Configure which documents require training
- Set training deadlines aligned with effective dates
- Monitor completion dashboards
- Escalate non-compliance to department managers
- Block document access for untrained personnel (Training Gate)

---

## 5. COMPLETE DOCUMENT LIFECYCLE — CREATION TO OBSOLETION

### Phase 1: Creation & Drafting (The Birth)

| Element | How It Works |
|---|---|
| Initiation | User creates DCR or selects "Create New Document" from template. System auto-generates Document Number (e.g., SOP-042) |
| Version Start | Document born as Draft v0.1. The "0" means not yet released |
| Authoring | Author edits. Each save tracked. Co-authoring supported with tracked changes |
| Attachments | Author can attach supporting files (images, data, references) |
| Metadata | Title, department, document type, regulatory requirement, keywords |

### Phase 2: Review & Approval (The Gauntlet)

| Step | What Happens | Version Status |
|---|---|---|
| Submit for Review | Author clicks "Submit" → document locks | Still v0.x |
| Primary Review | Dept Manager reviews → Approve or Reject | If rejected → back to Draft, v0.x+1 |
| Secondary Review | Plant Head reviews → Approve or Reject | If rejected → back to Draft |
| Final Approval | QA Manager e-signs → document approved | Promoted to v1.0 |
| Rejection Loop | Each rejection increments minor: v0.1 → v0.2 → v0.3 | Tracks review cycles |

### Phase 3: Effective & Active Use (The Working Life)

| Element | How It Works |
|---|---|
| Training Period | System assigns training. Users must complete before effective date |
| Training Gate | Blocks access: "You must complete training to view this document" |
| Effective Date | Configurable delay (default 7 days after approval) |
| Active Use | Document is THE official procedure. All previous versions superseded |
| Access Tracking | System logs every view, print, download |

### Phase 4: Maintenance & Periodic Review (The Check-Up)

| Element | How It Works |
|---|---|
| Review Trigger | Automated at configured interval (6/12/18/24/36 months) |
| Review Options | No changes needed / Minor revision / Major revision / Make obsolete |
| No Changes | Reviewer documents "reviewed, no changes" with signature. Next review date reset |
| Revision Needed | New draft created from current effective. Goes through full review cycle again |

### Phase 5: Revision & Superseding (The Evolution)

| Step | Version Tracking |
|---|---|
| New draft created | v1.1 (draft of revision) |
| During review cycles | v1.2, v1.3, etc. |
| Approved | Promoted to v2.0 |
| Previous v1.0 | Automatically marked "Superseded" |
| Superseded doc | View-only with watermark, no editing allowed |

### Phase 6: Obsolescence & Archiving (Retirement)

| Element | How It Works |
|---|---|
| Obsolete Trigger | Document no longer needed (process removed, product discontinued) |
| Requires DCR/ECO | Change request documents the reason for obsolescence |
| Approval Required | QA approval needed to obsolete |
| Access | View-only for audit purposes |
| Archive | System retains per retention policy (7+ years typically) |
| Deletion | NEVER manually deleted. Retention policy controls lifecycle |

### Version Timeline Example:
```
[Jan] v1.0 Effective ──────────────────────────┐
                                                │
[Mar] v1.1 Draft (in review) ────┐              │
                                  ↓              ↓
[Apr] v2.0 Effective ────────────┼─────────────>X (v1.0 becomes Superseded)
                                  │
[May] v2.1 Draft (in review) ────┘
```

---

## 6. VERSIONING, ATTACHMENTS & DOCUMENT RELATIONSHIPS

### Versioning Scheme
| Event | Version | Meaning |
|---|---|---|
| New document created | v0.1 | First draft, not released |
| Each review cycle | v0.2, v0.3 | Draft iterations |
| First approval | v1.0 | First released version |
| Minor revision draft | v1.1, v1.2 | Draft of revision |
| Revision approved | v2.0 | Second release |
| Editorial change | v1.0a | Letter suffix, no re-approval |

### Document Relationships
| Type | Description | Example |
|---|---|---|
| Parent-Child | One controls another | Policy (Parent) → SOP (Child) → WI (Grandchild) |
| Sibling | Documents that work together | SOP for Testing + SOP for Equipment Calibration |
| Supporting | Attachments providing evidence | Validation Report attached to Test Method SOP |
| Referential | Document mentions another | "See WI-128 for details" (clickable link in eQMS) |

### Attachment Rules by Lifecycle Stage
| Stage | Can Add? | Can Remove? | Notes |
|---|---|---|---|
| Draft | ✅ Yes | ✅ Yes | Full flexibility during drafting |
| In Review | ⚠️ Limited | ❌ No | Only if reviewer requests supporting evidence |
| Approved/Effective | ❌ No | ❌ No | Locked — any change requires new revision |
| Superseded | ❌ No | ❌ No | Historical record — frozen |
| Obsolete | ❌ No | ❌ No | Read-only archive |

---

## 7. WORKFLOW DIAGRAM — ALL STAGES & BACK-AND-FORTH

```
[START] --> Document Creation (Initiation)
         |
         v
    +---------+
    |  DRAFT  | <------------------------------------+
    | (v0.1)  |                                      |
    +---------+                                      |
         |                                           |
         | Author edits (multiple iterations)        |
         | (loop within Draft)                       |
         |                                           |
         v                                           |
    Submit for Review?                               |
    [YES] --+                                        |
            |                                        |
            v                                        |
    +-----------+                                    |
    | IN REVIEW |                                    |
    |  (v0.x)   |                                    |
    +-----------+                                    |
         |                                           |
         +-- All Reviewers Approve? --[NO]----------+
         |                            (Rejected:     |
         | [YES]                       back to Draft,|
         v                            v0.x increments)
    +----------+                                     |
    | APPROVED |                                     |
    |  (v1.0)  |                                     |
    +----------+                                     |
         |                                           |
         | Training period begins                    |
         v                                           |
    +-----------+                                    |
    | TRAINING  |                                    |
    | PERIOD    |                                    |
    +-----------+                                    |
         |                                           |
         | All training complete?                    |
         | [YES]                                     |
         v                                           |
    +-----------+                                    |
    | EFFECTIVE |                                    |
    |  (v1.0)   |                                    |
    +-----------+                                    |
         |                                           |
         +-- Periodic Review Due?                    |
         |   [YES] --> Review Decision:              |
         |      +-- No Changes --> Reset timer       |
         |      +-- Minor Rev --> New Draft (v1.1) --+
         |      +-- Major Rev --> New Draft (v1.1) --+
         |      +-- Obsolete --> OBSOLETE            |
         |                                           |
         +-- New Version Approved?                   |
         |   [YES] --> SUPERSEDED                    |
         |                                           |
         v                                           |
    +-------------+    +----------+    +----------+
    | SUPERSEDED  |    | OBSOLETE |    | ARCHIVED |
    | (view-only) |    |(view-only)|    |(retained)|
    +-------------+    +----------+    +----------+
         |                  |               ^
         +---> ARCHIVED <---+               |
                                            |
    +-------------+                         |
    | CANCELLED   | (abandoned drafts)      |
    +-------------+                         |
```

### All Possible Transitions:
| From | To | Trigger | Who |
|---|---|---|---|
| Draft | In Review | Author submits | Author |
| Draft | Cancelled | Abandon draft | Author + QA |
| In Review | Approved | All reviewers approve | Final Approver |
| In Review | Draft | Any reviewer rejects | Reviewer |
| Approved | Effective | Training complete + effective date | System/QA |
| Approved | Draft | Revoke approval (rare) | QA Director |
| Effective | Superseded | New version goes effective | System (auto) |
| Effective | Obsolete | Withdrawal decision | QA + Management |
| Effective | Under Review | Periodic review triggered | System |
| Superseded | Archived | Retention policy | System |
| Obsolete | Archived | Retention policy | System |

---

## 8. USER CHECKLISTS BY ROLE

### FOR AUTHORS & DOCUMENT OWNERS

#### Stage 1: Drafting a New Document
- ☐ Verify need — Is this document required? Is there an existing one to revise?
- ☐ Use correct template — Always select the approved company template
- ☐ Complete all metadata — Document number, title, department, document type
- ☐ Fill all sections — Don't leave placeholders. Mark N/A with explanation
- ☐ Add revision history — New doc: "Initial release." Revisions: describe changes
- ☐ Attach supporting files — Relevant images, forms, reference documents
- ☐ Self-review — Read the entire document before submitting

#### Stage 2: Submitting for Review
- ☐ Verify all sections complete — No [TBD] or placeholder text
- ☐ Add reviewers — Select all required reviewers/approvers
- ☐ Write submission note — Explain what reviewers should focus on
- ☐ Click "Submit for Review" — Document locks from editing

#### Stage 3: Handling Rejection
- ☐ Read ALL reviewer comments — Don't just fix one and resubmit
- ☐ Address each comment — Respond to each one (accepted/rejected with reason)
- ☐ Make changes — Update the document per feedback
- ☐ Note what you changed — Update revision history/comments
- ☐ Resubmit — System increments to v0.x+1

### FOR REVIEWERS
- ☐ Review within SLA — Typically 3-5 business days
- ☐ Use comment feature — Don't email feedback separately
- ☐ Be specific — Reference section numbers and page numbers
- ☐ Decision: Approve or Reject — Don't leave in limbo
- ☐ If rejecting: Provide actionable feedback

### FOR APPROVERS
- ☐ Verify all reviews complete — Check all reviewers have approved
- ☐ Review final document — Ensure all comments were addressed
- ☐ Apply electronic signature — Username + password + meaning
- ☐ If rejecting: Provide clear rationale — Document goes back to Author

---

## 9. SOP-042 NARRATIVE EXAMPLE

### Act 1: Birth of a Document
**Sarah** (Quality Engineer, Author) notices the sterilization process changed. She opens the eQMS, selects "Create New SOP", chooses the SOP template. System assigns **SOP-042**, version **v0.1 Draft**.

She writes the procedure over 3 days. System auto-saves every edit. She attaches equipment photos and validation data. Before submitting, she does a self-review.

### Act 2: The Review Gauntlet
Sarah submits SOP-042 for review. System notifies:
- **Dr. Patel** (Primary Reviewer, Dept Manager)
- **Mr. Kumar** (Secondary Reviewer, Plant Head)

**Round 1**: Dr. Patel reviews → finds missing safety step → **REJECTS**. System sends SOP-042 back to Sarah as **v0.2 Draft**. Sarah adds the safety step, resubmits.

**Round 2**: Dr. Patel **APPROVES**. Document moves to Mr. Kumar. He requests a minor wording change → **REJECTS**. Back to Sarah as **v0.3 Draft**. Sarah fixes it, resubmits.

**Round 3**: Both reviewers APPROVE. Document moves to **QA Manager** for final approval. QA Manager applies **electronic signature** (21 CFR Part 11). SOP-042 becomes **v1.0 Approved**.

### Act 3: Going Live (Effective Stage)
System sets **effective date**: 7 days from approval. Auto-assigns "Read & Acknowledge" training to all 15 Sterilization Technicians.

Sarah monitors the training dashboard. By Day 6, 14/15 complete. Raj hasn't. Sarah sends reminder. Raj tries to access the SOP — system blocks him: **"Complete training to view."** Raj completes training.

**Effective date arrives** → SOP-042 is now the official procedure. All personnel trained.

### Act 4: Life in Service
For months, technicians use SOP-042. System tracks every access. During an FDA audit, the auditor asks for proof that all technicians were trained on the latest version. Sarah pulls the training report — 100% compliance, with dates and signatures. **Audit passed.**

### Act 5: The Evolution
6 months later, new equipment arrives requiring a process change. Sarah creates a **revision** — system creates **v1.1 Draft** (inheriting from v1.0). Goes through the same review cycle (v1.2, v1.3...). Approved as **v2.0**.

System **automatically marks v1.0 as Superseded** with red watermark. New training assigned for v2.0.

### Act 6: Retirement
2 years later, Arni Medica discontinues the sterilization line. The QA team raises a **Document Change Request** to obsolete SOP-042 v2.0. After approval, it's marked **Obsolete** — view-only with watermark. Retained in archive for regulatory retention period.

---

## 10. WORKFLOW VERIFICATION & IMPROVEMENTS

### Assessment of Current eQMS Workflows

#### Document Lifecycle
| Stage | Status | Comment |
|---|---|---|
| Draft | ✅ Good | Standard starting point |
| In Review | ✅ Good | Document under review |
| Review Validation | ⚠️ Ambiguous | What does this mean? Consider removing or renaming |
| Sign-Off | ✅ Good | Final approval |
| Released | ⚠️ Problem | Missing training gate between approval and release |
| Superseded | ✅ Good | Standard |
| Obsolete | ✅ Good | Standard |
| Archived | ✅ Good | Retention stage |

#### Recommended Document Lifecycle (8 stages):
```
Draft → In Review → Approved → Training Period → Effective → Superseded → Obsolete → Archived
                                                                              ↓
                                                                          (+ Cancelled for abandoned drafts)
```

#### Key Missing Elements:
1. **Training Period stage** between Approved and Effective
2. **Effective vs Released** — "Effective" is the correct regulatory term
3. **Cancelled** state for abandoned drafts
4. **Rejection loops** sending documents back to Draft

### CAPA Workflow Improvements
- Add **Containment** step immediately after identification
- Add **Risk Classification** (Critical/Major/Minor)
- Add **Effectiveness Review** with defined criteria
- Ensure **CAPA-to-Document linkage** (changes to SOPs trigger document revision)

### Deviation Workflow Improvements
- Add **Immediate Containment** step
- Add **Impact Assessment** for product safety/quality
- Add **Disposition Decision** (rework, scrap, use-as-is)
- Add **CAPA decision branch** (CAPA needed or not?)
- Link to **Batch/Lot numbers** (critical for recalls)

### Change Control Improvements
- Add **Change Board Review** gate
- Add **Implementation Verification** step
- Add **Effectiveness Review** after implementation
- **Reopen loops** if verification fails

---

## 11. STAGE-BY-STAGE CONFIGURATION GUIDE

### Stage 1: Draft
| Configuration | Setting |
|---|---|
| Stage Name | Draft |
| Default Assignee | Document Author |
| SLA | No limit (warning at 30 days) |
| Permissions | Author: Full edit. Others: View only if shared |
| Required Fields | Title, Document Type, Department, Expected Review Date |
| Exit Criteria | All required fields filled, content not empty |
| Transition | "Submit for Review" button |

### Stage 2: In Review
| Configuration | Setting |
|---|---|
| Stage Name | In Review |
| Assignee | Configured reviewers (by document type/department) |
| SLA | 5 business days per reviewer |
| Permissions | Reviewers: Add comments. Author: View only |
| Escalation | Day 3: Reminder. Day 5: Escalate to manager |
| Actions | Approve, Reject with comments, Request clarification |
| Exit Criteria | All required reviewers have approved |

### Stage 3: Approval
| Configuration | Setting |
|---|---|
| Stage Name | Approval |
| Assignee | Configured approvers (QA Manager typically) |
| SLA | 3 business days |
| Permissions | Approver: View + Sign. Others: View only |
| E-Signature | Required (21 CFR Part 11 compliant) |
| Actions | Approve (e-sign), Reject with comments |
| Exit Criteria | All required approvers have signed |

### Stage 4: Training Period
| Configuration | Setting |
|---|---|
| Stage Name | Training Period |
| Assignee | System (auto-manages) |
| Duration | Configurable (default 7 days) |
| Auto-Actions | Create training assignments for affected personnel |
| Training Gate | Block document access for untrained users |
| Exit Criteria | All required training complete OR effective date reached |
| Monitoring | Dashboard shows completion % |

### Stage 5: Effective
| Configuration | Setting |
|---|---|
| Stage Name | Effective |
| Auto-Actions | Supersede previous version, Update document register |
| Permissions | All authorized: View + Print. Author: Cannot edit |
| Periodic Review | Timer starts based on review_period_months |
| Watermark | None (this is the controlled, current version) |

### Stage 6: Superseded
| Configuration | Setting |
|---|---|
| Stage Name | Superseded |
| Trigger | New version becomes Effective |
| Permissions | View-only with watermark |
| Watermark | "SUPERSEDED" in red diagonal |
| Visual | Gray background/border, header shows "Superseded on [Date] by v[X.X]" |
| No Actions | Cannot edit, comment, sign, or approve |

### Stage 7: Obsolete
| Configuration | Setting |
|---|---|
| Stage Name | Obsolete |
| Trigger | QA approval of obsolescence request |
| Permissions | View-only with watermark |
| Watermark | "OBSOLETE" in red diagonal |
| Requires | Document Change Request with reason |

### Stage 8: Archived
| Configuration | Setting |
|---|---|
| Stage Name | Archived |
| Trigger | Retention policy or manual archive |
| Permissions | QA/Regulatory: View only |
| Retention | Per document type retention schedule |
| Auto-Delete | NEVER — retention policy controls |

---

## 12. REGULATORY REFERENCES BY STAGE

### Stage 1: Draft
| Regulation | Clause | Requirement |
|---|---|---|
| ISO 13485:2016 | 4.2.3 | Documents shall be reviewed and approved by authorized personnel prior to issue |
| FDA 21 CFR 820 | 820.40(a) | Document controls shall ensure approval prior to issuance |
| FDA 21 CFR Part 11 | 11.10(b) | System shall generate accurate and complete copies |

### Stage 2: In Review
| Regulation | Clause | Requirement |
|---|---|---|
| ISO 13485:2016 | 4.2.3 | Documents shall be reviewed for adequacy |
| FDA 21 CFR 820 | 820.40(a) | Document controls shall ensure review by qualified personnel |
| ISO 13485:2016 | 5.5.2 | Responsibilities and authorities are defined |

### Stage 3: Approval
| Regulation | Clause | Requirement |
|---|---|---|
| ISO 13485:2016 | 4.2.3 | Documents approved prior to issue |
| FDA 21 CFR Part 11 | 11.50 | Signed records shall contain name, date/time, meaning |
| FDA 21 CFR Part 11 | 11.70 | Electronic signatures shall be unique to one individual |

### Stage 4: Training Period
| Regulation | Clause | Requirement |
|---|---|---|
| ISO 13485:2016 | 6.2 | Personnel shall be competent based on education, training, skills |
| FDA 21 CFR 820 | 820.25(b) | Training shall be documented |

### Stage 5: Effective
| Regulation | Clause | Requirement |
|---|---|---|
| ISO 13485:2016 | 4.2.3 | Current revision of applicable documents available at point of use |
| FDA 21 CFR 820 | 820.40(b) | Documents available at locations where essential |
| EU MDR | Annex IX, 2.2 | QMS shall ensure documents are up to date |

### Stage 6-8: Superseded/Obsolete/Archived
| Regulation | Clause | Requirement |
|---|---|---|
| ISO 13485:2016 | 4.2.3 | Prevent unintended use of obsolete documents |
| FDA 21 CFR 820 | 820.40(b) | Obsolete documents removed from points of use |
| ISO 13485:2016 | 4.2.5 | Records retained for defined period |

---

## 13. VALIDATION TEST SCRIPTS

### Test Script 1: Create New Document (Happy Path)
| Step | Action | Expected Result |
|---|---|---|
| 1.1 | Log in as Author | Dashboard loads |
| 1.2 | Navigate to Documents > Create New | Template selection appears |
| 1.3 | Select "SOP" template | Template loads with formatting |
| 1.4 | Verify doc number auto-generated | Format: SOP-XXX |
| 1.5 | Verify version shows v0.1 Draft | Correct version displayed |
| 1.6 | Fill all required fields | No validation errors |
| 1.7 | Save document | Document saved, visible in list |
| 1.8 | Verify audit trail entry | "Document Created" logged |

### Test Script 2: Submit for Review
| Step | Action | Expected Result |
|---|---|---|
| 2.1 | Open draft document as Author | Document opens |
| 2.2 | Click "Submit for Review" | Confirmation dialog appears |
| 2.3 | Confirm submission | Status changes to "In Review" |
| 2.4 | Verify document is locked | Author cannot edit |
| 2.5 | Verify reviewers notified | Email/notification sent |
| 2.6 | Log in as Reviewer | Pending review visible |

### Test Script 3: Review & Rejection Loop
| Step | Action | Expected Result |
|---|---|---|
| 3.1 | Log in as Reviewer | Dashboard shows pending review |
| 3.2 | Open document | Document displays read-only |
| 3.3 | Add review comments | Comments saved |
| 3.4 | Click "Reject" | Rejection reason dialog appears |
| 3.5 | Enter reason and confirm | Document returns to Draft |
| 3.6 | Verify version incremented | Now v0.2 |
| 3.7 | Verify Author notified | Notification with rejection reason |
| 3.8 | Log in as Author | Can edit document again |

### Test Script 4: Approval with E-Signature
| Step | Action | Expected Result |
|---|---|---|
| 4.1 | All reviewers have approved | Document at Approval stage |
| 4.2 | Log in as Approver (QA Manager) | Pending approval visible |
| 4.3 | Review document | All content accessible |
| 4.4 | Click "Approve" | E-signature dialog appears |
| 4.5 | Enter password + meaning | Signature validated |
| 4.6 | Verify status = "Approved" | Version promoted to v1.0 |
| 4.7 | Verify signature stored | Name, date/time, meaning recorded |

### Test Script 5: Training Gate
| Step | Action | Expected Result |
|---|---|---|
| 5.1 | Document becomes Effective | Training assigned to users |
| 5.2 | Log in as untrained user | Dashboard shows training required |
| 5.3 | Try to access effective document | **Blocked**: "Complete training first" |
| 5.4 | Complete training acknowledgment | Training marked complete |
| 5.5 | Try to access document again | Document accessible |

### Test Script 6: Superseding
| Step | Action | Expected Result |
|---|---|---|
| 6.1 | Create revision of v1.0 | New draft v1.1 created |
| 6.2 | Complete full review cycle | New version approved as v2.0 |
| 6.3 | Verify v1.0 status | Automatically "Superseded" |
| 6.4 | Open v1.0 | View-only with watermark |
| 6.5 | Try to edit v1.0 | **Blocked**: No edit actions available |

---

## 14. COMPREHENSIVE WORKFLOWS WITH REJECTION LOOPS

### Document Lifecycle (with all possibilities)
```
DRAFT
    |--(Submit)--> PRIMARY REVIEW
    |--(Cancel)--> [CANCELLED] (terminal)

PRIMARY REVIEW (Dept Manager)
    |--(Approve)--> SECONDARY REVIEW
    |--(Reject with comments)--> DRAFT (v0.x+1)
    |--(Overdue 5 days)--> [ESCALATE to Dept Head]

SECONDARY REVIEW (Plant Head/Director)
    |--(Approve)--> APPROVAL
    |--(Reject)--> DRAFT (v0.x+1)
    |--(Send Back to Primary)--> PRIMARY REVIEW
    |--(Overdue 5 days)--> [ESCALATE]

APPROVAL (QA Manager)
    |--(Approve with e-signature)--> TRAINING PERIOD
    |--(Reject)--> DRAFT (v0.x+1)

TRAINING PERIOD
    |--(All trained + effective date)--> EFFECTIVE (v promoted to N.0)
    |--(Training overdue)--> [ESCALATE to Dept Managers]
    |--(Extend training period)--> Continue waiting

EFFECTIVE
    |--(Periodic review: No changes)--> Reset review timer
    |--(Periodic review: Revision needed)--> New DRAFT (vN.1)
    |--(Periodic review: Obsolete)--> OBSOLETE
    |--(New version goes effective)--> SUPERSEDED (auto)

SUPERSEDED --> ARCHIVED (per retention policy)
OBSOLETE --> ARCHIVED (per retention policy)
```

---

## 15. TAILORED WORKFLOW (Author → Primary → Secondary → Approver)

### Role Responsibilities

| Role | Person | Responsibility | SLA |
|---|---|---|---|
| Author | Quality Engineer | Write/edit document, address feedback | No limit (30-day warning) |
| Primary Reviewer | Department Manager | Technical/content accuracy review | 5 business days |
| Secondary Reviewer | Plant Head/Director | Strategic/compliance review | 5 business days |
| Approver | QA Manager | Final regulatory sign-off (e-signature) | 3 business days |

### Key Rules:
1. **Rejection always goes to Author** — not back one step. This prevents ping-pong between reviewers.
2. **Primary must re-approve** after Author makes changes (even if Secondary rejected)
3. **Secondary can "Send Back to Primary"** if they disagree with Primary's approval
4. **Approver rejection requires clear rationale** — document goes all the way back to Author
5. **Escalation**: If any reviewer exceeds SLA, their manager is notified

---

## 16. SUPERSEDED DOCUMENTS — COMPLETE EXPLANATION

### View-Only Mode: ✅ YES
| Feature | Status | Why? |
|---|---|---|
| Editing | ❌ NO | Historical record — cannot be changed |
| Printing | ✅ YES (watermarked) | For audit/reference only |
| Download | ⚠️ Limited (watermarked) | Prevents uncontrolled copies |
| Comments | ❌ NO | No new comments |
| Approval actions | ❌ NO | Already approved in its time |
| E-signatures | ❌ NO | Cannot be re-signed |

### Visual Indicators:
- **Watermark**: "SUPERSEDED" in red/gray diagonal across every page
- **Header/footer**: "Superseded on [Date] by Version [X.X]"
- **Color coding**: Gray background or border
- **Banner**: At top of document view

### Regulatory Basis:
> **21 CFR Part 820.40(b)**: Obsolete documents must be "removed from all points of use or otherwise prevented from unintended use."

### Archiving vs Superseding:
| Aspect | Superseded | Archived |
|---|---|---|
| Status | Replaced by newer version | Stored for long-term retention |
| Visibility | Visible in system (view-only) | May be moved to cold storage |
| Access | Regular users can view (watermarked) | Restricted to QA/Regulatory |
| Purpose | Reference "what was the old version?" | Regulatory retention compliance |
| Duration | Until archived | Per retention policy (7-15 years) |
| Typical Trigger | New version goes Effective | Retention policy or manual |

### Cascade to Other Modules:
When a document is superseded:
1. **Training**: New training auto-assigned for new version
2. **CAPA**: If CAPA references old SOP, link updated
3. **Audits**: Old version available for audit trail
4. **Forms**: Filled forms linked to old version remain valid

---

## APPENDIX: KEY TERMS GLOSSARY

| Term | Definition |
|---|---|
| **DCR** | Document Change Request — formal request to create/modify a document |
| **DCO** | Document Change Order — approved change with implementation details |
| **ECN/ECO** | Engineering Change Notice/Order — engineering-specific change management |
| **SOP** | Standard Operating Procedure |
| **WI** | Work Instruction — detailed step-by-step procedure |
| **CAPA** | Corrective and Preventive Action |
| **NCR** | Non-Conformance Report |
| **DHF** | Design History File |
| **DMR** | Device Master Record |
| **DHR** | Device History Record |
| **IQ/OQ/PQ** | Installation/Operational/Performance Qualification |
| **SLA** | Service Level Agreement — time limit for an action |
| **21 CFR Part 11** | FDA regulation for electronic records and signatures |
| **ISO 13485** | Quality management system standard for medical devices |
| **EU MDR** | European Union Medical Device Regulation |
| **Vault State** | The lifecycle stage of a document in the eQMS |
| **Training Gate** | Mechanism blocking access until training is complete |
| **Watermark** | Visual indicator of document status on printed/viewed copies |

---

*This knowledge base was compiled from comprehensive eQMS training materials for medical device document management. It serves as the authoritative reference for building the Arni Medica eQMS Document Management module.*
