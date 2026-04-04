import frappe
from frappe.model.document import Document

class ProjectRosterEntry(Document):
    def before_save(self):
        if not self.daily_rate or self.daily_rate == 0:
            rates = {"Operator": 1200, "Captain": 1500, "Chief": 4000}
            self.daily_rate = rates.get(self.role, 1200)
