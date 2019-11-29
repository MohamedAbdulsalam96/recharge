# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class WarehouseTarget(Document):
	def add_warehouse(self):
		print(self.__dict__)
		if "New Warehouse Target" in self.name or not self.warehouse_target_details:
			warehouse = frappe.get_list("Warehouse", fields=["name"], order_by='name')
			print("test")
			for i in warehouse:
				warehouse_row = self.append('warehouse_target_details', {})
				warehouse_row.warehouse = i.name
