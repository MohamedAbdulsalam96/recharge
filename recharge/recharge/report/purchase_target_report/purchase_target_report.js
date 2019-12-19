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
	],
    "formatter": function(value, row, column, data, default_formatter) {
	    value = default_formatter(value, row, column, data);
	    if (value === "Total" || value === "Commision" || value === "%ge Target Achieved"){
	        value = '<b style="font-weight:bold">'+value+'</b>';
	    }
	    return value;
	}
};

