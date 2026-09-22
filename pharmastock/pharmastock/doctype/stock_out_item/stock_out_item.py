# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StockOutItem(Document):
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
		quantity: DF.Float
		selling_price: DF.Currency
	# end: auto-generated types

	_DOCTYPE_NAME = "Stock Out Item"
