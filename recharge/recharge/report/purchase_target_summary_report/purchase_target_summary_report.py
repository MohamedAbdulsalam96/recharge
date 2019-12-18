# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
from time import strptime


def execute(filters=None):
	columns = [{"label": "","width": 120,"fieldname": "dummy","fieldtype": "Data"}]
	data = []
	if filters.get("target"):
		warehouse_target = get_targets(filters.get("target"))

		for i in warehouse_target:
			columns.append({"label": i.set_warehouse,"width": 120,"fieldname": i.set_warehouse,"fieldtype": "Data"})
		columns.append({"label": "Total", "width": 120, "fieldname": "total", "fieldtype": "Data"})
		targets = {"dummy": "TARGET"}
		achieves = {"dummy": "ACHIEVED"}
		percentages = {"dummy": "%"}
		targets_total = 0
		achieves_total = 0
		for ii in warehouse_target:
			targets[ii.set_warehouse] = ii.target_amount
			targets_total += ii.target_amount
			achieves[ii.set_warehouse] = ii.total
			achieves_total += ii.total
			percentages[ii.set_warehouse] = round((ii.total / ii.target_amount) * 100,2)


		targets["total"] = targets_total
		achieves["total"] = achieves_total
		percentages["total"] = round((achieves_total / targets_total) * 100,2)
		data.append(targets)
		data.append(achieves)
		data.append(percentages)

	return columns, data

def get_targets(target):
	month_int = int(strptime(target.split()[0], '%B').tm_mon)

	

	warehouse_totals = frappe.db.sql(
		""" SELECT SUM(total) as total, set_warehouse, WTD.target_amount FROM `tabPurchase Invoice` AS PI2
 			INNER JOIN `tabWarehouse Target` AS WT ON WT.name=%s
			INNER JOIN `tabWarehouse Target Details` AS WTD ON WTD.parent = WT.name and WTD.warehouse = PI2.set_warehouse
			INNER JOIN `tabPurchase Invoice Item` ON PI2.name = `tabPurchase Invoice Item`.parent
			WHERE EXISTS (SELECT * FROM `tabItem`
			WHERE `tabItem`.name = `tabPurchase Invoice Item`.item_code
			and brand=WT.brand
			and item_group=WT.item_group)
			and PI2.status != %s
			and MONTH(posting_date) = %s
			and YEAR(posting_date) = WT.year
			and `tabPurchase Invoice Item`.idx = 1 AND EXISTS (SELECT * FROM `tabWarehouse Target Details`
			WHERE `tabWarehouse Target Details`.warehouse = PI2.set_warehouse) AND PI2.supplier=WT.supplier
			GROUP BY set_warehouse ASC""", (target, "Cancelled", month_int), as_dict=True)

	return warehouse_totals