# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_ot.models.sync.weladee_ot_type import sync_ot_type
from odoo.addons.Weladee_Attendances_ot.models.sync.weladee_ot_request import sync_ot

class weladee_attendance_ot(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_ot, self).init_param()

        # for ot
        r.employee_obj  = False
        r.translation_obj = False

        r.ot_type_obj = False
        r.ot_request_obj = False
        r.ot_type_odoo_weladee_ids = {}

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_ot, self).do_sync_options(req)
        if req.config.sync_ot and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...OT Types")
            req.employee_obj = self.env['hr.employee']
            req.ot_type_obj = self.env['fwot_ot_type']
            sync_ot_type(req)
        
        if req.config.sync_ot and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...OT Requests")
            req.employee_obj = self.env['hr.employee']
            req.ot_type_obj = self.env['fwot_ot_type']
            req.ot_request_obj = self.env['fwot_ot_requests']

            sync_ot(req)