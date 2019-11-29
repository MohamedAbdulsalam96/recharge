# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import *

def execute(filters=None):
	columns, data = [], []
	add_columns(columns,"Date", "date")
	if filters.get("warehouse_target"):
		warehouses = frappe.get_list("Warehouse", fields=["*"])
		warehouse_target = frappe.get_doc("Warehouse Target",filters.get("warehouse_target")).__dict__
		defaults = frappe.get_single("Global Defaults").__dict__
		number_of_working_days = warehouse_target['number_of_working_days']
		month = warehouse_target['month']
		year = warehouse_target['year']
		total_target_amount = warehouse_target['total_target_amount']
		for day in range(1,number_of_working_days+1):
			date_string = str(month) + " " + str(day) + " " + str(year)
			date = datetime.strptime(date_string, '%B %d %Y')

			total_purchase = 0
			purchases = {}
			purchases["date"] = day
			if not check_date_in_holiday(date.date(),defaults):
				for i in warehouses:
					total = get_total_purchases(i.name,date.date())
					if total > 0 and not check_if_column_labels(columns,i.warehouse_name):
						total_purchase += total
						add_columns(columns,i.warehouse_name,i.warehouse_name.lower().replace(" ","").replace("-","_"))
						purchases[i.warehouse_name.lower().replace(" ", "").replace("-", "_")] = total
					elif total > 0:
						total_purchase += total
						purchases[i.warehouse_name.lower().replace(" ","").replace("-","_")] = total
				purchases["total_purchase"] = total_purchase
				purchases["target_balance"] = total_target_amount - total_purchase
				purchases["complete_total_purchase"] = float(round((total_purchase / total_target_amount),2))
				purchases["complete_target_balance"] = float(round(((total_target_amount - total_purchase) / total_target_amount),2))
				data.append(purchases)

		add_columns(columns, "Total Purchase", "total_purchase")
		add_columns(columns, "Target Balance", "target_balance")
		add_columns(columns, "% Complete", "complete_total_purchase")
		add_columns(columns, "% Complete", "complete_target_balance")
		total_computations(columns,warehouses,data, warehouse_target)
		return columns, data
def get_total_purchases(warehouse, date):
	total = frappe.db.sql(
		""" SELECT SUM(total) FROM `tabPurchase Invoice` WHERE set_warehouse=%s and posting_date=%s""",
		(warehouse, date))[0][0]
	if total:
		return float(total)
	return 0

def add_columns(columns,label,fieldname):
	columns.append({
		"label": label,
		"width": 120,
		"fieldname": fieldname,
		"fieldtype": "Data"})

def check_if_column_labels(columns,label):
	for i in columns:
		if i["label"] == label:
			return True
	return False

def check_date_in_holiday(date,defaults):
	holiday_list = frappe.get_list("Holiday", filters={"parent": defaults["default_holidays"]}, fields=["holiday_date"])
	for i in holiday_list:
		if i.holiday_date == date:
			return True
	return False

#TOTAL COMPUTATIONS and DIFFERENCES
def total_computations(columns,warehouses,data, warehouse_target):
	warehouse_totals = {}
	warehouse_totals_difference = {}
	warehouse_totals["date"] = "Totals"
	for i in warehouses:
		if check_if_column_labels(columns,i.warehouse_name):
			sum_per_warehouse = sum(d[i.warehouse_name.lower().replace(" ","").replace("-","_")] if i.warehouse_name.lower().replace(" ","").replace("-","_") in d else 0 for d in data if d)
			get_target_amount_value = get_target_amount(warehouse_target["warehouse_target_details"],i.warehouse_name.lower().replace(" ","").replace("-","_"))
			difference = sum_per_warehouse - get_target_amount_value if get_target_amount_value > 0 else 0
			warehouse_totals[i.warehouse_name.lower().replace(" ","").replace("-","_")] = sum_per_warehouse
			warehouse_totals_difference[i.warehouse_name.lower().replace(" ","").replace("-","_")] = difference
	data.append({})
	data.append(warehouse_totals)
	data.append(warehouse_totals_difference)

	return warehouse_totals
#GET TARGET AMOUNT
def get_target_amount(warehouse_target_details, warehouse_name):
	for i in warehouse_target_details:
		data = i.__dict__
		get_warehouse_name = frappe.get_value("Warehouse", data["warehouse"], "warehouse_name")
		change_name = get_warehouse_name.lower().replace(" ","").replace("-","_")
		if change_name == warehouse_name and data["target_amount"] > 0:
			return data["target_amount"]
	return 0
