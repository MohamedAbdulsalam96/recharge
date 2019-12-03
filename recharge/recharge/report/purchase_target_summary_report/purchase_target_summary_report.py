# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import *
import calendar

from time import strptime

def execute(filters=None):
	columns, data = [], []
	quarters = ["March", "June", "September", "December"]
	year = datetime.now().year
	warehouse_targets = frappe.db.sql(""" SELECT * FROM `tabWarehouse Target` WHERE name like %s""", ("%" + str(year) + "%"), as_dict=True)
	warehouse_targets.sort(key=lambda date: datetime.strptime(date['name'], '%B %Y'))
	warehouses_count = frappe.db.sql(""" SELECT * FROM `tabWarehouse` """)

	for x in range(0,len(warehouses_count) + 5):
		add_columns(columns, " ", str(x))
	totals_per_warehouse_quarter = {}
	totals_acchieved_per_warehouse_quarter = {}
	acchieved_per_warehouse_divide_per_warehouse_quarter = {}
	total_percentage = {}
	bonus = {}
	for i in warehouse_targets:
		all_warehouse_total = 0
		total_achieved = 0
		data.append({})
		warehouses_name = {}

		targets = {}
		achieved = {}
		percentage = {}
		warehouses_name["0"] = i.name
		targets["0"] = "TARGET"
		achieved["0"] = "ACHIEVED"
		percentage["0"] = "%"
		warehouse_targets = frappe.get_list("Warehouse Target Details", filters={"parent": i.name}, fields=["*"], order_by="warehouse")
		xxx = 1
		for ii in warehouse_targets:
			print("test")
			warehouse_name = get_warehouse_name(ii.warehouse)
			warehouses_name[str(xxx)] = warehouse_name
			targets[str(xxx)] = ii.target_amount
			totals_per_warehouse_quarter[str(xxx)] = totals_per_warehouse_quarter[str(xxx)] + ii.target_amount if str(xxx) in totals_per_warehouse_quarter else ii.target_amount
			all_warehouse_total += ii.target_amount
			achieved[str(xxx)] = get_total_purchases(ii.warehouse,i.name,i.year)
			totals_acchieved_per_warehouse_quarter[str(xxx)] = round(totals_acchieved_per_warehouse_quarter[str(xxx)] + get_total_purchases(ii.warehouse,i.name,i.year),2) if str(xxx) in totals_acchieved_per_warehouse_quarter else round(get_total_purchases(ii.warehouse,i.name,i.year),2)
			total_achieved += get_total_purchases(ii.warehouse,i.name,i.year)
			percentage[str(xxx)] = round((get_total_purchases(ii.warehouse,i.name,i.year) / ii.target_amount * 100),2) if  ii.target_amount > 0 else 0
			total_percentage[str(xxx)] = round(total_percentage[str(xxx)] + round((get_total_purchases(ii.warehouse,i.name,i.year) / ii.target_amount * 100),2) if  ii.target_amount > 0 else 0,2) if str(xxx) in total_percentage else round((get_total_purchases(ii.warehouse,i.name,i.year) / ii.target_amount * 100))
			acchieved_per_warehouse_divide_per_warehouse_quarter[str(xxx)] = round((totals_acchieved_per_warehouse_quarter[str(xxx)] / totals_per_warehouse_quarter[str(xxx)]) * 100, 2)


			xxx += 1
		warehouses_name[xxx] = "Total"
		targets[xxx] = all_warehouse_total
		achieved[xxx] = total_achieved
		percentage[xxx] = round((total_achieved / all_warehouse_total) * 100)
		data.append(warehouses_name)
		data.append(targets)
		data.append(achieved)
		data.append(percentage)
		if i.name.split()[0] in quarters:
			data.append({})
			bonus_counter = 1
			while str(bonus_counter) in totals_acchieved_per_warehouse_quarter:
				quarter_commision = get_quarterly_commision(year,total_percentage[str(bonus_counter)] / 3)
				bonus[str(bonus_counter)] =  round(totals_acchieved_per_warehouse_quarter[str(bonus_counter)] * quarter_commision,2)
				bonus_counter+=1
			data.append(total_percentage)
			data.append(totals_per_warehouse_quarter)
			data.append(totals_acchieved_per_warehouse_quarter)
			data.append(acchieved_per_warehouse_divide_per_warehouse_quarter)
			data.append(bonus)

	data.append({})
	return columns, data

def add_columns(columns,label,fieldname):
	columns.append({
		"label": label,
		"width": 120,
		"fieldname": fieldname,
		"fieldtype": "Data"})
def get_warehouse_name(name):
	return frappe.get_value("Warehouse", name, "warehouse_name")

def get_total_purchases(warehouse, date_month,year):
	total = 0
	month = date_month.split()

	month_int = int(strptime(month[0], '%B').tm_mon)
	_to = int(str(calendar.monthrange(int(year), month_int))[4] + str(calendar.monthrange(int(year), month_int))[5])
	defaults = frappe.get_single("Global Defaults").__dict__
	for day in range(1,_to):
		date_string = str(month[0]) + "-" + str(day) + "-" + str(year)
		date = datetime.strptime(date_string, '%B-%d-%Y')

		if not check_date_in_holiday(date.date(),defaults):
			total_purchase = frappe.db.sql(
				""" SELECT SUM(total) FROM `tabPurchase Invoice` WHERE set_warehouse=%s and posting_date=%s""",
				(warehouse, date.date()))[0][0]
			if total_purchase:
				total += total_purchase

	if total > 0:
		return float(total)
	return 0

def check_date_in_holiday(date,defaults):
	holiday_list = frappe.get_list("Holiday", filters={"parent": defaults["default_holidays"]}, fields=["holiday_date"])
	for i in holiday_list:
		if i.holiday_date == date:
			return True
	return False

def get_quarterly_commision(year,total_percentage):
	get_quarterly_commisions = frappe.get_list("Quarterly Bonus", filters={"parent": "BONUSES " + str(year)}, fields=["q_percentage_target", "q_percentage_bonus"], order_by="q_percentage_bonus")

	percentage_bonus_return = 0
	for i in get_quarterly_commisions:
		if total_percentage >= int(i.q_percentage_target):
			percentage_bonus_return = (i.q_percentage_bonus/100)
	return percentage_bonus_return