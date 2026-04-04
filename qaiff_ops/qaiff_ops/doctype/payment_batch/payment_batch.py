import frappe
from frappe.model.document import Document

class PaymentBatch(Document):
    def before_save(self):
        self.calculate_totals()

    def calculate_totals(self):
        total = 0
        count = 0
        for record in self.payment_records:
            record.total_amount = (record.days_present or 0) * (record.daily_rate or 0)
            total += record.total_amount
            count += 1
        self.total_operators = count
        self.total_amount = total

    @frappe.whitelist()
    def generate_from_project(self):
        if not self.project:
            frappe.throw("Please set a project first.")
        attendance = frappe.db.sql("""
            SELECT operator, full_name,
                   SUM(CASE WHEN status='Present' THEN 1 WHEN status='Half Day' THEN 0.5 ELSE 0 END) as days_present
            FROM `tabDaily Attendance`
            WHERE project = %s AND approved_by IS NOT NULL
            GROUP BY operator, full_name
        """, self.project, as_dict=True)
        self.payment_records = []
        for row in attendance:
            op = frappe.get_doc("Operator Profile", row.operator)
            roster = frappe.db.get_value("Project Roster Entry",
                {"parent": self.project, "operator": row.operator},
                ["role", "daily_rate"], as_dict=True)
            self.append("payment_records", {
                "operator": row.operator,
                "full_name": row.full_name,
                "role": roster.role if roster else "Operator",
                "days_present": row.days_present,
                "daily_rate": roster.daily_rate if roster else 1200,
                "total_amount": row.days_present * (roster.daily_rate if roster else 1200),
                "upi_id": op.upi_id,
                "phone": op.phone,
                "wa_link": f"wa.me/+91{op.phone}" if op.phone else ""
            })
        self.calculate_totals()
        frappe.msgprint(f"Generated {len(self.payment_records)} payment records.")
