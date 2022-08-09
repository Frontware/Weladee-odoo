# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_timesheet.models.sync.weladee_customer import sync_customer
from odoo.addons.Weladee_Attendances_timesheet.models.sync.weladee_project import sync_project
from odoo.addons.Weladee_Attendances_timesheet.models.sync.weladee_task import sync_task
from odoo.addons.Weladee_Attendances_timesheet.models.sync.weladee_worktype import sync_work_type
from odoo.addons.Weladee_Attendances_timesheet.models.sync.weladee_timesheet import sync_timesheet

class weladee_attendance_timesheet(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_timesheet, self).init_param()

        # for timesheet
        r.customer_obj = False
        r.customer_odoo_weladee_ids = {}
        ''' map customer, key: weladee customer id,value: customer odoo id'''

        r.project_obj = False
        r.project_odoo_weladee_ids = {}
        ''' map project, key: weladee project id,value: project odoo id'''

        r.task_obj = False
        r.task_odoo_weladee_ids = {}
        ''' map task, key: weladee task id,value: task odoo id'''

        r.user_odoo_weladee_ids = {}
        ''' map user, key: weladee employee id,value: user odoo id'''

        r.work_type_obj = False
        r.work_type_odoo_weladee_ids = {}
        ''' map work type, key: weladee work type id,value: work type odoo id'''

        r.timesheet_obj = False  

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_timesheet, self).do_sync_options(req)

        if req.config.sync_timesheet and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Customer")
            req.customer_obj = self.env['res.partner']
            sync_customer(req)

        if req.config.sync_timesheet and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Project")
            req.project_obj = self.env['project.project']
            req.task_obj = self.env['project.task']
            req.timesheet_obj= self.env['account.analytic.line']
            sync_project(req)

        if req.config.sync_timesheet and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Task")
            sync_task(req)

        if req.config.sync_timesheet and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Work type")
            req.work_type_obj = self.env['mail.activity.type']
            sync_work_type(req)

        if req.config.sync_timesheet and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Timesheet")
            sync_timesheet(req)

