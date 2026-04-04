import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class DailyAttendance(Document):
    @frappe.whitelist()
    def approve_attendance(self):
        self.approved_by = frappe.session.user
        self.approved_on = now_datetime()
        self.save()
        frappe.msgprint(f"Attendance approved for {self.full_name} on {self.attendance_date}")
