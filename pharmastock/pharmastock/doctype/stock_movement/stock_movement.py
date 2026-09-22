# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StockMovement(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		batch_number: DF.Link
		medicine: DF.Link
		movement_type: DF.Literal["Stock In", "Sale", "Return", "Damage", "Expired", "Damaged"]
		quantity: DF.Float
		reference_document: DF.Data | None
		status: DF.Literal["Draft", "Submitted", "Cancelled"]
		transaction_date: DF.Date
	# end: auto-generated types

	_DOCTYPE_NAME = "Stock Movement"
