# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
    """Return columns and data for the report.

    This is the main entry point for the report. It accepts the filters as a
    dictionary and should return columns and data. It is called by the framework
    every time the report is refreshed or a filter is updated.
    """
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def execute_snapshot_report(filters: dict | None = None):
    """Return columns and data for the report.

    This is the main entry point for snapshot report. When 'Synced
    Report' is enabled in report, framework will call this method
    every time the report is refreshed or a filter is updated. It
    accepts the same filters as normal execute. But a utility method -
    get_latest_sync, is also imported.

    """
    from frappe.database.duckdb.database import get_latest_sync

    columns = get_columns()
    data = get_data()

    return columns, data


def get_columns() -> list[dict]:
    """Return columns for the report.

    One field definition per column, just like a DocType field definition.
    """
    return [
        {
            "fieldname": "movement_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "movement_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "medicine_code",
            "label": _("Medicine Code"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "medicine_name",
            "label": _("Medicine Name"),
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "fieldname": "batch_number",
            "label": _("Batch"),
            "fieldtype": "Link",
            "options": "Medicine Batch",
            "width": 150,
        },
        {
            "fieldname": "quantity",
            "label": _("Quantity"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "reference",
            "label": _("Reference"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "stock_after",
            "label": _("Stock After"),
            "fieldtype": "Float",
            "width": 120,
        },
    ]


def get_data(filters) -> list[list]:
    """Return data for the report.

    The report data is a list of rows, with each row being a list of cell values.
    """
    conditions = "1=1"

    if filters.get("from_date"):
        conditions += f" AND sm.transaction_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND sm.transaction_date <= '{filters.get('to_date')}'"
    if filters.get("medicine"):
        conditions += f" AND sm.medicine = '{filters.get('medicine')}'"
    if filters.get("movement_type"):
        conditions += f" AND sm.movement_type = '{filters.get('movement_type')}'"

    data = frappe.db.sql(
        f"""
        SELECT 
            sm.transaction_date as movement_date,
            sm.movement_type,
            m.medicine_code,
            m.medicine_name,
            sm.batch_number,
            sm.quantity,
            sm.reference_document as reference,
            CASE 
                WHEN sm.movement_type IN ('Stock In', 'Return') 
                THEN (SELECT current_stock FROM `tabMedicine` WHERE name = sm.medicine)
                ELSE (SELECT current_stock FROM `tabMedicine` WHERE name = sm.medicine) + sm.quantity
            END as stock_after
        FROM `tabStock Movement` sm
        LEFT JOIN `tabMedicine` m ON sm.medicine = m.name
        WHERE {conditions}
        AND sm.status = 'Completed'
        ORDER BY sm.transaction_date DESC, sm.creation DESC
        LIMIT 1000
    """,
        as_dict=True,
    )

    # Add color coding for movement types
    for row in data:
        if row["movement_type"] in ["Stock In", "Return"]:
            row["indicator"] = "Green"
        else:
            row["indicator"] = "Red"

    return data
