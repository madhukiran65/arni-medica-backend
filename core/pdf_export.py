"""
PDF export functionality for Arni Medica reports.
Generates professional PDF reports for CAPA, Deviation, and Audit records.
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, grey, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
    KeepTogether, Image
)
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from capa.models import CAPA
from deviations.models import Deviation
from audit_mgmt.models import AuditPlan, AuditFinding


class PDFPageWithFooter(canvas.Canvas):
    """Custom canvas for page numbers and footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_num = 0
        self.generated_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def showPage(self):
        self.page_num += 1
        self._draw_footer()
        super().showPage()

    def _draw_footer(self):
        """Draw footer on each page."""
        footer_style = ParagraphStyle(
            'footer',
            fontSize=9,
            textColor=grey,
            alignment=TA_CENTER
        )
        self.setFont('Helvetica', 8)
        self.setFillColor(grey)
        self.drawString(
            4.25 * inch,
            0.5 * inch,
            f"Page {self.page_num} | Generated: {self.generated_date}"
        )


def _get_header_elements(report_type):
    """Create header elements for the report."""
    styles = getSampleStyleSheet()
    elements = []

    # Company header
    header_style = ParagraphStyle(
        'header',
        fontSize=20,
        textColor=HexColor('#1a5490'),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("Arni eQMS", header_style))

    # Report type
    subheader_style = ParagraphStyle(
        'subheader',
        fontSize=14,
        textColor=HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph(f"{report_type} Report", subheader_style))
    elements.append(Spacer(1, 0.2*inch))

    return elements


def _create_info_table(label_value_pairs):
    """Create a formatted information table from label-value pairs."""
    data = []
    for label, value in label_value_pairs:
        if value is None:
            value = 'N/A'
        elif isinstance(value, bool):
            value = 'Yes' if value else 'No'
        elif isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            value = str(value)

        data.append([label, value])

    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), black),
        ('ALIGN', (0, 0), (0, -1), TA_LEFT),
        ('ALIGN', (1, 0), (1, -1), TA_LEFT),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, HexColor('#f9f9f9')]),
    ]))

    return table


def _format_choice_display(value, choices_dict):
    """Format a choice field value to its display name."""
    if isinstance(choices_dict, list):
        for choice_val, display_text in choices_dict:
            if choice_val == value:
                return display_text
    return str(value)


def _get_section_title_style():
    """Create style for section titles."""
    return ParagraphStyle(
        'sectiontitle',
        fontSize=12,
        textColor=HexColor('#1a5490'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )


def generate_capa_report(capa_id):
    """
    Generate a PDF report for a CAPA record.

    Args:
        capa_id: ID of the CAPA to export

    Returns:
        BytesIO: PDF file content as bytes

    Raises:
        ObjectDoesNotExist: If CAPA not found
    """
    try:
        capa = CAPA.objects.get(pk=capa_id)
    except CAPA.DoesNotExist:
        raise ObjectDoesNotExist(f"CAPA with ID {capa_id} not found")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        canvasmaker=PDFPageWithFooter
    )

    elements = []
    styles = getSampleStyleSheet()
    section_title_style = _get_section_title_style()
    normal_style = styles['Normal']

    # Header
    elements.extend(_get_header_elements("CAPA"))

    # Identification Section
    elements.append(Paragraph("1. Identification", section_title_style))
    id_data = [
        ["CAPA ID:", capa.capa_id],
        ["Title:", capa.title],
        ["Priority:", _format_choice_display(capa.priority, CAPA.PRIORITY_CHOICES)],
        ["Status:", _format_choice_display(capa.current_phase, CAPA.PHASE_CHOICES)],
        ["Type:", _format_choice_display(capa.capa_type, CAPA.CAPA_TYPE_CHOICES)],
    ]
    elements.append(_create_info_table(id_data))
    elements.append(Spacer(1, 0.2*inch))

    # Source & Classification
    elements.append(Paragraph("2. Source & Classification", section_title_style))
    source_data = [
        ["Source:", _format_choice_display(capa.source, CAPA.SOURCE_CHOICES)],
        ["Category:", _format_choice_display(capa.category, CAPA.CATEGORY_CHOICES)],
        ["Department:", capa.department.name if capa.department else "N/A"],
        ["Is Recurring:", "Yes" if capa.is_recurring else "No"],
    ]
    elements.append(_create_info_table(source_data))
    elements.append(Spacer(1, 0.2*inch))

    # Description
    if capa.description:
        elements.append(Paragraph("3. Description", section_title_style))
        elements.append(Paragraph(capa.description, normal_style))
        elements.append(Spacer(1, 0.2*inch))

    # 5W Analysis
    five_w_data = [
        ["What (Problem):", capa.what_happened or "N/A"],
        ["When (Date/Time):", capa.when_happened.strftime('%Y-%m-%d %H:%M') if capa.when_happened else "N/A"],
        ["Where (Location):", capa.where_happened or "N/A"],
        ["Who (Affected):", capa.who_affected or "N/A"],
        ["Why (Root Cause):", capa.why_happened or "N/A"],
        ["How (Discovery):", capa.how_discovered or "N/A"],
    ]
    elements.append(Paragraph("4. 5W Analysis", section_title_style))
    elements.append(_create_info_table(five_w_data))
    elements.append(Spacer(1, 0.2*inch))

    # Root Cause Analysis
    if capa.root_cause:
        elements.append(Paragraph("5. Root Cause Analysis", section_title_style))
        rca_data = [
            ["Method:", _format_choice_display(capa.root_cause_analysis_method, CAPA.ROOT_CAUSE_METHOD_CHOICES) or "N/A"],
            ["Root Cause:", capa.root_cause],
            ["Verified:", "Yes" if capa.root_cause_verified else "No"],
        ]
        if capa.contributing_factors:
            factors_text = ", ".join(capa.contributing_factors) if isinstance(capa.contributing_factors, list) else str(capa.contributing_factors)
            rca_data.append(["Contributing Factors:", factors_text])
        elements.append(_create_info_table(rca_data))
        elements.append(Spacer(1, 0.2*inch))

    # Risk Assessment
    elements.append(Paragraph("6. Risk Assessment", section_title_style))
    risk_data = [
        ["Severity (1-5):", str(capa.risk_severity)],
        ["Occurrence (1-5):", str(capa.risk_occurrence)],
        ["Detection (1-5):", str(capa.risk_detection)],
        ["RPN (Before Action):", str(capa.pre_action_rpn or capa.risk_priority_number)],
        ["RPN (After Action):", str(capa.post_action_rpn or "Pending")],
        ["Acceptability:", _format_choice_display(capa.risk_acceptability, CAPA.RISK_ACCEPTABILITY_CHOICES)],
    ]
    elements.append(_create_info_table(risk_data))
    elements.append(Spacer(1, 0.2*inch))

    # Timeline
    elements.append(Paragraph("7. Timeline & Dates", section_title_style))
    timeline_data = [
        ["Created:", capa.created_at.strftime('%Y-%m-%d %H:%M') if capa.created_at else "N/A"],
        ["Target Completion:", capa.target_completion_date.strftime('%Y-%m-%d') if capa.target_completion_date else "N/A"],
        ["Actual Completion:", capa.actual_completion_date.strftime('%Y-%m-%d') if capa.actual_completion_date else "Pending"],
        ["Current Phase:", _format_choice_display(capa.current_phase, CAPA.PHASE_CHOICES)],
        ["Phase Entered:", capa.phase_entered_at.strftime('%Y-%m-%d %H:%M') if capa.phase_entered_at else "N/A"],
    ]
    elements.append(_create_info_table(timeline_data))
    elements.append(Spacer(1, 0.2*inch))

    # Implementation & Effectiveness
    elements.append(Paragraph("8. Implementation & Effectiveness", section_title_style))
    impl_data = [
        ["Implementation Verified:", "Yes" if capa.implementation_verified else "No"],
        ["Effectiveness Result:", _format_choice_display(capa.effectiveness_result, CAPA.EFFECTIVENESS_RESULT_CHOICES)],
    ]
    if capa.implementation_notes:
        impl_data.append(["Implementation Notes:", capa.implementation_notes])
    if capa.effectiveness_evidence:
        impl_data.append(["Effectiveness Evidence:", capa.effectiveness_evidence])
    elements.append(_create_info_table(impl_data))
    elements.append(Spacer(1, 0.2*inch))

    # Responsibilities
    elements.append(Paragraph("9. Responsibilities", section_title_style))
    resp_data = [
        ["Responsible Person:", capa.responsible_person.get_full_name() if capa.responsible_person else "N/A"],
        ["Assigned To:", capa.assigned_to.get_full_name() if capa.assigned_to else "N/A"],
        ["CAPA Coordinator:", capa.coordinator.get_full_name() if capa.coordinator else "N/A"],
    ]
    elements.append(_create_info_table(resp_data))
    elements.append(Spacer(1, 0.3*inch))

    # Footer note
    footer_style = ParagraphStyle(
        'footer',
        fontSize=9,
        textColor=grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"CAPA ID: {capa.capa_id}</i>",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_deviation_report(deviation_id):
    """
    Generate a PDF report for a Deviation record.

    Args:
        deviation_id: ID of the Deviation to export

    Returns:
        BytesIO: PDF file content as bytes

    Raises:
        ObjectDoesNotExist: If Deviation not found
    """
    try:
        deviation = Deviation.objects.get(pk=deviation_id)
    except Deviation.DoesNotExist:
        raise ObjectDoesNotExist(f"Deviation with ID {deviation_id} not found")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        canvasmaker=PDFPageWithFooter
    )

    elements = []
    styles = getSampleStyleSheet()
    section_title_style = _get_section_title_style()
    normal_style = styles['Normal']

    # Header
    elements.extend(_get_header_elements("Deviation"))

    # Identification
    elements.append(Paragraph("1. Identification", section_title_style))
    id_data = [
        ["Deviation ID:", deviation.deviation_id],
        ["Title:", deviation.title],
        ["Type:", _format_choice_display(deviation.deviation_type, Deviation.TYPE_CHOICES)],
        ["Status:", _format_choice_display(deviation.current_stage, Deviation.STAGE_CHOICES)],
    ]
    elements.append(_create_info_table(id_data))
    elements.append(Spacer(1, 0.2*inch))

    # Classification
    elements.append(Paragraph("2. Classification", section_title_style))
    class_data = [
        ["Category:", _format_choice_display(deviation.category, Deviation.CATEGORY_CHOICES)],
        ["Severity:", _format_choice_display(deviation.severity, Deviation.SEVERITY_CHOICES)],
        ["Source:", _format_choice_display(deviation.source, Deviation.SOURCE_CHOICES)],
        ["Patient Safety Impact:", "Yes" if deviation.patient_safety_impact else "No"],
        ["Regulatory Reportable:", "Yes" if deviation.regulatory_reportable else "No"],
    ]
    elements.append(_create_info_table(class_data))
    elements.append(Spacer(1, 0.2*inch))

    # Description
    if deviation.description:
        elements.append(Paragraph("3. Description", section_title_style))
        elements.append(Paragraph(deviation.description, normal_style))
        elements.append(Spacer(1, 0.2*inch))

    # Impact Assessment
    elements.append(Paragraph("4. Impact Assessment", section_title_style))
    impact_data = [
        ["Process Affected:", deviation.process_affected or "N/A"],
        ["Product Affected:", deviation.product_affected or "N/A"],
    ]
    if deviation.batch_lot_number:
        impact_data.append(["Batch/Lot Number:", deviation.batch_lot_number])
    if deviation.quantity_affected:
        impact_data.append(["Quantity Affected:", str(deviation.quantity_affected)])
    if deviation.impact_assessment:
        impact_data.append(["Impact Assessment:", deviation.impact_assessment])
    elements.append(_create_info_table(impact_data))
    elements.append(Spacer(1, 0.2*inch))

    # Investigation
    if deviation.root_cause or deviation.investigation_summary:
        elements.append(Paragraph("5. Investigation", section_title_style))
        inv_data = []
        if deviation.root_cause:
            inv_data.append(["Root Cause:", deviation.root_cause])
        if deviation.investigation_summary:
            inv_data.append(["Investigation Summary:", deviation.investigation_summary])
        if deviation.investigated_by:
            inv_data.append(["Investigated By:", deviation.investigated_by.get_full_name()])
        if deviation.investigation_completed_at:
            inv_data.append(["Investigation Completed:", deviation.investigation_completed_at.strftime('%Y-%m-%d %H:%M')])
        if inv_data:
            elements.append(_create_info_table(inv_data))
        elements.append(Spacer(1, 0.2*inch))

    # Resolution
    if deviation.corrective_action or deviation.preventive_action or deviation.disposition:
        elements.append(Paragraph("6. Resolution", section_title_style))
        res_data = []
        if deviation.corrective_action:
            res_data.append(["Corrective Action:", deviation.corrective_action])
        if deviation.preventive_action:
            res_data.append(["Preventive Action:", deviation.preventive_action])
        if deviation.disposition:
            res_data.append(["Disposition:", _format_choice_display(deviation.disposition, Deviation.DISPOSITION_CHOICES)])
        if deviation.disposition_justification:
            res_data.append(["Disposition Justification:", deviation.disposition_justification])
        if deviation.capa:
            res_data.append(["Associated CAPA:", deviation.capa.capa_id])
        if res_data:
            elements.append(_create_info_table(res_data))
        elements.append(Spacer(1, 0.2*inch))

    # Dates & SLA
    elements.append(Paragraph("7. Timeline", section_title_style))
    date_data = [
        ["Reported Date:", deviation.reported_date.strftime('%Y-%m-%d %H:%M')],
        ["Days Open:", str(deviation.days_open)],
        ["Target Closure Date:", deviation.target_closure_date.strftime('%Y-%m-%d') if deviation.target_closure_date else "N/A"],
        ["Actual Closure Date:", deviation.actual_closure_date.strftime('%Y-%m-%d') if deviation.actual_closure_date else "Pending"],
    ]
    elements.append(_create_info_table(date_data))
    elements.append(Spacer(1, 0.2*inch))

    # Assignment
    elements.append(Paragraph("8. Assignment", section_title_style))
    assign_data = [
        ["Department:", deviation.department.name if deviation.department else "N/A"],
        ["Reported By:", deviation.reported_by.get_full_name() if deviation.reported_by else "N/A"],
        ["Assigned To:", deviation.assigned_to.get_full_name() if deviation.assigned_to else "N/A"],
        ["QA Reviewer:", deviation.qa_reviewer.get_full_name() if deviation.qa_reviewer else "N/A"],
    ]
    elements.append(_create_info_table(assign_data))
    elements.append(Spacer(1, 0.3*inch))

    # Footer
    footer_style = ParagraphStyle(
        'footer',
        fontSize=9,
        textColor=grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Deviation ID: {deviation.deviation_id}</i>",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_audit_report(audit_id):
    """
    Generate a PDF report for an Audit Plan with findings.

    Args:
        audit_id: ID of the Audit Plan to export

    Returns:
        BytesIO: PDF file content as bytes

    Raises:
        ObjectDoesNotExist: If Audit Plan not found
    """
    try:
        audit = AuditPlan.objects.get(pk=audit_id)
    except AuditPlan.DoesNotExist:
        raise ObjectDoesNotExist(f"Audit Plan with ID {audit_id} not found")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        canvasmaker=PDFPageWithFooter
    )

    elements = []
    styles = getSampleStyleSheet()
    section_title_style = _get_section_title_style()
    normal_style = styles['Normal']

    # Header
    elements.extend(_get_header_elements("Audit Plan"))

    # Identification
    elements.append(Paragraph("1. Audit Information", section_title_style))
    audit_data = [
        ["Audit ID:", audit.audit_id],
        ["Type:", _format_choice_display(audit.audit_type, AuditPlan.AUDIT_TYPE_CHOICES)],
        ["Status:", _format_choice_display(audit.status, AuditPlan.STATUS_CHOICES)],
    ]
    if audit.supplier:
        audit_data.append(["Supplier/Area:", audit.supplier])
    elements.append(_create_info_table(audit_data))
    elements.append(Spacer(1, 0.2*inch))

    # Scope
    if audit.scope:
        elements.append(Paragraph("2. Scope", section_title_style))
        elements.append(Paragraph(audit.scope, normal_style))
        elements.append(Spacer(1, 0.2*inch))

    # Schedule
    elements.append(Paragraph("3. Schedule", section_title_style))
    sched_data = [
        ["Planned Start Date:", audit.planned_start_date.strftime('%Y-%m-%d')],
        ["Planned End Date:", audit.planned_end_date.strftime('%Y-%m-%d')],
        ["Actual Start Date:", audit.actual_start_date.strftime('%Y-%m-%d') if audit.actual_start_date else "N/A"],
        ["Actual End Date:", audit.actual_end_date.strftime('%Y-%m-%d') if audit.actual_end_date else "N/A"],
    ]
    elements.append(_create_info_table(sched_data))
    elements.append(Spacer(1, 0.2*inch))

    # Summary of Findings
    elements.append(Paragraph("4. Findings Summary", section_title_style))
    findings_data = [
        ["Total Findings:", str(audit.findings_count)],
        ["Major Non-Conformances:", str(audit.major_nc)],
        ["Minor Non-Conformances:", str(audit.minor_nc)],
        ["Observations:", str(audit.observations)],
    ]
    if audit.lead_auditor:
        findings_data.append(["Lead Auditor:", audit.lead_auditor.get_full_name()])
    if audit.next_audit_planned:
        findings_data.append(["Next Audit Planned:", audit.next_audit_planned.strftime('%Y-%m-%d')])
    elements.append(_create_info_table(findings_data))
    elements.append(Spacer(1, 0.3*inch))

    # Detailed Findings Table
    findings = audit.findings.all()
    if findings.exists():
        elements.append(Paragraph("5. Detailed Findings", section_title_style))

        findings_table_data = [
            ["Finding ID", "Category", "Description", "Status"]
        ]

        for finding in findings:
            category_display = _format_choice_display(finding.category, AuditFinding.CATEGORY_CHOICES)
            status_display = _format_choice_display(finding.status, AuditFinding.STATUS_CHOICES)

            # Truncate long descriptions
            description = finding.description[:100] + "..." if len(finding.description) > 100 else finding.description

            findings_table_data.append([
                finding.finding_id,
                category_display,
                description,
                status_display
            ])

        findings_table = Table(findings_table_data, colWidths=[1.2*inch, 1.3*inch, 2.5*inch, 1*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), TA_LEFT),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f9f9f9')]),
        ]))

        elements.append(findings_table)
        elements.append(Spacer(1, 0.3*inch))

    # Footer
    footer_style = ParagraphStyle(
        'footer',
        fontSize=9,
        textColor=grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Audit ID: {audit.audit_id}</i>",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
