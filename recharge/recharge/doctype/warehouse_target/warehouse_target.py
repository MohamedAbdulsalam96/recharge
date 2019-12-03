# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class WarehouseTarget(Document):
	def add_warehouse(self):
		print(self.__dict__)

		if self.warehouse_group:
			warehouse = frappe.get_list("Warehouse", filters={"parent_warehouse": self.warehouse_group}, fields=["name"], order_by='name')
			for i in warehouse:
				warehouse_row = self.append('warehouse_target_details', {})
				warehouse_row.warehouse = i.name
