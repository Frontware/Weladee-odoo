# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_approval.models.sync.weladee_approvals_type import sync_approvals_type, delete_approvals_type
from odoo.addons.Weladee_Attendances_approval.models.sync.weladee_approvals_request import sync_approvals_request, delete_approvals_request

class weladee_attendance_approval(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_approval, self).init_param()

        # for approval
        r.employee_obj  = False
        r.translation_obj = False
        r.project_obj = False
        r.attach_obj = False

        r.approvals_type_obj = False
        r.approvals_type_approver_obj = False
        r.approvals_request_obj = False
        r.approvals_approver_1_obj = False
        r.approvals_approver_2_obj = False
        r.approvals_approver_3_obj = False

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_approval, self).do_sync_options(req)
        if req.config.sync_approval and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Approvals Types")
            req.employee_obj = self.env['hr.employee']
            req.approvals_type_obj = self.env['fw.approvals.type']
            req.translation_obj = self.env['ir.translation']
            sync_approvals_type(req)
        
        if req.config.sync_approval and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Approvals Requests")
            req.employee_obj = self.env['hr.employee']
            req.project_obj = self.env['project.project']
            req.attach_obj = self.env['ir.attachment']
            req.approvals_type_obj = self.env['fw.approvals.type']
            req.approvals_type_approver_obj = self.env['fw.approvals.type.approver']
            req.approvals_request_obj = self.env['fw.approvals.request']
            req.approvals_approver_1_obj = self.env['fw.approvals.approver1']
            req.approvals_approver_2_obj = self.env['fw.approvals.approver2']
            req.approvals_approver_3_obj = self.env['fw.approvals.approver3']

            sync_approvals_request(req)

    def do_delete_options(self, req):
        if req.config.sync_approval:
            delete_approvals_request(req)
            delete_approvals_type(req)

        super(weladee_attendance_approval, self).do_delete_options(req)

