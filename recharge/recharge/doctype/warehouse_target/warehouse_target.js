// Copyright (c) 2019, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warehouse Target', {
	onload: function(frm) {
		cur_frm.call({
				doc: cur_frm.doc,
				method: 'add_warehouse'
			})
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