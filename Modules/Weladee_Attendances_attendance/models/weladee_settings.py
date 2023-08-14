# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_LOG_PERIOD = 'weladee-log_period'
CONST_SETTING_LOG_PERIOD_UNIT = 'weladee-log_period_unit'

CONST_SETTING_SYNC_ATTENDANCE = 'weladee-sync-attendance'

class weladee_settings_attendance(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_attendance(self):
        return self._get_params_value(CONST_SETTING_SYNC_ATTENDANCE) == 'Y'
   
    @api.model
    def get_log_period_unit(self):
        return self._get_params_value(CONST_SETTING_LOG_PERIOD_UNIT, number=True, default=1)

    @api.model
    def get_log_period(self):
        return self._get_params_value(CONST_SETTING_LOG_PERIOD, number=False, default='w')


    log_period_unit = fields.Integer('Period unit',default=get_log_period_unit)
    log_period = fields.Selection([('w','week(s) ago'),
                                   ('m','month(s) ago'),
                                   ('y','year(s) ago'),
                                   ('all','All')],string='Since',default=get_log_period)
    
    sync_attendance = fields.Boolean('Sync Attendance', default=get_sync_attendance)
    
    @api.model
    def get_settings(self):
        r = super(weladee_settings_attendance, self).get_settings()
        r.sync_attendance = self.get_sync_attendance()
        r.period_settings = {'period': self.get_log_period(), 'unit': self.get_log_period_unit()}       
        return r

    def saveBtn(self):
        ret = super(weladee_settings_attendance, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        if self.sync_attendance:
           self._save_setting(config_pool, CONST_SETTING_LOG_PERIOD_UNIT, self.log_period_unit)
           self._save_setting(config_pool, CONST_SETTING_LOG_PERIOD, self.log_period)


        self._save_setting(config_pool, CONST_SETTING_SYNC_ATTENDANCE, "Y" if self.sync_attendance else "")
        return ret
