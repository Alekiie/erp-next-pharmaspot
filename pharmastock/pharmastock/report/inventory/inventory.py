# Copyright (c) 2026, Alexander Maina and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, cint
from datetime import datetime


def execute(filters: dict | None = None):
    """Return columns and data for the report.

    This is the main entry point for the report. It accepts the filters as a
    dictionary and should return columns and data. It is called by the framework
    every time the report is refreshed or a filter is updated.
    """
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)

    return columns, data, None, None, summary


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
            "fieldname": "expiry_date",
            "label": _("Expiry Date"),
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "batch_quantity",
            "label": _("Batch Stock"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "total_stock",
            "label": _("Total Stock"),
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "fieldname": "purchase_price",
            "label": _("Purchase Price"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "selling_price",
            "label": _("Selling Price"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "stock_value",
            "label": _("Stock Value"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "expiry_status",
            "label": _("Expiry Status"),
            "fieldtype": "Data",
            "width": 120,
        },
    ]


def get_data(filters):
    """Return data for the report.

    The report data is a list of rows, with each row being a list of cell values.
    """
    medicines = frappe.get_list(
        "Medicine",
        fields=[
            "name",
            "medicine_code",
            "medicine_name",
            "category",
            "current_stock",
            "purchase_price",
            "selling_price",
        ],
        filters={"is_active": 1},
    )
    data = []
    for med in medicines:
        batches = frappe.get_list(
            "Medicine Batch",
            filters={"medicine": med.name},
            fields=[
                "name",
                "batch_number",
                "expiry_date",
                "remaining_quantity",
                "quantity",
            ],
        )
        if batches:
            for batch in batches:
                row = {
                    "medicine_code": med.medicine_code,
                    "medicine_name": med.medicine_name,
                    "category": med.category,
                    "batch_number": batch.batch_number,
                    "expiry_date": batch.expiry_date,
                    "batch_quantity": batch.remaining_quantity or 0,
                    "total_stock": med.current_stock,
                    "purchase_price": med.purchase_price,
                    "selling_price": med.selling_price,
                    "stock_value": (batch.remaining_quantity or 0) * med.purchase_price,
                    "expiry_status": get_expiry_status(batch.expiry_date),
                }
                data.append(row)
        else:
            row = {
                "medicine_code": med.medicine_code,
                "medicine_name": med.medicine_name,
                "category": med.category,
                "batch_number": "N/A",
                "expiry_date": None,
                "batch_quantity": 0,
                "total_stock": med.current_stock,
                "purchase_price": med.purchase_price,
                "selling_price": med.selling_price,
                "stock_value": med.current_stock * med.purchase_price,
                "expiry_status": "No Batches",
            }
            data.append(row)
    return data


def get_expiry_status(expiry_date):
    if not expiry_date:
        return "Not Set"

    today = datetime.now().date()
    days_until_expiry = (expiry_date - today).days

    if days_until_expiry < 0:
        return "Expired"
    elif days_until_expiry <= 30:
        return f"Expiring in {days_until_expiry} days"
    elif days_until_expiry <= 90:
        return f"Expires in {days_until_expiry} days"
    else:
        return f"Valid (in {days_until_expiry} days)"


def get_summary(data):
    if not data:
        return []

    total_items = len(data)
    total_stock_value = sum(row.get("stock_value", 0) for row in data)
    unique_medicines = len(set(row.get("medicine_code") for row in data))

    expired_items = len([row for row in data if row.get("expiry_status") == "Expired"])
    expiring_soon = len(
        [
            row
            for row in data
            if row.get("expiry_status") and "Expiring in" in row.get("expiry_status")
        ]
    )

    return [
        {"label": _("Total Medicines"), "value": unique_medicines, "indicator": "Blue"},
        {"label": _("Total Batches"), "value": total_items, "indicator": "Blue"},
        {
            "label": _("Total Stock Value"),
            "value": f"{total_stock_value:,.2f}",
            "indicator": "Green",
        },
        {
            "label": _("Expired Batches"),
            "value": expired_items,
            "indicator": "Red" if expired_items > 0 else "Green",
        },
        {
            "label": _("Expiring Soon (30 days)"),
            "value": expiring_soon,
            "indicator": "Orange" if expiring_soon > 0 else "Green",
        },
    ]
