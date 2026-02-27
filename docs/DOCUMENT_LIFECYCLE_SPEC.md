# Document Lifecycle Workflow Specification
## Arni Medica Diagnostics eQMS

> This specification defines the complete document lifecycle workflow for the Arni eQMS.
> Use this as the reference when building/enhancing document management features.

---

## Document States (8 total)

| State | Code | Description | Editable | Visible |
|-------|------|-------------|----------|---------|
| **Draft** | `draft` | Document being authored/revised | Yes (by owner) | Owner + collaborators |
| **In Review** | `in_review` | Locked, awaiting reviewer actions | No (locked) | Reviewers + owner |
| **Approved** | `approved` | All approvals received, awaiting effective date | No | All authorized users |
| **Effective** | `effective` | Live document, currently in use | No | All authorized users |
| **Superseded** | `superseded` | Old version replaced by newer effective version | No (read-only) | Audit/reference only |
| **Obsolete** | `obsolete` | Retired, no replacement | No (read-only) | Audit/reference only |
| **Archive** | `archived` | Long-term retention | No (read-only) | Audit access only |
| **Cancelled** | `cancelled` | Draft cancelled before approval | No | Admin/audit only |

---

## State Transitions

### Valid Transitions Map

```
draft        -> in_review, cancelled
in_review    -> draft (reject), approved (all approvals)
approved     -> effective (on effective date)
effective    -> draft (revision creates NEW version), obsolete
superseded   -> archived
obsolete     -> archived
cancelled    -> (terminal state)
archived     -> (terminal state)
```

### Automatic Transitions

| Trigger | From | To | Condition |
|---------|------|----|-----------|
| Effective date reached | `approved` | `effective` | Scheduled date arrives AND training complete |
| New version becomes effective | old `effective` | `superseded` | New version of same document goes effective |
| Retention period expires | `superseded`/`obsolete` | `archived` | Regulatory retention period met |

### User-Initiated Transitions

| Action | From | To | Who Can Do It | Requires |
|--------|------|----|---------------|----------|
| Submit for Review | `draft` | `in_review` | Document Owner | All required fields filled |
| Reject/Request Changes | `in_review` | `draft` | Any Reviewer | Comment explaining reason |
| Approve (reviewer) | `in_review` | (stays `in_review`) | Assigned Reviewer | E-signature (21 CFR Part 11) |
| Final Approve | `in_review` | `approved` | Final Approver | All reviewers approved + E-signature |
| Initiate Revision | `effective` | new `draft` | Document Owner | Change request linked |
| Obsolete | `effective` | `obsolete` | Document Owner + QA approval | Justification required |
| Cancel Draft | `draft` | `cancelled` | Document Owner | Reason required |

---

## Versioning Scheme

| Version Pattern | Meaning |
|----------------|---------|
| v0.x (0.1, 0.2, 0.3) | Draft iterations (auto-incremented on each review cycle) |
| v1.0 | First approved/effective version |
| v1.1, v1.2 (draft) | Revision drafts based on v1.0 |
| v2.0 | Second major approved version |
| vN.0 | Major version = approval count |

### Rules
- Draft saves do NOT create new versions (auto-save within same version)
- Submitting for review increments minor version (v0.1 -> v0.2)
- Rejection and resubmit increments minor version (v0.2 -> v0.3)
- Final approval promotes to next major version (v0.5 -> v1.0)
- Revision drafts use parent.minor format (v1.0 -> v1.1 draft)

---

## Review Workflow

### Workflow Configuration
- **Parallel reviews**: All reviewers notified simultaneously
- **Sequential reviews**: Reviewers notified in order (optional)
- **Escalation**: If reviewer doesn't act within N days, escalate to their manager
- **Reminders**: Day 1, 3, 5 (configurable)
- **Deadline**: Configurable per document type

### Reviewer Actions
1. **Approve** - Signs off on the document (e-signature required)
2. **Reject** - Returns to draft with mandatory comments
3. **Request Changes** - Same as reject (alias)

### Approval Requirements
- All assigned reviewers must approve
- Final approver (usually QA Manager) signs last
- Each approval recorded with: name, date/time, meaning of signature, signature ID

---

## Electronic Signatures (21 CFR Part 11)

### Signature Manifestation
Each signature record must include:
- **Printed name** of the signer
- **Date and time** of signing
- **Meaning** of the signature (e.g., "Reviewed and Approved", "Authored", "Final QA Approval")
- **Signature ID** (unique, system-generated)

### Re-authentication
- User must re-enter password at time of signing
- Session token is NOT sufficient
- Failed attempts are logged

### Audit Trail
- Every signature action is logged
- Signatures cannot be modified or deleted
- Linked to specific document version

---

## Training Integration

### Training Assignment Rules
- When document transitions to `approved`, training is auto-assigned
- Training assigned to users based on: department, role, document type
- Training must be completed BEFORE effective date

### Training Gate
- Users cannot access `effective` document until training is complete
- System blocks access with message: "You must complete training to view this document"
- Training completion = "I have read and understood" acknowledgment

### Training Tracking
- Dashboard shows completion progress
- Owner can monitor who has/hasn't completed
- Overdue training generates notifications

---

## Periodic Review

### Configuration
- Review interval: 1-3 years (configurable per document type)
- Notification: Sent to document owner X days before due date
- Escalation: If not reviewed by due date, escalate to department head

### Review Outcomes
1. **No Changes Needed** - Reset review timer, document remains effective
2. **Minor Revisions** - Initiate revision workflow (new draft created)
3. **Major Revisions** - Initiate revision with expanded review team
4. **Obsolete** - Begin obsoletion workflow

### Review Documentation
- Even "no changes" must be documented with reviewer notes
- System logs: who reviewed, when, decision, comments

---

## Watermarking & Visual Indicators

| State | Watermark | Visual Indicator |
|-------|-----------|------------------|
| Draft | "DRAFT" (diagonal, gray) | Yellow status badge |
| In Review | "UNDER REVIEW" (diagonal, blue) | Blue status badge |
| Approved | None | Green status badge |
| Effective | None (clean copy) | Green "EFFECTIVE" badge |
| Superseded | "SUPERSEDED" (diagonal, red) | Gray status badge |
| Obsolete | "OBSOLETE" (diagonal, red) | Red status badge |
| Archived | "ARCHIVED" (diagonal, gray) | Gray status badge |

---

## Document Access Matrix

| State | Owner | Reviewers | All Users | Admin | Audit |
|-------|-------|-----------|-----------|-------|-------|
| Draft | Read/Write | - | - | Read | Read |
| In Review | Read | Read + Comment | - | Read | Read |
| Approved | Read | Read | Read* | Read | Read |
| Effective | Read | Read | Read** | Read | Read |
| Superseded | Read | Read | - | Read | Read |
| Obsolete | Read | Read | - | Read | Read |
| Archived | - | - | - | Read | Read |

\* After training completion
\** Gated by training acknowledgment

---

## Change Control Integration

### Revision Workflow
1. Document owner creates Change Request (linked to document)
2. Change Request approved -> new Draft version created
3. Draft inherits content from current Effective version
4. Normal review/approval cycle follows
5. When new version becomes Effective, old version auto-supersedes

### Emergency Changes
- Expedited review path (shorter deadlines, fewer reviewers)
- Must still follow e-signature requirements
- Flagged in audit trail as "Emergency Change"

---

## Audit Trail Requirements

### Logged Events
- Document creation
- Every save/edit (with diff if possible)
- Status transitions
- Reviewer assignments
- Review actions (approve/reject/comment)
- E-signature applications
- Training assignments and completions
- Access events (who viewed, when)
- Periodic review actions
- Obsoletion/archival events

### Retention
- Audit trail retained for lifetime of device + regulatory period
- Cannot be modified or deleted
- Exportable for regulatory audits

---

## API Endpoints Needed

### Document Lifecycle
```
POST   /api/documents/                     # Create new document
PATCH  /api/documents/{id}/                # Update draft
POST   /api/documents/{id}/submit/         # Submit for review
POST   /api/documents/{id}/reject/         # Reject (reviewer)
POST   /api/documents/{id}/approve/        # Approve (reviewer)
POST   /api/documents/{id}/final-approve/  # Final approval
POST   /api/documents/{id}/make-effective/ # Trigger effective transition
POST   /api/documents/{id}/revise/         # Create revision draft
POST   /api/documents/{id}/obsolete/       # Obsolete document
POST   /api/documents/{id}/cancel/         # Cancel draft
GET    /api/documents/{id}/history/        # Version history
GET    /api/documents/{id}/audit-trail/    # Audit trail
```

### Review Workflow
```
GET    /api/documents/{id}/reviewers/       # List assigned reviewers
POST   /api/documents/{id}/assign-reviewer/ # Assign reviewer
GET    /api/documents/{id}/review-status/   # Review progress
POST   /api/documents/{id}/escalate/        # Escalate overdue review
```

### Training
```
GET    /api/documents/{id}/training-status/  # Training completion status
POST   /api/documents/{id}/acknowledge/      # Training acknowledgment
GET    /api/training/my-assignments/         # User's pending training
```

### Periodic Review
```
GET    /api/documents/review-due/            # Documents due for review
POST   /api/documents/{id}/periodic-review/  # Submit review decision
```

---

## Frontend Components Needed

### Pages
- `DocumentLifecycle.jsx` - Visual workflow tracker (state diagram)
- `ReviewDashboard.jsx` - Pending reviews for current user
- `TrainingDashboard.jsx` - Training assignments and completion
- `PeriodicReviewQueue.jsx` - Documents due for periodic review
- `AuditTrailViewer.jsx` - Searchable audit log

### Components
- `StatusBadge.jsx` - Color-coded document status badge
- `WorkflowTracker.jsx` - Visual step indicator showing current state
- `ReviewerPanel.jsx` - Shows reviewer list with statuses
- `ESignatureModal.jsx` - Re-authentication + signature capture (DONE)
- `TrainingGate.jsx` - Blocks access until training complete
- `VersionHistory.jsx` - Timeline of all document versions
- `WatermarkOverlay.jsx` - Renders appropriate watermark on document view
- `PeriodicReviewForm.jsx` - Form for periodic review decision
- `DCOWorkflowTracker.jsx` - DCO-specific workflow visualization (DONE)

---

## Narrative Reference: SOP-042 Journey

The complete document lifecycle is illustrated through the story of SOP-042 (Sterilizer Operation Procedure):

1. **Draft** (Jan 10) - Created from SOP template by Sarah Chen
2. **In Review** (Jan 15-25) - Rejected twice (Tom: dwell time error, Maria: missing PPE), Dr. James delayed by vacation
3. **Approved** (Jan 26) - v1.0 approved with e-signature by QA Manager Lisa
4. **Effective** (Feb 2) - Training completed by all 15 technicians, training gate enforced
5. **Periodic Review** (Feb 2027) - No changes needed, timer reset
6. **Revision** (June 2027) - Software update requires Step 10 change, v2.0 created
7. **Superseded** (July 2027) - v1.0 auto-archived when v2.0 goes effective
8. **Obsolete** (Jan 2032) - Equipment retired, document obsoleted with QA approval
9. **Archive** - Long-term retention for regulatory compliance

This narrative should be used as test scenario and demo flow for the eQMS.
