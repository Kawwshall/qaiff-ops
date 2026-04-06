import frappe
from frappe.model.document import Document


class FFProject(Document):
    def validate(self):
        self.sync_chiefs_to_roster()

    def on_update(self):
        self.update_operator_assignments()

    def on_trash(self):
        self.free_all_operators()

    def sync_chiefs_to_roster(self):
        """When chief_1 or chief_2 is set, auto-add them to roster as Chief."""
        roster_operators = [r.operator for r in self.roster]

        for chief_field in ["chief_1", "chief_2"]:
            chief = self.get(chief_field)
            if chief and chief not in roster_operators:
                self.append("roster", {
                    "operator": chief,
                    "role_type": "Chief",
                    "daily_rate": self.rate_chief or 4000,
                })
                roster_operators.append(chief)

    def update_operator_assignments(self):
        """Update each rostered operator's assignment fields."""
        if self.status in ("Active", "Planning"):
            status = "Deployed" if self.status == "Active" else "Available"
            for row in self.roster:
                frappe.db.set_value("Operator", row.operator, {
                    "current_project": self.name,
                    "current_factory": self.factory_name,
                    "assignment_status": status,
                }, update_modified=False)
        elif self.status in ("Completed", "Cancelled"):
            self.free_all_operators()

    def free_all_operators(self):
        """Reset all rostered operators back to Available."""
        for row in self.roster:
            if frappe.db.exists("Operator", row.operator):
                op_project = frappe.db.get_value("Operator", row.operator, "current_project")
                if op_project == self.name:
                    frappe.db.set_value("Operator", row.operator, {
                        "current_project": "",
                        "current_factory": "",
                        "assignment_status": "Available",
                    }, update_modified=False)
