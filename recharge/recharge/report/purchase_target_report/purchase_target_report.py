# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
from time import strptime
from datetime import *
from frappe.utils import fmt_money
def execute(filters=None):
	columns, data = [], []
	warehouse_target = frappe.get_doc("Warehouse Target", filters.get("warehouse_target")).__dict__
	brand = warehouse_target['brand']
	item_group = warehouse_target['item_group']
	supplier = warehouse_target['supplier']
	total_target_amount = warehouse_target['total_target_amount']

	month_int = int(strptime(filters.get("warehouse_target").split()[0], '%B').tm_mon)
	date_field = {"label": "Date","width": 150,"fieldname": "date","fieldtype": "Data"}

	columns.append(date_field)

	warehouse_targets = get_purchase_invoice(brand,item_group,month_int,supplier)  # coming from frappe.db.sql in get_stock_ledger_entries()
	colnames = [key for key in warehouse_targets[0].keys()]  # create list of columns used in creating dataframe

	df = pd.DataFrame.from_records(warehouse_targets,
								   columns=colnames)  # this is key to get the data from frappe.db.sql loaded correctly.

	pvt = pd.pivot_table(
		df,
		values='total',
		index=['posting_date'],
		columns='set_warehouse',
		fill_value=0,
		aggfunc=sum,
		margins=True,
		margins_name='Total'
	)


	data = pvt.reset_index().values.tolist()  # reset the index and create a list for use in report.
	totals_array = data[len(data) - 1]
	for idx,i in enumerate(data):
		if idx != len(data) - 1:
			i.append( total_target_amount - i[len(i) - 1])

	for idx, ii in enumerate(data):
		if idx != len(data) - 1:
			ii.append( round(ii[len(ii) - 2] / total_target_amount,2))

	for idx, iii in enumerate(data):
		if idx != len(data) - 1:
			iii.append( round(iii[len(iii) - 2] / total_target_amount,2))

	columns += pvt.columns.values.tolist()# create the list of dynamic columns added to the previously defined static columns

	totals_commision = get_totals(filters,columns,totals_array)
	data.append(totals_commision[4])
	data.append(totals_commision[6])
	data.append(totals_commision[0])
	data.append(totals_commision[7])
	data.append(totals_commision[1])
	data.append(totals_commision[2])
	data.append([])

	data.append(totals_commision[3])
	data.append(totals_commision[5])

	columns = []
	columns.append(date_field)
	for value in pvt.columns.values.tolist():
		columns.append({"label": value,"width": 150,"fieldname": value,"fieldtype": "Data"})
	columns.append({"label": "Target Balance","width": 150,"fieldname": "target_balance","fieldtype": "Data"})
	complete_column_1 = len(columns)
	complete_column_2 = len(columns) + 1
	columns.append("% Complete")
	columns.append("% Complete")
	currency = frappe.db.get_single_value("Global Defaults", "default_currency")
	print("CURRRENCY")
	print(currency)
	for idx,arrays in enumerate(data):
		for idx2,amount in enumerate(arrays):
			try:
				data[idx][idx2] = fmt_money(amount, 2, currency) if (amount >= 0 or amount < 0) \
																 and data[idx][0] != "%ge Target Achieved" \
																 and idx2 != complete_column_1 \
																 and idx2 != complete_column_2 \
					else str(amount) + " %" if ((amount >= 0 or amount < 0) and data[idx][0] == "%ge Target Achieved") or (idx2 == complete_column_1 or idx2 == complete_column_2 ) else \
				data[idx][idx2]
			except:
				try:
					print(data[idx][idx2])
					data[idx][idx2] = datetime.strptime(str(data[idx][idx2]), "%Y-%m-%d").date()
					data[idx][idx2] = data[idx][idx2].strftime("%d") + "-" + data[idx][idx2].strftime("%m") + "-" + data[idx][idx2].strftime("%Y")
				except:
					print(frappe.get_traceback())

	return columns, data

def get_purchase_invoice(brand,item_group,month_int,supplier):


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
			WHERE `tabWarehouse Target Details`.warehouse = PI2.set_warehouse) AND supplier=%s) as PI 
			GROUP BY posting_date, set_warehouse""",(brand, item_group,"Cancelled", month_int, "2019",supplier), as_dict=True)


	return warehouse_targets

def get_totals(filters,columns,totals_array):
	warehouse_target = frappe.get_doc("Warehouse Target", filters.get("warehouse_target")).__dict__
	brand = warehouse_target['brand']
	item_group = warehouse_target['item_group']
	total_target_amount = warehouse_target['total_target_amount']
	supplier = warehouse_target['supplier']
	total = 0
	month_int = int(strptime(filters.get("warehouse_target").split()[0], '%B').tm_mon)
	warehouse_final_array = ["Difference"]
	warehouse_totals = frappe.db.sql(
		""" SELECT SUM(total) as total, set_warehouse  FROM `tabPurchase Invoice` AS PI2
            INNER JOIN `tabPurchase Invoice Item` ON PI2.name = `tabPurchase Invoice Item`.parent
            WHERE EXISTS (SELECT * FROM `tabItem`
            WHERE `tabItem`.name = `tabPurchase Invoice Item`.item_code
            and brand=%s
            and item_group=%s)
            and PI2.status != %s
            and MONTH(posting_date) = %s
            and YEAR(posting_date) = %s
            and `tabPurchase Invoice Item`.idx = 1 AND EXISTS (SELECT * FROM `tabWarehouse Target Details`
            WHERE `tabWarehouse Target Details`.warehouse = PI2.set_warehouse AND supplier=%s) 
            GROUP BY set_warehouse ASC""", (brand, item_group, "Cancelled", month_int, "2019",supplier))
	for i in warehouse_totals:
		target_amount = frappe.get_list("Warehouse Target Details", filters={"parent": filters.get("warehouse_target"), "warehouse": i[1]}, fields=["target_amount"])

		warehouse_final_array.append(i[0] - target_amount[0].target_amount)
		total += i[0] - target_amount[0].target_amount

	warehouse_final_array.append(round(total,2))
	warehouse_final_array.append(round(total_target_amount,2))
	get_percentage_data = get_percentage(warehouse_totals,filters,columns,totals_array)

	return warehouse_final_array,get_percentage_data[0],get_percentage_data[1],get_percentage_data[2],get_percentage_data[3],get_percentage_data[4],get_percentage_data[5],get_percentage_data[6]


def get_percentage(warehouse_totals,filters,columns,totals_array):
	nowd = frappe.get_value("Warehouse Target", filters.get("warehouse_target"), "number_of_working_days")
	bonus = frappe.get_value("Warehouse Target", filters.get("warehouse_target"), "bonus")
	total_target_amount = frappe.get_value("Warehouse Target", filters.get("warehouse_target"), "total_target_amount")
	percentage_bonus_return = ["Commision"]
	percentage_bonus_return_total = 0

	percentage_commision = ["%ge Target Achieved"]
	percentage_computation = 0

	targe_divide_nowd_array = ["Target per day"]
	targe_divide_nowd_array_total = 0

	targe_times_nowd_array = ["Purchase Target"]

	minus_array = ["Target to be Achieved"]
	minus_array_total = 0

	array_1 = ["", ""]
	array_2 = ["", ""]

	bonus_record = frappe.get_list("Monthly Bonus", filters={"parent": bonus}, fields=["percentage_target", "percentage_bonus"], order_by="percentage_bonus")

	for i in range(1,len(columns) - 1):
		sum = get_sum(columns[i],warehouse_totals)
		percentage_amount = 0
		target_amount = frappe.get_list("Warehouse Target Details",
										filters={"parent": filters.get("warehouse_target"), "warehouse": columns[i]},
										fields=["target_amount"])
		percentage = round((sum / target_amount[0].target_amount) * 100,2)
		targe_divide_nowd = round((target_amount[0].target_amount / nowd),2)
		targe_times_nowd = round((targe_divide_nowd * nowd),2)
		difference = round(targe_times_nowd - sum,2)
		for ii in bonus_record:
			if percentage >= int(ii.percentage_target):
				percentage_amount = sum * (ii.percentage_bonus / 100)

		percentage_bonus_return.append(round(percentage_amount,2))
		percentage_bonus_return_total += round(percentage_amount,2)

		percentage_commision.append(float(percentage))
		percentage_computation = round(( totals_array[len(totals_array) - 1] / total_target_amount ) * 100,2)
		targe_divide_nowd_array.append(float(targe_divide_nowd))
		targe_divide_nowd_array_total += float(targe_divide_nowd)

		targe_times_nowd_array.append(float(round(targe_times_nowd)))

		minus_array.append(float(difference))
		minus_array_total += float(difference)
		array_1.append("")
		array_2.append("")
	array_1.append(round(total_target_amount / nowd,2))
	array_2.append(round(totals_array[len(totals_array) - 1],2))
	percentage_bonus_return.append(round(percentage_bonus_return_total, 2))

	targe_divide_nowd_array.append(float(targe_divide_nowd_array_total))
	targe_divide_nowd_array.append(round(total_target_amount / nowd,2) * nowd)


	percentage_commision.append(float(percentage_computation))
	percentage_bonus_return.append(round(total_target_amount - totals_array[len(totals_array) - 1] ,2))

	minus_array.append(round(minus_array_total, 2))
	minus_array.append(round(total_target_amount / nowd,2) * nowd - round(totals_array[len(totals_array) - 1], 2))

	return percentage_bonus_return,percentage_commision,targe_divide_nowd_array,targe_times_nowd_array,minus_array,array_1,array_2

def get_sum(warehouse,warehouse_totals):
	for i in warehouse_totals:
		if i[1] == str(warehouse):
			return i[0]