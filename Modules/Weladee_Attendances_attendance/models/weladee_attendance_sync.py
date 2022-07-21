# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_attendance.models.sync.weladee_log import sync_log

class weladee_attendance_attendance(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_attendance, self).init_param()

        # for attendance
        r.log_obj = False  
        r.period_settings = False

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_attendance, self).do_sync_options(req)

        if req.config.sync_attendance and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Attendance")
            req.log_obj = self.env['hr.attendance']
            req.period_settings = req.config.period_settings
            sync_log(self, req )
