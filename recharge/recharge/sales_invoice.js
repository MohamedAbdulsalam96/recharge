frappe.ui.form.on('Sales Invoice Item', {
	item_code:function(frm,cdt,cdn){
		var row=locals[cdt][cdn];
		var doc=locals['Sales Invoice'][row.parent]
		// console.log(doc);
		for(var item in doc.items){
			if(doc.items[item].item_code==row.item_code && doc.items[item].start_series==row.start_series && doc.items[item].end_series==row.end_series){
				// console.log("true")
				if(doc.items[item].name!=row.name){
					frappe.model.set_value(cdt,cdn,"item_code","")
					frappe.throw("Item, Start Series and End Series Already Selected");
				}
			}
		}
	},
	start_series:function(frm,cdt,cdn){
		var row=locals[cdt][cdn];
		if(row.end_series){
			if(parseFloat(row.start_series)>parseFloat(row.end_series)){
				frappe.throw("End Series Must Be Greater Than Start Series")
			}
			var diff=parseFloat(row.end_series)-parseFloat(row.start_series) + 1
			frappe.model.set_value(cdt,cdn,"qty",diff)
		}
		var doc=locals['Sales Invoice'][row.parent]
		// console.log(doc);
		for(var item in doc.items){
			if(doc.items[item].item_code==row.item_code && doc.items[item].start_series==row.start_series && doc.items[item].end_series==row.end_series){
				// console.log("true")
				if(doc.items[item].name!=row.name){
					frappe.model.set_value(cdt,cdn,"start_series","")
					frappe.throw("Item, Start Series and End Series Already Selected");
				}
			}
		}
	},
	end_series:function(frm,cdt,cdn){
		var row=locals[cdt][cdn];
		if(row.start_series){
			if(parseFloat(row.start_series)>parseFloat(row.end_series)){
				frappe.throw("End Series Must Be Greater Than Start Series")
			}
			var diff=parseFloat(row.end_series)-parseFloat(row.start_series) + 1
			frappe.model.set_value(cdt,cdn,"qty",diff)
		}
		var doc=locals['Sales Invoice'][row.parent]
		// console.log(doc);
		for(var item in doc.items){
			if(doc.items[item].item_code==row.item_code && doc.items[item].start_series==row.start_series && doc.items[item].end_series==row.end_series){
				// console.log("true")
				if(doc.items[item].name!=row.name){
					frappe.model.set_value(cdt,cdn,"end_series","")
					frappe.throw("Item, Start Series and End Series Already Selected");
				}
			}
		}
	}
})
