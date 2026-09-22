# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from frappe.model.document import Document


class StockIn(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from pharmastock.pharmastock.doctype.stock_in_item.stock_in_item import StockInItem

        amended_from: DF.Link | None
        items: DF.Table[StockInItem]
        purchase_invoice_no: DF.Data | None
        status: DF.Literal["Draft", "Submitted", "Cancelled"]
        stock_in_date: DF.Date
        supplier: DF.Data | None
        total_amount: DF.Currency
    # end: auto-generated types

    def validate(self):
        self.validate_batches()
        self.calculate_total()
        self.validate_expiry_dates()

    def validate_batches(self):
        for item in self.items:
            if item.medicine and item.batch_number:
                batch = frappe.get_doc("Medicine Batch", item.batch_number)
                if batch.medicine != item.medicine:
                    frappe.throw(
                        _("Batch {0} does not belong to medicine {1}").format(
                            item.batch_number, item.medicine
                        )
                    )

                if batch.expiry_date and batch.expiry_date < datetime.now().date():
                    frappe.throw(
                        _("Cannot receive expired batch {0} (Expiry: {1})").format(
                            item.batch_number, batch.expiry_date
                        )
                    )

    def validate_expiry_dates(self):
        for item in self.items:
            batch = frappe.get_doc("Medicine Batch", item.batch_number)
            if batch.is_expired:
                frappe.throw(
                    _("Batch {0} is expired and cannot be received").format(
                        item.batch_number
                    )
                )

    def calculate_total(self):
        total = 0
        for item in self.items:
            item.amount = item.quantity * item.purchase_price
            total += item.amount
        self.total_amount = total

    def on_submit(self):
        self.update_stock_in()
        self.update_medicine_stock()

    def update_stock_in(self):
        for item in self.items:
            batch = frappe.get_doc("Medicine Batch", item.batch_number)
            batch.quantity = batch.quantity + item.quantity
            batch.remaining_quantity = batch.remaining_quantity + item.quantity
            batch.purchase_price = item.purchase_price
            batch.selling_price = item.selling_price
            batch.save()

            self.create_stock_movement(item, "Stock In")

    def update_medicine_stock(self):
        for item in self.items:
            medicine = frappe.get_doc("Medicine", item.medicine)
            medicine.current_stock = medicine.current_stock + item.quantity
            medicine.save()

    def create_stock_movement(self, item, movement_type):
        movement = frappe.get_doc(
            {
                "doctype": "Stock Movement",
                "movement_type": movement_type,
                "reference_document": self.name,
                "medicine": item.medicine,
                "batch_number": item.batch_number,
                "quantity": item.quantity,
                "transaction_date": self.stock_in_date,
                "status": "Submitted",
            }
        )
        movement.insert(ignore_permissions=True)

    def on_cancel(self):
        self.reverse_stock_in()

    def reverse_stock_in(self):
        for item in self.items:
            batch = frappe.get_doc("Medicine Batch", item.batch_number)
            if batch.quantity >= item.quantity:
                batch.quantity = batch.quantity - item.quantity
                batch.remaining_quantity = batch.remaining_quantity - item.quantity
                batch.save()
            else:
                frappe.throw(
                    _("Cannot cancel: Not enough stock in batch {0}").format(
                        item.batch_number
                    )
                )

            medicine = frappe.get_doc("Medicine", item.medicine)
            if medicine.current_stock >= item.quantity:
                medicine.current_stock = medicine.current_stock - item.quantity
                medicine.save()
            else:
                frappe.throw(
                    _("Cannot cancel: Not enough stock for medicine {0}").format(
                        item.medicine
                    )
                )


@frappe.whitelist()
def get_batch_query(doctype, txt, searchfield, start, page_len, filters):
    """Get valid batches for medicine."""
    medicine = filters.get("medicine") if filters else None
    if not medicine:
        return []

    query = """
        SELECT name, batch_number, expiry_date
        FROM `tabMedicine Batch`
        WHERE medicine = %s
        AND is_expired = 0
        AND docstatus < 2
        AND (batch_number LIKE %s OR name LIKE %s)
        ORDER BY expiry_date ASC
        LIMIT %s OFFSET %s
    """
    txt = f"%{txt}%"
    return frappe.db.sql(query, (medicine, txt, txt, page_len, start), as_list=True)

	

	
