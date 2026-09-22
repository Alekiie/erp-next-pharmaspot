# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StockInItem(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amount: DF.Currency
        batch_number: DF.Link
        medicine: DF.Link
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        purchase_price: DF.Currency
        quantity: DF.Float
        selling_price: DF.Currency

    # end: auto-generated types
    # Calculate the amount for each item based on quantity and selling price
    def validate(self):
        self.calculate_amount()

    def calculate_amount(self):
        if self.quantity is not None and self.purchase_price is not None:
            self.amount = self.quantity * self.purchase_price
        else:
            self.amount = 0.0

    _DOCTYPE_NAME = "Stock In Item"
