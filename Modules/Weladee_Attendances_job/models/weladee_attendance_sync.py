# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_job.models.sync.weladee_job_ads import sync_job_ads
from odoo.addons.Weladee_Attendances_job.models.sync.weladee_job_app import sync_job_applicant

class weladee_attendance_job(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_job, self).init_param()

        # for job
        r.jobads_obj = False  
        r.jobapp_obj = False 
        r.job_ads_odoo_weladee_ids = {}
        ''' map job, key: weladee job id,value: job odoo id'''

        r.lang_obj = False
        r.utm_source_obj = False
        r.translation_obj = False

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_job, self).do_sync_options(req)

        if req.config.sync_job and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Job ads")
            test_key = self.env['ir.config_parameter'].get_param('test-k1')
            if test_key:
               req.config.authorization = [('authorization', test_key)]
            req.jobads_obj = self.env['weladee_job_ads']
            req.jobapp_obj = self.env['hr.applicant']
            sync_job_ads(req)

            if test_key:
               req.config = self.env['weladee_attendance.synchronous.setting'].get_settings()

        if req.config.sync_job and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync,"Start sync...Job applicant")
            req.lang_obj = self.env['res.lang']
            req.utm_source_obj = self.env['utm.source']
            req.translation_obj = self.env['ir.translation']
            sync_job_applicant(req)
