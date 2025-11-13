// Copyright (c) 2025, sai
// Report JS for: Top Most Selling Items - Stock Report

frappe.query_reports["Top Most Selling Items - Stock report"] = {
    filters: [
        
        {
            fieldname: "limit",
            label: __("Most Selling"),
            fieldtype: "Select",
            options: ["50", "100"],
            default: "50"
        }
    ]
};
