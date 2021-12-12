# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import datetime
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api

from . import weladee_settings
from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2, expense_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .sync.weladee_base import stub

class weladee_expense_sheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def approve_expense_sheets(self):
        print('xxx')
        for each in self.expense_line_ids:
            if each.weladee_id:
               self._update_in_weladee(each)
        return super(weladee_expense_sheet, self).approve_expense_sheets()       

    def _update_in_weladee(self, line):
        '''
        create new record in weladee
        '''
        ret = weladee_settings.get_api_key(self)      
        
        if ret.authorization:
            WeladeeData = odoo_pb2.ExpenseOdoo()

            WeladeeData.odoo.odoo_id = line.id
            WeladeeData.odoo.odoo_created_on = int(time.time())
            WeladeeData.odoo.odoo_synced_on = int(time.time())

            WeladeeData.Expense.ID = int(line.weladee_id)
            WeladeeData.Expense.Status = expense_pb2.Status.ExpenseStatusRefunded
            # WeladeeData.Expense.EmployeeID = int(line.employee_id.weladee_id)
            # WeladeeData.Expense.Vendor = line.bill_partner_id.name
            WeladeeData.Expense.Amount = int(line.request_amount * 100)
            WeladeeData.Expense.AmountToRefund = int(line.total_amount * 100)
            # WeladeeData.Expense.Date = int(datetime.datetime.strptime(line.date.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())

            try:
                _logger.info("Odoo > %s" % WeladeeData)    
                result = stub.UpdateExpense(WeladeeData, metadata=ret.authorization)
                _logger.info("update expense on Weladee : %s" % result)
            except Exception as e:
                _logger.info("Odoo > %s" % WeladeeData)
                _logger.error("Error while update expense on Weladee : %s" % e)
        else:
          _logger.error("Error while update expense on Weladee : No authroized")
            