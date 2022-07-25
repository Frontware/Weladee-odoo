# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_SYNC_APPROVAL = 'weladee-sync-approval'
CONST_SETTING_APPROVAL_PERIOD = 'weladee-approval_period'
CONST_SETTING_APPROVAL_PERIOD_UNIT = 'weladee-approval_period_unit'

class weladee_settings_approval(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_approval(self):
        return self._get_params_value(CONST_SETTING_SYNC_APPROVAL) == 'Y'

    @api.model
    def get_approval_period_unit(self):
        return self._get_params_value(CONST_SETTING_APPROVAL_PERIOD_UNIT, number=True, default=1)

    @api.model
    def get_approval_period(self):
        return self._get_params_value(CONST_SETTING_APPROVAL_PERIOD, number=False, default='w')


    approval_period_unit = fields.Integer('Period unit',default=get_approval_period_unit)
    approval_period = fields.Selection([('w','week(s) ago'),
                                   ('m','month(s) ago'),
                                   ('y','year(s) ago'),
                                   ('all','All')],string='Since',default=get_approval_period)

    sync_approval = fields.Boolean('Sync Approval', default=get_sync_approval)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_approval, self).get_settings()
        r.sync_approval = self.get_sync_approval()

        r.approval_period_unit = self.get_approval_period_unit()
        r.approval_period = self.get_approval_period()

        return r

    def saveBtn(self):
        ret = super(weladee_settings_approval, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        if self.sync_approval:
            self._save_setting(config_pool, CONST_SETTING_APPROVAL_PERIOD_UNIT, self.approval_period_unit)
            self._save_setting(config_pool, CONST_SETTING_APPROVAL_PERIOD, self.approval_period)

        self._save_setting(config_pool, CONST_SETTING_SYNC_APPROVAL, "Y" if self.sync_approval else "")
        return ret
