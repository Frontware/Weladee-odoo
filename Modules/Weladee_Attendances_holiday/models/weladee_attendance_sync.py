# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_stop, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_holiday.models.sync.weladee_holiday import sync_holiday 

class weladee_attendance_holiday(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_holiday, self).init_param()

        # for holiday
        r.leave_obj = False  
        r.company_holiday_obj = False

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_holiday, self).do_sync_options(req)

        if req.config.sync_holiday and not sync_has_error(req.context_sync):

            if not req.config.tz:
               sync_stop(req.context_sync)
               sync_logerror(req.context_sync,'Please setup Timezone at Weladee settings -> Holiday')
               return

            if not req.config.holiday_status_id:
               sync_stop(req.context_sync)
               sync_logerror(req.context_sync,'Please setup Holiday status at Weladee settings -> Holiday')
               return

            if not req.config.sick_status_id:
               sync_stop(req.context_sync)
               sync_logerror(req.context_sync,'Please setup Sick status at Weladee settings -> Holiday')
               return

            sync_logdebug(req.context_sync,"Start sync...Holiday")
            req.leave_obj = self.env['hr.leave']
            req.company_holiday_obj = self.env['weladee_attendance.company.holidays']
            sync_holiday(self, req)
