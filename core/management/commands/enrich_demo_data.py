from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Deviation, ChangeControl, Supplier


class Command(BaseCommand):
    help = "Enrich existing demo data records with missing fields"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting demo data enrichment..."))

        self.enrich_deviations()
        self.enrich_change_controls()
        self.enrich_suppliers()

        self.stdout.write(self.style.SUCCESS("Demo data enrichment completed!"))

    def enrich_deviations(self):
        """Enrich Deviation records with missing fields."""
        self.stdout.write("Enriching Deviation records...")

        deviations_data = [
            {
                "deviation_id": "DEV-2025-001",
                "source_reference": "INC-TEMP-001",
                "batch_lot_number": "LOT-2024-MED-045",
                "quantity_affected": "200 units",
                "reported_date": timezone.now() - timedelta(days=15),
                "target_closure_date": timezone.now() + timedelta(days=5),
                "current_stage": "investigation",
                "root_cause": "Thermostat malfunction in Incubator Unit 5",
                "investigation_summary": "Temperature data logger showed excursion to 42°C for 3 hours",
                "disposition": "quarantine",
                "disposition_justification": "All affected media lots quarantined pending further testing",
                "requires_capa": True,
                "regulatory_reportable": True,
            },
            {
                "deviation_id": "DEV-2025-002",
                "source_reference": "VAL-2024-008",
                "batch_lot_number": "N/A",
                "reported_date": timezone.now() - timedelta(days=12),
                "target_closure_date": timezone.now() + timedelta(days=10),
                "current_stage": "qa_review",
                "disposition": "use_as_is",
                "disposition_justification": "Additional replicates to be performed",
                "requires_capa": False,
            },
            {
                "deviation_id": "DEV-2025-003",
                "source_reference": "PR-2024-LBL-067",
                "batch_lot_number": "LOT-2024-PDP-112",
                "quantity_affected": "500 units",
                "reported_date": timezone.now() - timedelta(days=8),
                "target_closure_date": timezone.now() + timedelta(days=3),
                "current_stage": "investigation",
                "disposition": "rework",
                "disposition_justification": "All affected units to be relabeled",
                "requires_capa": False,
            },
            {
                "deviation_id": "DEV-2025-004",
                "source_reference": "IR-2024-MAT-023",
                "batch_lot_number": "LOT-VIAL-2024-089",
                "quantity_affected": "10000 vials",
                "reported_date": timezone.now() - timedelta(days=10),
                "target_closure_date": timezone.now() + timedelta(days=7),
                "current_stage": "capa_plan",
                "disposition": "reject",
                "disposition_justification": "Entire lot rejected, return to supplier",
                "requires_capa": True,
                "regulatory_reportable": True,
            },
            {
                "deviation_id": "DEV-2025-005",
                "source_reference": "PM-2024-EQ-015",
                "reported_date": timezone.now() - timedelta(days=5),
                "target_closure_date": timezone.now() + timedelta(days=20),
                "current_stage": "opened",
                "requires_capa": False,
            },
            {
                "deviation_id": "DEV-2025-006",
                "source_reference": "AUD-2025-001-F3",
                "reported_date": timezone.now() - timedelta(days=7),
                "target_closure_date": timezone.now() + timedelta(days=30),
                "current_stage": "qa_review",
                "requires_capa": False,
            },
        ]

        for dev_data in deviations_data:
            try:
                deviation = Deviation.objects.get(deviation_id=dev_data["deviation_id"])
                # Update fields
                for key, value in dev_data.items():
                    if key != "deviation_id":
                        setattr(deviation, key, value)
                deviation.save()
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Updated {dev_data['deviation_id']}")
                )
            except Deviation.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Deviation {dev_data['deviation_id']} not found, skipping"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error updating {dev_data['deviation_id']}: {str(e)}"
                    )
                )

    def enrich_change_controls(self):
        """Enrich ChangeControl records with missing fields."""
        self.stdout.write("Enriching ChangeControl records...")

        change_controls_data = [
            {
                "change_id": "CC-2025-001",
                "justification": "Current aseptic parameters need updating to match revised FDA guidance on filling operations",
                "proposed_implementation_date": timezone.now() + timedelta(days=30),
                "target_completion_date": timezone.now() + timedelta(days=45),
                "affected_areas": ["Manufacturing", "Quality Assurance", "Validation"],
                "impact_summary": "Requires revalidation of filling line A, updated training for 12 operators",
                "quality_impact": "Improved sterility assurance level",
                "regulatory_impact": "Aligns with updated FDA guidance",
                "safety_impact": "Reduced contamination risk",
                "training_impact": "12 operators require retraining on new parameters",
                "requires_validation": True,
                "requires_regulatory_notification": False,
            },
            {
                "change_id": "CC-2025-002",
                "justification": "Current LIMS version lacks critical audit trail features required by FDA",
                "proposed_implementation_date": timezone.now() + timedelta(days=20),
                "target_completion_date": timezone.now() + timedelta(days=35),
                "affected_areas": ["IT", "Quality Assurance", "All Labs"],
                "impact_summary": "System downtime 8 hours, data migration required",
                "quality_impact": "Enhanced data integrity and audit trail",
                "regulatory_impact": "Improved 21 CFR Part 11 compliance",
                "training_impact": "All LIMS users require 2-hour refresher",
                "requires_validation": True,
            },
            {
                "change_id": "CC-2025-003",
                "justification": "Current supplier has recurring quality issues; new supplier has better track record and ISO 13485 certification",
                "proposed_implementation_date": timezone.now() + timedelta(days=45),
                "target_completion_date": timezone.now() + timedelta(days=60),
                "affected_areas": ["Procurement", "Quality Assurance", "Manufacturing"],
                "impact_summary": "Requires new supplier qualification, bridge studies, and regulatory notification",
                "quality_impact": "Expected improvement in reagent consistency",
                "regulatory_impact": "Requires notification to regulatory bodies per change notification requirements",
                "safety_impact": "No negative safety impact expected",
                "requires_validation": True,
                "requires_regulatory_notification": True,
            },
            {
                "change_id": "CC-2025-004",
                "justification": "Usage data analysis shows current intervals are conservative; adjustment will improve efficiency without impacting quality",
                "proposed_implementation_date": timezone.now() + timedelta(days=10),
                "target_completion_date": timezone.now() + timedelta(days=15),
                "affected_areas": ["Maintenance", "Quality Assurance"],
                "impact_summary": "Minor schedule adjustment, no production impact",
                "quality_impact": "Maintained calibration accuracy with optimized intervals",
                "requires_validation": False,
            },
        ]

        for cc_data in change_controls_data:
            try:
                change_control = ChangeControl.objects.get(change_id=cc_data["change_id"])
                # Update fields
                for key, value in cc_data.items():
                    if key != "change_id":
                        setattr(change_control, key, value)
                change_control.save()
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Updated {cc_data['change_id']}")
                )
            except ChangeControl.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ ChangeControl {cc_data['change_id']} not found, skipping"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error updating {cc_data['change_id']}: {str(e)}"
                    )
                )

    def enrich_suppliers(self):
        """Enrich Supplier records with additional fields."""
        self.stdout.write("Enriching Supplier records...")

        suppliers_data = [
            {
                "supplier_id": "SUP-RAW-001",
                "description": "Leading supplier of biochemical raw materials for IVD manufacturing",
                "address": "1200 Innovation Drive",
                "city": "San Diego",
                "state": "California",
                "postal_code": "92121",
                "website": "https://www.biochemmaterials.com",
                "iso_certified": True,
                "iso_certificate_number": "ISO-13485-2024-001",
                "iso_expiry_date": timezone.now() + timedelta(days=365),
                "risk_justification": "Medium risk due to single-source for 2 critical reagents",
                "qualified_date": timezone.now() - timedelta(days=180),
                "next_evaluation_date": timezone.now() + timedelta(days=185),
                "products_services": [
                    "Biochemical reagents",
                    "Buffer solutions",
                    "Enzyme substrates",
                ],
            },
            {
                "supplier_id": "SUP-REAG-002",
                "description": "Global supplier of specialty reagents and antibodies for diagnostics",
                "address": "Industriestraße 45",
                "city": "Munich",
                "state": "Bavaria",
                "postal_code": "80331",
                "website": "https://www.reagentsource.de",
                "iso_certified": True,
                "iso_certificate_number": "ISO-13485-2024-002",
                "iso_expiry_date": timezone.now() + timedelta(days=300),
                "risk_justification": "High risk - sole source for proprietary antibodies, long lead times",
                "qualified_date": timezone.now() - timedelta(days=365),
                "next_evaluation_date": timezone.now() + timedelta(days=90),
                "products_services": [
                    "Monoclonal antibodies",
                    "Conjugated reagents",
                    "Calibrators",
                ],
            },
            {
                "supplier_id": "SUP-PKG-003",
                "description": "Manufacturer of medical-grade plastic packaging components",
                "address": "500 Industrial Pkwy",
                "city": "Chicago",
                "state": "Illinois",
                "postal_code": "60616",
                "website": "https://www.plastitech.com",
                "iso_certified": True,
                "iso_certificate_number": "ISO-9001-2024-003",
                "iso_expiry_date": timezone.now() + timedelta(days=400),
                "risk_justification": "Medium risk - alternative suppliers available but qualification required",
                "qualified_date": timezone.now() - timedelta(days=270),
                "next_evaluation_date": timezone.now() + timedelta(days=95),
                "products_services": [
                    "Plastic vials",
                    "Test tube assemblies",
                    "Reagent bottles",
                    "Packaging inserts",
                ],
            },
            {
                "supplier_id": "SUP-CAL-004",
                "description": "NIST-traceable calibration and metrology services",
                "address": "300 Precision Blvd",
                "city": "Boston",
                "state": "Massachusetts",
                "postal_code": "02101",
                "website": "https://www.precisioncal.com",
                "iso_certified": True,
                "iso_certificate_number": "ISO-17025-2024-004",
                "iso_expiry_date": timezone.now() + timedelta(days=350),
                "risk_justification": "Low risk - multiple alternative providers available, non-critical path",
                "qualified_date": timezone.now() - timedelta(days=200),
                "next_evaluation_date": timezone.now() + timedelta(days=165),
                "products_services": [
                    "Equipment calibration",
                    "Metrology services",
                    "Calibration certificates",
                ],
            },
            {
                "supplier_id": "SUP-DIST-005",
                "description": "Healthcare product distribution and logistics across Americas",
                "address": "8000 Logistics Way",
                "city": "Dallas",
                "state": "Texas",
                "postal_code": "75201",
                "website": "https://www.globaldist.com",
                "iso_certified": False,
                "risk_justification": "Medium risk - new supplier, evaluation in progress, critical for US distribution",
                "next_evaluation_date": timezone.now() + timedelta(days=60),
                "products_services": [
                    "Cold chain logistics",
                    "Warehousing",
                    "Last-mile delivery",
                ],
            },
        ]

        for sup_data in suppliers_data:
            try:
                supplier = Supplier.objects.get(supplier_id=sup_data["supplier_id"])
                # Update fields
                for key, value in sup_data.items():
                    if key != "supplier_id":
                        setattr(supplier, key, value)
                supplier.save()
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Updated {sup_data['supplier_id']}")
                )
            except Supplier.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Supplier {sup_data['supplier_id']} not found, skipping"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error updating {sup_data['supplier_id']}: {str(e)}"
                    )
                )
