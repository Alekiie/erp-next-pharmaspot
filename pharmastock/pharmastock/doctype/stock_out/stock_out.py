# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime

from frappe import _
from frappe.model.document import Document


class StockOut(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from pharmastock.pharmastock.doctype.stock_out_item.stock_out_item import StockOutItem

        amended_from: DF.Link | None
        customer: DF.Data
        items: DF.Table[StockOutItem]
        sales_invoice_no: DF.Data | None
        status: DF.Literal["Draft", "Submitted", "Cancelled"]
        stock_out_date: DF.Date
        total_amount: DF.Currency
        transaction_type: DF.Literal["Sale", "Return", "Damage", "Expired", "Other"]
    # end: auto-generated types

    def validate(self):
        self.validate_batches()
        self.calculate_total()
        self.validate_stock_availability()

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
                        _("Cannot sell expired batch {0} (Expiry: {1})").format(
                            item.batch_number, batch.expiry_date
                        )
                    )

    def validate_stock_availability(self):
        for item in self.items:
            batch = frappe.get_doc("Medicine Batch", item.batch_number)
            if batch.remaining_quantity < item.quantity:
                frappe.throw(
                    _(
                        "Insufficient stock in batch {0}. Available: {1}, Required: {2}"
                    ).format(item.batch_number, batch.remaining_quantity, item.quantity)
                )

            medicine = frappe.get_doc("Medicine", item.medicine)
            if medicine.current_stock < item.quantity:
                frappe.throw(
                    _(
                        "Insufficient stock for medicine {0}. Available: {1}, Required: {2}"
                    ).format(item.medicine, medicine.current_stock, item.quantity)
                )

    def calculate_total(self):
        total = 0
        for item in self.items:
            item.amount = item.quantity * item.selling_price
            total += item.amount
        self.total_amount = total

    def on_submit(self):
        self.update_stock_out()
        self.update_medicine_stock()

    def update_stock_out(self):
        for item in self.items:
            batch = frappe.get_doc("Medicine Batch", item.batch_number)
            batch.remaining_quantity = batch.remaining_quantity - item.quantity
            batch.save()

            self.create_stock_movement(item, self.transaction_type)

    def update_medicine_stock(self):
        for item in self.items:
            medicine = frappe.get_doc("Medicine", item.medicine)
            medicine.current_stock = medicine.current_stock - item.quantity
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
                "transaction_date": self.stock_out_date,
                "status": "Submitted",
            }
        )
        movement.insert(ignore_permissions=True)

    def on_cancel(self):
        self.reverse_stock_out()

    def reverse_stock_out(self):
        for item in self.items:
            batch = frappe.get_doc("Medicine Batch", item.batch_number)
            batch.remaining_quantity = batch.remaining_quantity + item.quantity
            batch.save()

            medicine = frappe.get_doc("Medicine", item.medicine)
            medicine.current_stock = medicine.current_stock + item.quantity
            medicine.save()


DOCTYPE_NAME = "Stock Out"
