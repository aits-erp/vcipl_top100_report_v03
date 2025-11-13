# Copyright (c) 2025
# Report: Top Selling Items Which Are Out of Stock
# Author: Sai More

import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


# -------------------------------------
#  REPORT COLUMNS
# -------------------------------------
def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Total Sold Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 120},
        {"label": "Total Sales Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Current Stock", "fieldname": "current_stock", "fieldtype": "Float", "width": 120},
        {"label": "Safety Stock", "fieldname": "safety_stock", "fieldtype": "Float", "width": 120},
        {"label": "Shortage Qty", "fieldname": "shortage_qty", "fieldtype": "Float", "width": 120},
    ]


# -------------------------------------
#  FETCH DATA
# -------------------------------------
def get_data(filters):

    # --------------------------
    # DATE FILTERS
    # --------------------------
    conditions = ["si.docstatus = 1"]
    params = {}

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("si.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        params["from_date"] = filters.get("from_date")
        params["to_date"] = filters.get("to_date")

    elif filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        params["from_date"] = filters.get("from_date")

    elif filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        params["to_date"] = filters.get("to_date")

    where_clause = "WHERE " + " AND ".join(conditions)

    # --------------------------
    # LIMIT HANDLING (Top 50 / Top 100)
    # --------------------------
    limit_value = filters.get("limit")

    try:
        # User selected "50" or "100"
        limit = int(limit_value) if limit_value else 50
    except:
        # In case user enters “Top 50”, “top100”, etc.
        import re
        match = re.search(r"\d+", str(limit_value))
        limit = int(match.group()) if match else 50

    # --------------------------
    # MAIN QUERY
    # --------------------------
    query = f"""
        SELECT
            sii.item_code AS item_code,
            i.item_name AS item_name,
            SUM(sii.qty) AS total_qty,
            SUM(sii.base_net_amount) AS total_amount,

            -- TOTAL STOCK FROM ALL WAREHOUSES
            COALESCE((
                SELECT SUM(actual_qty)
                FROM `tabBin`
                WHERE item_code = sii.item_code
            ), 0) AS current_stock,

            COALESCE(i.safety_stock, 0) AS safety_stock,

            -- Shortage = Safety Stock - Current Stock
            (COALESCE(i.safety_stock, 0) -
             COALESCE((
                SELECT SUM(actual_qty)
                FROM `tabBin`
                WHERE item_code = sii.item_code
            ), 0)
            ) AS shortage_qty

        FROM
            `tabSales Invoice Item` sii
        INNER JOIN
            `tabSales Invoice` si ON si.name = sii.parent
        LEFT JOIN
            `tabItem` i ON i.name = sii.item_code

        {where_clause}

        GROUP BY
            sii.item_code, i.item_name, i.safety_stock

        HAVING
            shortage_qty > 0   -- Only items below safety stock

        ORDER BY
            shortage_qty DESC

        LIMIT {limit}
    """

    return frappe.db.sql(query, params, as_dict=True)
