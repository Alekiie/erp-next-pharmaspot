# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta


def execute(filters: dict | None = None):
    """Return columns and data for the report.

    This is the main entry point for the report. It accepts the filters as a
    dictionary and should return columns and data. It is called by the framework
    every time the report is refreshed or a filter is updated.
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, chart, None


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
            "fieldname": "batch_number",
            "label": _("Batch Number"),
            "fieldtype": "Link",
            "options": "Medicine Batch",
            "width": 150,
        },
        {
            "fieldname": "manufacturing_date",
            "label": _("Manufacturing Date"),
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "expiry_date",
            "label": _("Expiry Date"),
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "quantity",
            "label": _("Remaining Quantity"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "days_remaining",
            "label": _("Days Remaining"),
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 150,
        },
    ]


def get_data(filters) -> list[list]:
    """Return data for the report.

    The report data is a list of rows, with each row being a list of cell values.
    """
    conditions = "1=1"

    # Date range filters
    if filters.get("from_date"):
        conditions += f" AND expiry_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND expiry_date <= '{filters.get('to_date')}'"

    # Status filters
    if filters.get("status"):
        today = datetime.now().date()
        if filters.get("status") == "Expired":
            conditions += f" AND expiry_date < '{today}'"
        elif filters.get("status") == "Expiring Soon":
            soon_date = today + timedelta(days=30)
            conditions += f" AND expiry_date BETWEEN '{today}' AND '{soon_date}'"
        elif filters.get("status") == "Valid":
            conditions += f" AND expiry_date > '{today}'"

    if filters.get("medicine"):
        conditions += f" AND medicine = '{filters.get('medicine')}'"
    if filters.get("category"):
        conditions += f" AND medicine IN (SELECT name FROM `tabMedicine` WHERE category = '{filters.get('category')}')"

    data = frappe.db.sql(
        f"""
        SELECT 
            m.medicine_code,
            m.medicine_name,
            m.category,
            b.batch_number,
            b.manufacturing_date,
            b.expiry_date,
            b.remaining_quantity as quantity,
            DATEDIFF(b.expiry_date, CURDATE()) as days_remaining,
            CASE 
                WHEN b.expiry_date < CURDATE() THEN 'Expired'
                WHEN DATEDIFF(b.expiry_date, CURDATE()) <= 30 THEN 'Expiring Soon'
                WHEN DATEDIFF(b.expiry_date, CURDATE()) <= 90 THEN 'Expires in 30-90 days'
                ELSE 'Valid'
            END as status
        FROM `tabMedicine Batch` b
        LEFT JOIN `tabMedicine` m ON b.medicine = m.name
        WHERE b.quantity > 0
        AND {conditions}
        ORDER BY b.expiry_date ASC
    """,
        as_dict=True,
    )

    # Add color coding for status
    for row in data:
        if row["status"] == "Expired":
            row["indicator"] = "Red"
        elif row["status"] == "Expiring Soon":
            row["indicator"] = "Orange"
        else:
            row["indicator"] = "Green"


def get_chart(data):
    if not data:
        return None

    # Count by status
    status_counts = {}
    for row in data:
        status = row["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    labels = list(status_counts.keys())
    values = list(status_counts.values())

    colors = []
    for label in labels:
        if "Expired" in label:
            colors.append("#dc3545")
        elif "Expiring Soon" in label:
            colors.append("#ffc107")
        else:
            colors.append("#28a745")

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Batch Status", "values": values}],
        },
        "type": "pie",
        "colors": colors,
    }
