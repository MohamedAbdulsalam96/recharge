// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Target Report"] = {
	"filters": [
        {
            "fieldname": "warehouse_target",
            "label": __("Warehouse Target"),
            "fieldtype": "Link",
            "options": "Warehouse Target",
            "reqd": 1
        }
	]
};
