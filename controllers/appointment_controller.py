from __future__ import annotations

from models.data_manager import DataManager

def _ok(data=None, message: str = "") -> dict:
    return {"ok": True, "data": data, "message": message}

def _fail(message: str, error: str = "general") -> dict:
    return {"ok": False, "error": error, "message": message}

class AppointmentController:

    def __init__(self, data_manager: DataManager) -> None:
        self._dm = data_manager

    def get_all(self) -> dict:
        return _ok(data=self._dm.get_all_appointments())

    def get_by_id(self, appt_id: str) -> dict:
        appt_id = appt_id.strip().upper()
        if not appt_id:
            return _fail("Appointment ID cannot be empty.")
        record = self._dm.get_appointment_by_id(appt_id)
        if record is None:
            return _fail(f"No appointment found with ID: {appt_id}")
        return _ok(data=record)

    def search(self, query: str) -> dict:
        return _ok(data=self._dm.search_appointments(query))

    def get_by_date(self, date_str: str) -> dict:
        return _ok(data=self._dm.get_appointments_by_date(date_str))

    def add(self, form_data: dict) -> dict:
        name    = form_data.get("patient_name", "").strip()
        contact = form_data.get("contact", "").strip()

        if not name:
            return _fail("Patient Name is required.", error="validation")
        if not contact:
            return _fail("Contact Information is required.", error="validation")
        if not (contact.isdigit() and len(contact) == 11):
            return _fail("Contact Information must be exactly 11 digits.", error="validation")

        physician = form_data["physician"]
        date_str  = form_data["date"]
        time_str  = form_data["time"]

        conflict = self._dm.find_conflict(physician, date_str, time_str)
        if conflict:
            return _fail(
                f"{physician} already has an appointment on {date_str} at "
                f"{time_str} (ID: {conflict['id']}).",
                error="double_booking",
            )

        new_id = self._dm.insert_appointment({
            "patient_name": name,
            "contact":      contact,
            "physician":    physician,
            "date":         date_str,
            "time":         time_str,
            "status":       form_data.get("status", "Scheduled"),
        })
        return _ok(data=new_id, message=f"Appointment saved. ID: {new_id}")

    def update(self, appt_id: str, form_data: dict) -> dict:
        name    = form_data.get("patient_name", "").strip()
        contact = form_data.get("contact", "").strip()

        if not name:
            return _fail("Patient Name is required.", error="validation")
        if not contact:
            return _fail("Contact Information is required.", error="validation")
        if not (contact.isdigit() and len(contact) == 11):
            return _fail("Contact Information must be exactly 11 digits.", error="validation")

        physician = form_data["physician"]
        date_str  = form_data["date"]
        time_str  = form_data["time"]

        conflict = self._dm.find_conflict(
            physician, date_str, time_str, exclude_id=appt_id
        )
        if conflict:
            return _fail(
                f"{physician} already has an appointment on {date_str} at "
                f"{time_str} (ID: {conflict['id']}).",
                error="double_booking",
            )

        success = self._dm.update_appointment(appt_id, {
            "patient_name": name,
            "contact":      contact,
            "physician":    physician,
            "date":         date_str,
            "time":         time_str,
            "status":       form_data.get("status", "Scheduled"),
        })
        if not success:
            return _fail(f"Appointment ID {appt_id} not found.", error="not_found")
        return _ok(message=f"Appointment {appt_id} updated successfully.")

    def cancel(self, appt_id: str) -> dict:
        if not self._dm.cancel_appointment(appt_id):
            return _fail(f"Appointment ID {appt_id} not found.", error="not_found")
        return _ok(message=f"Appointment {appt_id} marked as Cancelled.")

    def delete(self, appt_id: str) -> dict:
        if not self._dm.delete_appointment(appt_id):
            return _fail(f"Appointment ID {appt_id} not found.", error="not_found")
        return _ok(message=f"Appointment {appt_id} permanently deleted.")

    def get_arrived_appointments(self) -> dict:
        return _ok(data=self._dm.get_due_scheduled_appointments())

    def record_outcome(self, appt_id: str, successful: bool) -> dict:
        new_status = "Completed" if successful else "No Show"
        if not self._dm.update_appointment_status(appt_id, new_status):
            return _fail(f"Appointment ID {appt_id} not found.", error="not_found")
        outcome_label = "Successful (Completed)" if successful else "Not Successful (No Show)"
        return _ok(message=f"Appointment {appt_id} marked as {outcome_label}.")

    def get_dashboard_analytics(self) -> dict:
        from datetime import date
        today_str = date.today().isoformat()
        all_appts = self._dm.get_all_appointments()
        today_appts = [a for a in all_appts if str(a.get("date", "")) == today_str]

        status_counts = {}
        physician_counts = {}

        for a in all_appts:
            st = a.get("status", "Scheduled")
            status_counts[st] = status_counts.get(st, 0) + 1

            doc = a.get("physician", "Unassigned")
            physician_counts[doc] = physician_counts.get(doc, 0) + 1

        total = len(all_appts)
        completed = sum(v for k, v in status_counts.items() if k in ("Completed", "Successful", "Completed (Successful)"))
        scheduled = status_counts.get("Scheduled", 0)
        cancelled = status_counts.get("Cancelled", 0)
        noshow = sum(v for k, v in status_counts.items() if k in ("No Show", "Not Successful", "No Show (Not Successful)"))

        return _ok(data={
            "total": total,
            "today_total": len(today_appts),
            "today_appts": today_appts,
            "completed": completed,
            "scheduled": scheduled,
            "cancelled": cancelled,
            "noshow": noshow,
            "status_counts": status_counts,
            "physician_counts": physician_counts,
        })
