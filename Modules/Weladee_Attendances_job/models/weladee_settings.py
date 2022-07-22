# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_SYNC_JOB = 'weladee-sync-job'

class weladee_settings_job(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_job(self):
        return self._get_params_value(CONST_SETTING_SYNC_JOB) == 'Y'

    sync_job = fields.Boolean('Sync job', default=get_sync_job)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_job, self).get_settings()
        r.sync_job = self.get_sync_job()
               
        return r

    def saveBtn(self):
        ret = super(weladee_settings_job, self).saveBtn()

        config_pool = self.env['ir.config_parameter']

        self._save_setting(config_pool, CONST_SETTING_SYNC_JOB, "Y" if self.sync_job else "")
        return ret
