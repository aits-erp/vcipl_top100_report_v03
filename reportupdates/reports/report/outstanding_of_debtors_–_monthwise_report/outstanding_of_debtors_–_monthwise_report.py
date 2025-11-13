# Copyright (c) 2025
# Report: Top Most Selling Items - Stock report
# Author: Sai More

import frappe
import re


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


# ---------------------------------------------------------
# COLUMNS
# ---------------------------------------------------------
def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
        {"label": "Total Sold Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 120},
        {"label": "Total Sales Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Current Stock", "fieldname": "current_stock", "fieldtype": "Float", "width": 120},
        {"label": "Safety Stock", "fieldname": "safety_stock", "fieldtype": "Float", "width": 120},
        {"label": "Shortage Qty", "fieldname": "shortage_qty", "fieldtype": "Float", "width": 120}
    ]


# ---------------------------------------------------------
# MAIN DATA FUNCTION
# ---------------------------------------------------------
def get_data(filters):

    # -------------------------
    # LIMIT FILTER
    # -------------------------
    limit_value = filters.get("limit")

    try:
        limit = int(limit_value) if limit_value else 50
    except:
        match = re.search(r"\d+", str(limit_value))
        limit = int(match.group()) if match else 50

    # -------------------------
    # ITEM GROUP FILTER
    # -------------------------
    ig_condition = ""
    params = {}

    if filters.get("item_group"):
        ig_condition = " AND i.item_group = %(item_group)s "
        params["item_group"] = filters.get("item_group")

    # -------------------------
    # MAIN QUERY
    # -------------------------
    query = f"""
        SELECT
            sii.item_code AS item_code,
            i.item_name AS item_name,
            i.item_group AS item_group,
            SUM(sii.qty) AS total_qty,
            SUM(sii.base_net_amount) AS total_amount,

            -- All warehouse stock
            COALESCE((
                SELECT SUM(actual_qty)
                FROM `tabBin`
                WHERE item_code = sii.item_code
            ), 0) AS current_stock,

            COALESCE(i.safety_stock, 0) AS safety_stock,

            (COALESCE(i.safety_stock, 0) -
            COALESCE((
                SELECT SUM(actual_qty)
                FROM `tabBin`
                WHERE item_code = sii.item_code
            ), 0)
            ) AS shortage_qty

        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        LEFT JOIN `tabItem` i ON i.name = sii.item_code

        WHERE si.docstatus = 1
        {ig_condition}

        GROUP BY sii.item_code, i.item_name, i.item_group, i.safety_stock

        ORDER BY total_qty DESC

        LIMIT {limit}
    """

    return frappe.db.sql(query, params, as_dict=True)
