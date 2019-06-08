frappe.ui.form.on("Payment Entry", "payment_type", function(frm) {
    if (cur_frm.doc.payment_type == "Pay") {
	cur_frm.set_value("party_type", "Supplier");
    } else if (cur_frm.doc.payment_type == "Receive") {
	cur_frm.set_value("party_type", "Customer");
    }
});
