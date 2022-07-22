# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID = 'weladee-timesheet_account_analytic_id'
CONST_SETTING_TIMESHEET_PERIOD = 'weladee-timesheet_period'
CONST_SETTING_TIMESHEET_PERIOD_UNIT = 'weladee-timesheet_period_unit'

CONST_SETTING_SYNC_TIMESHEET = 'weladee-sync-timesheet'

class weladee_settings_timesheet(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_timesheet(self):
        return self._get_params_value(CONST_SETTING_SYNC_TIMESHEET) == 'Y'

    @api.model
    def get_timesheet_period_unit(self):
        return self._get_params_value(CONST_SETTING_TIMESHEET_PERIOD_UNIT, number=True, default=1)

    @api.model
    def get_timesheet_period(self):
        return self._get_params_value(CONST_SETTING_TIMESHEET_PERIOD, number=False, default='w')

    @api.model
    def get_timesheet_account_analytic(self):
        return self._get_params_value(CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID, number=True)

    timesheet_period_unit = fields.Integer('Period Unit', default=get_timesheet_period_unit)
    timesheet_period = fields.Selection([('w','week(s) ago'),
                                        ('m','month(s) ago'),
                                        ('y','year(s) ago'),
                                        ('all', 'All')], string='Since', default=get_timesheet_period)
    timehsheet_account_analytic_id = fields.Many2one('account.analytic.account', string="Account Analytic", default=get_timesheet_account_analytic)
    sync_timesheet = fields.Boolean('Sync Timesheet', default=get_sync_timesheet)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_timesheet, self).get_settings()
        r.sync_timesheet = self.get_sync_timesheet()
        
        r.timesheet_period_unit = self.get_timesheet_period_unit()
        r.timesheet_period = self.get_timesheet_period()
        r.timehsheet_account_analytic_id = self.get_timesheet_account_analytic()
       
        return r

    def saveBtn(self):
        ret = super(weladee_settings_timesheet, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        if self.sync_timesheet:
           self._save_setting(config_pool, CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID, self.timehsheet_account_analytic_id.id)
           self._save_setting(config_pool, CONST_SETTING_TIMESHEET_PERIOD_UNIT, self.timesheet_period_unit)
           self._save_setting(config_pool, CONST_SETTING_TIMESHEET_PERIOD, self.timesheet_period)

        self._save_setting(config_pool, CONST_SETTING_SYNC_TIMESHEET, "Y" if self.sync_timesheet else "")
        return ret
