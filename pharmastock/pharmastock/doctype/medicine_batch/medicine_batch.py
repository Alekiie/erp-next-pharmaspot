import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, getdate
import re
from frappe.model.naming import getseries


class MedicineBatch(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        batch_abbreviation: DF.Data | None
        batch_number: DF.Data | None
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

    # Automate Batch Number Generation Instead of manual typing.Itatumia letter za kwanza za kila jina kwa Batch alafu inajoin na nummber nne.

    def autoname(self):
        
        if not self.medicine:
            frappe.throw(_("Please select a medicine first."))

        # Get the readable medicine name using its Title Field
        medicine_meta = frappe.get_meta("Medicine")
        title_field = medicine_meta.title_field

        medicine_name = None

        if title_field:
            medicine_name = frappe.db.get_value("Medicine", self.medicine, title_field)

        # Fall back to the document ID if no title is configured
        medicine_name = (medicine_name or self.medicine).strip()

        # Extract initials from the medicine name
        words = re.findall(r"[A-Za-z0-9]+", medicine_name)

        if not words:
            frappe.throw(_("Unable to generate a batch abbreviation."))

        abbreviation = "BAT-"+"".join(word[:3] for word in words).upper()

        # Store the abbreviation in your actual DocType field
        self.batch_abbreviation = abbreviation

        # Generate the next four-digit sequence for this medicine prefix
        prefix = f"{abbreviation}-"
        number = getseries(prefix, 4)

        # Use the same value for the document ID and Batch Number
        self.name = f"{prefix}{number}"
        self.batch_number = self.name


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
