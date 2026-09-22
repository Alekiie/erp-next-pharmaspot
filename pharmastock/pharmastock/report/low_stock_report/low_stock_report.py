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
    chart = get_chart(data)

    return columns, data, None, chart


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
            "fieldname": "category",
            "label": _("Category"),
            "fieldtype": "Link",
            "options": "Medicine Category",
            "width": 150,
        },
        {
            "fieldname": "generic_name",
            "label": _("Generic Name"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "current_stock",
            "label": _("Current Stock"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "reorder_level",
            "label": _("Reorder Level"),
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "to_order",
            "label": _("Recommended Order"),
            "fieldtype": "Int",
            "width": 120,
        },
    ]


def get_data(filters):
    """Return data for the report.

    The report data is a list of rows, with each row being a list of cell values.
    """
    conditions = "1=1"

    if filters.get("category"):
        conditions += f" AND category = '{filters.get('category')}'"

    if filters.get("status") and filters.get("status") != "All":
        if filters.get("status") == "Low":
            conditions += " AND current_stock <= reorder_level AND current_stock > 0"
        elif filters.get("status") == "Out of Stock":
            conditions += " AND current_stock = 0"
        elif filters.get("status") == "Sufficient":
            conditions += " AND current_stock > reorder_level"

    data = frappe.db.sql(
        f"""
        SELECT 
            medicine_code,
            medicine_name,
            category,
            generic_name,
            current_stock,
            reorder_level,
            CASE 
                WHEN current_stock = 0 THEN 'Out of Stock'
                WHEN current_stock <= reorder_level THEN 'Low'
                ELSE 'Sufficient'
            END as status,
            CASE 
                WHEN current_stock <= reorder_level THEN reorder_level - current_stock
                ELSE 0
            END as to_order
        FROM `tabMedicine`
        WHERE is_active = 1
        AND {conditions}
        ORDER BY current_stock ASC
    """,
        as_dict=True,
    )

    return data


def get_chart(data):
    if not data:
        return None

    # Count status distribution
    status_counts = {"Out of Stock": 0, "Low": 0, "Sufficient": 0}

    for row in data:
        if row["status"] in status_counts:
            status_counts[row["status"]] += 1

    return {
        "data": {
            "labels": ["Out of Stock", "Low", "Sufficient"],
            "datasets": [
                {
                    "name": "Stock Status",
                    "values": [
                        status_counts["Out of Stock"],
                        status_counts["Low"],
                        status_counts["Sufficient"],
                    ],
                }
            ],
        },
        "type": "pie",
        "colors": ["#dc3545", "#ffc107", "#28a745"],
    }
