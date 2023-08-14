# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_JOB_PERIOD = 'weladee-job_period'
CONST_SETTING_JOB_PERIOD_UNIT = 'weladee-job_period_unit'

CONST_SETTING_SYNC_JOB = 'weladee-sync-job'

class weladee_settings_job(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_job(self):
        return self._get_params_value(CONST_SETTING_SYNC_JOB) == 'Y'
    
    @api.model
    def get_job_period_unit(self):
        return self._get_params_value(CONST_SETTING_JOB_PERIOD_UNIT, number=True, default=1)

    @api.model
    def get_job_period(self):
        return self._get_params_value(CONST_SETTING_JOB_PERIOD, number=False, default='w')

    job_period_unit = fields.Integer('Period unit',default=get_job_period_unit)
    job_period = fields.Selection([('w','week(s) ago'),
                                   ('m','month(s) ago'),
                                   ('y','year(s) ago'),
                                   ('all','All')],string='Since',default=get_job_period)
    
    sync_job = fields.Boolean('Sync job', default=get_sync_job)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_job, self).get_settings()
        r.sync_job = self.get_sync_job()

        r.job_period_unit = self.get_job_period_unit()
        r.job_period = self.get_job_period()
               
        return r

    def saveBtn(self):
        ret = super(weladee_settings_job, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        if self.sync_job:
           self._save_setting(config_pool, CONST_SETTING_JOB_PERIOD_UNIT, self.job_period_unit)
           self._save_setting(config_pool, CONST_SETTING_JOB_PERIOD, self.job_period)

        self._save_setting(config_pool, CONST_SETTING_SYNC_JOB, "Y" if self.sync_job else "")
        return ret
