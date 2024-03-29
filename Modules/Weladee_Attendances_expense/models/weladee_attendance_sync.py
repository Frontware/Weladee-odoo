# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_expense.models.sync.weladee_expense import sync_expense
from odoo.addons.Weladee_Attendances_expense.models.sync.weladee_expense_type import sync_expense_type

class weladee_attendance_expense(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_expense, self).init_param()

        # for expense
        r.expense_obj = False
        r.expense_sheet_obj = False
        r.attach_obj = False
        r.customer_obj = False
        r.employee_user = {}
        ''' map employee user, key:employee id, value: odoo user object '''

        r.expense_type_obj = False
        r.expense_type_odoo_weladee_ids = {}
        ''' map expense type, key:type id, value: odoo id '''

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_expense, self).do_sync_options(req)

        if req.config.sync_expense and not sync_has_error(req.context_sync):

            if not req.config.expense_product_id:
               sync_stop(req.context_sync)
               sync_logerror(req.context_sync,'Please setup Expense product at Weladee settings -> Expense')
               return

            if not req.config.expense_journal_id:
               sync_stop(req.context_sync)
               sync_logerror(req.context_sync,'Please setup Expense journal at Weladee settings -> Expense')
               return

            sync_logdebug(req.context_sync,"Start sync...Expense type")
            req.expense_type_obj = self.env['weladee_expense_type']
            sync_expense_type(req)

            sync_logdebug(req.context_sync,"Start sync...Expense")
            req.expense_obj = self.env['hr.expense']
            req.expense_sheet_obj = self.env['hr.expense.sheet']
            req.attach_obj = self.env['ir.attachment']
            req.customer_obj = self.env['res.partner']
            sync_expense(req)
