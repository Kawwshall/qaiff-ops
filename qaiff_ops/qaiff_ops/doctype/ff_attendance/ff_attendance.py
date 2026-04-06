import frappe
from frappe.model.document import Document


class FFAttendance(Document):
    def before_save(self):
        if not self.marked_by:
            self.marked_by = frappe.get_value("User", frappe.session.user, "full_name") or frappe.session.user

        if not self.daily_rate and self.operator and self.project:
            rate = frappe.db.get_value(
                "FF Roster Entry",
                {"parent": self.project, "operator": self.operator},
                "daily_rate",
            )
            if rate:
                self.daily_rate = rate
