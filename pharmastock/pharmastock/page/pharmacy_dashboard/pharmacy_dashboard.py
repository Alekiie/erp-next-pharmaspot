import frappe
from frappe import _
from datetime import datetime
from typing import Dict, Any, Optional, List


@frappe.whitelist()
def get_dashboard_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch all data for the dashboard with optional filters."""
    if filters is None:
        filters = {}

    category = filters.get("category")
    status = filters.get("status")

    data = {
        "total_medicines": get_total_medicines(),
        "in_stock": get_in_stock_count(),
        "low_stock": get_low_stock_count(category, status),
        "total_stock_value": get_total_stock_value(category),
        "low_stock_items": get_low_stock_items(category, status),
        "category_data": get_category_stock_data(),
        "expiry_data": get_expiry_status_data(),
    }
    return data


@frappe.whitelist()
def get_categories() -> List[Dict[str, str]]:
    """Return list of all Medicine Categories for filter dropdown."""
    return frappe.get_all("Medicine Category", fields=["name"])


# ------------------------------------------------------------------
# Helper functions (no @frappe.whitelist needed)
# ------------------------------------------------------------------


def get_total_medicines() -> int:
    return frappe.db.count("Medicine", {"is_active": 1})


def get_in_stock_count() -> int:
    return frappe.db.count("Medicine", {"is_active": 1, "current_stock": [">", 0]})


def get_low_stock_count(
    category: Optional[str] = None, status: Optional[str] = None
) -> int:
    conditions = "is_active = 1 AND current_stock <= reorder_level"
    if category:
        conditions += f" AND category = '{category}'"
    if status == "Out of Stock":
        conditions += " AND current_stock = 0"
    elif status == "Low":
        conditions += " AND current_stock > 0"
    result = frappe.db.sql(
        f"""
        SELECT COUNT(*) as count
        FROM `tabMedicine`
        WHERE {conditions}
    """,
        as_dict=True,
    )
    return result[0].count if result else 0


def get_total_stock_value(category: Optional[str] = None) -> float:
    conditions = "m.is_active = 1"
    if category:
        conditions += f" AND m.category = '{category}'"
    result = frappe.db.sql(
        f"""
        SELECT SUM(m.current_stock * m.purchase_price) as total_value
        FROM `tabMedicine` m
        WHERE {conditions}
    """,
        as_dict=True,
    )
    return result[0].total_value or 0.0


def get_low_stock_items(
    category: Optional[str] = None, status: Optional[str] = None
) -> List[Dict[str, Any]]:
    conditions = "m.is_active = 1 AND m.current_stock <= m.reorder_level"
    if category:
        conditions += f" AND m.category = '{category}'"
    if status == "Out of Stock":
        conditions += " AND m.current_stock = 0"
    elif status == "Low":
        conditions += " AND m.current_stock > 0"
    elif status == "Sufficient":
        conditions = "m.is_active = 1 AND m.current_stock > m.reorder_level"

    return frappe.db.sql(
        f"""
        SELECT 
            m.name,
            m.medicine_name,
            m.category,
            m.current_stock,
            m.reorder_level
        FROM `tabMedicine` m
        WHERE {conditions}
        ORDER BY m.current_stock ASC
        LIMIT 20
    """,
        as_dict=True,
    )


def get_expired_medicines_count() -> int:
    today = datetime.now().date()
    result = frappe.db.sql(
        """
        SELECT COUNT(DISTINCT medicine) as count
        FROM `tabMedicine Batch`
        WHERE expiry_date < %s AND remaining_quantity > 0
    """,
        today,
        as_dict=True,
    )
    return result[0].count if result else 0


def get_category_stock_data() -> Dict[str, List]:
    data = frappe.db.sql(
        """
        SELECT 
            c.category_name as category,
            SUM(m.current_stock) as total_stock
        FROM `tabMedicine` m
        LEFT JOIN `tabMedicine Category` c ON m.category = c.name
        WHERE m.is_active = 1
        GROUP BY m.category
        ORDER BY total_stock DESC
    """,
        as_dict=True,
    )
    return {
        "labels": [row.category for row in data],
        "values": [row.total_stock for row in data],
    }


def get_expiry_status_data() -> Dict[str, List]:
    today = datetime.now().date()
    data = frappe.db.sql(
        """
        SELECT 
            CASE 
                WHEN expiry_date < %s THEN 'Expired'
                WHEN DATEDIFF(expiry_date, %s) <= 30 THEN 'Expiring Soon'
                WHEN DATEDIFF(expiry_date, %s) <= 90 THEN 'Expires in 30-90 days'
                ELSE 'Valid'
            END as status,
            SUM(remaining_quantity) as total_quantity
        FROM `tabMedicine Batch`
        WHERE remaining_quantity > 0
        GROUP BY status
    """,
        (today, today, today),
        as_dict=True,
    )

    status_map = {
        "Expired": 0,
        "Expiring Soon": 0,
        "Expires in 30-90 days": 0,
        "Valid": 0,
    }
    for row in data:
        if row.status in status_map:
            status_map[row.status] = row.total_quantity
    return {"labels": list(status_map.keys()), "values": list(status_map.values())}
