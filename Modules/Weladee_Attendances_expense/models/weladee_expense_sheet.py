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
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub

class weladee_expense_sheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def approve_expense_sheets(self):
        return super(weladee_expense_sheet, self).with_context({'mail_create_nosubscribe':False}).approve_expense_sheets()       

    def write(self, vals):
        ret = super(weladee_expense_sheet, self).write(vals)
        
        if ('state' in vals) and ret and self.env.context.get('send2-weladee', True):
           if vals.get('state')  == 'done':
              for each in self:
                  for line in each.expense_line_ids:
                      if line.weladee_id:  
                          self._update_in_weladee(line)

        return ret

    def _update_in_weladee(self, line):
        '''
        create new record in weladee
        '''
        ret = self.env['weladee_attendance.synchronous.setting'].get_settings()
        
        if ret.authorization:
            WeladeeData = odoo_pb2.ExpenseStatus()            
            WeladeeData.ID = int(line.weladee_id)
            WeladeeData.status = expense_pb2.ExpenseStatusRefunded

            try:
                _logger.info("Odoo > %s" % WeladeeData)    
                result = stub.UpdateExpenseStatus(WeladeeData, metadata=ret.authorization)
                _logger.info("update expense on Weladee : %s" % result)
            except Exception as e:
                _logger.info("Odoo > %s" % WeladeeData)
                _logger.error("Error while update expense on Weladee : %s" % e)
        else:
          _logger.error("Error while update expense on Weladee : No authroized")
            