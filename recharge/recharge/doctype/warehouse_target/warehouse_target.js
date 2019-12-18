// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warehouse Target', {
	warehouse_group: function(frm) {
		if(cur_frm.doc.warehouse_group){
			cur_frm.clear_table("warehouse_target_details")
			cur_frm.doc.total_target_amount = 0
			cur_frm.refresh()
			cur_frm.call({
				doc: cur_frm.doc,
				method: 'add_warehouse'
			})
		}

	}
});

cur_frm.cscript.target_amount = function (frm) {
	var total = 0
	for (var i = 0; i < cur_frm.doc.warehouse_target_details.length; i+=1) {
		total += cur_frm.doc.warehouse_target_details[i].target_amount
	}
	cur_frm.doc.total_target_amount = total
	cur_frm.refresh_field("total_target_amount")
};

cur_frm.cscript.refresh = function (frm) {
	cur_frm.add_custom_button(__("Purchase Target"), function() {
		frappe.set_route("query-report", "Purchase Target Report", {"warehouse_target": cur_frm.doc.name});
	});
	cur_frm.add_custom_button(__("Purchase Target Summary"), function() {
		frappe.set_route("query-report", "Purchase Target Summary Report", {"target": cur_frm.doc.name});
	});

};

cur_frm.fields_dict["warehouse_group"].get_query = function() {
	return {
		filters: {
			"is_group": 1
		}
	};
};
