# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Medicine(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        category: DF.Link | None
        current_stock: DF.Float
        description: DF.SmallText | None
        generic_name: DF.Data
        is_active: DF.Check
        manufacturer: DF.Data | None
        medicine_code: DF.Data
        medicine_name: DF.Data
        purchase_price: DF.Currency
        reorder_level: DF.Int
        selling_price: DF.Currency
        unit: DF.Literal["Tablet", "Capsule", "Syrup", "Injection", "Cream", "Drops", "Inhaler", "Suppossitory", "Other"]
    # end: auto-generated types

    def validate(self):
        self.check_low_stock()

    def check_low_stock(self):
        if self.current_stock and self.reorder_level:
            if self.current_stock <= self.reorder_level:
                frappe.msgprint(
                    _(
                        "Warning: Low stock for {0}. Current: {1}, Reorder level: {2}"
                    ).format(
                        self.medicine_name, self.current_stock, self.reorder_level
                    ),
                    alert=True,
                )


@frappe.whitelist()
def get_low_stock_items():
    """Get all items with low stock"""
    return frappe.db.sql(
        """
        SELECT 
            medicine_name,
            category,
            current_stock,
            reorder_level,
            CASE 
                WHEN current_stock <= reorder_level THEN 'Low'
                ELSE 'Sufficient'
            END as status
        FROM `tabMedicine`
        WHERE current_stock <= reorder_level
        AND is_active = 1
        ORDER BY current_stock ASC
    """,
        as_dict=True,
    )
