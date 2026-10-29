# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Supplier(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		email: DF.Data | None
		phone_number: DF.Phone
		supplier_name: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "Supplier"
