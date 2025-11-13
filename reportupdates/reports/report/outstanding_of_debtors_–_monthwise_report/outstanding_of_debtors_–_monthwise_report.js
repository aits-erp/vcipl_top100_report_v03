frappe.query_reports["Top Most Selling Items - Stock report"] = {
    filters: [
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group",
            reqd: 0
        },
        {
            fieldname: "limit",
            label: __("Top Items"),
            fieldtype: "Select",
            options: "50\n100",
            default: "50"
        }
    ]
};
