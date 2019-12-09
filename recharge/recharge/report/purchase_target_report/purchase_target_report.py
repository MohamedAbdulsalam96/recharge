# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
from datetime import *
import calendar
from time import strptime
def execute(filters=None):
	columns, data = [], []
	columns.append({"label": "Date","width": 120,"fieldname": "date","fieldtype": "Data"})

	warehouse_targets = get_sales_invoice(filters)  # coming from frappe.db.sql in get_stock_ledger_entries()
	colnames = [key for key in warehouse_targets[0].keys()]  # create list of columns used in creating dataframe
	print(colnames)
	df = pd.DataFrame.from_records(warehouse_targets,
								   columns=colnames)  # this is key to get the data from frappe.db.sql loaded correctly.
	print(df)
	pvt = pd.pivot_table(
		df,
		values='total',
		index=['posting_date'],
		columns='set_warehouse',
		fill_value=0
	)

	data = pvt.reset_index().values.tolist()  # reset the index and create a list for use in report.

	columns += pvt.columns.values.tolist()# create the list of dynamic columns added to the previously defined static columns

	print(data)
	return columns, data

def get_sales_invoice(filters):
	warehouse_target = frappe.get_doc("Warehouse Target", filters.get("warehouse_target")).__dict__
	brand = warehouse_target['brand']
	item_group = warehouse_target['item_group']

	month_int = int(strptime(filters.get("warehouse_target").split()[0], '%B').tm_mon)

	warehouse_targets = frappe.db.sql(
		""" SELECT PI.posting_date, SUM(PI.total) as total, PI.set_warehouse FROM 
			(SELECT PI2.posting_date, PI2.status, PI2.total, PI2.set_warehouse FROM `tabPurchase Invoice` AS PI2  
			INNER JOIN `tabPurchase Invoice Item` ON PI2.name = `tabPurchase Invoice Item`.parent  
			WHERE EXISTS (SELECT * FROM `tabItem` 
			WHERE `tabItem`.name = `tabPurchase Invoice Item`.item_code 
			and brand=%s 
			and item_group=%s) 
			and PI2.status != %s 
			and MONTH(posting_date) = %s
			and YEAR(posting_date) = %s 
			and `tabPurchase Invoice Item`.idx = 1 AND EXISTS (SELECT * FROM `tabWarehouse Target Details` 
			WHERE `tabWarehouse Target Details`.warehouse = PI2.set_warehouse) ) as PI 
			GROUP BY posting_date, set_warehouse""",(brand, item_group,"Cancelled", month_int, "2019"), as_dict=True)


	return warehouse_targets
