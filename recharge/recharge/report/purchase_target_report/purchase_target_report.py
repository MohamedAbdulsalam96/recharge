# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import *
import calendar
from time import strptime

def execute(filters=None):
	columns, data = [], []
	add_columns(columns,"Date", "date")
	if filters.get("warehouse_target"):
		warehouses = frappe.get_list("Warehouse", fields=["*"])
		warehouse_target = frappe.get_doc("Warehouse Target",filters.get("warehouse_target")).__dict__
		defaults = frappe.get_single("Global Defaults").__dict__
		month = warehouse_target['month']
		year = warehouse_target['year']
		total_target_amount = warehouse_target['total_target_amount']
		month_int = int(strptime(month, '%B').tm_mon)
		_to = int(str(calendar.monthrange(int(year), month_int))[4] + str(calendar.monthrange(int(year), month_int))[5])
		for day in range(1,_to):
			date_string = str(month) + " " + str(day) + " " + str(year)
			date = datetime.strptime(date_string, '%B %d %Y')

			total_purchase = 0
			purchases = {}
			purchases["date"] = day
			if total_target_amount > 0:
				for i in warehouses:
					total = get_total_purchases(i.name,date.date(),warehouse_target)
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
		total_computations(columns,warehouses,data, warehouse_target,filters)
		return columns, data
def get_total_purchases(warehouse, date, warehouse_target):
	brand = warehouse_target['brand']
	item_group = warehouse_target['item_group']
	total_that_will_be_returned = 0
	pi = frappe.db.sql(
		""" SELECT name, total FROM `tabPurchase Invoice` WHERE set_warehouse=%s and posting_date=%s""",
		(warehouse, date), as_dict=True)
	for i in pi:
		valid_pi = check_valid_pi(i.name,brand,item_group)
		if valid_pi:
			total_that_will_be_returned += float(i.total)
	return total_that_will_be_returned

def check_valid_pi(pi_name,brand,item_group):
	pi_details = frappe.get_list("Purchase Invoice Item", filters={"parent": pi_name}, fields=["*"])
	for i in pi_details:
		get_item = frappe.get_list("Item", filters={"name": i.item_code, "brand": brand, "item_group": item_group}, fields=["*"])
		if len(get_item) == 0:
			return False
	return True
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
def total_computations(columns,warehouses,data, warehouse_target,filters):
	warehouse_totals = {}
	warehouse_totals_difference = {}
	commissions = {}
	commissions_amount = {}
	target_over_number_of_working_days = {}
	sum_multiplied_to_number_of_working_days = {}
	sum_multiplied_to_number_of_working_days_minus_sum = {}


	warehouse_totals["date"] = "Totals"
	for i in warehouses:
		if check_if_column_labels(columns,i.warehouse_name):
			sum_per_warehouse = sum(d[i.warehouse_name.lower().replace(" ","").replace("-","_")] if i.warehouse_name.lower().replace(" ","").replace("-","_") in d else 0 for d in data if d)
			get_target_amount_value = get_target_amount(warehouse_target["warehouse_target_details"],i.warehouse_name.lower().replace(" ","").replace("-","_"))
			no_of_working_days = frappe.get_doc("Warehouse Target",filters.get("warehouse_target")).__dict__['number_of_working_days']
			difference = sum_per_warehouse - get_target_amount_value if get_target_amount_value > 0 else 0
			commission_value = commission_check(sum_per_warehouse,get_target_amount_value,filters)[0]
			commission_amount_value = commission_check(sum_per_warehouse,get_target_amount_value,filters)[1]
			warehouse_totals[i.warehouse_name.lower().replace(" ","").replace("-","_")] = sum_per_warehouse
			warehouse_totals_difference[i.warehouse_name.lower().replace(" ","").replace("-","_")] = difference
			commissions[i.warehouse_name.lower().replace(" ","").replace("-","_")] = float(round(commission_value,2))
			commissions_amount[i.warehouse_name.lower().replace(" ","").replace("-","_")] = float(round(commission_amount_value,2))
			target_over_number_of_working_days[i.warehouse_name.lower().replace(" ","").replace("-","_")] = float(round(get_target_amount_value / no_of_working_days,2))
			sum_multiplied_to_number_of_working_days[i.warehouse_name.lower().replace(" ","").replace("-","_")] = float(round(((get_target_amount_value / no_of_working_days) * no_of_working_days),2))
			sum_multiplied_to_number_of_working_days_minus_sum[i.warehouse_name.lower().replace(" ","").replace("-","_")] = float(round((get_target_amount_value / no_of_working_days) * no_of_working_days - sum_per_warehouse,2))

	data.append({})
	data.append(warehouse_totals)
	data.append({})
	data.append(warehouse_totals_difference)
	data.append({})
	data.append(commissions_amount)
	data.append(commissions)
	data.append({})
	data.append(target_over_number_of_working_days)
	data.append(sum_multiplied_to_number_of_working_days)
	data.append(sum_multiplied_to_number_of_working_days_minus_sum)
	data.append({})



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

#COMPUTE COMMISION
def commission_check(sum_per_warehouse,target_amount_value,filters):
	percentage_bonus_return = 0
	warehouse_target = frappe.get_doc("Warehouse Target", filters.get("warehouse_target")).__dict__

	year = warehouse_target['year']

	get_monthly_commisions = frappe.get_list("Monthly Bonus", filters={"parent": "BONUSES " + str(year)}, fields=["percentage_target", "percentage_bonus"], order_by="percentage_bonus")

	if target_amount_value == 0:
		return 0,percentage_bonus_return

	percentage = (sum_per_warehouse / target_amount_value) * 100

	for i in get_monthly_commisions:
		if percentage >= int(i.percentage_target):
			percentage_bonus_return = sum_per_warehouse * (i.percentage_bonus/100)

	return percentage,percentage_bonus_return