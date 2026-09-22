import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, getdate


class MedicineBatch(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        batch_number: DF.Data
        expiry_date: DF.Date
        is_expired: DF.Check
        manufacturing_date: DF.Date
        medicine: DF.Link
        purchase_price: DF.Currency
        quantity: DF.Float
        remaining_quantity: DF.Float
        selling_price: DF.Currency
    # end: auto-generated types

    _DOCTYPE_NAME = "Medicine Batch"

    def validate(self):
        self.validate_expiry()
        self.validate_medicine_consistency()
        self.update_expiry_status()

    def validate_expiry(self):
        if self.expiry_date:
            if getdate(self.expiry_date) < getdate(today()):
                self.is_expired = 1

                frappe.msgprint(
                    _(
                        f"Warning: This batch {self.batch_number} "
                        f"of medicine {self.medicine} "
                        f"expired on {self.expiry_date}"
                    ),
                    alert=True,
                )

    def validate_medicine_consistency(self):
        if self.medicine:
            batch_exists = frappe.db.exists(
                "Medicine Batch",
                {
                    "batch_number": self.batch_number,
                    "medicine": self.medicine,
                },
            )

            if batch_exists and batch_exists != self.name:
                frappe.throw(
                    _("Batch {0} already exists for this medicine").format(
                        self.batch_number
                    )
                )

    def update_expiry_status(self):
        if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
            self.is_expired = 1
        else:
            self.is_expired = 0


@frappe.whitelist()
def validate_expiry(batch_number: str):
    batch = frappe.get_doc("Medicine Batch", batch_number)

    if not batch.expiry_date:
        return {
            "status": "error",
            "message": "This batch does not have an expiry date.",
        }

    if getdate(batch.expiry_date) < getdate(today()):
        return {
            "status": "expired",
            "message": (
                f"Batch {batch.batch_number} of medicine "
                f"{batch.medicine} has expired."
            ),
        }

    return {
        "status": "valid",
        "message": (
            f"Batch {batch.batch_number} of medicine " f"{batch.medicine} is valid."
        ),
    }
